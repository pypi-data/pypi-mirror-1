#!/usr/bin/env python
# encoding: utf-8
"""
spasmodic_periodic_logger.py

Created by Doug Fort on 2006-09-29.
Copyright (c) 2006 Doug Fort Consultiing, Inc.. All rights reserved.
"""
#!/usr/bin/env python
# encoding: utf-8
"""
spasmodic_socket_acceptor.py

Created by Doug Fort on 2006-09-04.
Copyright (c) 2006 Doug Fort Consultiing, Inc.. All rights reserved.
"""      

import logging
import time  

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
    def periodic_logger_coroutine(module_config, blackboard):
        """
        <module name="periodic_logger" log_name="test-log-name" interval="1.0">
            %(item1)s %05(item2)d
            <log_items>
                <log_item key="item1" />
                <log_item key="item2" clear_to="0"/>
            </log_items>
        </module>
        """
        assert module_config.tag == "module", module_config.tag
        log = logging.getLogger(module_config.get("log_name"))
        interval = float(module_config.get("interval"))   
        log_format = module_config.get("log_format")
        
        items_element = module_config.find("log_items")
        assert items_element is not None
        
        clear_to_dict = dict()
        for item_element in items_element.findall("log_item"):
            # if this item has no clear_to attribute, i.e. it is not cleared,
            # this will set it to None.
            clear_to = item_element.get("clear_to") 
            
            if clear_to is not None:
                # try int() first, because float() will cast
                try:
                    clear_to = int(clear_to)
                except ValueError:            
                    try:
                        clear_to = float(clear_to)
                    except ValueError:
                        pass
            clear_to_dict[item_element.get("key")] = clear_to  
        
        this_generator = (yield None) # first send() is our own handle
        assert this_generator is not None
    
        while not blackboard["halt-event"].isSet():
            start_time = time.time()
                                
            # we don't want a bad format to kill everything
            try:
                log.info(log_format % blackboard)
            except Exception, message:
                log.error("%s '%s'", message, log_format)
            
            for key, clear_to in clear_to_dict.items():
                if clear_to is not None:
                    blackboard[key] = clear_to
            
            elapsed_time = time.time() - start_time
            delta = interval - elapsed_time if elapsed_time >= 0.0 else 0.0
            yield (make_task(this_generator, data=None, start_time=time.time()+delta), )
    
    # return a task for the queue, set to run asap
    return (make_task(periodic_logger_coroutine(module_config, blackboard), data=None, start_time=time.time()), )        

