#!/usr/bin/env python

#program to animate simulations from database using matplotlib
import cPickle, glob, os, epigdal
from math import *
from qt import *
from numpy import *
import sqlobject as SO
import pylab as P
from matplotlib.patches import Polygon
from matplotlib import cm
from matplotlib.colors import rgb2hex

class viewer:
    """
    """
    def __init__(self, host='localhost', port=3306, user='epigrass', pw='epigrass', db='epigrass',backend='mysql',encoding='latin-1'):
        self.host = host
        self.port = port
        self.user = user
        self.pw = pw
        self.db = db
        self.backend = backend
        self.encoding = encoding
        
        if backend == 'sqlite':
            db_filename = os.path.abspath('Epigrass.db')
            connection_string = 'sqlite:' + db_filename
        elif backend == 'mysql':
            connection_string = r'%s://%s:%s@%s/%s'%(backend,user,pw,host,db)
        elif backend == 'csv':
            pass
        else:
            sys.exit('Invalid Database Backend specified: %s'%backend)
        if not backend == 'csv':
            self.connection = SO.connectionForURI(connection_string)
        self.dmap = 0#int(input('Draw Map?(0,1) '))
        self.tables = self.getTables()

        #self.nodes = self.readNodes(self.tables[table])
        #self.numbnodes = len(self.nodes)
        #self.data = self.readData(self.tables[table])
        #self.numbsteps = len(self.data)/self.numbnodes
        #self.viewGraph()
        
    def getTables(self):
        """
        Returns list of table names from current database connection
        """
        if self.backend == 'sqlite':
            r = [i[0] for i in self.connection.queryAll("select name from sqlite_master where type='table';")]
        elif self.backend == 'mysql':
            r = [i[0] for i in self.connection.queryAll('SHOW TABLES')]
        elif self.backend =='csv':
            r = glob.glob('*.tab')
        
        return r
    def getFields(self,table):
        """
        Returns a list of fields (column names) for a given table.
        table is a string with table name
        """
        if self.backend == 'sqlite':
            r = [i[1] for i in self.connection.queryAll('PRAGMA table_info(%s)'%table)]
        elif self.backend == 'mysql':
            r = [i[0] for i in self.connection.queryAll('SHOW FIELDS FROM %s'%table)]
        elif self.backend == 'csv':
            f = open(table,'r')
            r = f.read().strip().split(',')
            f.close()

        #select only the key names (each element in r is a tuple, containing
        # name and field descriptors )
        
        return r
    
    def readNodes(self,name,table):
        """
        Reads geocode and coords from database table
        for each node and adjacency matrix.
        """
        if self.backend =="csv":
            # the equivalent of a select for a csv file
            f=open(table,"r")
            names = f.readline().strip().split(",")#remove header
            d = {}
            for l in f:
                l=l.strip().split(',')
                d[l[names.index('geocode')]]=[l[names.index('geocode')],l[names.index('lat')],l[names.index('longit')],l[names.index('name')]]
            r= d.values()
            f.close()
                
        else:
            r = self.connection.queryAll('SELECT geocode,lat,longit,name FROM %s WHERE time = 0'%table)

        # get adjacency matrix
        #print os.getcwd()
        file = open('adj_'+name)
        m = cPickle.load(file)
        file.close()
        return r,m
    
    
    def readData(self,table):
        """
        read node time series data
        """
        if self.backend =="csv":
            f=open(table,"r")
            f.readline()#remove header
            r = []
            for l in f:
                l=l.strip().split(',')
                r.append(l)
            f.close()
        else:
            r = self.connection.queryAll('SELECT * FROM %s'%table)
        

        return r

    def readEdges(self,table):
        """
        Read edge time series
        """
        if self.backend =="csv":
            tab = table.split(".")[0]+"_e.tab"
            f = open(tab,"r")
            f.readline()#remove header
            r = [l.strip().split(',') for l in f]
            f.close()
        else:
            tab = table+'e'
            r = self.connection.queryAll('SELECT * FROM %s'%tab)

        return r
        
    def viewGraph2D(self, fname, geocfield):
        """
        Starts the pylab display of the graph.
        fname: shapefile with the polygons
        """
        fig  = P.figure()
        ax = fig.add_subplot(111)
        ax.set_title("Epidemic Dynamics")
        #Get the polygons
        g = ogr.Open (fname)
        L = g.GetLayer(0)
        N = 0
        pl = {}#polygon patch dictionary (by geocode)
        feat = L.GetNextFeature()
        while feat is not None:
            try:
                gc = feat.GetFieldAsInteger(geocfield)
            except:
                gc = 0
            field_count = L.GetLayerDefn().GetFieldCount()
            geo = feat.GetGeometryRef()
            if geo.GetGeometryCount()<2:
                g1 = geo.GetGeometryRef( 0 )
                x =[g1.GetX(i) for i in range(g1.GetPointCount()) ]
                y =[g1.GetY(i) for i in range(g1.GetPointCount()) ]
                m=transpose(r_[[x],[y]]) #Vértices del polígono
                poligono = matplotlib.patches.Polygon( m ) #Definimos el polígono
                #Le añadimos color al polígono, basado en un campo de la base de datos
                #poligono.set_facecolor ( color_map[feat.GetFieldAsInteger('color_map')-1])
                #Add the polygon to the figure axes
                pl[gc]=poligono
                ax.add_patch ( poligono )
            for c in range( geo.GetGeometryCount()):
                ring = geo.GetGeometryRef ( c )
                for cnt in range( ring.GetGeometryCount()):
                    g1 = ring.GetGeometryRef( cnt )
                    x =[g1.GetX(i) for i in range(g1.GetPointCount()) ]
                    y =[g1.GetY(i) for i in range(g1.GetPointCount()) ]
                    m=transpose(r_[[x],[y]]) #VÃ©rtices del polÃ­gono
                    poligono = matplotlib.patches.Polygon( m ) #Definimos el polÃ­gono
                    #Le aÃ±adimos color al polÃ­gono, basado en un campo de la base de datos
                    #poligono.set_facecolor ( color_map[feat.GetFieldAsInteger('color_map')-1])
                    #Add the polygon to the figure axes
                    pl[gc]=poligono
                    ax.add_patch ( poligono )
            feat = L.GetNextFeature()
        return ax, pl
            
    def anim2D(self,data, numbsteps,pos,ax,pl):
        """
        Starts the animation
        - data: time series from database
        - pos: column number of variable to animate
        - ax: is the axis containing the polygons
        - pl is the polygon dictionary
        """
        P.ion()
        jet  = cm.get_cmap("jet",100)
        for t in range(numbsteps):
            V.rate(rate)
            self.gr.timelabel.text=str(t) 
            for i in self.gr.nodes:
                start = i*numbsteps+t
                #print data[start][pos]
                color = jet(data[start][pos]/float(data[:,pos].max()))
                pl[data[start][0]].set_facecolor (color)
                n.ts.append(float(data[start][pos]))
            P.draw()

    
    def paintNode(self,t,node,numbsteps,col='r'):
        """
        Paints red the box corresponding to the node in the visual display
        """
        if col =='r':
            if not node.painted: 
                red = (int(numbsteps)-t)/float(numbsteps)
                blue = 1-red**6
                node.box.color = (red,0.,blue)
                node.painted = 1
        elif col =='g':
            node.box.color=V.color.green

    def plotTs(self,ts,name):
        """
        Uses gcurve to plot the time-series of a given city object
        """
##        try:
##            self.gg.display.visible=0
##        except:pass
        self.gg = VG.gdisplay(title='%s'%name,xtitle='time',ytitle='count')
        g=VG.gcurve(color=VG.color.green)
        for t,n in enumerate(ts):
            g.plot(pos=(t,n))
    
    def keyin(self,data,edata,numbsteps,pos,rate):
        """
        Implements keyboard and mouse interactions
        """
        while 1:
            ob = self.gr.display.mouse.pick
            try:
                ob.sn(2)
                if self.gr.display.mouse.alt and not ob.paren.tsdone:
                    self.plotTs(ob.paren.ts,ob.paren.name)
                    ob.paren.tsdone = 1
            except:pass
            if self.gr.display.mouse.clicked:
                m = self.gr.display.mouse.getclick()
                #print m.click
                loc = m.pos
                self.gr.display.center = loc
            if self.gr.display.kb.keys: # is there an event waiting to be processed?
                s = self.gr.display.kb.getkey() # obtain keyboard information
                if s == 'r': #Replay animation
                    self.anim2D(data,edata,numbsteps,pos,rate)
                else:
                    pass
        
if __name__ == "__main__":
    Display=viewer(user='root',pw='mysql')
    Display.anim()
    Display.keyin()
