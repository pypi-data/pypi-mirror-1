#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################


import os
import cfgparse
import ConfigParser


def generateParser(name, LOG=None, parser=None):
    """ Generate a configuration parser for all modules described.
        'name' is either a directory containing model files (must
        end with .ini) or a single model file (also with .ini sufix).
        A new cfg.ConfigParser instance will be created unless
        specified as 'parser' parameter.
    """

    if os.path.isfile(name):
        filenames = [name]
    elif os.path.isdir(name):
        filenames = list()
        for n in os.listdir(name):
            filenames.append(os.path.join(name, n))
    else:
        raise ValueError('%s is neither a file nor a directory' % name)

    if parser is None:
        parser = cfgparse.ConfigParser()
    for filename in filenames:
        if not filename.endswith('.ini'): 
            continue
        parseModel(filename, parser,  LOG)
    return parser


def parseModel(filename, parser, LOG=None):
    """ Parse a model specified as an ini-style configuration file """

    filename = os.path.abspath(filename)

    if LOG:
        LOG.debug('Processing: %s' % filename)

    if not os.path.exists(filename):
        raise IOError('Model file %s does not exist' % filename)

    CP = ConfigParser.RawConfigParser()
    CP.read([filename])
    for section in CP.sections():
        if LOG:
            LOG.debug('  Section: %s' % section)
        for option in CP.options(section):

            value = CP.get(section, option).strip()
            default = None
            type = 'string'
            if value:
                if ',' in value:
                    type, other = value.split(',', 1)
                else:
                    type, other = value, ''

                if 'default' in other:
                    default = eval(other.split('=', 1)[1])

            dest = '%s.%s' % (section, option)
            parser.add_option(option, 
                              type=type, 
                              default=default, 
                              dest=dest,
                              keys=section)


class OptionLookup(object):
    """ Lookup values of configurations by a dotted name """

    def __init__(self, opts, prefix=None):
        self.opts = opts
        self.prefix = prefix
        # Optimization: has() should have 0(1) running time
        self.known_opts = dict()
        for k in self.opts.__dict__.keys():
            if '.' in k:
                self.known_opts[k] = True

    def get(self, name, expand_env=False):
        if self.prefix and not name.startswith(self.prefix):
            name = '%s.%s' % (self.prefix, name)
        try:
            v = getattr(self.opts, name)
        except AttributeError:
            raise ValueError('Unknown key: %s' % name)

        if expand_env:
            return os.path.expandvars(v)
        else:
            return v

    def has(self, name):
        if self.prefix and not name.startswith(self.prefix):
            name = '%s.%s' % (self.prefix, name)
        return self.known_opts.has_key(name)

