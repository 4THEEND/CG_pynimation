from typing import Dict, Any


class _Singleton(type):
    """
    Singleton base class. Classes inheriting from this class will only ever
    have one instance. The first constructor call will create the object and
    return it. Later calls will return the existing instance
    """

    _instances: Dict[Any, Any] = {}

    def __call__(cls, *args, **kwargs) -> Any:
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls]
