#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################


"""'
ZCML directives for haufe.hrs.configuration
"""

import os
from zope.interface import Interface
from zope.schema import TextLine 
from service_hrs import HRSConfigurationService

class IModelDefinition(Interface):
    """ Used for defining a model"""

    configuration = TextLine(
        title=u"Directory name containing model files or a single model file",
        description=u"Directory name containing model files or a single model file",
        default=u"",
        required=True)

class IConfigurationFile(Interface):
    """ Used for defining a configuration file"""

    configuration = TextLine(
        title=u"Directory name containing configuration files or a single configuration filename",
        description=u"Directory name containing configuration files or a single configuration filename",
        default=u"",
        required=True)


def registerModel(_context, configuration):
    HRSConfigurationService.registerModel(configuration)

def registerConfiguration(_context, configuration):
    # str() because cfgparse.add_file performs an explicit check
    # for <str> type
    HRSConfigurationService.loadConfiguration(str(configuration))

