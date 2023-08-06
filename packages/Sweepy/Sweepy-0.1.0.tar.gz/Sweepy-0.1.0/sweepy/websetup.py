"""Setup the Sweepy application"""
import logging

from sweepy.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup sweepy here"""
    load_environment(conf.global_conf, conf.local_conf)
