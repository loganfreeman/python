def detect_flask_apps():
    """
    Automatically try to discover Flask apps files,
    return them as relative module paths.
    """

    matches = []
    for root, dirnames, filenames in os.walk(os.getcwd()):
        for filename in fnmatch.filter(filenames, '*.py'):
            full = os.path.join(root, filename)
            if 'site-packages' in full:
                continue

            full = os.path.join(root, filename)

            with open(full, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    app = None

                    # Kind of janky..
                    if '= Flask(' in line:
                        app = line.split('= Flask(')[0].strip()
                    if '=Flask(' in line:
                        app = line.split('=Flask(')[0].strip()

                    if not app:
                        continue

                    package_path = full.replace(os.getcwd(), '')
                    package_module = package_path.replace(os.sep, '.').split('.', 1)[1].replace('.py', '')
                    app_module = package_module + '.' + app

                    matches.append(app_module)

    return matches
