# -*- coding: iso-8859-1 -*-

from CGIHTTPServer import CGIHTTPRequestHandler
import xmlrpclib
import socket
import os
import pmap
import utils


class nmCollectClient:
    def __init__(self, ip, port=8081, ssl_enable=False, pem_file="", ssl_idx="net6monssl", ssl_depth=10, ssl_version="sslv23"):
        self._ip = ip
        if ssl_enable and os.access(pem_file, os.R_OK):
            print "enabling ssl"
            from M2Crypto import SSL
            from M2Crypto.m2xmlrpclib import SSL_Transport, Server
            self._init_ssl_context(pem_file, ssl_idx, ssl_depth, ssl_version)  
            self._agent=Server("https://" + str(ip) + ":" + str(port), SSL_Transport(ssl_context=self.ssl_context))
        else:
            self._agent = xmlrpclib.ServerProxy("http://" + str(ip) + ":" + str(port))

    def _init_ssl_context(self, pem_file, ssl_idx, ssl_depth, ssl_version):
        self.ssl_context = SSL.Context()
        self.ssl_context.load_cert(pem_file)
        self.ssl_context.load_client_ca(pem_file)
        self.ssl_context.load_verify_info(pem_file)
        #self.ssl_verify = SSL.verify_peer|SSL.verify_fail_if_no_peer_cert
        self.ssl_verify = SSL.verify_none 
        # peer|SSL.verify_fail_if_no_peer_cert
        self.ssl_context.set_verify(self.ssl_verify, ssl_depth)
        self.ssl_context.set_allow_unknown_ca('True')
        self.ssl_context.set_session_id_ctx(ssl_idx)

    def test_up(self):
        data = pmap.scan_host(self._ip)
        if (data['hostsup'] == '1'):
            return 1
        else:
            return 0

    def get_available_plugins(self):
        return self._agent.get_available_plugins()

    def get_instance_config(self,instance_name):
        return self._agent.get_instance_config(instance_name)

    def get_instance_description(self,instance_name):
        return self._agent.get_instance_description(instance_name)

    def get_instance_interval(self,instance_name):
        return self._agent.get_instance_interval(instance_name)

    def get_instance_type(self,instance_name):
        return self._agent.get_instance_type(instance_name)

    def get_instance_result(self,instance_name,date=0):
        if not date: 
            return self._agent.get_instance_result(instance_name)
        return self._agent.get_instance_result(instance_name,date)

    def get_instances_list(self):
		return self._agent.get_instances_list()

    def get_actives_instances(self):
        return self._agent.get_actives_instances()

    def set_instance_config(self, instance_name, config):
        self._agent.set_instance_config(instance_name,config)

    def set_instance_description(self, instance_name, config):
        self._agent.set_instance_description(instance_name,config)

    def set_instance_interval(self, instance_name, config):
        self._agent.set_instance_interval(instance_name,config)

    def get_os(self):
        return self._agent.get_os()
    
    def get_hostname(self):
        return self._agent.get_hostname()

    def get_bind_iface(self):
        bif = self._agent.get_bind_iface(); 

        if bif == "0.0.0.0":
            try:
                bif = socket.gethostbyaddr(self._ip)
            except: 
                return "0.0.0.0"
        return socket.gethostbyaddr(self._ip)[2] 
    def get_uid(self):
        return str(self._agent.get_uid())
    
    
    def get_instance_result(self, instance_name, date):
        """
        Get an instance result at date <date>
        @param date: date of result (timestamp)
        @return: the closest result found in the database
        """
        return self._agent.get_instance_result(self, instance_name, date)

    def get_instance_result(self, instance_name):
        """
        Get an instance result for now. Run plugin instance's get_result and 
        search in the instance database for a record.
        @param instance_name: name of the instance
        @return: a list containing table schema and table record: 
            [ [ col1, col2, ...], [ [ l1col1, l1col2,...], [ l2col1, l2col2, ...], ...] ]
        """
        return self._agent.get_instance_result(instance_name)

    def get_instance_results_between(self, instance_name, date_start, date_stop):
        """
        Get records in instance's database from date_start to date_stop
        """
        return self._agent.get_instance_results_between(instance_name, date_start, date_stop)
   
    def get_instance_results(self, instance_name):
        """
        Get all record in instance database
        """
        return self._agent.get_instance_results(instance_name)

    def ping(self):
        """
        Dummy function
        """
        return self._agent.ping()
    
    def get_instance_table_creation_query(self, instance_name):
        return self._agent.get_instance_table_creation_query(instance_name)



def print_results(results):

    id=0
    for i in results[0]:
        print results[0][id].ljust(12) + "|" , 
        id=id+1
    for i in results[1]:
        for j in i:
            print str(j).ljust(12) + "|" , 
        print    




def ssl_agent():
    agent = nmCollectClient("192.168.1.4", 8081) #, ssl_enable=True, pem_file="client.pem"); 
    print agent.get_available_plugins()
    print agent.get_os()
    print agent.get_hostname()
    print agent.get_bind_iface()
    print agent.get_uid()
    print agent.ping()
    il = agent.get_instances_list()
    for i in il:
        print agent.get_instance_table_creation_query(i['plugin_instance_name'])
        print agent.get_instance_results_between(i['plugin_instance_name'], 0 , 0)
        #print i['plugin_instance_name']
        #print "-----------------------"
        #results=agent.get_instance_results(i['plugin_instance_name'])
        #print_results(results)
        #print agent.get_instance_result(i['plugin_instance_name']) # , utils.get_timestamp()-100)
        #print_results(results)

if __name__ == "__main__" :
    #agent = nmCollectClient("195.220.28.122")
    #print agent.get_available_plugins()
    ssl_agent()

    #agent = xmlrpclib.ServerProxy("http://195.220.28.122:8081");
    
    #print agent.get_available_plugins()
    #print agent.get_actives_instances()
    #print agent.get_instance_result("os")
    #print agent.get_instance_config("os")
    #print agent.get_instances_list()

#    print agent.get_instance_description("os")
#    print agent.get_instance_interval("os")
#    print agent.get_instance_type("os")































