#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
import sys
import os
import time
import string
from ConfigParser import ConfigParser, SafeConfigParser



""" 
    Ce module contien les fonctions/classes nécéssaires pour le traitement
    des fichier de configuration.
"""

__all__ = [ 'Config', 'DaemonConfig' ]

_daemon_valid_keys = [ 'host', 'port', 'debug', 'database_dir' , 'plugins', 'logfile', 'plugin_dir', 'enable_docserv', 'docserv_port', 'enable_ssl', 'pem_file', 'ssl_version', 'ssl_depth', 'ssl_identifier']
_plugin_valid_keys = [ 'plugin_type', 'description', 'interval' ]



class Config:
    """
    Cette classe utilise l'api de  base (ConfigParser) de python
    """

    def __init__(self, filename): 
        self._filename = filename
        self._parser = ConfigParser()
        
        if self._parser.read([ self._filename ]) is [] : 
            raise "Cannot parse configuration file"


    def set(self, section, name, value):
        """Change a configuration value.

        These changes are not persistent unless saved with `save()`.
        """
        if not self.parser.has_section(section):
            self.parser.add_section(section)
        return self.parser.set(section, name, value)

    def sections(self):
        return self.parser.section()


    def remove(self, section, name):
        if self.parser.has_section(section):
            self.parser.remove_option(section, name)


    

class DaemonConfig(Config):
    """
    Cette classe permet de rapatrier et de parser la configuration 
    principale.
    """
    def __init__(self, filename):
        self.set_default_config()
        Config.__init__(self, filename)
        self.parse_config()

    def set_default_config(self):
        """
        Positione la confuguration par défaut
        """
        self.plugin_dir=[]
        self.plugins = {}
        self.host = 'localhos'
        self.port = 8080
        self.debug = 'no'
        self.enable_docserv = 'no'
        self.docserv_port = 8081
        self.enable_ssl='no'
        self.pem_file=None
        self.ssl_version='sslv23'
        self.ssl_depth=10
        self.ssl_identifier='net6monssl'

    def parse_config(self):
        """
        Parse le fichier de configuration et position toutes les valeurs
        de configuration dans l'objet courant.
        """
        self.plugin_dir = []
        if self._parser.has_section("main"):
            # self.parse_daemon_config(self)
            for daemon_key in self._parser.options("main"):
                if daemon_key in _daemon_valid_keys:
                    """ directive plugin_dir de la forme : 
                            # plugin_dir = /foo , /bar,/prout/paf
                    """
                    #if daemon_key == "plugin_dir":
                    #    foo=self._parser.get("main","plugin_dir")
                    #    self.plugin_dir = foo.split(",")

                    if daemon_key == "plugins": 
                        for plug in self._parser.get("main", daemon_key).split(","):
                            self.plugins[plug.strip()]={}
                            self.parse_instance(plug.strip())
                    else: 
                        self.__dict__[daemon_key] = self._parser.get("main", daemon_key)
        else:
            raise "No main section, please, check config file"
    
        #if self.__dict__ not in _daemon_valid_keys:
        #    raise "Missing parameters" 


    def parse_instance(self, plugin_name):
        """
        Récupere la configuration relative à une instance de plugin.

        @param plugin_name: nom de l'instance à paser
        """
        if self._parser.has_section(plugin_name):
            for plugin_key in self._parser.options(plugin_name):
                if plugin_key in _plugin_valid_keys: 
                    val = self._parser.get(plugin_name, plugin_key) 
                    self.plugins[plugin_name][plugin_key]=val.strip()
        else:
            raise "plugin %s enabled but no [%s] section found"%(plugin_name, plugin_name)
   
        self.parse_instance_config(plugin_name)

        
    def parse_instance_config(self, plugin_name):
        """
        Recupere la configuration spécifique à une instance de plugin.

        @param plugin_name: nom de l'instance 

        @return: True en cas de succes, None si cette configuration n'existe pas
        """
        self.plugins[plugin_name]['config']={}
        if self._parser.has_section(plugin_name+":config"):
            for plug_key in self._parser.options(plugin_name+":config"):
                self.plugins[plugin_name]['config'][plug_key]=self._parser.get(plugin_name+":config", plug_key)
            return True
        else:
            return None
        
    def save_config(self, newfile=""):
        """
        Enregistre la configuration présente dans l'instance dans un fichier

        @param newfile: nom de fichier dans lequelle sauver la nouvelle configuration
        """
        if newfile == "": 
            newfile=self._filename

        new_conf=SafeConfigParser()
        new_conf.add_section("main")
        for i in self.plugins.keys(): 
            new_conf.add_section(i)
            for j in _plugin_valid_keys:
                new_conf.set(i, j, self.plugins[i][j])
        for i in self.plugins.keys():
            new_conf.add_section(i+":config")
            for j in self.plugins[i]['config'].keys():
                new_conf.set(i+":config", j , self.plugins[i]['config'][j])

        for i in _daemon_valid_keys: 
            if i != "plugins":
                new_conf.set("main", i, self.__dict__[i])
       
        # FIXME
        new_conf.set("main", "plugins", string.join(self.plugins.keys(), ","))
        new_conf.set("main", "plugin_dir" , self.plugin_dir)
       
        if os.path.isfile(newfile):
            os.rename(newfile, newfile+str(time.time()).split(".")[0]) 
        fileobj = file(newfile, 'w')
        try:
            new_conf.write(fileobj)
        finally:
            fileobj.close()
         
    def get_plugin_instance_config(self, instance_name ):
        """
        Renvoie le dictionaire de configuration d'un plugin à partir du nom de l'instance

        @param instance_name: nom de l'instance pour laquelle il faut récuperer la configuration
        """
        if not self.plugins.has_key(instance_name):
            self.log.error("No such instance name %s ", instance_name)
            return None
        if not self.plugins[instance_name].has_key('config'):
            return {}
        return self.plugins[instance_name]['config']

    def get_plugin_instance_type(self, instance_name): 
        """
        Renvoir la classe du plugin à instancier

        @param instance_name: nom de l'instance
        """

        if not self.plugins.has_key(instance_name): 
            self.log.error("No such instance name %s", instance_name)
            return None
        if not self.plugins[instance_name].has_key('plugin_type'):
            self.log.error("No plugins type specified for instance %s", instance_name)
            return None
        
        return self.plugins[instance_name]['plugin_type']
          

                
def test():
    myconf = DaemonConfig("netmon.conf")
    myconf.parse_config()
    print str(myconf.__dict__)
    myconf.save_config("test.new")


if __name__ == "__main__": 
    test()
