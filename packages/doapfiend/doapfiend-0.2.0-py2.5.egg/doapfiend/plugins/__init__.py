
# pylint: disable-msg=W0142,C0103


"""
Writing Plugins
===============

doapfiend supports setuptools_ entry point plugins.

There are two basic rules for plugins:

 - Plugin classes should subclass `doapfiend.plugins.Plugin`_.
 - Plugins may implement any of the methods described in the class
   PluginInterface in doapfiend.plugins.base. Please note that this class is for
   documentary purposes only; plugins may not subclass PluginInterface.

Setuptools: http://peak.telecommunity.com/DevCenter/setuptools
Doapfiend Plugins: http://trac.doapspace.org/doapfiend/wiki/DoapfiendPlugins 

Registering
-----------

For doapfiend to find a plugin, it must be part of a package that uses
setuptools, and the plugin must be included in the entry points defined
in the setup.py for the package::

  setup(name='Some plugin',
        ...
        entry_points = {
            'doapfiend.plugins': [
                'someplugin = someplugin:SomePlugin'
                ]
            },
        ...
        )

Once the package is installed with install or develop, doapfiend will be able
to load the plugin.

Defining options
----------------

All plugins must implement the methods ``add_options(self, parser, env)``
and ``configure(self, options, conf)``. Subclasses of doapfiend.plugins.Plugin
that want the standard options should call the superclass methods.

doapfiend uses optparse.OptionParser from the standard library to parse
arguments. A plugin's ``add_options()`` method receives a parser
instance. It's good form for a plugin to use that instance only to add
additional arguments that take only long arguments (--like-this). Most
of doapfiend's built-in arguments get their default value from an environment
variable. This is a good practice because it allows options to be
utilized when run through some other means than the doapfiendtests script.

A plugin's ``configure()`` method receives the parsed ``OptionParser`` options 
object, as well as the current config object. Plugins should configure their
behavior based on the user-selected settings, and may raise exceptions
if the configured behavior is nonsensical.

Logging
-------

doapfiend uses the logging classes from the standard library. To enable users
to view debug messages easily, plugins should use ``logging.getLogger()`` to
acquire a logger in the ``doapfiend.plugins`` namespace.

"""

import logging
import pkg_resources
from warnings import warn
from inspect import isclass
from doapfiend.plugins.base import Plugin

LOG = logging.getLogger(__name__)

# +==== IMPORTANT ====+
#If you add any builtin plugins in doapfiend.plugins you must add them 
#to this list for them to be loaded. It's okay to add other Python modules
#in the doapfiend.plugins namespace, but they won't be recognized as a plugin
#unless listed here:

builtin_plugins = ['n3', 'xml', 'text', 'sourceforge', 'pypi', 'freshmeat',
        'homepage', 'url']

def call_plugins(plugins, method, *arg, **kw):
    """Call all method on plugins in list, that define it, with provided
    arguments. The first response that is not None is returned.
    """
    for plug in plugins:
        func = getattr(plug, method, None)
        if func is None:
            continue
        LOG.debug("call plugin %s: %s", plug.name, method)
        result = func(*arg, **kw)
        if result is not None:
            return result
    return None
        
def load_plugins(builtin=True, others=True):
    """Load plugins, either builtin, others, or both.
    """
    loaded = []
    if builtin:
        for name in builtin_plugins:
            try:
                parent = __import__(__name__, globals(), locals(), [name])
                #print name
                pmod = getattr(parent, name)
                for entry in dir(pmod):
                    obj = getattr(pmod, entry)
                    if (isclass(obj)
                        and issubclass(obj, Plugin)
                        and obj is not Plugin
                        and not obj in loaded):
                        #LOG.debug("load builtin plugin %s (%s)" % (name, obj))
                        #print "load builtin plugin %s (%s)" % (name, obj)
                        yield obj
                        loaded.append(obj)
            except KeyboardInterrupt:
                raise
            except Exception, e:
                warn("Unable to load builtin plugin %s: %s" % (name, e),
                     RuntimeWarning)
    for entry_point in pkg_resources.iter_entry_points('doapfiend.plugins'):
        LOG.debug("load plugin %s" % entry_point)
        try:
            plugin = entry_point.load()
        except KeyboardInterrupt:
            raise
        except Exception, err_msg:
            # never want a plugin load to exit doapfiend
            # but we can't log here because the logger is not yet
            # configured
            warn("Unable to load plugin %s: %s" % \
                    (entry_point, err_msg), RuntimeWarning)
            continue
        #print plugin.__module__
        if plugin.__module__.startswith('doapfiend.plugins'):
            if builtin:
                yield plugin
        elif others:
            yield plugin

