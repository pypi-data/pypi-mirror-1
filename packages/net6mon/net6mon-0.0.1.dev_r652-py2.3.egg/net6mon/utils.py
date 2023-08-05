# -*- coding: iso-8859-1 -*-
import time

    
def get_timestamp():
    """
        return a timestamp suitable for 
    """
    ts="%s"%time.time();
    return int(ts.split(".")[0])

