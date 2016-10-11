def detect_django_settings():
    """
    Automatically try to discover Django settings files,
    return them as relative module paths.
    """

    matches = []
    for root, dirnames, filenames in os.walk(os.getcwd()):
        for filename in fnmatch.filter(filenames, '*settings.py'):
            full = os.path.join(root, filename)
            if 'site-packages' in full:
                continue
            full = os.path.join(root, filename)
            package_path = full.replace(os.getcwd(), '')
            package_module = package_path.replace(os.sep, '.').split('.', 1)[1].replace('.py', '')

            matches.append(package_module)
    return matches
