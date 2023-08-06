from ZODB.PersistentMapping import PersistentMapping
from ZODB.PersistentList import PersistentList
import sqlite
from DateTime import DateTime

"""
 store(padre_url,mi_url,owner_id,attrs_dict)
 bicho get_obj(url)
 bicho.childs()
 bicho.owner()
 bicho.keys()
 bicho.get_attr(attr)
"""
DUBLIN_CORE = ["contributors","created","creators", "description", "effective",
                "expires", "modified", "publisher", "subjects", "title"]

class SQLMonger(object):
    def __init__(self, dbpath):
        self.dbpath = dbpath
        super(SQLMonger, self).__init__()
        self.db = sqlite.connect(self.dbpath)
        self.db.autocommit = True
        self.initialize()

    def initialize(self):
        cursor = self.db.cursor()
        cursor.execute("pragma table_info(objects)")
        if len(cursor.fetchall()) == 0:
            query = """CREATE TABLE objects (   url VARCHAR PRIMARY KEY,
                                                parent_url VARCHAR,
                                                contributors VARCHAR,
                                                created VARCHAR,
                                                creators VARCHAR,
                                                description VARCHAR,
                                                effective VARCHAR,
                                                expires VARCHAR,
                                                modified VARCHAR,
                                                publisher VARCHAR,
                                                subjects VARCHAR,
                                                title VARCHAR )
                                                """
            cursor.execute(query)
            query = """ CREATE TABLE attributes(    object  VARCHAR,
                                                    name    VARCHAR,
                                                    value   VARCHAR,
                                                    PRIMARY KEY (object, name) )
                                                   """
            cursor.execute(query)
            cursor.close()


    def store(self, url, parent_url, attrs):
        """
        Saves an object and its attributes in the database
        """
        cursor = self.db.cursor()
        dc_ordered_keys = [key for key in attrs.keys() if (key.lower() in DUBLIN_CORE) and
                                                                    attrs.get(key)]
        dc_fields = ','.join(dc_ordered_keys)

        extra_values = [url,parent_url]
        query = """INSERT INTO objects (url, parent_url, %s ) VALUES (%%s, %%s """ % dc_fields
        extra_attr_holders = ",%s"*len(dc_ordered_keys)
        extra_values += [attrs.get(key) for key in dc_ordered_keys]

        cursor.execute(query+extra_attr_holders+')', tuple(extra_values))


        #Extra Attributes
        to_be_saved = [aKey for aKey in attrs.keys() if aKey not in DUBLIN_CORE]
        while to_be_saved:
            attribute = to_be_saved.pop()
            cursor.execute(u"""INSERT INTO attributes (object, name, value)
                                VALUES  (%s, %s, %s) """, (url,attribute,attrs.get(attribute)) )

        #closing
        cursor.close()

    def generic_load(self, criteria):
        cursor = self.db.cursor()
        query_fields = ['url', 'parent_url'] + DUBLIN_CORE
        query = u"""SELECT %s FROM objects WHERE """ + u",".join(["""%s="%s" """ % (key, criteria.get(key)) for key in criteria])
        query = query % u",".join(query_fields)
        cursor.execute(query)

        result = []
        for each_row in cursor.fetchall():
            sub_cursor = self.db.cursor()
            sub_cursor.execute(u"""SELECT name, value FROM attributes WHERE object=%s""", each_row[0])
            extra_fields = [keyvaluepair for keyvaluepair in sub_cursor.fetchall()]
            base_fields = dict(zip(query_fields,each_row ))
            base_fields.update(dict(extra_fields))
            result.append(base_fields)
            sub_cursor.close()
        cursor.close()
        return result

    def load(self, url):
        result = self.generic_load({'url':url})
        result = result[:1]

        if result:
            result = result[0]
            del(result['url'])
        else:
            result = {}
        return Bicho(self, url, result)

    def load_many(self, url):
        result = self.generic_load({'parent_url':url})
        bichos = []
        for each_result in result:
            child_url = each_result['url']
            del(each_result['url'])
            bichos.append(Bicho(self, child_url, each_result))
        return bichos



class Bicho(object):
    def __init__(self, db, url, attrs):
        extra_attrs = attrs
        self._childs = []
        self.db = db
        self.url = url
        for element in DUBLIN_CORE:
            setattr(self, element, extra_attrs.get(element, None))
            if element in extra_attrs.keys():
                del(extra_attrs[element])

        self._extra_attrs = extra_attrs

    def keys(self):
        return DUBLIN_CORE + self._extra_attrs.keys()

    def childs(self):
        if not self._childs:
            try:
                self._childs = self.db.load_many(self.url.replace('%','%%'))
            except:
                pass
        return self._childs



    def __getattribute__(self, attribute):
        if attribute in object.__getattribute__(self,'_extra_attrs').keys():
            try:
                returnatable = eval(self._extra_attrs.get(attribute))
            except:
                returnatable = self._extra_attrs.get(attribute)
            return make_persistent(returnatable)
        if attribute in DUBLIN_CORE:
            try:
                returnatable = eval(super(Bicho, self).__getattribute__(attribute))
            except:
                returnatable = super(Bicho, self).__getattribute__(attribute)
            return make_persistent(returnatable)
        try:
            an_attr = super(Bicho, self).__getattribute__(attribute)
        except: 
            an_attr = None
        return an_attr

def make_persistent(item):
    if not isinstance(item,(dict,list)):
        return item
    if isinstance(item,list):
        return PersistentList([make_persistent(subitem) for subitem in item])
    if isinstance(item,dict):
        new_map = dict([(key,make_persistent(subitem)) for key,subitem in item.values()])
        return PersistentMapping(new_map)

if __name__ == '__main__':
    algo = SQLMonger("sqlitemonger")
    algun = algo.load('http://localhost:8080/knmp/welkom-bij-de-knmp')
