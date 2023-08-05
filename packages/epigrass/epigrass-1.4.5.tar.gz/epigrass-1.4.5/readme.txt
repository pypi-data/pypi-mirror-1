
Please refer to the user guide for detailed instalation instructions. 

If you have all the pre-requisites installed just edit the setup.py 
and check the database configuration.

Pre-installation procedures:
============================
If this is the first installation on this machine and you plan to use the MySQL backend (recommended for large simulations) before installing you must create the "epigrass" database on your MySQL server:

$ mysqladmin -u<your_mysql_username> create epigrass -p<your_password>

For this to work, the user on the above command must have th right to create new databases on the MySQL server.
Then from the MySQL console type the following query:

$ GRANT ALL ON epigrass.* TO '<your_mysql_username>'@'localhost'IDENTIFIED BY '<your_password>'

If your MySQL server is located on another machine, please replace "localhost" by the appropriate IP address of the machine in which Epigrass will be running.

Instalation from source:
========================
IMPORTANT: If this is your first installation, Refer to the pre-installation procedures above.

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


Please remember that in addition to installing epigrass, in order to generated reports, you must have a working latex/pdflatex installation. If you decide to use the MySQL database, you must ensure access to a MySQL server, and create a databse named "epigrass".




enjoy!

Flávio Codeço Coelho
fccoelho@fiocruz.br 
