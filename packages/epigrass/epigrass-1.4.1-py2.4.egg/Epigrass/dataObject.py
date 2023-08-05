# Module for interacting with the database backend through SQLObject 
# 10/2005 - Flavio Codeco Coelho
from    sqlobject import *



##user='root'
##pw='mysql'
##host='localhost'
##db='epigrass'
##name='testando'



class Site(SQLObject):
    _uri = r'mysql://root:mysql@localhost/epigrass'
    _connection = connectionForURI(_uri)
    _table = 'site'
    geocode = IntCol()
    time = IntCol()
    totpop = IntCol()
    name = StringCol()
    lat = FloatCol()
    longit = FloatCol()
    
class Edge(SQLObject):
    _uri = r'mysql://root:mysql@localhost/epigrass'
    _connection = connectionForURI(_uri)
    _table = 'site'+'e'
    source_code = IntCol()
    dest_code = IntCol()
    time = IntCol()
    ftheta = FloatCol()
    btheta =FloatCol()
    
if __name__ =='__main__':
    Site._table='testando'
    Site.createTable()
    Edge.createTable()
    dicin={'geocodigo':0000000,'time':0,'name':'euheim','lat':10.1,'longit':20.3}
    Site(**dicin)
    
