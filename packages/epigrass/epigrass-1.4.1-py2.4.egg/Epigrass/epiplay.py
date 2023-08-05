#!/usr/bin/env python

#program to play simulations from database
import MySQLdb, dgraph, cPickle
import visual as V
import visual.graph as VG
from math import *
from qt import *
from Numeric import *
#from pylab import *



class viewer:
    """
    """
    def __init__(self, host='localhost', port=3306, user='epigrass', pw='epigrass', db='epigrass'):
        self.host = host
        self.port = port
        self.user = user
        self.pw = pw
        self.db = db
        
        self.dmap = 0#int(input('Draw Map?(0,1) '))
        self.tables = self.getTables()

        #self.nodes = self.readNodes(self.tables[table])
        #self.numbnodes = len(self.nodes)
        #self.data = self.readData(self.tables[table])
        #self.numbsteps = len(self.data)/self.numbnodes
        #self.viewGraph()
        
    
    def getTables(self):
        """
        Returns a list of tables.
        """
        con=None
        try:
            con = MySQLdb.connect(host=self.host, port=self.port, user=self.user,passwd=self.pw, db=self.db)
            Cursor = con.cursor()
            Cursor.execute('SHOW TABLES')
            r=Cursor.fetchall()
        finally:
            if con:
                con.close()
                
        res = [i[0] for i in r]
        return res
        
    def getFields(self,table):
        """
        Returns a list of fields (column names) for a given table.
        """
        con=None
        try:
            con = MySQLdb.connect(host=self.host, port=self.port, user=self.user,passwd=self.pw, db=self.db)
            Cursor = con.cursor()
            Cursor.execute('SHOW FIELDS FROM %s'%table)
            r=Cursor.fetchall()
        finally:
            if con:
                con.close()
        #select only the key names (each element in r is a tuple, containing
        # name and field descriptors )
        res = [i[0] for i in r]
        return res
    
    def readNodes(self,name,table):
        """
        Reads geocode and coords from database table
        for each node and adjacency matrix.
        """
        con=None
        try:
            con = MySQLdb.connect(host=self.host, port=self.port, user=self.user,passwd=self.pw, db=self.db)
            Cursor = con.cursor()
            Cursor.execute('SELECT geocode,lat,longit,name FROM %s WHERE time = 0'%table)
            r=Cursor.fetchall()
            # get adjacency matrix
            file = open('adj_'+name)
            m = cPickle.load(file)
            file.close()
            
        finally:
            if con:
                con.close()
        return r,m
    
    
    def readData(self,table):
        """
        read node time series data
        """
        con=None
        try:
            con = MySQLdb.connect(host=self.host, port=self.port, user=self.user,passwd=self.pw, db=self.db)
            Cursor = con.cursor()
            Cursor.execute('SELECT * FROM %s'%table)
            r=Cursor.fetchall()
        finally:
            if con:
                con.close()
        return r

    def readEdges(self,table):
        """
        Read edge time series
        """
        tab = table+'e'
        con=None
        try:
            con = MySQLdb.connect(host=self.host, port=self.port, user=self.user,passwd=self.pw, db=self.db)
            Cursor = con.cursor()
            Cursor.execute('SELECT * FROM %s'%tab)
            r=Cursor.fetchall()
        finally:
            if con:
                con.close()
        return r
        
    def viewGraph(self, nodes, am, var,mapa=''):
        """
        Starts the Vpython display of the graph.
        """
        self.gr = dgraph.Graph(0.04, name='Epigrass Display - %s'%var)
        #self.gr.display.visible=0
    
        Nlist = [dgraph.Node(3,(i[2],i[1],0),name=i[3].strip(),geocode=i[0]) for i in nodes]
        
        self.gr.insertNodeList(Nlist)
        el = self.gr.getEdgeFromMatrix(am)
        #print am,el
        El = [dgraph.RubberEdge(self.gr.nodes[c],self.gr.nodes[l],1,damping=0.8) for c,l in el]
        #print El
        self.gr.insertEdgeList(El)
        
        self.gr.centerView()
        if mapa != 'No map':
            if mapa!= 'Nenhum mapa':
                m = dgraph.Map(mapa)
                self.gr.insertMap(m)
        self.gr.centerView()
        #self.gr.display.visible=1
            
    def anim(self,data,edata, numbsteps,pos, rate=20):
        """
        Starts the animation
        - data: time series from database
        - edata: infectious traveling for edge painting
        - pos: column number of variable to animate
        """
        for t in range(numbsteps):
            V.rate(rate)
            self.gr.timelabel.text=str(t) 
            for i,n in enumerate(self.gr.nodes):
                start = i*numbsteps+t
                n.box.width = n.box.height = n.box.length = (log10(data[start][pos]+10))**1/3.
                n.ts.append(data[start][pos])
                if data[start][pos] > 1:
                    self.paintNode(t,n,numbsteps)
                else:
                    self.paintNode(t,n,numbsteps,col='g')
            #paint Edges when there are infectious coming or going 
            if not edata:
                continue
            for i,e in enumerate(self.gr.edges):
                start = i*numbsteps+t
                if edata[start][-1]+edata[start][-2]:
                    e.cylinder.color = (255,0,0)#bright red
                else:
                    e.cylinder.color = (0.5,0.5,0.5)#dark gray
    
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
                if self.gr.display.mouse.alt:
                    self.plotTs(ob.paren.ts,ob.paren.name)
            except:pass
            if self.gr.display.mouse.clicked:
                m = self.gr.display.mouse.getclick()
                #print m.click
                loc = m.pos
                self.gr.display.center = loc
            if self.gr.display.kb.keys: # is there an event waiting to be processed?
                s = self.gr.display.kb.getkey() # obtain keyboard information
                if s == 'r': #Replay animation
                    for i in self.gr.nodes:
                        self.paintNode(0,i,numbsteps,col='g')
                        i.painted=0
                    self.anim(data,edata,numbsteps,pos,rate)
                else:
                    pass
        
                

if __name__ == "__main__":
    Display=viewer(user='root',pw='mysql')
    Display.anim()
    Display.keyin()
