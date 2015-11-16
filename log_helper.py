#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.config

import yaml

import config


def init_logger():
    with open(config.logging_yaml) as f:
        data = yaml.load(f)
    logging.config.dictConfig(data)


def get_logger():
    return logging.getLogger('logger')
