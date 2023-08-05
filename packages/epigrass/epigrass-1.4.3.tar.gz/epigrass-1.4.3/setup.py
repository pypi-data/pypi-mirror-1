# -*- coding:utf8 -*-
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
#from distutils.core import setup 
import os 

print """If this is your first installation please edit setup.py
as documented in it, and re-run the installation"""
# Edit the lines below if you already have a MySQL server installed 
# with root user and password defined.
sqluser = 'root'
sqlpass = ''
host = 'localhost'
# Is this installation an upgrade?  1 if yes, 0 if no.
print 'If this installation is not an upgrade to a previous one,\nand you plan to use the MySQL database backend,\nPlease edit setup.py and set upgrade=0'
upgrade = 1
#===========================================================================
if not upgrade:
    import MySQLdb
    con = None
    try:
        os.system('mysqladmin -u %s create epigrass -p%s'%(sqluser,sqlpass))
        con = MySQLdb.connect(host=host, port=3306, user=sqluser,passwd=sqlpass, db='epigrass')
        Cursor = con.cursor()
        Cursor.execute("GRANT ALL ON epigrass.* TO 'epigrass'@'localhost'IDENTIFIED BY 'epigrass';")
        print Cursor.fetchall()
    finally:
        if con:
            con.close()

setup(name='epigrass',
        version='1.4.3',
        author = 'Flavio Codeco Coelho, Claudia Torres Codeco',
        author_email = 'fccoelho@fiocruz.br',
	maintainer = 'Flavio Codeco Coelho',
	maintainer_email = 'fccoelho@fiocruz.br',
	url = 'http://epigrass.sourceforge.net',
	description = 'Epidemiological Geo-Referenced Analysis and Simulation System',
	long_description = 'EpiGrass is a simulator of epidemics over networks.  Its is a scientific tool created for simulations and scenario analysis in Network epidemiology.',
	download_url = 'http://sourceforge.net/project/showfiles.php?group_id=128000',
        license = 'GPL',
	install_requires=['SQLObject>=0.7','matplotlib>=0.87','pysqlite>=2.2'],
        packages = ['Epigrass'],
        scripts = ['epigrass.py'],
        data_files = [('share/epigrass/demos',['demos/script.epg', 'demos/mesh.epg', 'demos/star.epg','demos/flu.epg','demos/sitios3.csv','demos/edgesout.csv', 'demos/nodes.csv','demos/mesh.csv','demos/star.csv','demos/limites.map']),
                    ('share/epigrass/docs',['docs/userguide.pdf'])
                    ]
        )
