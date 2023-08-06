#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################

# pre-defined services

from service import ConfigurationServiceFactory as factory
CentralConfigurationService = factory(watch=False)
CentralConfigurationServiceSupervised = factory(watch=True)
