#!/usr/bin/env python
# encoding: utf-8
"""
spasmodic_pollster.py

Created by Doug Fort on 2006-09-04.
Copyright (c) 2006 Doug Fort Consultiing, Inc.. All rights reserved.
"""      

import errno
import logging
import select
import time

HANGUP_FLAG = select.POLLHUP
ERROR_FLAGS = select.POLLERR | select.POLLHUP | select.POLLNVAL
READ_FLAGS = select.POLLIN | select.POLLPRI
WRITE_FLAGS = select.POLLOUT

_FLAG_VALUES = {
    select.POLLERR:"select.POLLERR",
    select.POLLHUP:"select.POLLHUP",
    select.POLLNVAL:"select.POLLNVAL",
    select.POLLIN:"select.POLLIN",
    select.POLLPRI:"select.POLLPRI",
    select.POLLOUT:"select.POLLOUT",
}

def decode_flags(flags):
    """return a string of flag names"""

    flag_string = ""
    for flag_value in _FLAG_VALUES.keys():
        if flag_value & flags:
            flag_string += "0x%04X %s, " % (
                flag_value, _FLAG_VALUES[flag_value] 
            )
    if len(flag_string) > 2:
        flag_string = flag_string[:-2]
        
    return flag_string 
    
try:
    from spasmodic_engine import make_task, spasmodic_coroutine
except ImportError:
    # if we fail to import, assume we are running locally;
    # so add '..' to the search path
    import os.path
    sys.path.append(os.path.dirname(sys.path[0]))
    from spasmodic_engine import make_task, spasmodic_coroutine
    
def factory(module_config, blackboard):
    @spasmodic_coroutine
    def pollster_coroutine(blackboard):
        assert module_config.tag == "module", module_config.tag
        log = logging.getLogger(module_config.get("name")) 
        interval = float(module_config.get("interval"))
        assert interval  > 0.0
        timeout_seconds = float(module_config.get("timeout"))
        timeout_milliseconds = int(1000 * timeout_seconds)
        assert timeout_milliseconds > 0
        log.info("interval = %s, timeout = %s", interval, timeout_seconds)
                                        
        pollster_pending = blackboard.setdefault("pollster-pending", dict())
        
        pollster = select.poll()
        
        this_generator = (yield None) # first send() is our own handle  
        assert this_generator is not None
       
        try:
            while not blackboard["halt-event"].isSet():
            
                for task_fileno, (_, event_mask) in pollster_pending.items():
                    pollster.register(task_fileno, event_mask)
        
                # poll to see if any filenos are ready for I/O 
                try:
                    ready_items = pollster.poll(timeout_milliseconds)
                except select.error, error:
                    if error[0] != errno.EINTR:
                        raise
                    ready_items = tuple()
            
                returned_tasks = [make_task(this_generator, data=None, start_time=time.time()+interval)]
                for fileno, event_flags in ready_items:
            
                    # it's up for the task to add himself back in if he's suitable
                    pollster.unregister(fileno)
            
                    try:
                        task, _ = pollster_pending.pop(fileno)
                    except KeyError:
                        log.error("No pending task entry for fileno %s" % (fileno,))
                        continue             
                
                    # task is ready for i/o (or in error)
                    # push him onto the queue for immediate action
                    returned_tasks.append(make_task(task, data=event_flags, start_time=time.time()))
                
                yield tuple(returned_tasks)
        finally:
            for task, _ in pollster_pending.values():
                task.close()
            
    return (make_task(pollster_coroutine(blackboard)),)
