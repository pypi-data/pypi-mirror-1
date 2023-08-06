import logging
import os
import zc.buildout
from zc.recipe.egg.egg import Eggs

WRAPPER_TEMPLATE = """\
import sys
syspaths = [
    %(syspath)s,
    ]

for path in reversed(syspaths):
    if path not in sys.path:
        sys.path[0:0]=[path]

# Enable tracing. Run 'python win32traceutil.py' from site-packages\win32\lib to watch messages.
if %(debug)s and hasattr(sys, "isapidllhandle"): 
    import win32traceutil

# The entry point for the ISAPI extension.
def __ExtensionFactory__():
    from paste.deploy import loadapp
    from paste.script.util.logging_config import fileConfig

    configfile=r"%(config)s"
    fileConfig(configfile)
    application = loadapp("config:" + configfile)

    import isapi_wsgi

    return isapi_wsgi.ISAPIThreadPoolHandler(application)

# ISAPI installation
if __name__=='__main__':
    from isapi.install import ISAPIParameters, ScriptMapParams, VirtualDirParameters, HandleCommandLine
    
    params = ISAPIParameters()
    sm = [
        ScriptMapParams(Extension="*", Flags=0)
    ]
    
    vd = VirtualDirParameters(Name="%(directory)s",
                              Description = "%(description)s",
                              ScriptMaps = sm,
                              ScriptMapUpdate = "replace"
                              )
    
    params.VirtualDirs = [vd]
    HandleCommandLine(params)
"""

class Recipe:
    def __init__(self, buildout, name, options):
        self.buildout=buildout
        self.name=name
        self.options=options
        self.logger=logging.getLogger(self.name)

        
        if "config-file" not in options:
            self.logger.error("You need to specify a paste configuration file")
            raise zc.buildout.UserError("No paste configuration given")

        self.options.setdefault('directory', '/')
        self.options.setdefault('description', 'WSGI application')
        self.options.setdefault('debug', 'False')
        self.options.setdefault('server', None)
        
        if self.options.get('debug', '').lower() == 'true':
            self.options['debug'] = 'True'
        else:
            self.options['debug'] = 'False'

    def install(self):
        egg=Eggs(self.buildout, self.options["recipe"], self.options)
        reqs,ws=egg.working_set()
        path=[pkg.location for pkg in ws]
        extra_paths = self.options.get('extra-paths', '')
        extra_paths = extra_paths.split()
        path.extend(extra_paths)

        output=WRAPPER_TEMPLATE % dict(
            config=self.options["config-file"],
            syspath=",\n    ".join((repr(p) for p in path)),
            directory=self.options['directory'],
            description=self.options['description'],
            debug=self.options['debug'],
            )

        location=os.path.join(self.buildout["buildout"]["parts-directory"], self.name)
        if not os.path.exists(location):
            os.mkdir(location)
            self.options.created(location)

        target=os.path.join(location, "isapiwsgi.py")
        f=open(target, "wt")
        f.write(output)
        f.close()
        self.options.created(target)
        
        # Install if a server was given
        
        if self.options['server']:
            cwd = os.getcwd()
            try:
                os.chdir(location)
                os.system("%s isapiwsgi.py install --server=%s " % (self.options['executable'], self.options['server'],))
            finally:
                os.chdir(cwd)
        
        return self.options.created()


    def update(self):
        self.install()

