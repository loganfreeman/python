def flatten(iterable):
    """Yield each element of 'iterable', recursively interpolating 
       lists and tuples.  Examples:
       [1, [2, 3], 4]  =>  iter([1, 2, 3, 4])
       [1, (2, 3, [4]), 5) => iter([1, 2, 3, 4, 5])
    """
    for elm in iterable:
        if isinstance(elm, (list, tuple)):
            for relm in flatten(elm):
                yield relm
        else:
            yield elm
