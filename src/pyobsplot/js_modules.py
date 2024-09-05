from collections.abc import Callable


class JSModule(type):
    """
    Metaclass to allow JavaScript module and methods handling.
    """

    def __getattr__(cls: type, name: str) -> Callable:
        """
        Intercept methods calling and returns a parsed and typed dict object.
        """

        def wrapper(*args, **kwargs) -> dict:
            if kwargs:
                msg = f"kwargs must not be passed to {cls.__name__}.{name} : {kwargs}"
                raise ValueError(msg)
            return {
                "pyobsplot-type": "function",
                "module": cls.__name__,
                "method": name,
                "args": args,
            }

        return wrapper


class d3(metaclass=JSModule):  # noqa: N801
    """
    JSModule class to allow d3 objects in specification.
    """

    pass


class Math(metaclass=JSModule):
    """
    JSModule class to allow Math objects in specification.
    """

    pass
