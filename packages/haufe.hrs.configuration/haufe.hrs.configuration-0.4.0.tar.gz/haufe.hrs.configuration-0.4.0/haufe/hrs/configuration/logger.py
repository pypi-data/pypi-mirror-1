#################################################################
# haufe.hrs.configuration - a pseudo-hierarchical configuration
# management infrastructure
# (C) 2008, Haufe Mediengruppe, Freiburg
#################################################################

"""
A simple logger for haufe.hrs.configuration
"""

import logging
import logging.handlers

def getLogger():

    LOG = logging.getLogger()
    LOG.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s %(levelname)-6s %(message)s')
    streamhandler = logging.StreamHandler()
    streamhandler.setFormatter(formatter)
    LOG.addHandler(streamhandler)
    return LOG

