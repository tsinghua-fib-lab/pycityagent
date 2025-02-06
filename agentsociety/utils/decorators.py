import time
import functools
import inspect

CALLING_STRING = 'function: `{func_name}` in "{file_path}", line {line_number}, arguments: `{arguments}` start time: `{start_time}` end time: `{end_time}` output: `{output}`'

__all__ = [
    "record_call_aio",
    "record_call",
    "lock_decorator",
]


def record_call_aio(record_function_calling: bool = True):
    """
    Decorator to log the async function call details if `record_function_calling` is True.
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            cur_frame = inspect.currentframe()
            assert cur_frame is not None
            frame = cur_frame.f_back
            assert frame is not None
            line_number = frame.f_lineno
            file_path = frame.f_code.co_filename
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            start_time = time.time()
            result = await func(*args, **kwargs)
            end_time = time.time()
            if record_function_calling:
                print(
                    CALLING_STRING.format(
                        func_name=func,
                        line_number=line_number,
                        file_path=file_path,
                        arguments=signature,
                        start_time=start_time,
                        end_time=end_time,
                        output=result,
                    )
                )
            return result

        return wrapper

    return decorator


def record_call(record_function_calling: bool = True):
    """
    Decorator to log the function call details if `record_function_calling` is True.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            cur_frame = inspect.currentframe()
            assert cur_frame is not None
            frame = cur_frame.f_back
            assert frame is not None
            line_number = frame.f_lineno
            file_path = frame.f_code.co_filename
            args_repr = [repr(a) for a in args]
            kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
            signature = ", ".join(args_repr + kwargs_repr)
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            if record_function_calling:
                print(
                    CALLING_STRING.format(
                        func_name=func,
                        line_number=line_number,
                        file_path=file_path,
                        arguments=signature,
                        start_time=start_time,
                        end_time=end_time,
                        output=result,
                    )
                )
            return result

        return wrapper

    return decorator


def lock_decorator(func):
    async def wrapper(self, *args, **kwargs):
        lock = self._lock
        await lock.acquire()
        try:
            return await func(self, *args, **kwargs)
        finally:
            lock.release()

    return wrapper
