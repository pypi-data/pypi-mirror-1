"""Setup the darcs-cgi application"""
import logging

from darcscgi.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup darcscgi here"""
    load_environment(conf.global_conf, conf.local_conf)
