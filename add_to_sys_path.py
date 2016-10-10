def add_to_sys_path(pathnames, index=0):
    """
    Adds specified paths at specified index into the sys.path list.
    :param paths:
        A list of paths to add to the sys.path
    :param index:
        (Default 0) The index in the sys.path list where the paths will be
        added.
    """
    for pathname in pathnames[::-1]:
        sys.path.insert(index, pathname)
