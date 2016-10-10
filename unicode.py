# Use unicode strings if possible.
_base = str               # Python 3 str (=unicode), or Python 2 bytes.
if os.path.supports_unicode_filenames:
    try:
        _base = unicode   # Python 2 unicode.
    except NameError:
        pass
