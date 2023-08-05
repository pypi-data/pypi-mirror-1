"""The migrate command-line tool.
"""
import sys
from migrate.versioning.base import *
from optparse import OptionParser,Values
from migrate.versioning import api

alias = dict(
    s=api.script,
    ci=api.commit,
    vc=api.version_control,
    dbv=api.db_version,
    v=api.version,
)
def alias_setup():
    global alias
    for key,val in alias.iteritems():
        setattr(api,key,val)
alias_setup()

def MigrateOptionParser():
    usage="""%%prog COMMAND ...
Available commands:
%s

Enter "%%prog help COMMAND" for information on a particular command."""
    commands = list(api.__all__)
    commands.sort()
    commands = '\n'.join(map((lambda x:'\t'+x),commands))
    usage = usage%commands

    ret = OptionParser(usage)
    ret.add_option('-T','--table',action='store')
    ret.add_option('-p','--repository',action='store')
    ret.add_option('-v','--verbose',action='store_true',help="Verbose output")
    ret.add_option('-d','--debug',action='store_true',help="Debugging output")
    ret.add_option('-f','--force',action='store_true',help="Don't prompt for input")
    ret.add_option('--preview_py',action='store_true')
    ret.add_option('--preview_sql',action='store_true')
        
    return ret

class OptionValues(Values):
    def from_values(self,values):
        dummy=values.__class__()
        dkeys=dir(dummy)
        for key in dir(values):
            if key not in dkeys:
                setattr(self,key,getattr(values,key))
        return self
    def from_dict(self,item):
        for key,val in item.iteritems():
            setattr(self,key,val)
        return self
    def keys(self):
        dummy=self.__class__()
        dkeys=dir(dummy)
        ret = []
        for key in dir(self):
            if key not in dkeys:
                ret.append(key)
        return ret
    def to_dict(self,purge_none=False):
        ret=dict()
        for field in self.keys():
            if (not purge_none) or (getattr(self,field) is not None):
                ret[field]=getattr(self,field)
        return ret

def main(args=None):
    """Parse command line args and run the appropriate function"""
    parser = MigrateOptionParser()
    options,args=parser.parse_args(args=args)
    options=OptionValues().from_values(options)

    if len(args)<1:
        parser.error("Not enough arguments")
    command=args.pop(0)

    shell=Shell(parser,options)
    shell.run(command,args)

class Shell:
    def __init__(self,parser,options):
        self.parser=parser
        self.opts = self.setup_options(options)
    
    def setup_options(self,options):
        if options.verbose:
            log.setLevel(logging.INFO)
        del options.verbose
        if options.debug:
            log.setLevel(logging.DEBUG)
        del options.debug
        if options.force:
            pass #TODO
        del options.force
        return options

    def run(self,cmdname,args):
        cmd=getattr(api,cmdname,None)
        global alias
        # Command not found, private attr, not in all nor aliases
        if (cmd is None) or (cmdname.startswith('_')) or (not(
            (cmdname in api.__all__) or (cmdname in alias))): 
            # undefined command or private func
            self.parser.error("Invalid command")
        opts=self.opts.to_dict(purge_none=True)
        try:
            ret=cmd(*args,**opts)
            if ret is not None:
                print ret
        except TypeError,e:
            self.parser.error("Incorrect # arguments")
        except api.UsageError,e:
            self.parser.error(e.args[0])
        except api.KnownError,e:
            self.die(e.args[0])
    
    def die(self,message):
        """Display a message; quit; return some error status"""
        #log.error(message)
        sys.stderr.write(message)
        raise SystemExit(1)

if __name__=="__main__":
    main()
