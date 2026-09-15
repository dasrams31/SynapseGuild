from __future__ import annotations
import functools
from typing import Any, Callable, Iterable, Optional
from pipeline import Step, Context, ErrorPolicy


class ValidationError(Exception):
    """Raised when data fails a ValidateStep assertion."""
    pass


class MapStep(Step):
    def __init__(
        self,
        mapper: Callable[[Any], Any],
        name: Optional[str] = None,
        error_policy: ErrorPolicy = ErrorPolicy.HALT,
        max_retries: int = 0,
        retry_delay: float = 0.0,
        iterate: bool = True,
    ) -> None:
        super().__init__(name=name, error_policy=error_policy, max_retries=max_retries, retry_delay=retry_delay)
        self.mapper = mapper
        self.iterate = iterate

    def execute(self, context: Context) -> Any:
        if self.iterate and isinstance(context.data, Iterable) and not isinstance(context.data, (str, bytes, dict)):
            return [self.mapper(item) for item in context.data]
        return self.mapper(context.data)


class FilterStep(Step):
    def __init__(
        self,
        predicate: Callable[[Any], bool],
        name: Optional[str] = None,
        error_policy: ErrorPolicy = ErrorPolicy.HALT,
        max_retries: int = 0,
        retry_delay: float = 0.0,
    ) -> None:
        super().__init__(name=name, error_policy=error_policy, max_retries=max_retries, retry_delay=retry_delay)
        self.predicate = predicate

    def execute(self, context: Context) -> Any:
        if isinstance(context.data, Iterable) and not isinstance(context.data, (str, bytes, dict)):
            return [item for item in context.data if self.predicate(item)]
        elif isinstance(context.data, dict):
            return {k: v for k, v in context.data.items() if self.predicate((k, v))}
        else:
            return context.data if self.predicate(context.data) else None


class ValidateStep(Step):
    def __init__(
        self,
        validator: Callable[[Any], bool],
        error_message: str = "Validation failed",
        name: Optional[str] = None,
        error_policy: ErrorPolicy = ErrorPolicy.HALT,
        max_retries: int = 0,
        retry_delay: float = 0.0,
    ) -> None:
        super().__init__(name=name, error_policy=error_policy, max_retries=max_retries, retry_delay=retry_delay)
        self.validator = validator
        self.error_message = error_message

    def execute(self, context: Context) -> Any:
        valid = self.validator(context.data)
        if not valid:
            raise ValidationError(self.error_message)
        return context.data


class AggregateStep(Step):
    def __init__(
        self,
        reducer: Callable[[Any, Any], Any],
        initial: Any = None,
        name: Optional[str] = None,
        error_policy: ErrorPolicy = ErrorPolicy.HALT,
        max_retries: int = 0,
        retry_delay: float = 0.0,
    ) -> None:
        super().__init__(name=name, error_policy=error_policy, max_retries=max_retries, retry_delay=retry_delay)
        self.reducer = reducer
        self.initial = initial

    def execute(self, context: Context) -> Any:
        if not isinstance(context.data, Iterable) or isinstance(context.data, (str, bytes)):
            raise TypeError(f"AggregateStep expects iterable data, got {type(context.data).__name__}")
        
        items = list(context.data)
        if not items and self.initial is None:
            raise ValueError("AggregateStep received empty sequence with no initial value")

        if self.initial is not None:
            return functools.reduce(self.reducer, items, self.initial)
        return functools.reduce(self.reducer, items)
