def create_lambda_zip(self, prefix='lambda_package', handler_file=None,
                      minify=True, exclude=None, use_precompiled_packages=True, include=None, venv=None):
    """
    Create a Lambda-ready zip file of the current virtualenvironment and working directory.
    Returns path to that file.
    """
    import pip

    print("Packaging project as zip...")

    if not venv:
        if 'VIRTUAL_ENV' in os.environ:
            venv = os.environ['VIRTUAL_ENV']
        elif os.path.exists('.python-version'):  # pragma: no cover
            logger.debug("Pyenv's local virtualenv detected.")
            try:
                subprocess.check_output('pyenv', stderr=subprocess.STDOUT)
            except OSError:
                print("This directory seems to have pyenv's local venv"
                      "but pyenv executable was not found.")
            with open('.python-version', 'r') as f:
                env_name = f.read()[:-1]
                logger.debug('env name = {}'.format(env_name))
            bin_path = subprocess.check_output(['pyenv', 'which', 'python']).decode('utf-8')
            venv = bin_path[:bin_path.rfind(env_name)] + env_name
            logger.debug('env path = {}'.format(venv))
        else:  # pragma: no cover
            print("Zappa requires an active virtual environment.")
            quit()

    cwd = os.getcwd()
    zip_fname = prefix + '-' + str(int(time.time())) + '.zip'
    zip_path = os.path.join(cwd, zip_fname)

    # Files that should be excluded from the zip
    if exclude is None:
        exclude = list()

    # Exclude the zip itself
    exclude.append(zip_path)

    def splitpath(path):
        parts = []
        (path, tail) = os.path.split(path)
        while path and tail:
            parts.append(tail)
            (path, tail) = os.path.split(path)
        parts.append(os.path.join(path, tail))
        return map(os.path.normpath, parts)[::-1]
    split_venv = splitpath(venv)
    split_cwd = splitpath(cwd)

    # Ideally this should be avoided automatically,
    # but this serves as an okay stop-gap measure.
    if split_venv[-1] == split_cwd[-1]:  # pragma: no cover
        print(
            "Warning! Your project and virtualenv have the same name! You may want "
            "to re-create your venv with a new name, or explicitly define a "
            "'project_name', as this may cause errors."
        )

    # First, do the project..
    temp_project_path = os.path.join(tempfile.gettempdir(), str(int(time.time())))

    if minify:
        excludes = ZIP_EXCLUDES + exclude + [split_venv[-1]]
        copytree(cwd, temp_project_path, symlinks=False, ignore=shutil.ignore_patterns(*excludes))
    else:
        copytree(cwd, temp_project_path, symlinks=False)

    # Then, do the site-packages..
    temp_package_path = os.path.join(tempfile.gettempdir(), str(int(time.time() + 1)))
    if os.sys.platform == 'win32':
        site_packages = os.path.join(venv, 'Lib', 'site-packages')
    else:
        site_packages = os.path.join(venv, 'lib', 'python2.7', 'site-packages')
    if minify:
        excludes = ZIP_EXCLUDES + exclude
        copytree(site_packages, temp_package_path, symlinks=False, ignore=shutil.ignore_patterns(*excludes))
    else:
        copytree(site_packages, temp_package_path, symlinks=False)

    # We may have 64-bin specific packages too.
    site_packages_64 = os.path.join(venv, 'lib64', 'python2.7', 'site-packages')
    if os.path.exists(site_packages_64):
        if minify:
            excludes = ZIP_EXCLUDES + exclude
            copytree(site_packages_64, temp_package_path, symlinks=False, ignore=shutil.ignore_patterns(*excludes))
        else:
            copytree(site_packages_64, temp_package_path, symlinks=False)

    copy_tree(temp_package_path, temp_project_path, update=True)

    # Then the pre-compiled packages..
    if use_precompiled_packages:
        installed_packages_name_set = {package.project_name.lower() for package in
                                       pip.get_installed_distributions()}

        for name, details in lambda_packages.items():
            if name.lower() in installed_packages_name_set:
                tar = tarfile.open(details['path'], mode="r:gz")
                for member in tar.getmembers():
                    # If we can, trash the local version.
                    if member.isdir():
                        shutil.rmtree(os.path.join(temp_project_path, member.name), ignore_errors=True)
                        continue

                    tar.extract(member, temp_project_path)

    # If a handler_file is supplied, copy that to the root of the package,
    # because that's where AWS Lambda looks for it. It can't be inside a package.
    if handler_file:
        filename = handler_file.split(os.sep)[-1]
        shutil.copy(handler_file, os.path.join(temp_project_path, filename))

    # Then zip it all up..
    try:
        # import zlib
        compression_method = zipfile.ZIP_DEFLATED
    except ImportError:  # pragma: no cover
        compression_method = zipfile.ZIP_STORED

    zipf = zipfile.ZipFile(zip_path, 'w', compression_method)
    for root, dirs, files in os.walk(temp_project_path):

        for filename in files:

            # If there is a .pyc file in this package,
            # we can skip the python source code as we'll just
            # use the compiled bytecode anyway..
            if filename[-3:] == '.py':
                abs_filname = os.path.join(root, filename)
                abs_pyc_filename = abs_filname + 'c'
                if os.path.isfile(abs_pyc_filename):

                    # but only if the pyc is older than the py,
                    # otherwise we'll deploy outdated code!
                    py_time = os.stat(abs_filname).st_mtime
                    pyc_time = os.stat(abs_pyc_filename).st_mtime

                    if pyc_time > py_time:
                        continue

            zipf.write(os.path.join(root, filename), os.path.join(root.replace(temp_project_path, ''), filename))

        if '__init__.py' not in files:
            tmp_init = os.path.join(temp_project_path, '__init__.py')
            open(tmp_init, 'a').close()
            zipf.write(tmp_init, os.path.join(root.replace(temp_project_path, ''), os.path.join(root.replace(temp_project_path, ''), '__init__.py')))

    # And, we're done!
    zipf.close()

    # Trash the temp directory
    shutil.rmtree(temp_project_path)
    shutil.rmtree(temp_package_path)

    # Warn if this is too large for Lambda.
    file_stats = os.stat(zip_path)
    if file_stats.st_size > 52428800:  # pragma: no cover
        print("\n\nWarning: Application zip package is likely to be too large for AWS Lambda.\n\n")

    return zip_fname
