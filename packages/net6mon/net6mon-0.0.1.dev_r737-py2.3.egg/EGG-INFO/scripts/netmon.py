#!/usr/bin/python

from net6mon.daemon import Daemon, xmlRpcDaemon


def test_config():
    a = xmlRpcDaemon("netmon.conf")
    a.run()
    a.launch_server()
    print "Created agent " + a.env.config.host + ":" + str(a.env.config.port)
    

if __name__ == "__main__": 
    
    test_config()
    # st_object()
    #
    # test_logging()
    



