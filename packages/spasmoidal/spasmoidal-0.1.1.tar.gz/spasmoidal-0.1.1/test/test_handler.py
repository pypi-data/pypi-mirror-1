#!/usr/bin/env python
# encoding: utf-8
"""
test_handler.py

Created by Doug Fort on 2006-09-04.
Copyright (c) 2006 Doug Fort Consultiing, Inc.. All rights reserved.
"""      

import logging

try:
    from spasmodic_engine import make_task, spasmodic_coroutine
except ImportError:
    # if we fail to import, assume we are running locally;
    # so add '..' to the search path
    import os.path
    sys.path.append(os.path.dirname(sys.path[0]))
    from spasmodic_engine import SpasmodicEngine, spasmodic_coroutine
    
def factory(handler_config, blackboard, accept_result):
    @spasmodic_coroutine
    def test_handler_coroutine(handler_config, blackboard, accept_result):
        blackboard["handler"] = "accept_result"   
        log = logging.getLogger("test_handler_coroutine") 
        this_generator = yield None #get our own handle
        assert this_generator is not None
        while True:
            x = yield None
    test_handler_coroutine(handler_config, blackboard, accept_result)
    return tuple()

