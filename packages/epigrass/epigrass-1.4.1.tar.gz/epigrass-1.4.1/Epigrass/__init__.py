# Package initialisation
import os, commands



class GrassError:
    """
    """
    def __init__(self):
        print "I can't Find your GRASS instalation"
        print 'Please, check your GRASS instalation'
    
class prep:
    """
    Checks if GRASS is installed and prepares the environment for interacting with it.
    This code is run whenever the package or one of its modules is imported.
    """
    def __init__(self):
        try:
            self.test_inst()
            self.create_env()
            print 'tests ok!'
        except GrassError:
            pass
                
    
    def test_inst(self):
        """
        Check for a sane GRASS environment
        """
        if os.access('/usr/grass5',1):
           self.gisbase = '/usr/grass5' 
           return 1
        elif os.access('/usr/local/grass5',1):
            self.gisbase = '/usr/local/grass5'
            return 1
            
        elif os.access('/usr/lib/grass',1):
            self.gisbase = '/usr/lib/grass'
            return 1

        elif os.access('/usr/local/grass-6.0.0',1):
            self.gisbase = '/usr/local/grass-6.0.0'
            return 1
        elif os.access('/usr/grass60',1):
            self.gisbase = '/usr/grass60'
            return 1
        
        else:
            raise GrassError()
            
    def create_env(self):
        """
        Create environmental variables necessary to call grass functions.
        """
        os.environ['GISBASE'] = self.gisbase
        os.environ['GISRC'] = os.environ['HOME'] + '/.grassrc5'
        os.environ['PATH'] = os.environ['PATH']+':'+os.environ['GISBASE']+'/bin:'+os.environ['GISBASE']+'/scripts'
       
        #print os.environ['GISBASE'],os.environ['GISRC'],os.environ['PATH']
        
run = prep()

