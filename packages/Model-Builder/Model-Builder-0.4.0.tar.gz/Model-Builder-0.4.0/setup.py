#-*- coding:latin-1 -*-
import ez_setup
ez_setup.use_setuptools()

import setuptools, os, glob
from setuptools import setup
#from numpy.distutils.core import setup, Extension

###Configuring Build     
##libs=[];libdirs=[];f2pyopts=[]
##if os.name == 'nt':
##    pass#f2pyopts.extend(["--compiler=mingw32","--fcompiler=gnu"])
##
##    
##
##flib = Extension(name='model_builder.Bayes.flib',
##                        libraries=libs,
##                        library_dirs=libdirs,
##                        f2py_options=f2pyopts,
##                        sources=['model_builder/Bayes/flib.f']
##                        )

setup(name = 'Model-Builder',
      version = '0.4.0',
      author = 'Flavio Codeco Coelho',
      author_email = 'fccoelho@fiocruz.br',
      license = 'GPL',
      url = 'http://model-builder.sourceforge.net',
      download_url = 'http://sourceforge.net/project/showfiles.php?group_id=164374',
      description='Model Builder is a graphical ODE simulator',
      long_description='Model Builder is a graphical tool for designing, simulating and analyzing Mathematical model consisting of a system of ordinary differential equations(ODEs).',
      include_package_data=True,
      entry_points = {'gui_scripts':['PyMB = model_builder.PyMB:main',]},
      packages = ['model_builder','model_builder/Bayes'],
      package_data = {'':['MB*','*.pdf','*.desktop'],'model_builder':['Docs/*.pdf', 'model-builder.desktop']},
      data_files=[('/usr/share/pixmaps',['model_builder/MB.ico']),('/usr/share/applications',['model_builder/model-builder.desktop']),('/usr/share/model-builder/examples',glob.glob("model_builder/Examples/*.ode")),('/usr/share/model-builder/docs',['model_builder/Docs/Quick-start.pdf'])],
     )
