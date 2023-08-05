# -*- coding: iso-8859-1 -*-

import os
import time
# from plugin import *
from env import Environment
from pysqlite2 import dbapi2 as sqlite
from net6mon import uuid

# __all__ = [ 'SQLMapper' ]

_valid_type = [ 'STRING' , 'INTEGER', 'REAL', 'TEXT', 'BLOB' ]

class SQLdb(object):
    
    def __init__(self, dbname):
        
        if not os.access( dbname, os.R_OK):
            raise "Cannot acces database %s"%dbname
        
        self._db = dbname;

    def connect(self):
        # connection à la base de donnée
        self._con = sqlite.connect(self._db)
        self._con.isolation_level = "IMMEDIATE"
        # sqlite.enable_shared_cache(True)
        if self._con is None: 
            return None 
        # récupération d'un cursseur
        self._cur =self._con.cursor()
        return True

    def close(self):
        if self._cur: 
            self._con.commit()
            self._cur.close()
            self._con.close()
            self._con=None
            self._cur=None
        return True
        

    def is_table_exists(self, tablename):
        """
            Vérifie si la table existe déja.
            Dans le cas ou la table existe, vérifie si le schéma de la
            table existante est le meme que celui de l'objet courant.
            Si le schéma n'est pas le meme, la table est surpprimé et la valeur renvoyé
            est 'False'.
            Si le schéma est la table existe et le schéma est le meme, renvoie 'True'.
            Si la table n'existe pas, renvoie 'False'

            @return: False si la table n'existe pas ou existe avec un schéma différent,
                     True si la table existe avec le meme schéma
        """
        tablename=tablename.replace("-", "_")
        self.connect()
        self._cur.execute("pragma table_info(%s);"%tablename)
        list = self._cur.fetchall()
        return len(list)


    def insert(self, tablename, **values):
        """
            Insert des valeurs dans la table
            
            @param values: Représente un dictionaire de valeures de la forme suivante: E{lb} 'nom_de_colonne':<valeure> , ...  E{rb}
        """
        vals=""
        a=0
        for i in values.keys():
            if not self._col_exists_in_schema(i):
                raise "No such column name %s"%i
        max=len(values.keys())
        for i in values.keys():
            if self._col_exists_in_schema(i):
                coltype = self._get_col_type(i)
                if coltype in [ 'INTEGER' , 'REAL' ]: 
                    vals=vals + " %s "%(values[i])
                if coltype in ['STRING'  , 'TEXT' ]:
                    str = "%s"%values[i]
                    str=str.replace("'", "''")
                    vals=vals + " '%s'"%(str)
                if coltype in [ 'BLOB'  ]: 
                    vals=vals + " '%s' "%(values[i])
                a=a+1
                if a < max: 
                    vals = vals + ", "
        cols=""
        a=0
        for i in values.keys():
            cols=cols+i
            a=a+1
            if a<max:
                cols = cols + ", " 
        ts="%s"%time.time();
        ts=ts.split(".")[0]
        query = "insert into %s (timestamp, instance, hostid, %s) values ('%s', '%s', '%s', %s);"%(tablename,  cols, str(hostid), ts, self._instance, vals)
        self.connect()
        try:
            self._cur.execute(query)
        except sqlite.OperationalError:
            print "locked or error in querry"

        self.close()


    def _get_table_schema(self, tblname):
        query = "select * from %s where instance=='%s'"%(self._table, self._instance)
        self.connect()
        self._cur.execute(query)
        schema = []
        for field in self._cur.description: 
            schema.append(field[0])
        return tuple(schema)

    
    def get_schema(self,tblname):
        s = self._get_table_schema(tblname)
        return s





class SQLMapper(object):
    
    
    def __new__(self, dbname, table_name, instance_name, hostid = "" ): 
        """ 
            cré un nouveau SQLMapper
            @param dbname: nom de fichier de la base de données
            @param table_name: nom de la table
            @param instance_name: nom de l'instance 
        """
        obj = object.__new__(self, dbname, table_name, instance_name)

        # Tout schéma de base contien un timestamp et le nom d'une instance 
        obj._schema = [ { u'timestamp':u'INTEGER' },
                        { u'instance':u'STRING' },
                        { u'hostid':u'STRING' } ]
        obj._con=None
        obj._cur=None
        obj._db = dbname
        obj._table = table_name.replace("-", "_")
        obj._instance = instance_name
        if not hostid:
            self._hostid = "NET6MON:"+str(uuid.getaddr())
        else: 
            self._hostid = hostid
        
        return obj
       
    def __init__(self, dbname, table_name, instance_name):
        pass

    def connect(self):
        # connection à la base de donnée
        self._con = sqlite.connect(self._db)
        self._con.isolation_level = "IMMEDIATE"
        # sqlite.enable_shared_cache(True)
        if self._con is None: 
            return None 
        # récupération d'un cursseur
        self._cur =self._con.cursor()
        return True

    def close(self):
        if self._cur: 
            self._con.commit()
            self._cur.close()
            self._con.close()
            self._con=None
            self._cur=None
        return True
        
    def _col_exists_in_schema(self, name ): 
        """
            Vérifie si une colone existe déja dans le schéma courant de la table 

            @param name: nom de la colonne
        """
        for i in self._schema:
            if name in i.keys():
                return True
        return False

    def _get_col_type(self, name):
        """
            Renvoie le type de la colonne
            @param name: nom de la colonne 
            @return:False si pas de colonne nomée ''name'', INTEGER/STRING/TEXT/BLOB sinon
        """
        for i in self._schema:
            if i.has_key(name): 
                return i[name]
        return False

            
    def string_col(self,name):
        """
            Ajoute une colone de type string au schéma 
            @param name: nom de la colonne
        """
        if not self._col_exists_in_schema(name): 
            self._schema.append({ name:u'STRING'})
    def int_col(self,name):
        """
            Ajoute une colonne de type int au schéma
            @param name: nom de la colonne
        """
        if not self._col_exists_in_schema(name): 
            self._schema.append({name:u'INTEGER'})
    def blob_col(self,name):
        """
            Ajoute une colonne de type blob au schéma
            @param name: nom de la colonne
        """
        if not self._col_exists_in_schema(name): 
            self._schema.append({ name:u'BLOB' } )
    def real_col(self,name):
        """
            Ajoute une colonne de type real au schéma
            @param name: nom de la colonne
        """
        if not self._col_exists_in_schema(name): 
            self._schema.append({ name:u'REAL'} )
    def text_col(self,name):
        """
            Ajoute une colonne de type text au schéma
            @param name: nom de la colonne
        """
        if not self._col_exists_in_schema(name): 
            self._schema.append( { name:u'TEXT' } )
    
    def _is_table_exists(self):
        """
            Vérifie si la table existe déja.
            Dans le cas ou la table existe, vérifie si le schéma de la
            table existante est le meme que celui de l'objet courant.
            Si le schéma n'est pas le meme, la table est surpprimé et la valeur renvoyé
            est 'False'.
            Si le schéma est la table existe et le schéma est le meme, renvoie 'True'.
            Si la table n'existe pas, renvoie 'False'

            @return: False si la table n'existe pas ou existe avec un schéma différent,
                     True si la table existe avec le meme schéma
        """
        self.connect()
        self._cur.execute("pragma table_info(%s);"%self._table)
        list = self._cur.fetchall()
        if list:
            cols = []
            for i in list:
                cols.append({ i[1]:i[2]})

            if self._schema == cols:
                return True
            else:
                self._cur.execute("drop table %s"%self._table)
                self._con.commit()
        self._con.commit()
        self.close()
        return False

    def init_db(self):
        """
            Appel la fonction privé _create_table(..).
            Cette fonction sert à éffectuer les opérations préalables à
            l'utilisation de la base de donnée
            Note Importante: Cette appel toit etre effectué apres la construction du schéma
            par les fonction <type>_col(name).
        """
        self._create_table()
        
        
    def _create_table(self):
        """
            Cré une table
        """
        if ( self._is_table_exists() ):
            return 

        table = ""
        a=0
        max=len(self._schema)
        for i in self._schema:
            table=table + i.keys()[0] + " " + i.values()[0]
            a=a+1
            if a < max :
                table = table + ", "
    
        query = "create table %s(%s);"%(self._table,table)
        self.connect()
        self._cur.execute(query)
        self._con.commit()
        self.close()

    def insert(self, **values):
        """
            Insert des valeurs dans la table
            
            @param values: Représente un dictionaire de valeures de la forme suivante: E{lb} 'nom_de_colonne':<valeure> , ...  E{rb}
        """
        vals=""
        a=0
        for i in values.keys():
            if not self._col_exists_in_schema(i):
                raise "No such column name %s"%i
        max=len(values.keys())
        for i in values.keys():
            if self._col_exists_in_schema(i):
                coltype = self._get_col_type(i)
                if coltype in [ 'INTEGER' , 'REAL' ]: 
                    vals=vals + " %s "%(values[i])
                if coltype in ['STRING'  , 'TEXT' ]:
                    str = "%s"%values[i]
                    str=str.replace("'", "''")
                    vals=vals + " '%s'"%(str)
                if coltype in [ 'BLOB'  ]: 
                    vals=vals + " '%s' "%(values[i])
                a=a+1
                if a < max: 
                    vals = vals + ", "
        cols=""
        a=0
        for i in values.keys():
            cols=cols+i
            a=a+1
            if a<max:
                cols = cols + ", " 
        ts="%s"%time.time();
        ts=ts.split(".")[0]
        query = "insert into %s (timestamp, instance, hostid,  %s) values ('%s', '%s', '%s', %s);"%(self._table,  cols, ts, self._instance, self._hostid,  vals)
        self.connect()
        try:
            self._cur.execute(query)
        except sqlite.OperationalError:
            print "locked or error in querry"

        self.close()

    def set_hostid(self, hostid): 
        self._hostid = hostid

    def get_hostid(self):
        return self._hostid

    def _get_table_schema(self):
        query = "select * from %s where instance=='%s'"%(self._table, self._instance)
        self.connect()
        self._cur.execute(query)
        schema = []
        for field in self._cur.description: 
            schema.append(field[0])
        return tuple(schema)

    def get_tbl_creation_query(self):
        query = "SELECT sql FROM sqlite_master WHERE tbl_name='%s'"%self._table
        self.connect()
        self._cur.execute(query)
        return self._cur.fetchall()[0][0]
    
    def get_schema(self):
        s = self._get_table_schema()
        return s

    def get_row_at_date(self, date):
        query1 = "select * from %s where (timestamp >= %s and instance == '%s') limit 1"%(self._table, date, self._instance)
        query2 = "select * from %s where (timestamp <= %s and instance == '%s') limit 1"%(self._table, date, self._instance)
        self.connect()
        try:
            self._cur.execute(query1)
        except sqlite.OperationalError:
            raise "Error in query or db locked"
        l = self._cur.fetchone() 
        self.close()
        return l

    def get_rows_between_dates(self, date_start, date_stop):
        
        if date_start == 0 and date_stop == 0:
            query1 = "select * from %s"%self._table
        elif date_start ==0:
            query1 = "select * from %s where timestamp <= %s"%(self._table, date_stop)
        elif date_stop == 0:
            query1 = "select * from %s where timestamp >= %s"%(self._table, date_start)
        else: 
            query1 = "select * from %s where (timestamp >= %s and timestamp <= %s)"%(self._table, date_start, date_stop)
        
        self.connect()
        try:
            self._cur.execute(query1)
        except sqlite.OperationalError:
            raise "Error in query or db locked"
        r = self._cur.fetchall()
        self.close()
        return r

    def get_rows(self):
        query1 = "select * from %s"%(self._table)
        self.connect()
        try:
            self._cur.execute(query1)
        except sqlite.OperationalError:
            raise "Error in query or db locked"
        r = self._cur.fetchall()
        self.close()
        return r
    



    def purge_rows(self):
        query1 = "delete from %s"%self._table
        self.connect()
        self._cur.execute(query1)
        try:
            self._cur.execute(query)
        except sqlite.OperationalError:
            raise "Error in query or db locked"
        self.close()
        return True
   
    def purge_rows_from(self, date_start): 
        query = "delete from %s where timestamp <= %s"%(self._table, start_start)
        self.connect()
        self._cur.execute(query1)
        try:
            self._cur.execute(query)
        except sqlite.OperationalError:
            raise "Error in query or db locked"
        self.close()
        return True
  
    def purge_rows_between(self, date_start, date_stop):
        query = "delete from %s where (timestamp >= %s and timestamp <= %s)"%(self._table, date_start, date_stop)
        self.connect()
        self._cur.execute(query1)
        try:
            self._cur.execute(query)
        except sqlite.OperationalError:
            raise "Error in query or db locked"
        self.close()
        return True
    
    



class TestSQLMapper(SQLMapper):
    """ 
        Classe de test

    """
    def __init__(self,dbname,table_name, instance_name):
        # appel du constructeur parent
        # SQLMapper.__init__(self, dbname, table_name, instance_name) 
  
        # création d'un schéma potable
        self.string_col('Nom')
        self.real_col('ts')
        
        # intialisation de la base de donné 
        self.init_db()
    




def drop_table_if_exists(db,table):
    """
        Fonction utilisé pour supprimer une table d'une base si elle existe
    """
    try:
        con = sqlite.connect(db)
    except:
        raise "Cannot connect to %s"%db

    # récupération d'un cursseur
    cur = con.cursor()
    
    cur.execute("pragma table_info(%s);"%table)

    list = cur.fetchall()
    if len(list) != 0:
        cur.execute("drop table %s"%table)
        con.commit()
    
    cur.close()
    con.close()    
    return True





if __name__ == '__main__': 
    
    t = TestSQLMapper("foo.db", "TimeCooler", "instance0")
    print t._schema
    t.insert(Nom="qsdlkqsdk", ts=time.time())
    print t.get_row_between_dates(0, 200000000000)

