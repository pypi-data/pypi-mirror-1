#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
import sys
import os
from net6mon.platform import platform
import xmlrpclib
import socket
from xmlrpclib import *
from DocXMLRPCServer import *
from M2Crypto import SSL
from M2Crypto.m2xmlrpclib import SSL_Transport, Server
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from net6mon.env import Environment
from net6mon.pluginfarm import pluginFarm
import uuid

class SimpleSSLXMLRPCServer(SSL.SSLServer, SimpleXMLRPCServer):
    """
    An extension of SimpleXMLRPCServer that allows SSL handling.
    """
    def __init__(self, ssl_context, address, handler=None, handle_error=None):
        if handler is None: 
            handler = SimpleXMLRPCRequestHandler
        if handle_error is None:
            self.handle_error = self._quietErrorHandler
        SSL.SSLServer.__init__(self, address, handler, ssl_context) 
        self.funcs = {}
        self.logRequests = 0
        self.instance = None
     
    def _quietErrorHandler(self):
        "Discard any errors during SSL communications"
        return



"""
    Daemon

    Ce module est le module principal
"""
class Daemon:
    """
        La classe daemon représente la classe principale de l'application, c'est à dire 
        le point d'entrée.
        C'est cette classe qui est chargée d'orchestrer tout les appels à d'autres modules
    """
    def __init__(self,configfile):
        self.env=Environment(configfile)
        self.pluginfarm=pluginFarm(self.env)

        self.pluginfarm.load_instances()
        self.env.log.debug("Lauching server")
    

    """
        fork main loops
    """
    def run(self):
 
#        try: 
#            pid = os.fork() 
#            if pid > 0:
#                # exit first parent
#                sys.exit(0) 
#        except OSError, e: 
#            print >>sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror) 
#            sys.exit(1)
#
#            # decouple from parent environment
#        os.chdir("/") 
#        os.setsid() 
#        os.umask(0) 
#
        # do second fork
        try: 
            pid = os.fork() 
            if pid > 0:
                # exit from second parent, print eventual PID before
                print "Daemon PID %d" % pid 
                self.pluginfarm.schedule_forever()
                sys.exit(0) 
        except OSError, e: 
            print >>sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror) 
            sys.exit(1) 
        
            
    
    
    def launch_server(self):
        """
        Cette fonction lance le serveur principal
        """
             

class daemonWrapper:

    def __init__(self, pluginfarm, config):
        self._pluginfarm=pluginfarm
        self._config = config 

    def get_config_key(self, key):
        """ Return a global configuration key """
        return self._config.__dict__[key]
    
    def set_config_key(self, key, value):
        """ Set a global config key """
        self._config.__dict__[key]=value

    def save_config(self):
        """ Save configuration """
        self._config.save_config()
        pass

    def get_available_plugins(self):
        """ Return a list of installed plugins """
        return self._pluginfarm._get_available_plugins() 

    def add_instance(instance_name, plugin_type, description="", interval=0, config={}):
        """ 
        Add an instance to scheduler
        
        @param instance_name: name of instance
        @param plugin_type: plugin type
        @param description: a description for this instance
        @interval interval: interval (in seconds) to run plugin_instance.get_value()
        """
        return self._pluginfarm.add_instance(instance_name, plugin_type, description, interval, config)

    def remove_instance(self, instance_name):
        """
        Delete an instance from scheduler
        @param instance_name: instance to remove
        """
        return self._pluginfarm.remove_instance(instance_name)

    def set_instance_config(self, instance_name, config):
        """
        Set an instance configuration
        @param instance_name: name of instance
        @param config: a dictionary representing instance configuration
        """
        return self._pluginfarm.set_instance_config(instance_name, config)

    def set_instance_description(self, instance_name, description):
        """
        Set instance description
        @param instance_name: name of instance
        @param description: description of the instance
        """
        return self._pluginfarm.get_instance_description(instance_name, description)

    def set_instance_interval(self, instance_name, interval):
        """
        Set instance run-interval
        @param instance_name: name of the instance
        @param interval: interval in seconds
        """
        return self._pluginfarm.set_instance_interval(instance_name, interval)

    def get_instance_config(self, instance_name):
        """
        Retrieve an instance configuration
        @param instance_name: name of the instance
        @return: a dictionary representing instance configuration
        """
        return self._pluginfarm.get_instance_config(instance_name)

    def get_instance_description(self, instance_name):
        """
        Retrieve instance description
        @param instance_name: name of the instance
        @return: a string representing instance description
        """
        return self._pluginfarm.get_instance_description(instance_name)

    def get_instance_interval(self, instance_name):
        """
        Retrieve instance run-interval
        @param instance_name: name of the instance 
        @return: an int representing instance run-interval in seconfs
        """
        return self._pluginfarm.get_instance_interval(instance_name)

    def get_instance_type(self, instance_name):
        """
        Retrieve plugin type of the instance
        @param instance_name: name of the instance
        @return: a string representing the instance type
        """
        return self._pluginfarm.get_instance_type(instance_name)

    def get_instances_list(self):
        """
        Return a liste of currently running instances
        @return: a list of dictionary containing all instances description
        """
        return self._pluginfarm.get_instance_list()

    def get_instance_result(self, instance_name, date):
        """
        Get an instance result at date <date>
        @param date: date of result (timestamp)
        @return: the closest result found in the database
        """
        return self._pluginfarm.get_instance_result_at_date(instance_name, date)

    def get_instance_result(self, instance_name):
        """
        Get an instance result for now. Run plugin instance's get_result and 
        search in the instance database for a record.
        @param instance_name: name of the instance
        @return: a list containing table schema and table record: 
            [ [ col1, col2, ...], [ [ l1col1, l1col2,...], [ l2col1, l2col2, ...], ...] ]
        """
        return self._pluginfarm.get_instance_result(instance_name)

    def get_instance_results_between(self, instance_name, date_start, date_stop):
        """
        Get records in instance's database from date_start to date_stop
        """
        return self._pluginfarm.get_instance_results_between(instance_name, date_start, date_stop)


    def get_instance_table_creation_query(self, instance_name):
        """
        Return an instance_table creation query
        ex: "CREATE TABLE netmap (......)"
        """
        return self._pluginfarm.get_instance_table_creation_query(instance_name)

   
    def get_instance_results(self, instance_name):
        """
        Get all record in instance database
        """

        print self._pluginfarm.get_instance_results(instance_name)
        return self._pluginfarm.get_instance_results(instance_name)

    def purge_instance_table(self, instance_name):
        """
        Purge all record in instance table
        """
        return self._pluginfarm.purge_instance_table(instance_name)

    def purge_instance_table_from(self, instance_name, date_from):
        """
        Purge all record in instance's table from date_from
        """
        return self._pluginfarm.purge_instance_table_from(intance_name, date_from)

    def purge_all_instances_table(self, only_active=True):
        """
        Purge records in all actives instance's tables
        """
        return self._pluginfarm.purge_all_instances_table()

    def purge_all_instances_table_from(self, date):
        """
        Purge all instance's table from date <date>
        """
        return self._pluginfarm.purge_all_instances_table_from(date)
        
    def purge_all_instances_table_between(self, date_start, date_stop):
        """
        Purge all instance's table records from <date_start>  to <date_stop>
        """
        return self._pluginfarm.purge_all_instances_table_between(date_start, date_stop)

    def get_databases_list(self):
        """
        List all databases present in database directory
        """
        p = self.config.database_dir
        dblist = []
        for f in os.listdir(p):
            dblist.append(f)
        return dblist

    def get_actives_instances(self):
        """
        Return a liste of currently running instances
        @return: a list of dictionary containing all instances description
        """
        return self._pluginfarm.get_instance_list()


    def get_os(self):
        """
        Return an os type
        """
        return platform(0.0) 
    
    def get_hostname(self):
        """
        Return hostname
        """
        return socket.gethostbyaddr(socket.gethostname())[0]
        
    def get_bind_iface(self):
        """
        Return interface connected to the network
        """
        bindaddr = ""

        try:
            bindaddr = socket.gethostbyaddr(self._config.host)[2]
        except: 
            return "0.0.0.0"
        return "%s"%socket.gethostbyaddr(self._config.host)[2]

    def get_uid(self):
        return "NET6MON:"+str(uuid.getaddr()) 

    def ping(self):
        return "Ok"

class xmlRpcDaemon(Daemon):


    def __init__(self,configfile):
        Daemon.__init__(self,configfile)

        if self.env.config.enable_ssl.lower() == 'yes':
            if self.env.config.pem_file is None: 
                raise "pem file not specified whereas ssl is activated"
            if not os.access(self.env.config.pem_file, os.R_OK):
                raise '%s does not exist or is not readable\n' % self.env.config.pem_file
            self._init_ssl_context(self.env.config.pem_file, self.env.config.ssl_version,self.env.config.ssl_identifier, self.env.config.ssl_depth)
            self.server = SimpleSSLXMLRPCServer(self.ssl_context, (self.env.config.host, int(self.env.config.port)))
        else:
            self.server = SimpleXMLRPCServer((self.env.config.host, int(self.env.config.port)))
        
        self.xmlrpcwrapper = daemonWrapper(self.pluginfarm, self.env.config)
        self.register_functions()
        
        # check if docserv is enable
        if self.env.config.enable_docserv.lower() == 'yes' and self.env.config.docserv_port:
            self.doc_serv = DocXMLRPCServer((self.env.config.host, int(self.env.config.docserv_port)))
            self.doc_serv.register_instance(self.xmlrpcwrapper)
   
    def _init_ssl_context(self, pemfile, ssl_version,session_id, ssl_depth): 
        self.ssl_context = SSL.Context()
        self.ssl_context.load_cert(pemfile)
        self.ssl_context.load_client_ca(pemfile)
        self.ssl_context.load_verify_info(pemfile)
        #self.ssl_verify = SSL.verify_peer|SSL.verify_fail_if_no_peer_cert
        self.ssl_verify = SSL.verify_none 
        # peer|SSL.verify_fail_if_no_peer_cert
        self.ssl_context.set_allow_unknown_ca('True')
        self.ssl_context.set_verify(self.ssl_verify, ssl_depth)
        self.ssl_context.set_session_id_ctx(session_id)
        # self.ssl_context.set_info_callback(self.callback)


    def register_functions(self):
        self.server.register_introspection_functions()
        self.server.register_instance( self.xmlrpcwrapper )

    def launch_server(self):
        if self.env.config.enable_docserv.lower() == 'yes' and self.env.config.docserv_port:
            try: 
                pid = os.fork() 
                if pid > 0:
                    # exit from second parent, print eventual PID before
                    self.launch_doc_server()
                    sys.exit(0) 
            except OSError, e: 
                print >>sys.stderr, "fork failed: %d (%s)" % (e.errno, e.strerror) 
                sys.exit(1) 

        self.server.serve_forever()

    def launch_doc_server(self):
        self.doc_serv.serve_forever()


# see http://linux.duke.edu/~icon/misc/xmlrpcssl.py
