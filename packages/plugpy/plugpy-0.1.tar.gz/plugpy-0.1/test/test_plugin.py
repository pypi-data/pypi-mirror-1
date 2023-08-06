from plugpy import *

config = dict(plugin_path='./test/plugin', debug=True)

def test_load():
    res = load_plugins(config)
    assert res != None
    assert len(res) == 2

def test_dispath():
    res = reload_plugins(config)
    res = dispatch('test', 1,2)
    print res
    assert res != None
    assert len(res) == 1
    assert res[0][0] == 3
