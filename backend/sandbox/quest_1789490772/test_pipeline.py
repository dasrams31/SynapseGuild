import asyncio
import unittest
from pipeline import Pipeline, Step, Context, ErrorPolicy, StepStatus
from transformers import MapStep, FilterStep, ValidateStep, AggregateStep, ValidationError


class FlakyStep(Step):
    def __init__(self, fail_times: int, name: str = "FlakyStep", **kwargs):
        super().__init__(name=name, **kwargs)
        self.fail_times = fail_times
        self.attempts = 0

    def execute(self, context: Context):
        self.attempts += 1
        if self.attempts <= self.fail_times:
            raise RuntimeError(f"Failure attempt {self.attempts}")
        return context.data + 10


class TestPipelineEngine(unittest.TestCase):
    def test_linear_execution_with_transformers(self):
        pipeline = Pipeline(name="ETL_Pipeline")
        pipeline.pipe(FilterStep(lambda x: x % 2 == 0, name="FilterEvens")) \
                .pipe(MapStep(lambda x: x * 10, name="MultiplyTen")) \
                .pipe(ValidateStep(lambda data: all(x >= 20 for x in data), name="ValidateAllGTE20")) \
                .pipe(AggregateStep(lambda acc, x: acc + x, initial=0, name="SumAll"))

        context = pipeline.run(initial_data=[1, 2, 3, 4, 5, 6])

        # Filter: [2, 4, 6], Map: [20, 40, 60], Validate: Pass, Sum: 120
        self.assertEqual(context.data, 120)
        self.assertFalse(context.halted)
        self.assertIsNone(context.error)
        self.assertEqual(len(context.history), 4)
        for record in context.history:
            self.assertEqual(record.status, StepStatus.SUCCESS)
            self.assertGreaterEqual(record.duration, 0.0)

    def test_halt_policy_on_failure(self):
        pipeline = Pipeline(name="HaltPipeline")
        executed_after_fail = False

        def doomed_step(ctx: Context):
            raise ValueError("Unrecoverable catastrophe")

        def step_after(ctx: Context):
            nonlocal executed_after_fail
            executed_after_fail = True
            return ctx

        pipeline.pipe(MapStep(lambda x: x + 1, name="FirstStep")) \
                .pipe(ValidateStep(lambda x: False, error_message="Forced Fail", error_policy=ErrorPolicy.HALT, name="FailingValidation")) \
                .pipe(step_after)

        ctx = pipeline.run(initial_data=10)

        self.assertTrue(ctx.halted)
        self.assertIsInstance(ctx.error, ValidationError)
        self.assertFalse(executed_after_fail)
        self.assertEqual(len(ctx.history), 2)
        self.assertEqual(ctx.history[0].status, StepStatus.SUCCESS)
        self.assertEqual(ctx.history[1].status, StepStatus.FAILED)

    def test_skip_policy_on_failure(self):
        pipeline = Pipeline(name="SkipPipeline")

        class NonFatalStep(Step):
            def execute(self, context: Context):
                raise ArithmeticError("Ignorable calculation error")

        pipeline.pipe(MapStep(lambda x: [x, x + 1], name="InitStep")) \
                .pipe(NonFatalStep(name="SkippedStep", error_policy=ErrorPolicy.SKIP)) \
                .pipe(MapStep(lambda items: [i * 2 for i in items], iterate=False, name="NextStep"))

        ctx = pipeline.run(initial_data=5)

        self.assertFalse(ctx.halted)
        self.assertIsNone(ctx.error)
        self.assertEqual(ctx.data, [10, 12])
        self.assertEqual(len(ctx.history), 3)
        self.assertEqual(ctx.history[1].status, StepStatus.SKIPPED)

    def test_retry_policy_success(self):
        pipeline = Pipeline(name="RetryPipeline")
        step = FlakyStep(fail_times=2, max_retries=3, retry_delay=0.01, error_policy=ErrorPolicy.RETRY)
        pipeline.pipe(step)

        ctx = pipeline.run(initial_data=5)

        self.assertFalse(ctx.halted)
        self.assertEqual(ctx.data, 15)
        self.assertEqual(step.attempts, 3)
        self.assertEqual(len(ctx.history), 1)
        self.assertEqual(ctx.history[0].status, StepStatus.SUCCESS)
        self.assertEqual(ctx.history[0].attempts, 3)

    def test_retry_policy_exhausted(self):
        pipeline = Pipeline(name="RetryExhaustPipeline")
        step = FlakyStep(fail_times=3, max_retries=1, retry_delay=0.01, error_policy=ErrorPolicy.RETRY)
        pipeline.pipe(step)

        ctx = pipeline.run(initial_data=5)

        self.assertTrue(ctx.halted)
        self.assertEqual(step.attempts, 2)
        self.assertEqual(len(ctx.history), 1)
        self.assertEqual(ctx.history[0].status, StepStatus.FAILED)
        self.assertEqual(ctx.history[0].attempts, 2)

    def test_async_execution(self):
        async def run_test():
            pipeline = Pipeline(name="AsyncPipeline")

            class AsyncStep(Step):
                async def execute(self, context: Context):
                    await asyncio.sleep(0.01)
                    return context.data.upper()

            pipeline.pipe(AsyncStep(name="ToUpper")) \
                    .pipe(MapStep(lambda s: f"Processed: {s}", iterate=False, name="Format"))

            ctx = await pipeline.run_async(initial_data="forge")
            return ctx

        ctx = asyncio.run(run_test())
        self.assertEqual(ctx.data, "Processed: FORGE")
        self.assertFalse(ctx.halted)
        self.assertEqual(len(ctx.history), 2)

    def test_metadata_context_operations(self):
        pipeline = Pipeline()
        
        def meta_writer(ctx: Context):
            ctx.set("user", "craftsman")
            ctx.set("role", "builder")
            return ctx.data

        pipeline.pipe(meta_writer)
        ctx = pipeline.run(initial_data="hello", initial_metadata={"env": "production"})

        self.assertEqual(ctx.get("env"), "production")
        self.assertEqual(ctx.get("user"), "craftsman")
        self.assertEqual(ctx.get("role"), "builder")
        self.assertEqual(ctx.get("nonexistent", "default"), "default")


if __name__ == "__main__":
    unittest.main()
