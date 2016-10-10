def load_config(tricks_file_pathname):
    """
    Loads the YAML configuration from the specified file.
    :param tricks_file_path:
        The path to the tricks configuration file.
    :returns:
        A dictionary of configuration information.
    """
    f = open(tricks_file_pathname, 'rb')
    content = f.read()
    f.close()
    config = yaml.load(content)
    return config
