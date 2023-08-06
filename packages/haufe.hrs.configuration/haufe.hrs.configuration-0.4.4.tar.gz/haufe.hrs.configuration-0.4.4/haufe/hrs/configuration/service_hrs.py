#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################

import os

from service import ConfigurationServiceFactory as factory
watch = not os.environ.has_key('TESTING')
HRSConfigurationService = factory(watch=watch)
