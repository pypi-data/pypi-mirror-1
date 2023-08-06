"""
Handy utilities that don't have a specific module yet

Oisin Mulvihill
2009-02-04

"""
import logging


def log_init(level=logging.CRITICAL):
    """Used mainly in testing to create a default catch all logging set up
       Note, this is not necessary if you've used setup() above and specified logging config 
       in the config file

    This set up catches all channels regardless of whether they
    are in other projects or in our own project.

    """
    log = logging.getLogger()
    hdlr = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    log.addHandler(hdlr)
    log.setLevel(level)
