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

try:
    from spasmodic_engine import make_task, spasmodic_coroutine
    from spasmodic_pollster import HANGUP_FLAG, ERROR_FLAGS, READ_FLAGS, WRITE_FLAGS, decode_flags
except ImportError:
    # if we fail to import, assume we are running locally under .../spasmodic/examples/echo;
    # so add '..' to the search path
    import os.path                                           
    echo_path = os.path.dirname(sys.path[0])
    examples_path = os.path.dirname(echo_path)  
    spasmodic_path = os.path.dirname(examples_path)
    sys.path.append(spasmodic_path)
    from spasmodic_engine import make_task, spasmodic_coroutine
    from spasmodic_pollster import HANGUP_FLAG, ERROR_FLAGS, READ_FLAGS, WRITE_FLAGS, decode_flags  
    
class EchoHandlerCoroutineError(Exception):
    pass
class EchoHandlerSocketError(EchoHandlerCoroutineError):
    pass
class EchoHandlerDisconnectError(EchoHandlerSocketError):
    pass

def _test_flags(event_flags):    
    if event_flags & HANGUP_FLAG:
        raise EchoHandlerDisconnectError("received select.POLLHUP, assuming connection lost") 
    if event_flags & ERROR_FLAGS:
        raise EchoHandlerSocketError("Error flag(s) from poll() %s" % decode_flags(event_flags)) 
                    
def factory(handler_config, blackboard, accept_result):
    @spasmodic_coroutine
    def echo_handler_coroutine(handler_config, blackboard, accept_result):
        assert handler_config.tag == "handler", handler_config.tag
        log = logging.getLogger(handler_config.get("name")) 
        handler_socket, sender_address = accept_result
        log.info("sender = %s", sender_address) 
        
        blackboard.setdefault("bytes_sent", 0) 
        blackboard.setdefault("bytes_received", 0) 
                
        this_generator = (yield None) # first send() is our own handle
        assert this_generator is not None
        
        # 'with' would be nice here
        try:
        
            pollster_pending = blackboard.setdefault("pollster-pending", dict())
            assert not pollster_pending.has_key(handler_socket.fileno())
            pollster_pending[handler_socket.fileno()] = (this_generator, ERROR_FLAGS | READ_FLAGS,)
              
            data_string = ""
            while not blackboard["halt-event"].isSet():
            
                # read until we get a linefeed
                while (data_string.rfind("\n") == -1) and (not blackboard["halt-event"].isSet()):
            
                    # put ourselves into pollster pending for read
                    pollster_pending[handler_socket.fileno()] = (this_generator, ERROR_FLAGS | READ_FLAGS,)
            
                    event_flags = (yield None)
                    _test_flags(event_flags)
            
                    data_string += handler_socket.recv(4096) 
                
                blackboard["bytes_received"] += len(data_string)
                
                # write back what we just read
                while (len(data_string) > 0) and (not blackboard["halt-event"].isSet()):
            
                    # put ourselves into pollster pending for write
                    pollster_pending[handler_socket.fileno()] = (this_generator, ERROR_FLAGS | WRITE_FLAGS,)
            
                    event_flags = (yield None)
                    _test_flags(event_flags)
                    
                    bytes_sent = handler_socket.send(data_string)
                    data_string = data_string[bytes_sent:]
                    blackboard["bytes_sent"] += bytes_sent
                     
        except EchoHandlerDisconnectError, message:
            # let this slide: the other can can re-connect if they want to 
            log.warn(message)
            pass
            
        finally:
            handler_socket.close()
    
    # create the coroutine, but do not return it
    # we want the pollster to put us in the queue when we  have incoming
    echo_handler_coroutine(handler_config, blackboard, accept_result)        
    return tuple()

