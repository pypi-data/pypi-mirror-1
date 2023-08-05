#!/bin/bash

black='\E[30;47m'
red='\E[31;47m'
green='\E[32;47m'
yellow='\E[33;47m'
blue='\E[34;47m'
magenta='\E[35;47m'
cyan='\E[36;47m'
white='\E[37;47m'


#remove previouly frozen distribution
echo -e $red '===> Removing previouly frozen distribution...'
tput sgr0
rm -rf freeze
#freeze
echo -e $red '===> Freezing Epigrass...'
~fccoelho/Downloads/cx_Freeze-3.0.2/FreezePython epigrass.py -O -c --init-script=/home/fccoelho/Downloads/cx_Freeze-3.0.2/initscripts/ConsoleSetLibPath.py --target-dir=freeze --include-modules=sqlobject,matplotlib,rpy,_rpy2011,sip,_rpy2021,matplotlib.backends.backend_agg,matplotlib.numerix.random_array,numarray,numarray.libnumarray,numarray.dotblas,pysqlite2,pysqlite2.dbapi2,visual,unicodedata,codecs,encodings,encodings.utf_8
#copy other needed qt libs
echo -e $red '===> Copying other qt libs...'
tput sgr0
cp /usr/qt/3/lib/libqt-mt.so freeze/
#Copy matplotlib data files
echo -e $red '===> Copying matplotlib data files...'
tput sgr0
cp -R /usr/lib/python2.4/site-packages/matplotlib-0.87.2-py2.4-linux-i686.egg/matplotlib/mpl-data freeze/matplotlibdata
echo -e $red '===> Copying other libs...'
tput sgr0
cp /usr/lib/python2.4/site-packages/numarray/*.so freeze/
cp /usr/lib/libpng.so.3 freeze/
cp COPYING.txt freeze/license.txt
cp README freeze/readme.txt
cp /usr/lib/R/lib/libR.so freeze/
cp /usr/lib/R/lib/libRlapack.so freeze/
cp /usr/lib/libboost_python.so.1.33.1 freeze/
#qtext,qtcanvas,qtgl,qtnetwork,qtsql,qttable,qtui,qtxml