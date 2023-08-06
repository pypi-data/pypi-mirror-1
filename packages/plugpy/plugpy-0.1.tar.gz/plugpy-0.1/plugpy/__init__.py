import sys
import os
import os.path as path
import logging

VERSION = (0, 1, None)

default_plugin_path = os.path.join(os.environ['HOME'], '.plugpy/plugins')

_instance = []

#DEBUG = False
#logger = None

def setup_log():
    global logger
    logger = logging.getLogger(__name__)
    hdlr = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.DEBUG)
    global DEBUG
    DEBUG = True

def debug(msg):
    if DEBUG:
        logger.debug(msg)

class Plugin(object):
    
    priority = 0    

    def __init__(self, *args, **kwargs):
        pass


def list_module(dir):
    if path.isdir(dir):
        return [path.splitext(file)[0] for file in os.listdir(dir) if not
                file.startswith('__') and file.endswith('.py')]
    return []

def init_plugins(config):
    
    if not default_plugin_path in sys.path:
        sys.path.insert(0, default_plugin_path)
        debug('add sys.path %s' % default_plugin_path)

    plugin_path = config.get('plugin_path', './plugin')
    if not plugin_path in sys.path:
        sys.path.insert(0, plugin_path)
        debug('add sys.path %s' % plugin_path)
    
    plugins = []
    plugins.extend(list_module(default_plugin_path) or [])
    plugins.extend(list_module(plugin_path) or [])
    
    import_plugins(plugins)

def import_plugins(plugins):
    for plugin in plugins:
        if plugin:
            __import__(plugin, None, None, [''])
            debug('import plugin %s' % plugin)

def find_plugins(plugin_class):
    res = []
    for clazz in plugin_class:
        sub = clazz.__subclasses__()
        debug("find plugin class %s's plugin classes %s" % (clazz, sub))
        res.extend(sub)
    
    def _key(clazz):
        if hasattr(clazz, "priority"):
            return clazz.priority
        return clazz

    res.sort(key=_key)
    debug('all target plugin classes %s' % res)
    return res

def load_plugins(config):
    if not config:
        config = dict()
    if config.get('debug', None):
        setup_log()
    
    debug('plugin load config %s' % config)
    init_plugins(config)
    results = []
    for plug in find_plugins(config.get('plugin_class', [Plugin])):
        if plug in config.get('ignore_plugin', []):
            continue

        ins = plug(**config)
        if  not ins in _instance:
            _instance.append(ins)
        results.append(ins)

    debug('loaded plugins %s' % _instance)
    return results

def dispatch(message, *args, **kwargs):
    res = []
    clazz = kwargs.get('plugin_class', Plugin)
    prefix = kwargs.get('prefix', 'on_')
    attr = prefix + message
    debug("dispatch send message:'%s' call_method: '%s'" % (message, attr))
    for plugin in _instance:
        if issubclass(plugin.__class__, clazz) and hasattr(plugin, attr):
            func = getattr(plugin, attr)
            result = func(*args, **kwargs)
            debug("dispatch to %s call_method '%s' arg_info: %s %s : result %s" % (plugin, attr,
                args, kwargs, result ))
            res.append((result, plugin.__class__))
    debug("dispatch finish message:'%s' call_method: '%s' : results %s" %
            (message, attr, res))
    return res

def reload_plugins(config):
    del _instance[:]
    return load_plugins(config)
    
#load_plugins({})


