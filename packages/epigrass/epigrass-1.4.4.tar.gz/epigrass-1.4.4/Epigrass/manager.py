#! /usr/bin/env python
"""
Model Management and simulation objects.
"""
import cPickle, time
import os, codecs
from simobj import graph, edge, siteobj
from numpy import *
from numpy.random import uniform
from sqlobject import *
from math import *
from Epigrass.data_io import *
import ConfigParser
import string, sys, getpass
import Epigrass.report as Rp
import encodings.utf_8
import encodings.latin_1

# Import Psyco if available
##try:
##    import psyco
##    from psyco.classes import __metaclass__
##    psyco.profile()
##    psyco.full()
##except ImportError:
##    pass

class simulate:
    """
    This class takes care of setting up the model, simulating it, and storing the results 
    """
    def __init__(self, fname=None, host='localhost',port=3306,db='epigrass',user='epigrass', password='epigrass',backend = 'mysql'):
        nargs = len(sys.argv)
        if nargs > 2:
            print "Usage: manager.py <model file>\nSpecify only one model."
            sys.exit(2)
        elif nargs < 2 and not fname:
            print "Usage: manager.py <model file>"
            sys.exit(2)
        elif nargs < 2 and fname:
            self.fname = fname
        elif nargs == 2 and fname:
            self.fname = fname
        else:
            self.fname = sys.argv[1]
        
        self.host = host
        self.port = port
        self.usr = user
        self.db = db
        self.backend = backend
        self.passw = password
        self.repname = None
        self.dir = os.getcwd()
        sys.path.insert(0,self.dir) #add current path to sys.path
        self.gui = 0 # True if this object was created by the gui
        self.now = time.asctime().replace(' ','_').replace(':','') #current date and time
        self.modelName = self.fname.split('.')[0]
        self.config = self.loadModelScript(self.fname)
        self.evalConfig(self.config)
        self.chkScript()
        self.encoding = 'latin-1'#default encoding for strings in the sites and edges files
        self.round = 0 #No replicates
        sitios = loadData(self.sites, sep=',', encoding=self.encoding)
        ed = loadData(self.edges,sep=',', encoding=self.encoding)
        l = self.instSites(sitios)
        e = self.instEdges(l,ed)
        self.g = self.instGraph(self.modelName,1,l,e)
        #if self.layer:
        #    pass
            #self.grassVect2ascii(self.layer)
        
        #self.g.plotDegreeDist()

        
    def loadModelScript(self,fname):
        """
        Loads the model specification from the text file.
        Returns a dictionary with keys of the form
        <section>.<option> and the corresponding values.
        """
        config = {}
        config = config.copy()
        cp =ConfigParser.SafeConfigParser()
        cp.read(fname)
        for sec in cp.sections():
            name =  string.lower(sec)
            for opt in cp.options(sec):
                config[name+"."+string.lower(opt)] = string.strip(cp.get(sec,opt))
        return config
        
    def evalConfig(self,config):
        """
        Takes in the config dictionary and generates the global variables needed.
        """
        try:
            #WORLD
            #self.location = config['the world.location']
            #self.layer = config['the world.vector layer']
            self.sites = config['the world.sites'] #file containing site info
            self.edges = config['the world.edges'] #file containing edge info
            if config['the world.encoding']:
                self.encoding = config['the world.encoding']#encoding specification
            #Epidemiological model
            self.modtype = config['epidemiological model.modtype']
            #self.models = eval(config['epidemiological model.models'])
            #PARAMETERS
            self.beta = config['model parameters.beta']
            self.alpha = config['model parameters.alpha']
            self.e = config['model parameters.e']
            self.r = config['model parameters.r']
            self.delta = config['model parameters.delta']
            self.B = config['model parameters.b']
            self.w = config['model parameters.w']
            self.p = config['model parameters.p']
            #INITIAL CONDITIONS  (inits are string to evaluated inside siteobj.createmodel)
            self.S = config['initial conditions.s']
            self.E = config['initial conditions.e']
            self.I = config['initial conditions.i']
            #EPIDEMIC EVENTS
            self.seed = eval(config['epidemic events.seed'])
            self.vaccinate = eval(config['epidemic events.vaccinate'])
            self.quarantine = eval(config['epidemic events.quarantine'])
            
            #[TRANSPORTATION MODEL]
            self.doTransp = eval(config['transportation model.dotransp'])
            self.stochTransp = eval(config['transportation model.stochastic'])
            self.speed = eval(config['transportation model.speed'])
            
            #SIMULATION AND OUTPUT
            self.steps = eval(config['simulation and output.steps'])
            self.outdir = config['simulation and output.outdir']
            self.MySQLout = eval(config['simulation and output.mysqlout'])
            self.Rep = eval(config['simulation and output.report'])
            self.siteRep = eval(config['simulation and output.siterep'])
            self.replicas = eval(config['simulation and output.replicas'])
            self.randomize_seeds = eval(config['simulation and output.randseed'])
            self.Batch = eval(config['simulation and output.batch'])
        except KeyError, v:
            V = v.__str__().split('.')
            sys.exit("Please check the syntax of your '.epg' file.\nVariable %s, from section %s was not specified."%(V[1],V[0]))
        if self.replicas:
            self.Rep = 0 #Turns off reports
            self.Batch = []#Turns off Batch mode
            self.round = 0# Initialize replicate counter
    # generate dictionaries for parameters and inits
        self.inits = {}
        self.parms = {}
        for k,v in config.items():
            if k.startswith('initial conditions'):
                self.inits[k.split('.')[-1]] = v
            elif k.startswith('model parameters'):
                self.parms[k.split('.')[-1]] = v
            else:pass
    
    def chkScript(self):
        """
        Checks the type of the variables on the script
        """
        self.Say("Checking syntax of model script...")
        
        if not os.access(self.sites,os.F_OK):
            self.Say('Sites file %s does not exist, please check your script.'%self.sites)
            sys.exit()
        if not os.access(self.edges,os.F_OK):
            self.Say('Egdes file %s does not exist, please check your script.'%self.edges)
            sys.exit()
        if not self.modtype in ['SIS','SIS_s','SIR','SIR_s','SEIS','SEIS_s','SEIR','SEIR_s','SIpRpS','SIpRpS_s','SIpR,SIpR_s','Influenza','Custom']:
            self.Say('Model type %s is invalid, please check your script.'%self.modtype)

        
        
        
        self.Say('Script %s passed syntax check.'%self.modelName)
    def deg2dec(self,coord):
        """
        converts lat/long to decimal
        """
        co = coord.split(':')
        if int(co[0])<0:
            result = float(co[0])-float(co[1])/60-float(co[2])/3600
        else:
            result = float(co[0])+float(co[1])/60+float(co[2])/3600
            
        return result
        

    def instSites(self,sitelist):
        """
        Instantiates and returns a list of siteobj instances, from a list of site specification 
        as returned by data_io.loadData.
        Here the site specific events are passed to each site, and the site models are created.
        """
        header = sitelist.pop(0)
        objlist=[]
        for site in sitelist:
            if ':' in site[0]:
                lat = self.deg2dec(site[0])
                long = self.deg2dec(site[1])
            else:
                lat = float(site[0])
                long = float(site[1])
            objlist.append(siteobj(site[2],site[3],(lat,long),int(strip(site[4])),tuple([float(strip(i)) for i in site[4:]])))
        for o in objlist:
            if self.stochTransp: o.stochtransp = 1
            N = o.totpop #local copy for reference on model creation
            values = o.values #local copy for reference on model creation
            inits={}
            parms={}
            #eval parms and inits
            for k,v in self.inits.items():
                inits[k] = eval(v)
            for k,v in self.parms.items():
                parms[k] = eval(v)
            I = eval(self.I)
            E = eval(self.E)
            S = eval(self.S)
            beta = eval(self.beta)
            alpha = eval(self.alpha)
            e = eval(self.e)
            r = eval(self.r)
            delta = eval(self.delta)
            B = eval(self.B)
            w = eval(self.w)
            p = eval(self.p)
            if self.vaccinate:
                if self.vaccinate[0][0] == 'all':
                    o.vaccination = [self.vaccinate[0][1],self.vaccinate[0][2]]
                else:
                    for i in self.vaccinate:
                        if int(o.geocode) == i[0]:
                            o.vaccination = [i[1],float(i[2])]
            if self.quarantine:
                for i in self.quarantine:
                    if int(o.geocode) == i[0]:
                        o.quarantine == i[1:]
                            
             
            if self.seed:
                #print type(o.geocode), type(self.seed[0])
                for j in self.seed:
                    if int(o.geocode) == j[0]:
                        self.Say("%s infected case(s) arrived at %s"%(j[2],o.sitename))
                        I += j[2]
                        inits[j[1].lower()] +=j[2]
                        o.createModel((E,I,S),(beta,alpha,e,r,delta,B,w,p),self.modtype,self.modelName,v=values,bi=inits,bp=parms)
                    else:
                        o.createModel((E,I,S),(beta,alpha,e,r,delta,B,w,p),self.modtype,self.modelName,v=values,bi=inits,bp=parms)
            else:
                o.createModel((E,I,S),(beta,alpha,e,r,delta,B,w,p),self.modtype,self.modelName,v=values,bi=inits,bp=parms)
           
        return objlist
    
    def instEdges(self,sitelist, edgelist):
        """
        Instantiates and returns a list of edge objects, 
        
        sitelist -- list of siteobj objects.
        
        edgelist -- list of edge specifications as returned by data_io.loadData.
        """
        header = edgelist.pop(0)
        #print [i.sitename for i in sitelist]
        objlist=[]
        source = dest = None
        for edg in edgelist:
            #print edgelist.index(edg)
            for site in sitelist:
                #print site.sitename
                if str(site.geocode) == edg[5]: 
                    source = site
                    #print 'found source = ',source.sitename
                elif str(site.geocode) == edg[6]: 
                    dest = site
                    #print 'found dest = ',dest.sitename
                if source and dest:
                    #print 'next edge!'
                    break
            if not source and dest:
                print source ,dest
                sys.exit('One of the vertices on edge '+edg[0]+'-'+edg[1]+' could not be found on the site list')
            
            objlist.append(edge(source,dest,edg[2],edg[3],float(edg[4])))
            source = dest = None
            
            
        return objlist

    def instGraph(self,name, digraph, siteobjlist, edgeobjlist):
        """
        Instantiates and returns a graph object from a list of edge objects.
        """
        g = graph(name,digraph)
        g.speed = self.speed
            
        for j in siteobjlist:
            g.addSite(j)
            
        for i in edgeobjlist:
            g.addEdge(i)
            
        return g
        
    def randomizeSeed(self):
        """
        Generate and return a list of randomized seed sites 
        to be used in a repeated runs scenario.
        Seed sites are sampled with a probability proportional to the
        log of their population size.
        """
        poplist = [log10(site.totpop) for site in self.g.site_list]
        lpl = len(poplist)
        popprob = array(poplist)/sum(poplist) #acceptance probability
        u = floor(uniform(0,lpl, self.replicas))
        sites=[]
        i=0
        while i < self.replicas:
            p = uniform(0,1)
            if p <= popprob[int(u[i])]:
                sites.append(self.g.site_list[int(u[i])])
                i += 1
        return sites
        
    def setSeed(self,seed,n=1):
        '''
        Resets the number of infected to zero in all nodes but seed,
        which get n infected cases.
        seed must be a siteobj object.
        '''
        self.seed =[(seed.geocode,n)]
        for site in self.g.site_list:
            if site.geocode == seed.geocode:
                site.ts[0][1] = n
                
                self.Say("%s infected case(s) arrived at %s"%(n,seed.sitename))
            else:
                site.ts[0][1] = 0
    
    def start(self):
        """
        Start the simulation
        """
        start = time.time()
        self.runGraph(self.g,self.steps,transp=self.doTransp)
        elapsed = time.time()-start
        print 'Simulation lasted ',elapsed, ' seconds'
        if self.gui:
            self.gui.textEdit1.insertParagraph('Simulation lasted %s seconds.'%elapsed,-1)
        if '/' in self.modelName:
            modelname = self.modelName.split('/')[-1]
        else:
            modelname = self.modelName
        if self.MySQLout:
            self.outToODb(modelname)
            #self.outToDb(modelname)
            #qnplot(self.outtable)
        self.dumpData()
            
        #print len(self.g.site_list[-1].ts)
        
##        for i in self.g.site_list:
##            i.plotItself()
##        show()
        
    def createDataFrame(self,site):
        """
        Saves the time series *site.ts* to outfile as specified on the
        model script.
        """
        data = array(site.ts, Float)
        inc  = site.incidence
        f = open(self.outdir+self.outfile,'w')
        f.write('time,E,I,S,incidence\n')
        try:
            for t,i in enumerate(data):
                j = [str(k) for k in i]
                line = str(t)+','.join(j) + str(inc[t])+'\n'
                f.write(line)
        finally:
            f.close()

        return 'E,I,S\n'+tss
    
    def grassVect2ascii(self,layer):
        """
        Convert Grass vector layer to an ascii file epigrass can read
        """
        com = 'v.out.ascii input=%s output=map.txt format=standard'%layer 
        os.system(com)
    
    def outToODb(self,table):
        """
        Insert simulation results in a database using sqlobject
        """
        self.Say('Saving data on %s database...'%self.backend)
        #basic connection variables
        name = table+'_'+self.now
        self.outtable = name
        import dataObject as DO
        #set connection parameters
        DO.Connect(self.backend.lower(),self.usr,self.passw,self.host,self.port,self.db)
        DO.Site.sqlmeta.table = name
        DO.Edge.sqlmeta.table = name+'e'
        #adding columns to sites table
        DO.Site.sqlmeta.addColumn(StringCol('incidence'))
        DO.Site.sqlmeta.addColumn(StringCol('arrivals'))
        if self.g.site_list[0].values:#add columns for 'values' variables
            for i in range(len(self.g.site_list[0].values)):
                DO.Site.sqlmeta.addColumn(StringCol('values%s'%i))
        for s in self.g.site_list[0].vnames: #add columns for state variables
            DO.Site.sqlmeta.addColumn(StringCol(s))
        #creating tables
        DO.Site.createTable()
        DO.Edge.createTable()
        #inserting data in sites table
        for site in self.g.site_list:
            dicin={
            'geocode':site.geocode,
            'lat':float(site.pos[0]),
            'longit':float(site.pos[1]),
            'name':site.sitename.replace('"',''),#.decode('iso-8859-1'),
            'totpop':int(site.totpop)}
            if site.values:
                for n,v in enumerate(site.values):
                    #print v,type(v)
                    dicin['values%s'%n] = str(v)
            ts = array(site.ts[1:]) #remove init conds so that ts and inc are the same size
            t = 0
            for i in ts:
                dicin['incidence']= str(site.incidence[t])
                dicin['arrivals'] = str(site.thetahist[t])
                dicin['time'] = t
                for n,v in enumerate(site.vnames):
                    #print i[n],type( i[n])
                    dicin[v] = str(i[n])
                DO.Site(**dicin)
                t += 1
            DO.Site._connection.commit()
        
        #inserting data in edges table
        for e in self.g.edge_list:
            edicin={
            'source_code':e.source.geocode,
            'dest_code':e.dest.geocode}
            t=0
            for f,b in zip(e.ftheta,e.btheta):
                edicin['time'] = t
                edicin['ftheta'] = f
                edicin['btheta'] = b
                DO.Edge(**edicin)
                t += 1
            DO.Edge._connection.commit()
        #saving pickle of adjacency matrix
        matname = 'adj_'+self.modelName.split('/')[-1] # table
        adjfile = open(matname,'w')
        cPickle.dump(self.g.getConnMatrix(),adjfile)
        adjfile.close()
        
    def outToDb(self,table):
        """
        Insert simulation results on a mysql table
        """
        self.Say('Saving data on MySQL...')
        con=None
        try:
            table = table+'_'+self.now
            self.outtable = table
            con = MySQLdb.connect(host=self.host, port=self.port,
                                    user=self.usr,passwd=self.passw, db=self.db)
            # Define number of variables to be stored                         
            nvar = len(self.g.site_list[0].ts[0]) +4 #state variables,  plus coords, plus incidence, plus infected arrivals.
            str1 = '`%s` FLOAT(9),'*nvar #nvar variables in the table
            varnames = ['lat','longit']+list(self.g.site_list[0].vnames)+['incidence']+['Arrivals']
            str1 = str1[:len(str1)-1] % tuple(varnames) #insert variable names
            Cursor = con.cursor()
            str2 = """CREATE TABLE %s(
            `geocode` INT( 9 ) DEFAULT '0' NOT NULL ,
            `time` INT( 9 ) DEFAULT '' NOT NULL,
            `name` varchar(128) DEFAULT '' NOT NULL,
            """ % table
            sql = str2+str1+');'
            
            Cursor.execute(sql)
            str3 = (nvar+3)*'%s,'
            str3 = str3[:-1]+')'
            sql2 = 'INSERT INTO %s' % table + ' VALUES('+str3
            
            for site in self.g.site_list:
                geoc = site.geocode
                lat = site.pos[0]
                long = site.pos[1]
                name = site.sitename
                ts = array(site.ts[1:]) #remove init conds so that ts and inc are the same size
                inc = site.incidence
                thist = site.thetahist
                t = 0
                for i in ts:
                    tstep = str(t)
                    Cursor.execute(sql2,tuple([geoc,tstep,name]+[lat,long]+list(i)+[inc[t]]+[thist[t]]))
                    t += 1
            
            #Creating a table for edge data
            self.etable = etable = table+'e'
            esql = """CREATE TABLE %s(
            `source_code` INT( 9 ) DEFAULT '0' NOT NULL ,
            `dest_code` INT( 9 ) DEFAULT '0' NOT NULL ,
            `time` INT( 9 ) DEFAULT '0' NOT NULL ,
            `ftheta` FLOAT(9) DEFAULT '0' NOT NULL ,
            `btheta` FLOAT(9) DEFAULT '0' NOT NULL);"""%etable
            Cursor.execute(esql)
            esql2 = 'INSERT INTO %s' % etable + ' VALUES(%s,%s,%s,%s,%s)'
            for e in self.g.edge_list:
                s = e.source.geocode
                d = e.dest.geocode
                t=0
                for f,b in zip(e.ftheta,e.btheta):
                    Cursor.execute(esql2,(s,d,t,f,b))
                    t += 1
            
            
        finally:
            if con:
                con.close()
        #saving pickle of adjacency matrix
        matname = 'adj_'+self.modelName.split('/')[-1] # table
        adjfile = open(matname,'w')
        cPickle.dump(self.g.getConnMatrix(),adjfile)
        adjfile.close()
        
    def dumpData(self):
        """
        Dumps data as csv (comma-separated-values)
        """
        curdir = os.getcwd()
        if not self.outdir:
            self.outdir = outdir = 'outdata-'+self.modelName.split('/')[-1]
            try:
                os.system('mkdir %s'%outdir)
            except: pass #In case dir already exists (replicate runs)
            os.chdir(outdir)
        else:
            os.system('mkdir %s'%self.outdir)
            os.chdir(self.outdir)
        codeslist = [str(i.geocode) for i in self.g.site_list]
        # saving the adjacency  matrix
        if not os.path.exists('adjmat.csv'): 
            self.Say('Saving the adjacency  matrix...')
            am = self.g.getConnMatrix()
            amf = open ('adjmat.csv','w')
            amf.write(','.join(codeslist)+'\n')
            for row in am:
                row = [str(i) for i in row]
                amf.write(','.join(row)+'\n')
            amf.close()
            self.Say('Done!')
        #saving the shortest path matrices
        if not os.path.exists('spmat.csv'):
            self.Say('Saving the shortest path matrices...')
            ap = self.g.getAllPairs()
            f = open('ap','w')
            cPickle.dump(ap,f)
            f.close()
            spd = self.g.shortDistMatrix
            apf = open ('spmat.csv','w')
            apf.write(','.join(codeslist)+'\n')
            spdf = open ('spdmat.csv','w')
            spdf.write(','.join(codeslist)+'\n')
            for row in ap:
                row = [str(i) for i in row]
                apf.write(','.join(row)+'\n')
            apf.close()
            for row in spd:
                row = [str(i) for i in row]
                spdf.write(','.join(row)+'\n')
            spdf.close()
            self.Say('Done!')
        
        #Saving epidemic path
        self.Say('Saving Epidemic path...')
        if self.round:
            epp = codecs.open('epipath%s.csv'%str(self.round),'w',self.encoding)
        else:
            epp = codecs.open('epipath.csv','w',self.encoding)
        epp.write('time,site,infector\n')
        for i in self.g.epipath:
            #print i
            infectors = i[-1]
            # sorting infectors by number of infective contributed
            if len(infectors):
                reverse_infectors = [ [v[1],v[0]] for v in infectors.items()]
                reverse_infectors.sort()
                mli = [reverse_infectors[j][1] for j in range(0,len(reverse_infectors))][-1]#Most likely infector
            else:
                mli = 'NA'
            #print i[1].sitename, type(i[1].sitename)
            epp.write(str(i[0])+','+i[1].sitename+','+mli+'\n')
        epp.close()
        self.Say('Done!')
        
        #saving Epistats
        self.Say('Saving Epidemiological results...')
        stats = [str(i) for i in self.g.getEpistats()]
        seed = [s for s in self.g.site_list if s.geocode == self.seed[0][0]][0]
        stats.pop(1) #Remove epispeed which is a vector
        if os.path.exists('epistats.csv'):
            stf = codecs.open('epistats.csv','a',self.encoding)#append to file
        else:
            stf = codecs.open('epistats.csv','w',self.encoding)#create a new file
            stf.write('seed,name,size,infected_cities,spreadtime,median_survival,totvaccinated,totquarantined,seedcentrality,seedbetw,seedthidx,seeddeg,seedpop\n')
        scent = str(seed.getCentrality())
        sbetw = str(seed.getBetweeness())
        sthidx = str(seed.getThetaindex())
        sdeg = str(seed.getDegree())
        spop = str(seed.totpop)
        sname =seed.sitename
        sstats = '%s,%s,%s,%s,%s'%(scent,sbetw,sthidx,sdeg,spop)
        stf.write(str(self.seed[0][0])+','+sname+','+','.join(stats)+','+sstats+'\n')
        stf.close()
        self.Say('Done!')
        
        #Saving site stats
        self.Say('Saving site statistics...')
        #self.g.getAllPairs()
        if os.path.exists('sitestats.csv'):
            sitef = codecs.open('sitestats.csv','a',self.encoding) #append to file
        else:
            sitef = codecs.open('sitestats.csv','w',self.encoding)
        #sitef.write('site,centrality,degree,theta_index,betweeness,infection_time\n')
        sitef.write('round,geocode,name,infection_time,degree,centrality,betweeness,theta_index,distance,seed,seedname\n')
        for s in self.g.site_list:
            degree = str(s.getDegree())
            central = str(s.getCentrality())
            bet = str(s.getBetweeness())
            thidx = str(s.getThetaindex())
            seedgc = str(self.seed[0][0])
            seedname = seed.sitename
            f = open('ap','r')
            ap = cPickle.load(f)
            f.close()
            distseed = str(ap[codeslist.index(str(s.geocode)),codeslist.index(str(self.seed[0][0]))])
            it = str(s.infected) #infection time
            if it == 'FALSE':
                it = 'NA'
##            st = ','.join([str(i) for i in s.doStats()])
##            sitef.write(str(s.sitename)+','+st+it+'\n')
            sitef.write(str(self.round)+','+str(s.geocode)+','+s.sitename+','+it+','+degree+','+central+','+bet+','+thidx+','+distseed+','+seedgc+','+seedname+'\n')
            
        os.chdir(curdir)
        
        self.Say('Done saving data!')
    
    def saveModel(self,graph,fname):
        """
        Save the fully specified graph.
        """
        f = open(fname,'w')
        cPickle.dump(graph,f)
        f.close()
        
    def loadModel(self,fname):
        """
        Loads a pre-saved graph.
        """
        g = cPickle.load(fname)
        return g

    
    def runGraph(self,graphobj,iterations=1, transp=0):
        """
        Starts the simulation on a graph.
        """
        g = graphobj
        g.maxstep = iterations
        sites = tuple(graphobj.site_list)
        edges = tuple(graphobj.edge_list)
        if transp:
            for n in xrange(iterations):
                for i in sites:
                    i.runModel()
                for j in edges:
                    j.transportStoD()
                    j.transportDtoS()
                g.simstep += 1
                if self.gui:
                    self.gui.stepLCD.display(g.simstep)
                    
                if g.gr:
                    g.gr.timelabel.text = 'time = %s'%g.simstep
        else:
            for n in xrange(iterations):
                for i in sites:
                    i.runModel()
                g.simstep += 1
                if self.gui:
                    self.gui.stepLCD.display(g.simstep)
                if g.gr:
                    g.gr.timelabel.text = 'time = %s'%g.simstep
    def Say(self,string):
        """
        Exits outputs messages to the console or the gui accordingly 
        """
        if self.gui:
            self.gui.textEdit1.insertParagraph(string,-1)
        else:
            print string
def storeSimulation(s,db='epigrass', host='localhost',port=3306):
    """
    store the Simulate object *s* in the epigrass database
    to allow distributed runs. Currently not working.
    """
    now = time.asctime().replace(' ','_').replace(':','')
    table = 'Model_'+S.modelName+now
    con = MySQLdb.connect(host=host, port=port, user=usr,passwd=passw, db=db)
    Cursor = con.cursor()
    sql = """CREATE TABLE %s(
        `simulation` BLOB);""" % table
    Cursor.execute(sql)
    blob = cPickle.dumps(s)
    sql2 = 'INSERT INTO %s' % table + ' VALUES(%s)'
    Cursor.execute(sql2,blob)
    con.close()
    
class Bunch:
    """
    class to store a bunch os variables
    """
    def __init__(self, **kw):
       self.__dict__.update(kw)

class Tree:
    """
    Tree object representing the spread of an epidemic
    """
    def __init__(self,Simulation):
        self.g = Simulation.g
        Self.S = Simulation
        pass
    
    def writeNexus(self):
        """
        Writes a Nexus file containing(.nex) the phylogeographical 
        tree of the epidemic.
        """
        ntax = len(self.g.epipath)
        sitenames = [i[1].sitename for i in self.g.epipath]
        Name = self.S.modelName
        header = """#NEXUS
        [written %s from model % by EpiGrass]
        """%(time.asctime(),Name)
        taxablock = """BEGIN TAXA;
                            TITLE %s;
                            DIMENSIONS NTAX=%s;
                            TAXLABELS
                                %s
                                ;
                        END;
                            
        """%(Name,ntax,' '.join(sitenames))
        
        treeblock = """BEGIN TREES;
                        Title Epidemic_Path;
                        LINK Taxa = %s;"""%(Name,)
                        
        transtring = ','.join(['%s %s'%(i,j) for i,j in zip(range(1,len(sitenames)+1),sitenames)])+';'
        treeblock2 = """TRANSLATE
                            %s
                            """%transtring
        venn = self.getVenn()                    
        treeblock3 = """TREE 'Default ladder+' = %;
                        END;"""%venn
    def getVenn(self):
        """"
        Generates Venn Diagram from epipath.
        """
        pass
        
        
if __name__ == '__main__':
    
    S = simulate()
    usr = raw_input('Enter MySQL user name:')
    passw = getpass.getpass()
    S.usr = usr
    S.passw = passw
    #storeSimulation(S.g)
    if S.Batch:
        for i in S.Batch:
            T = simulate(i)
            T.start()
            if S.Rep:
                rep = Rp.report(T)
                rep.Assemble(S.Rep)

    else:
        S.start()
        if S.Rep:
            rep = Rp.report(S)
            rep.Assemble(S.Rep)

