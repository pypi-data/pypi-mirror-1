#!/usr/bin/env python
# encoding: utf-8
"""
spasmodic_echo.py

Created by Doug Fort on 2006-09-21.
Copyright (c) 2006 Doug Fort Consultiing, Inc.. All rights reserved.
"""

import logging
import os.path
import sys
import xml.etree.ElementTree 

from option_parser import OptionParser
try:
    from spasmodic_engine import SpasmodicEngine
except ImportError:
    # if we fail to import, assume we are running locally under .../spasmodic/examples/echo;
    # so add '..' to the search path
    import os.path                                           
    examples_path = os.path.dirname(sys.path[0])
    spasmodiic_path = os.path.dirname(examples_path)
    sys.path.append(spasmodiic_path)
    from spasmodic_engine import SpasmodicEngine

class SpasmodicEchoError(Exception):
    """general echo exception"""
    pass
    
class SpasmodicEcho(object):
    """spasmodic echo example main module"""
    
    def __init__(self, args):
        """create an echo object"""
        super(SpasmodicEcho, self).__init__() 
        
        log = logging.getLogger("echo-init")
        
        self._blackboard = dict()
        self._blackboard["options"], leftover_args = OptionParser().parse_args(args) 
        assert self._blackboard["options"].config_file_path is not None 
        self._config = xml.etree.ElementTree.parse(self._blackboard["options"].config_file_path)            
        
    def run(self):
        """main processing loop"""
        log = logging.getLogger("echo-main")
        log.info("main run starts")   
        spasmodic_engine = SpasmodicEngine()
        try:          
            spasmodic_engine.run(module_config=self._config)
        except Exception:
            log.exception("")
        spasmodic_engine.close()
        log.info("main run ends")
        return 0


if __name__ == '__main__':
    import logging.config
    
    logging.LOGFILE="spasmodic_echo.log"
    logging.config.fileConfig("spasmodic_echo_log.config")
    
    sys.exit(SpasmodicEcho(sys.argv[1:]).run())

