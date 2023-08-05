import sys
import optparse

opt_config = optparse.make_option(
    "-c", "--config",
    dest="config", metavar="FILE",
    help="Specify a configuration file to load.")
        
opt_log = optparse.make_option(
    "-l", "--log",
    dest="log", metavar="FILE",
    help="Specify location for the log file.")

opt_verbose = optparse.make_option(
    "-v", "--verbose",
    action="count", dest="verbosity",
    help="Verbose output. Use twice for greater effect.")

opt_quiet = optparse.make_option(
    "-q", "--quiet",
    action="store_const", dest="verbosity",
    help="Quiet output, don't show anything",
    const=0)

opt_username = optparse.make_option(
    "-u", "--username",
    action="store", dest="username",
    help="The username to use for this action")

opt_password = optparse.make_option(
    "-p", "--password",
    action="store", dest="password",
    help="The password to use for this action")

opt_enable = optparse.make_option(
    "--enable",
    action="append", dest="enable",
    help="Modules to enable")

opt_disable = optparse.make_option(
    "--disable",
    action="append", dest="disable",
    help="Modules to disable")

class Clee(optparse.OptionParser):
    standard_option_list = [opt_config,
                            opt_log,
                            opt_verbose,
                            opt_quiet]

    def __init__(self, *args, **kwargs):
        optparse.OptionParser.__init__(self, *args, **kwargs)
        opts = [getattr(self, k) for k in dir(self) if k[:4] == "opt_"]
        for opt in opts:
            self.add_option(opt)

class ContextClee(Clee):
    def __init__(self,contexts={},*args,**kwargs):
        Clee.__init__(self,*args,**kwargs)
        self._contexts = contexts
    
    def parse_args(self,args=None):
        if args is None:
            args = sys.argv
        if len(args) < 2:
            raise Exception("Not enough args, dude")
        context = args[1]
        try:
            args = args[2:]
        except IndexError:
            args = []
        options, args = self.get_context_parser(context).parse_args(args)
        options.context = context
        return options, args
    
    def get_context_parser(self,context):
        return self._contexts[context]

    def add_context_parser(self,context_name,parser):
        self._contexts[context_name] = parser

"""These are things that are extras if you are using some of the other
   things I wrote"""
try:
    import scribe
except ImportError:
    import logging as scribe
    
try:
    from sprinkles import ISprinkle, implements, fromPackage
    
    class ICleeSprinkle(ISprinkle):
        pass
        
    class IContextCleeSprinkle(ISprinkle):
        pass

    class SprinkledClee(Clee):
        def __init__(self, package=None,
                     filterer=ICleeSprinkle.implementedBy,
                     *args,**kwargs):
            Clee.__init__(self,*args,**kwargs)
            if package:
                self.load_sprinkles(package=package, filterer=filterer)
                
        def load_sprinkles(self, package=None, filterer=None):
            scribe.debug("Looking for Clee Sprinkles")
            self.sprinkles = fromPackage(package, filterer)
            
            for x in self.sprinkles:
                scribe.debug("Executing sprinkle %s"%(x))
                f = x()
                f(self)


    class SprinkledContextClee(ContextClee,SprinkledClee):
        def __init__(self, contexts={}, package=None,
                     filterer=IContextCleeSprinkle.implementedBy,
                     *args,**kwargs):
            ContextClee.__init__(self, contexts=contexts, *args, **kwargs)
            SprinkledClee.__init__(self, package=package,
                                   filterer=filterer, *args, **kwargs)
        
    
    class ContextCleeSprinkleMixin(object):
        context = 'default'
        cli = Clee()
        def __call__(self,cli):
            cli.add_context_parser(self.context,self.cli)
            
    class CleeOptionSprinkleMixin(object):
        option = None
        def __call__(self,cli):
            cli.add_option(self.option)

except ImportError:
    pass

Option = optparse.Option
make_option = optparse.make_option

_cli = Clee()

def parse_args(*args,**kwargs):
    return _cli.parse_args(*args,**kwargs)

def add_option(*args,**kwargs):
    return _cli.add_option(*args,**kwargs)
