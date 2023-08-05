#!/usr/bin/env python

from meatoo_client.cli import *

def test_print_results():
    """print_results test"""
    assert print_results([[""]], None) == None
