import logging
import os
import sys
import ConfigParser

def usage(code):
    print __doc__
    sys.exit(exit)

def _instantiate(config, name, components):
    if name in components:
        return components[name]
    args = dict(config.items(name))
    module, factoryname = args.pop('factory').split(':')
    next = args.pop('next', None)
    if next is not None:
        args['next'] = _instantiate(config, next, components)
    factory = getattr(__import__(module, fromlist=[factoryname]), factoryname)
    instance = components[name] = factory(**args)
    return instance

def start(config):
    start_sections = config.get('mailprocess', 'start').split()
    components = {} # already initialized components
    for section in start_sections:
        _instantiate(config, section, components)()

def main():
    if len(sys.argv) != 2:
        usage(1)
    fn = sys.argv[1]
    if not os.path.isfile(fn):
        usage(1)

    config = ConfigParser.ConfigParser()
    config.read(fn)

    # XXX: We need to read logging parameters from our config file
    # http://www.python.org/doc/lib/module-logging.html
    logger = logging.getLogger('mailprocess')
    logging.basicConfig()
    logger.setLevel(10)
    
    start(config)

if __name__ == '__main__':
    main()
