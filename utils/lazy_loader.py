import functools
from typing import Any, Callable, Dict, Optional

class LazyProperty:
    """Descriptor for lazy initialization of properties"""

    def __init__(self, func: Callable):
        self.func = func
        self.attr_name = f"_lazy_{func.__name__}"
        functools.update_wrapper(self, func)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        if not hasattr(instance, self.attr_name):
            value = self.func(instance)
            setattr(instance, self.attr_name, value)

        return getattr(instance, self.attr_name)

    def __set__(self, instance, value):
        setattr(instance, self.attr_name, value)

    def __delete__(self, instance):
        if hasattr(instance, self.attr_name):
            delattr(instance, self.attr_name)

class LazyLoader:
    """Centralized lazy loading manager"""

    def __init__(self):
        self._instances: Dict[str, Any] = {}
        self._cleanup_handlers: Dict[str, Callable] = {}

    def register_lazy_property(self, name: str, factory: Callable[[], Any], 
                             cleanup: Optional[Callable[[Any], None]] = None):
        if cleanup:
            self._cleanup_handlers[name] = cleanup

        def property_getter(self):
            if name not in self._instances:
                self._instances[name] = factory()
            return self._instances[name]

        return property(property_getter)

    def get_or_create(self, name: str, factory: Callable[[], Any]) -> Any:
        if name not in self._instances:
            self._instances[name] = factory()
        return self._instances[name]

    def cleanup_instance(self, name: str) -> None:
        if name in self._instances:
            instance = self._instances[name]
            if name in self._cleanup_handlers:
                try:
                    self._cleanup_handlers[name](instance)
                except Exception:
                    pass
            del self._instances[name]

    def cleanup_all(self) -> None:
        for name in list(self._instances.keys()):
            self.cleanup_instance(name)

def lazy_property(func):
    return LazyProperty(func)

_global_lazy_loader = LazyLoader()

def get_global_lazy_loader() -> LazyLoader:
    return _global_lazy_loader

def cleanup_lazy_components():
    _global_lazy_loader.cleanup_all()