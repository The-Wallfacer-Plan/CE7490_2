#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import logging.config
import os

import yaml

import config


def init_logger():
    with open(config.logging_yaml) as f:
        data = yaml.load(f)
    logger_dir = 'log'
    if not os.path.isdir(logger_dir):
        os.mkdir(logger_dir)
    logging.config.dictConfig(data)


def get_logger():
    return logging.getLogger('logger')