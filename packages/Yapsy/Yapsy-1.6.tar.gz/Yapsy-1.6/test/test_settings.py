#!/usr/bin/python
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys

import logging
TEST_MESSAGE = logging.debug

# set correct loading path for yapsy's files
sys.path.append(
	os.path.dirname(
		os.path.dirname(
			os.path.abspath(__file__))))

sys.path.append(
	os.path.dirname(
		os.path.dirname(
			os.path.dirname(
				os.path.abspath(__file__)))))



