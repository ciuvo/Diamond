#!/usr/bin/env python
################################################################################

import os
import sys
import optparse

from configobj import ConfigObj

#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'collectors')))

from diamond import *
from diamond.collector import Collector

collectors = {}
def getCollectors(path):
    for f in os.listdir(path):
        cPath = os.path.abspath(os.path.join(path, f))

        if os.path.isfile(cPath) and len(f) > 3 and f[-3:] == '.py' and f[0:4] != 'test':
            sys.path.append(os.path.dirname(cPath))
            modname = f[:-3]
            
            try:
                # Import the module
                module = __import__(modname, globals(), locals(), ['*'])
                
                # Find the name
                for attr in dir(module):
                    if not attr.endswith('Collector'):
                        continue
                    
                    cls = getattr(module, attr)

                    if not collectors.has_key(cls.__name__):
                        collectors[cls.__name__] = module
            except Exception, e:
                print "Failed to import module: %s. %s" % (modname, traceback.format_exc())
                collectors[modname] = False
                continue

    for f in os.listdir(path):
        cPath = os.path.abspath(os.path.join(path, f))
        if os.path.isdir(cPath):
            getCollectors(cPath)

handlers = {}
def getHandlers(path):
    for f in os.listdir(path):
        cPath = os.path.abspath(os.path.join(path, f))

        if os.path.isfile(cPath) and len(f) > 3 and f[-3:] == '.py':
            sys.path.append(os.path.dirname(cPath))
            modname = f[:-3]
            
            try:
                # Import the module
                module = __import__(modname, globals(), locals(), ['*'])
                
                # Find the name
                for attr in dir(module):
                    if not attr.endswith('Handler') or attr.startswith('Handler'):
                        continue
                    
                    cls = getattr(module, attr)
                    
                    if not handlers.has_key(cls.__name__):
                        handlers[cls.__name__] = module
            except Exception, e:
                print "Failed to import module: %s. %s" % (modname, traceback.format_exc())
                handlers[modname] = False
                continue

    for f in os.listdir(path):
        cPath = os.path.abspath(os.path.join(path, f))
        if os.path.isdir(cPath):
            getHandlers(cPath)

################################################################################

if __name__ == "__main__":
    
    # Initialize Options
    parser = optparse.OptionParser()
    parser.add_option("-c", "--configfile", dest="configfile", default="/etc/diamond/diamond.conf", help="Path to the config file")
    parser.add_option("-C", "--collector", dest="collector", default=None, help="Configure a single collector")
    parser.add_option("-p", "--print", action="store_true", dest="dump", default=False, help="Just print the defaults")

    # Parse Command Line Args
    (options, args) = parser.parse_args()
    
    # Initialize Config
    if os.path.exists(options.configfile):
        config = configobj.ConfigObj(os.path.abspath(options.configfile))
        config['configfile'] = options.configfile
    else:
        print >> sys.stderr, "ERROR: Config file: %s does not exist." % (options.configfile)
        print >> sys.stderr, "Please run python config.py -c /path/to/diamond.conf"
        parser.print_help(sys.stderr)
        sys.exit(1)
    
    collector_path = config['server']['collectors_path']
    docs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'docs'))
    handler_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'src', 'diamond', 'handler'))
    
    getCollectors(collector_path)
    
    collectorIndexFile = open(os.path.join(docs_path, "Collectors.md"), 'w')
    collectorIndexFile.write("## Collectors\n")
    collectorIndexFile.write("\n")
    
    for collector in sorted(collectors.iterkeys()):
        
        # Skip configuring the basic collector object
        if collector == "Collector":
            continue
        
        print "Processing %s..." % (collector)
        
        if not hasattr(collectors[collector], collector):
            continue
        
        cls = getattr(collectors[collector], collector)
        
        obj = cls(config = config, handlers = {})
        
        options = obj.get_default_config_help()

        docFile = open(os.path.join(docs_path, "collectors-"+collector+".md"), 'w')
        
        collectorIndexFile.write(" - [%s](collectors-%s)\n" % (collector, collector))
        
        docFile.write("%s\n" % (collector))
        docFile.write("=====\n")
        docFile.write("%s" % (collectors[collector].__doc__))
        docFile.write("#### Options\n")
        docFile.write("\n")
        docFile.write(" * [Generic Options](Configuration)\n")
        for option in options:
            docFile.write(" * %s: %s\n" %(option, options[option]))
        docFile.write("\n")
        docFile.write("#### Example Output\n")
        docFile.write("\n")
        docFile.write("All keys are prefixed with nodes.hostname by default\n")
        docFile.write("\n")
        docFile.write("```\n")
        docFile.write("```\n")
        docFile.write("\n")
        
        docFile.close()
        
    collectorIndexFile.close()
    
    getHandlers(handler_path)
    
    handlerIndexFile = open(os.path.join(docs_path, "Handlers.md"), 'w')
    handlerIndexFile.write("## Handlers\n")
    handlerIndexFile.write("\n")
    
    for handler in sorted(handlers.iterkeys()):
        
        # Skip configuring the basic handler object
        if handler == "Handler":
            continue
        
        print "Processing %s..." % (handler)
        
        if not hasattr(handlers[handler], handler):
            continue
        
        docFile = open(os.path.join(docs_path, "handler-"+handler+".md"), 'w')
        
        handlerIndexFile.write(" - [%s](handler-%s)\n" % (handler, handler))
        
        docFile.write("%s\n" % (handler))
        docFile.write("====\n")
        docFile.write("%s" % (handlers[handler].__doc__))
        
        docFile.close()
        
    handlerIndexFile.close()
    

