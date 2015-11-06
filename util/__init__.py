#!/usr/bin/env python
# -*- coding: utf-8 -*-  
"""
__init__ file for util
"""
import sys
import os

broc_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, broc_dir)

from util import Log
from util import Function
