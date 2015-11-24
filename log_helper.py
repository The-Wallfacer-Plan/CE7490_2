import logging
import logging.config

import yaml

import config


def init_logger():
    """
    bootstrap our logging system
    """
    with open(config.logging_yaml) as f:
        data = yaml.load(f)
    logging.config.dictConfig(data)


def get_logger():
    """
    get the default global logger
    :return:
    """
    return logging.getLogger('logger')
