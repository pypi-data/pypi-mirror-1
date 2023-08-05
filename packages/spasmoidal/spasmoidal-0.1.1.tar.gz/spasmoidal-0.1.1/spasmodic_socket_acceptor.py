#!/usr/bin/env python
# encoding: utf-8
"""
spasmodic_socket_acceptor.py

Created by Doug Fort on 2006-09-04.
Copyright (c) 2006 Doug Fort Consultiing, Inc.. All rights reserved.
"""      

import errno
import logging
import select
import socket
import time  

def SpasmodicSocketAcceptorError(Exception):
    """acceptor exception"""
    pass

try:
    from spasmodic_engine import make_task, spasmodic_coroutine
    from spasmodic_pollster import HANGUP_FLAG, ERROR_FLAGS, READ_FLAGS, WRITE_FLAGS, decode_flags
except ImportError:
    # if we fail to import, assume we are running locally;
    # so add '..' to the search path
    import os.path
    sys.path.append(os.path.dirname(sys.path[0]))
    from spasmodic_engine import make_task, spasmodic_coroutine
    from spasmodic_pollster import HANGUP_FLAG, ERROR_FLAGS, READ_FLAGS, WRITE_FLAGS, decode_flags
    
def factory(module_config, blackboard):
    @spasmodic_coroutine
    def acceptor_coroutine(module_config, blackboard):
        assert module_config.tag == "module", module_config.tag
        log = logging.getLogger(module_config.get("name")) 
        ip_address = module_config.get("ip_address")
        if ip_address is None:
            ip_address = ""
        port = int(module_config.get("port"))
        assert port > 0
        timeout_seconds = float(module_config.get("timeout"))
        timeout_milliseconds = int(1000 * timeout_seconds)
        assert timeout_milliseconds > 0
        log.info("host = (%s, %s), timeout = %s", ip_address, port, timeout_seconds)  
        
        handler_config = module_config.find("handler")
        assert handler_config is not None
        log.info("Loading handler factory for %s", handler_config.get("name"))
        import_name = handler_config.text.strip()
        module = __import__(import_name)
        components = import_name.split('.')
        for component in components[1:]:
            module = getattr(module, component)
        handler_factory = module.factory
        
        # 'with' would be nice here
        acceptor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
        
            acceptor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            acceptor_socket.setblocking(0)
            acceptor_socket.bind((ip_address, port))
            acceptor_socket.listen(5) 
              
            this_generator = (yield None) # first send() is our own handle
            assert this_generator is not None
        
            pollster_pending = blackboard.setdefault("pollster-pending", dict())
            assert not pollster_pending.has_key(acceptor_socket.fileno())
            pollster_pending[acceptor_socket.fileno()] = (this_generator, ERROR_FLAGS | READ_FLAGS,)
            
            while not blackboard["halt-event"].isSet():
            
                event_flags = (yield None)
            
                if event_flags & ERROR_FLAGS:
                    message = ("Error flag(s) from poll() %s" % decode_flags(event_flags))
                    log.error(message)
                    raise SpasmodicSocketAcceptorError(message)
                
                # create a handler, giving it the result of accept() (socket, address)
                # do not put the handler in the task queue: 
                # it should register itself in the pollster pending map  
                try:
                    accept_result = acceptor_socket.accept()
                    handler_factory(handler_config, blackboard, accept_result)
                except socket.error, message:
                    log.error(message)
                    if message[0] != errno.EAGAIN:
                        raise
                
                # put ourselves back in the pollster pending map 
                # (but not in the task queue - the pollster will do that when we have a connect)
                assert not pollster_pending.has_key(acceptor_socket.fileno())
                pollster_pending[acceptor_socket.fileno()] = (this_generator, ERROR_FLAGS | READ_FLAGS,) 
            
        finally:
            acceptor_socket.close()
    
    # create the coroutine, but do not return it
    # we want the pollster to put us in the queue when we  have incoming
    acceptor_coroutine(module_config, blackboard)        
    return tuple()

if __name__ == '__main__':
    """Enter the program from the command line.

    This is intended for running unit tests.
    In normal prooduction, this file will be imported.
    """
    import logging.config
    import unittest      
    
    logging.LOGFILE="tc_spasmodic_acceptor.log"
    logging.config.fileConfig("test/test_log.config")
    
    from test.tc_spasmodic_acceptor import SpasmodicAcceptorTestCase
    unittest.main()

