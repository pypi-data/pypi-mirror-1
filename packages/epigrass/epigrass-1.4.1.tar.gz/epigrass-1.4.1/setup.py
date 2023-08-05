# -*- coding: utf-8 -*-
from setuptools import setup
#from distutils.core import setup 
import MySQLdb, os 

print """If this is your first installation please edit setup.py
as documented in it, and re-run the installation"""
# Edit the lines below if you already have a MySQL server installed 
# with root user and password defined.
sqluser = 'root'
sqlpass = ''
host = 'localhost'
# Is this installation an upgrade?  1 if yes, 0 if no.
print 'If this installation is not an upgrade to a previous one,\nPlease edit setup.py and set upgrade=1'
upgrade = 1
#===========================================================================
if not upgrade:
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
        version='1.4.1',
        author = 'Flávio Codeço Coelho, Cláudia Torres Codeço',
        author_email = 'fccoelho@fiocruz.br',
	maintainer = 'Flávio Codeço Coelho',
	maintainer_email = 'fccoelho@fiocruz.br',
	url = 'http://epigrass.sourceforge.net',
	description = 'System for building and simulating epidemics over networks',
	long_description = 'EpiGrass is a simulator of epidemics over networks.  Its is a scientific tool created for simulations and scenario analysis in Network epidemiology.',
	download_url = 'http://sourceforge.net/project/showfiles.php?group_id=128000',
        license = 'GPL',
        packages = ['Epigrass'],
        scripts = ['epigrass.py'],
        data_files = [('share/epigrass/demos',['demos/script.epg', 'demos/mesh.epg', 'demos/star.epg','demos/sitios2.csv','demos/edgesout.csv', 'demos/nodes.csv','demos/mesh.csv','demos/star.csv','demos/limites.map']),
                    ('share/epigrass/docs',['docs/userguide.pdf'])
                    ]
        )
