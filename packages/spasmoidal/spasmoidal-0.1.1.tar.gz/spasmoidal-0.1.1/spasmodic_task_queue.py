#!/usr/bin/env python
# encoding: utf-8
"""
spasmodic_task_queue.py

Created by Doug Fort on 2006-09-04.
Copyright (c) 2006 Doug Fort Consultiing, Inc.. All rights reserved.
"""

import heapq
import logging
import sys
import time           

class SpasmodicTaskQueueError(Exception):
    pass             
    
class SpasmodicTaskQueue(object):
    """a priority queue of Spasmodic tasks"""
    
    def __init__(self):
        """create a task queue"""
        self._log           = logging.getLogger("task_queue")        
        self._queue         = list()
        
    def push(self, task, data=None, start_time=time.time()):
        """push one task onto the queue""" 
        assert task is not None
        heapq.heappush(self._queue, (start_time, task, data,))
        
    def extend(self, tasks):
        """push a sequence of tasks onto the queue"""
        if tasks is None:
            return
        for task, task_data, start_time in tasks:
            self.push(task, data=task_data, start_time=start_time) 
        
    def pop(self):
        """
        return the next task,
        """
        return heapq.heappop(self._queue)             
        
    def __len__(self):
        """report the size of the queue"""
        return len(self._queue)   
        
if __name__ == "__main__":
    """Enter the program from the command line.

    This is intended for running unit tests.
    In normal prooduction, this file will be imported.
    """
    import logging.config
    import unittest      
    
    logging.LOGFILE="tc_spasmodic_task_queue.log"
    logging.config.fileConfig("test/test_log.config")
    
    from test.tc_spasmodic_task_queue import SpasmodicTaskQueueTestCase
    unittest.main()
                                                                                                                