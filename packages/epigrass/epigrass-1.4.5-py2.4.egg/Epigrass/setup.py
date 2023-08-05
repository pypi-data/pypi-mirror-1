# -*- coding: utf-8 -*-
from distutils.core import setup 
import MySQLdb, os 
# Edit the lines below if you already have a MySQL server installed 
# with root user and password defined.
sqluser = 'root'
sqlpass = ''
host = 'localhost'
#===========================================================================

os.system('mysqladmin -u %s create epigrass -p%s'%(sqluser,sqlpass))
con = MySQLdb.connect(host=host, port=3306, user=sqluser,passwd=sqlpass, db='epigrass')
Cursor = con.cursor()
Cursor.execute("GRANT ALL ON epigrass.* TO 'epigrass'@'localhost'IDENTIFIED BY 'epigrass';")
print Cursor.fetchall()
con.close()

setup(name='EpiGrass',
        version='0.20.0',
        description = 'Network epidemiology simulator',
        author = 'Flávio Codeço Coelho, Cláudia Torres Codeço',
        author_email = 'fccoelho@fiocruz.br',
        license = 'GPL',
        packages = ['Epigrass'],
        scripts = ['epigrass.py','manager.py'],
        data_files = [('share/epigrass/demos',['demos/script.epg', 'demos/mesh.epg', 'demos/star.epg', 'nodes.csv','mesh.csv','star.csv']),
                    ('share/epigrass/docs',['docs/userguide.pdf'])
                    ]
        )
