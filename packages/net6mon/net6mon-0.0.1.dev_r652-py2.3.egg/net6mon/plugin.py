# -*- coding: iso-8859-1 -*-
from sets import Set
import inspect
from sql import SQLMapper

"""
	Ce module contient les classes de bases, c'est à dire les classes prototype
	des plugins

	Quelques lignes empruntées de :
	http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/204349
"""

class InterfaceOmission(Exception):
    """
    	Exception appelée quand une méthode non implémentée est trouvée
    	dans le plugin
    """


class nmBasePluginInterface(object):
    """
    	Cette classe est une interface de base pour notre système de plugin.
    	Chaque plugin doit l'implémenter.
    
    	On déclare ici les méthodes que chaque plugin peut implémenter
    """

    def get_result(self):
        """
            get_result
        """
        pass
    
    

   
class InterfaceChecker(type):
    """
    	Cette classe sert à valider la présence des attributs nécessaires à un objet plugin
    """
    
    def __new__(cls, classname, bases, classdict):
        obj = type.__new__(cls, classname, bases, classdict)
        interface = classdict.get('__implements__')
        if interface:
            defined = Set(dir(obj))
            required = Set(dir(interface))
            if not required.issubset(defined):
                missing = list(required - defined)
                error = "Not implemented methods from %s : %r"
                raise InterfaceOmission, error % (interface.__name__,
                                                  missing)

        # safety check
        if classname != 'nmPlugin':
            assert obj.implements(nmBasePluginInterface), \
                   "You need to implement at least nmBasePluginInterface in %r" % classname
        
        return obj


class nmPlugin(SQLMapper):
    """
    	Cette classe est la classe de base de nos plugins

    	Chaque plugin doit hériter de cette classe et au moins implémenter la classe nmBasePluginInterface
    """
   
    __metaclass__ = InterfaceChecker

    def __new__(cls,mytype,myname, config, logger, db):
        obj = SQLMapper.__new__(cls, db, mytype, myname)
        obj.config=config
        obj.logger=logger
        obj.instance_name=myname
        obj.database=db
        return obj;

    def __init__(self,mytype, myname, config, logger, db):
        print "fooo"
        pass

    def implements(cls, interface):
        """
        	Vérifie si la classe implémente l'interface de base
        	recherchée dans la liste __implements__t.
        """

        assert hasattr(cls, '__implements__'), "Missing __implements__ in %r" % cls

        def findInterface(interface, iface,doInspect=True):
            """ 
                echerche une interface 
            
                @param iface: liste des interfaces
                @param interface: interface à chercher 
            """
            if doInspect:
                classTree = inspect.getclasstree([iface,])
            else:
                classTree = iface
            for item in classTree:
                try:
                    (typ, subTree) = item
                except TypeError:
                    return False
                except ValueError:
                    (typ, subTree) = item[0]
                if (interface.__name__ == typ.__name__) \
                       or findInterface(interface, subTree,doInspect=False) :
                    return True
            return False

        return findInterface(interface, cls.__implements__)
    
    implements = classmethod(implements)

