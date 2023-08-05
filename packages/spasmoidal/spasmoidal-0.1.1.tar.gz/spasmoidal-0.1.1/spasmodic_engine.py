#!/usr/bin/env python
# encoding: utf-8
"""
spasmodic_engine.py

Created by Doug Fort on 2006-09-01.
Copyright (c) 2006 Doug Fort Consultiing, Inc.. All rights reserved.
"""       
import functools    
import logging
import sys
import threading 
import time

from spasmodic_task_queue import SpasmodicTaskQueue       

class SpasmodicEngineError(Exception):
    """spasmodic engine exception""" 
    pass

def spasmodic_coroutine(function):
    """decorator to create a coroutine generator"""
    @functools.wraps(function)
    def wrapper(*args, **kw):
        generator = function(*args, **kw)
        generator.next() # one to get ready
        generator.send(generator) # two to store our own handle
        return generator        
    return wrapper
    
def make_task(task, data=None, start_time=time.time()):
    """create a  task in known format"""
    return (task, data, start_time,)
    
class SpasmodicEngine(object): 
    
    def __init__(self, halt_event=None, lag_threshold=-0.5):
        """
        Create an engine.
        We take an external halt_event that could be set by a signal handler.
        """
        self._log = logging.getLogger("engine")
        self._log.debug("creating SpasmodicEngine")
        
        self._lag_threshold = lag_threshold
        assert self._lag_threshold < 0.0
        
        # we expose the blackboard for post processing and debugging
        self.blackboard = dict()
        
        # we expose the halt event for signal handlers
        self.halt_event = halt_event or threading.Event()
        self.blackboard["halt-event"] = self.halt_event
        
        self._task_queue = SpasmodicTaskQueue()
        
    def run(self, initial_tasks=(), module_config=None):
        """
        Loop over the task queue until told to stop
        """               
        self._task_queue.extend(initial_tasks)
        self._task_queue.extend(self._load_module_tasks(module_config))
               
        self._log.info("run loop starts with %s tasks in queue", len(self._task_queue))
        while len(self._task_queue) > 0 and not self.halt_event.isSet():
            
            start_time, task, task_data = self._task_queue.pop() 
            
            # execute the task, pushing any new tasks that it returns
            try:                     
                time_delta = start_time - time.time()
                if time_delta < self._lag_threshold:
                    self._log.warn("transaction time lag %s", time_delta)
                self.halt_event.wait(time_delta)
                self._task_queue.extend(task.send(task_data)) 
                
            except StopIteration:
                # if a coroutine falls through here, we assume it knows 
                # what it's doing: it just wants to quit.
                pass
                    
            except KeyboardInterrupt:
                self._log.warn("received keyboard interrupt")
                self.halt_event.set()
                                
        self._log.info("run loop ends with %s tasks in queue", len(self._task_queue))
        
    def close(self):
        """close all active tasks"""  
        self._log.info("close with %s tasks in queue", len(self._task_queue))
        while len(self._task_queue) > 0:
            _, task, _ = self._task_queue.pop()
            task.close()         
            
    def _load_module_tasks(self, module_config):
        """load tasks from confugurable modules"""
        if module_config is None:
            return None
        
        config_modules = module_config.find("modules")
        if config_modules is None:          
            message = "Unable to find <modules> in config"
            self._log.error(message)
            raise SpasmodicEngineError(message)
        
        tasks = []
        for config_module in config_modules.findall("module"):
            self._log.debug("loading module '%s'", config_module.get("name"))
            import_name = config_module.text.strip()
            module = __import__(import_name)
            components = import_name.split('.')
            for component in components[1:]:
                module = getattr(module, component)
            tasks.extend(module.factory(config_module, self.blackboard))
        return tuple(tasks)

if __name__ == '__main__':
    """Enter the program from the command line.

    This is intended for running unit tests.
    In normal prooduction, this file will be imported.
    """
    import logging.config
    import unittest      
    
    logging.LOGFILE="tc_spasmodic_engine.log"
    logging.config.fileConfig("test/test_log.config")
    
    from test.tc_spasmodic_engine import SpasmodicEngineTestCase
    unittest.main()
