import sys
import unittest
import logging


class _UnittestLogHandler(object):
    """acts as a StreamHandler on stdout (does some additional formatting)"""
    
    def __init__(self, log_name):
        self.__log_name = log_name

    def write(self, msg):
        sys.stdout.write(">>> %s: %s" % (self.__log_name, msg))
    
    def __getattr__(self, name):
        return getattr(sys.stdout, name)


def monitor_log(log_name):
    """monitors a log for unit tests"""
    logger = logging.getLogger(log_name)
    logger.addHandler(logging.StreamHandler(_UnittestLogHandler(log_name)))
    logger.setLevel(logging.INFO)


###############################################################################
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

COVERAGE = [
    '--with-coverage',
    '--cover-package=stockpyle',
    ]

FLAGS = ["-v"] + COVERAGE# + ["--tests=test_sqlalchemy_store"]

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
###############################################################################

if __name__ == "__main__":

    import sys
    import os
    import nose
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    # run nosetests
    sys.argv = sys.argv + FLAGS
    nose.core.TestProgram(defaultTest="tests", argv=sys.argv)

