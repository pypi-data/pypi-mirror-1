# -*- coding:utf8 -*-
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
#from distutils.core import setup 


setup(name='epigrass',
        version='1.4.4',
        author = 'Flavio Codeco Coelho, Claudia Torres Codeco',
        author_email = 'fccoelho@fiocruz.br',
	maintainer = 'Flavio Codeco Coelho',
	maintainer_email = 'fccoelho@fiocruz.br',
	url = 'http://epigrass.sourceforge.net',
	description = 'Epidemiological Geo-Referenced Analysis and Simulation System',
	long_description = 'EpiGrass is a simulator of epidemics over networks.  Its is a scientific tool created for simulations and scenario analysis in Network epidemiology.',
	download_url = 'http://sourceforge.net/project/showfiles.php?group_id=128000',
        license = 'GPL',
        packages = ['Epigrass'],
        scripts = ['epigrass.py'],
        data_files = [('share/epigrass/demos',['demos/script.epg', 'demos/mesh.epg', 'demos/star.epg','demos/flu.epg','demos/sitios3.csv','demos/edgesout.csv', 'demos/nodes.csv','demos/mesh.csv','demos/star.csv','demos/limites.map']),
                    ('share/epigrass/docs',['docs/userguide.pdf'])
                    ]
        )
