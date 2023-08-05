# -*- coding: iso-8859-1 -*-

from CGIHTTPServer import CGIHTTPRequestHandler
import xmlrpclib
import pmap

class nmCollectClient:
    def __init__(self,ip):
        self._ip = ip
        self._agent = xmlrpclib.ServerProxy("http://" + str(ip) + ":8081")

    def test_up(self):
        data = pmap.scan_host(self._ip)
        if (data['hostsup'] == '1'):
            return 1
        else:
            return 0

    def get_available_plugins(self):
        return self._agent.get_available_plugins()

    def get_instance_result(self,instance_name,date=0):
        if not date: 
            return self._agent.get_instance_result(instance_name)
        return self._agent.get_instance_result(instance_name,date)

if __name__ == "__main__" :
    collect = nmCollectClient("195.220.28.119")
    output = collect.test_up()
    print output


    output = collect.get_available_plugins()
    i=1
    for elem in output:
        print "Plugin " + str(i) + " " + str(elem)
        i=i+1 

    print collect.get_instance_result("foo", 0)

    
# * get_config_key(key(string)) -> return(string)
#       retourne la valeure d'une variable de configuration
#
# * set_config_key(key(string), value(string))
#       met a jour la valeure d'une variable de configuration
#
# * save_config()
#       sauve la configuration dans le fichier de conf.
#
# * get_available_plugins()  -> return(list)
#       renvoie une liste des plugins disponibles sur la machine
#
# * add_instance(instance_name(string), plugin_type(string), description(string), interval(int), config(dict))#
#       ajoute une instance de plugin dans la liste en cours.
#
# * remove_instance(instance_name(string))
#       supprime une instance en cour d'instantiation
#
# * set_instance_config(instance_name(string),config(dict))
#       met a jour la configuration d'une instance
#
# * set_instance_description(instance_name(string),description(string))
#       met a jour la description d'une instance
#
# * set_instance_interval(instance_name(string),interval(int))
#       fixe l'intervale d'execution d'une instance
#
# * get_instance_config(instance_name(string))  -> return(dict)
#       renvoie un dictionaire représentant la configuration d'une
#       instance
#
# * get_instance_type(instance_name(string)) -> return(string)
#       renvoie le type de plugin instancié sous le nom "instance_name"
#
# * get_instance_description(instance_name(string))  -> return(string)
#       renvoie la description de l'instance "instance_name"
#
# * get_instance_interval(instance_name(string) -> return(int)
#       renvoie l'interval d'execution de l'instance "instance_name"
#
# * get_instances_list()  -> return(list)
#       renvoie une liste d'instance en execution
#
# * get_result(instance_name(string), date(timestamp)) -> return(dict)
#       renvoie un dictionaire représentant les lignes de la table
#       associé a l'instance "instance_name" à la data la plus proche de
#       "date".
#
# * get_results(instance_name(string), date_start(timestamp), date_stop(timestamp)) -> return(tuple)   (list of dict)
#       renvoie le contenu de la table associé à la base entre
#       "date_start" et "date_stop".
#       si "date_start" vaut 0 alors elle est consideré à 0
#       si "date_stop" vaut 0 alors elle est consideré comme infinie
#
#       renvoie un tuple de la forme suivante
#               ( <colones de la table>, [ ( <ligne1> ) , .... , <lignen> ])
#       ou ligne1...lignen sont des tuples.
#
# * purge_instance_table(instance_name(string))
#       purge la table associé à l'instance "instance_name"
#
# * purge_instance_table_from(instance_name(string), date_from(timestamp))
#       purge la table associé a l'instance "instance_name" depuis la
#       data la plus petite usqu'a la date "date_from".
#
# * purge_all_instances_table(bool only_for_actives_instances=True)
#       purge toutes le tables de toutes les instance.
#
# * purge_all_instances_table_from(date_from(timestamp), bool only_for_actives_instances=True)
#       purge toutes les tables de toutes les instance depuis la date la
#       plus petite jusqu'a la date "data_from".
#
# * get_databases_list() -> return(list).
#       liste toutes les bases de donnée présentes.
