from __future__ import annotations
import asyncio
import enum
import inspect
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union


class ErrorPolicy(str, enum.Enum):
    HALT = "HALT"
    SKIP = "SKIP"
    RETRY = "RETRY"


class StepStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    RETRIED = "RETRIED"


@dataclass
class StepExecutionRecord:
    step_name: str
    status: StepStatus
    start_time: float
    end_time: float
    duration: float
    error: Optional[str] = None
    attempts: int = 1


@dataclass
class Context:
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[StepExecutionRecord] = field(default_factory=list)
    halted: bool = False
    error: Optional[Exception] = None

    def get(self, key: str, default: Any = None) -> Any:
        return self.metadata.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.metadata[key] = value

    def log_record(self, record: StepExecutionRecord) -> None:
        self.history.append(record)


class Step(ABC):
    def __init__(
        self,
        name: Optional[str] = None,
        error_policy: ErrorPolicy = ErrorPolicy.HALT,
        max_retries: int = 0,
        retry_delay: float = 0.0,
    ) -> None:
        self.name = name or self.__class__.__name__
        self.error_policy = error_policy
        self.max_retries = max(0, max_retries)
        self.retry_delay = max(0.0, retry_delay)

    @abstractmethod
    def execute(self, context: Context) -> Union[Context, Any]:
        """Executes the step logic, returning updated Context or updated data."""
        pass

    def on_failure(self, context: Context, error: Exception) -> Optional[Context]:
        """Hook called when execution encounters an unhandled exception."""
        return None


class LambdaStep(Step):
    def __init__(
        self,
        fn: Callable[[Context], Any],
        name: Optional[str] = None,
        error_policy: ErrorPolicy = ErrorPolicy.HALT,
        max_retries: int = 0,
        retry_delay: float = 0.0,
    ) -> None:
        super().__init__(name=name, error_policy=error_policy, max_retries=max_retries, retry_delay=retry_delay)
        self.fn = fn

    def execute(self, context: Context) -> Any:
        return self.fn(context)


class Pipeline:
    def __init__(self, name: str = "Pipeline", default_policy: ErrorPolicy = ErrorPolicy.HALT) -> None:
        self.name = name
        self.default_policy = default_policy
        self.steps: List[Step] = []

    def add_step(self, step: Union[Step, Callable[[Context], Any]]) -> Pipeline:
        if isinstance(step, Step):
            self.steps.append(step)
        elif callable(step):
            self.steps.append(LambdaStep(fn=step, name=getattr(step, "__name__", "lambda_step")))
        else:
            raise TypeError(f"Invalid step type: {type(step)}")
        return self

    def pipe(self, step: Union[Step, Callable[[Context], Any]]) -> Pipeline:
        return self.add_step(step)

    async def _execute_step_logic(self, step: Step, context: Context) -> Context:
        attempts = 0
        max_attempts = 1 + (step.max_retries if step.error_policy == ErrorPolicy.RETRY else 0)

        start_time = time.time()
        last_error: Optional[Exception] = None

        while attempts < max_attempts:
            attempts += 1
            try:
                if inspect.iscoroutinefunction(step.execute):
                    res = await step.execute(context)
                else:
                    res = step.execute(context)

                if inspect.isawaitable(res):
                    res = await res

                if isinstance(res, Context):
                    context = res
                else:
                    context.data = res

                end_time = time.time()
                context.log_record(
                    StepExecutionRecord(
                        step_name=step.name,
                        status=StepStatus.SUCCESS,
                        start_time=start_time,
                        end_time=end_time,
                        duration=end_time - start_time,
                        attempts=attempts,
                    )
                )
                return context
            except Exception as exc:
                last_error = exc
                if attempts < max_attempts and step.error_policy == ErrorPolicy.RETRY:
                    if step.retry_delay > 0:
                        await asyncio.sleep(step.retry_delay)
                    continue
                break

        end_time = time.time()
        err_str = f"{type(last_error).__name__}: {str(last_error)}"
        context.error = last_error

        fallback_res = step.on_failure(context, last_error)
        if isinstance(fallback_res, Context):
            context = fallback_res

        policy = step.error_policy or self.default_policy

        if policy == ErrorPolicy.SKIP:
            context.log_record(
                StepExecutionRecord(
                    step_name=step.name,
                    status=StepStatus.SKIPPED,
                    start_time=start_time,
                    end_time=end_time,
                    duration=end_time - start_time,
                    error=err_str,
                    attempts=attempts,
                )
            )
            context.error = None
            return context
        else:
            context.log_record(
                StepExecutionRecord(
                    step_name=step.name,
                    status=StepStatus.FAILED,
                    start_time=start_time,
                    end_time=end_time,
                    duration=end_time - start_time,
                    error=err_str,
                    attempts=attempts,
                )
            )
            context.halted = True
            return context

    async def run_async(
        self, initial_data: Any = None, initial_metadata: Optional[Dict[str, Any]] = None
    ) -> Context:
        context = Context(
            data=initial_data,
            metadata=dict(initial_metadata) if initial_metadata else {},
        )

        for step in self.steps:
            if context.halted:
                break
            context = await self._execute_step_logic(step, context)

        return context

    def run(self, initial_data: Any = None, initial_metadata: Optional[Dict[str, Any]] = None) -> Context:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in an active event loop (e.g. jupyter, nested),
                # run step-by-step synchronously where possible or via task
                import nest_asyncio  # optional fallback
                nest_asyncio.apply()
                return loop.run_until_complete(self.run_async(initial_data, initial_metadata))
            return loop.run_until_complete(self.run_async(initial_data, initial_metadata))
        except RuntimeError:
            return asyncio.run(self.run_async(initial_data, initial_metadata))
