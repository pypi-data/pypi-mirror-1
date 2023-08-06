from wfront import _internal


def test_import_dotted_path():
    assert _internal._string_loader('sys.path')

    mod = _internal._string_loader('os.path')
    assert isinstance(mod, type(_internal))

    try:
        _internal._string_loader('wfront.squiznart')
        assert False
    except NameError:
        assert True

    try:
        _internal._string_loader('zojosjdfoijowjofijsoidfjos')
        assert False
    except ImportError:
        assert True

def test_import_path_eval():
    assert _internal._string_loader('sys:path')
    assert _internal._string_loader('os:environ["PATH"]')
