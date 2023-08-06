##########################################################################
# haufe.testrunner
#
# (C) 2007, Haufe Mediengruppe
##########################################################################


import os
from z3c.sqlalchemy import createSAWrapper

from config import WRAPPER_NAME
from model import getModel


def setup(dsn=None, echo=False):

    dsn = os.environ.get('TESTING_DSN', dsn)
    if not dsn:
        raise ValueError('$TESTING_DSN undefined or the [default]/dsn option of your '
                         'configuration file is not configured properly.')

    wrapper = createSAWrapper(dsn,
                              forZope=False,
                              model=getModel,
                              echo=echo,
                              convert_unicode=False,
                              name=WRAPPER_NAME)
    return wrapper


