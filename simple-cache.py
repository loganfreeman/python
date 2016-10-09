def simple_cache(func):
    """
    Save results for the :meth:'path.using_module' classmethod.
    When Python 3.2 is available, use functools.lru_cache instead.
    """
    saved_results = {}

    def wrapper(cls, module):
        if module in saved_results:
            return saved_results[module]
        saved_results[module] = func(cls, module)
        return saved_results[module]
    return wrapper
