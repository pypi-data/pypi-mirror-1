#!/usr/bin/env python
# encoding: utf-8
"""
echo_client.py

Created by Doug Fort on 2006-10-01.
Copyright (c) 2006 Doug Fort Consultiing, Inc.. All rights reserved.
"""

import errno
import logging
import select
import socket 
import sys
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
    echo_path = os.path.dirname(sys.path[0])
    examples_path = os.path.dirname(echo_path)
    spasmodic_path = os.path.dirname(examples_path)
    sys.path.append(spasmodic_path)
    from spasmodic_engine import make_task, spasmodic_coroutine
    from spasmodic_pollster import HANGUP_FLAG, ERROR_FLAGS, READ_FLAGS, WRITE_FLAGS, decode_flags
    
class EchoClientCoroutineError(Exception):
    pass
class EchoClientSocketError(EchoClientCoroutineError):
    pass
class EchoClientDisconnectError(EchoClientSocketError):
    pass

def _test_flags(event_flags):    
    if event_flags & HANGUP_FLAG:
        raise EchoClientDisconnectError("received select.POLLHUP, assuming connection lost") 
    if event_flags & ERROR_FLAGS:
        raise EchoClientSocketError("Error flag(s) from poll() %s" % decode_flags(event_flags)) 
                    
def factory(module_config, blackboard):
    @spasmodic_coroutine
    def client_coroutine(module_config, blackboard):
        assert module_config.tag == "module", module_config.tag
        log = logging.getLogger(module_config.get("name")) 
        ip_address = module_config.get("ip_address")
        if ip_address is None:
            ip_address = ""
        port = int(module_config.get("port"))
        assert port > 0
        instance_count = int(module_config.get("count"))
        assert instance_count > 0
        log.info("host = (%s, %s), instances = %s", ip_address, port, instance_count)  
                
        blackboard.setdefault("bytes_sent", 0) 
        blackboard.setdefault("bytes_received", 0) 
                
        this_generator = (yield None) # first send() is our own handle
        assert this_generator is not None
        
        # 'with' would be nice here
        echo_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
        
            echo_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            echo_socket.setblocking(0)
            
            try:
                echo_socket.connect((ip_address, port))
            except socket.error, message:
                if message[0] != errno.EINPROGRESS:
                    raise
                          
            pollster_pending = blackboard.setdefault("pollster-pending", dict())
            assert not pollster_pending.has_key(echo_socket.fileno())
            pollster_pending[echo_socket.fileno()] = (this_generator, ERROR_FLAGS | WRITE_FLAGS,)
            
            event_flags = (yield None) # wait for connect
            _test_flags(event_flags)
                            
            while not blackboard["halt-event"].isSet():
                   
                # write a big string
                data_string = ('*' * (65 * 1024)) + "\n"
                while (len(data_string) > 0) and (not blackboard["halt-event"].isSet()):
                
                    pollster_pending[echo_socket.fileno()] = (this_generator, ERROR_FLAGS | WRITE_FLAGS,)
                    event_flags = (yield None)
                    _test_flags(event_flags)
                        
                    bytes_sent = echo_socket.send(data_string)
                    blackboard["bytes_sent"] += bytes_sent
                    data_string = data_string[bytes_sent:]
                    
                # read back the echo
                while (data_string.rfind("\n") == -1) and (not blackboard["halt-event"].isSet()):
            
                    # put ourselves into pollster pending for read
                    pollster_pending[echo_socket.fileno()] = (this_generator, ERROR_FLAGS | READ_FLAGS,)
            
                    event_flags = (yield None)
                    _test_flags(event_flags)
                    
                    data_string += echo_socket.recv(4096) 
                    
                blackboard["bytes_received"] += len(data_string)
                
        except EchoClientDisconnectError:
            # we really should try to reconnect here
            log.warn("connection closed by remote host")
            
        finally:
            echo_socket.close()
    
    # create the coroutine, but do not return it
    # we want the pollster to put us in the queue when we  have incoming
    client_coroutine(module_config, blackboard)        
    return tuple()

if __name__ == '__main__':
    """Enter the program from the command line.

    This is intended for running unit tests.
    In normal prooduction, this file will be imported.
    """
    import logging.config
    import unittest      
    
    logging.LOGFILE="tc_echo_client.log"
    logging.config.fileConfig("test/test_log.config")
    
    from test.tc_echo_client import EchoClientTestCase
    unittest.main()

