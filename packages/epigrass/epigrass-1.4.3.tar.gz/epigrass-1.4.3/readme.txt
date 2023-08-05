
Please refer to the user guide for detailed instalation instructions. 

If you have all the pre-requisites installed just edit the setup.py 
and check the database configuration.

Instalation from source:
========================
IMPORTANT: If this is your first installation, and you plan to use the MySQL database backend, please set the upgrade variable,
on the setup.py file to 0.

Now you are set!

just type:
    
python setup.py install

Note that if one or more of the pre-requisites are missing, this
installation will not fail, but EpiGrass will not run.

Installation from the Frozen Installer:
=======================================

Just run the executable installer!

if you want to be able to run epigrass from other locations than the installation folder, do this as root:

$ ln -s <install-path>/epigrass /usr/bin/epigrass

enjoy!

Flávio Codeço Coelho
fccoelho@fiocruz.br 
