#!/usr/bin/env python
# encoding: utf-8
"""
options.py

Created by Doug Fort on 2006-09-22.
Copyright (c) 2006 Doug Fort Consultiing, Inc.. All rights reserved.
"""

import optparse        

class OptionParser(optparse.OptionParser):
    """parse commandline arguments"""
    
    def __init__(self):
        """create an options object"""
        optparse.OptionParser.__init__(self) # initialize old-style class   
        self.add_option("-c", "--config-file", dest="config_file_path", help="path to XML config file")

