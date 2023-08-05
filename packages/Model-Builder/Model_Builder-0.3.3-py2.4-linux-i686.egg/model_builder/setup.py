#-*- coding:latin-1 -*-
import ez_setup
ez_setup.use_setuptools()

import setuptools, os
from numpy.distutils.core import setup, Extension

#Configuring Build     
libs=[];libdirs=[];f2pyopts=[]
if os.name == 'nt':
    pass#f2pyopts.extend(["--compiler=mingw32","--fcompiler=gnu"])

    

flib = Extension(name='model_builder.Bayes.flib',
                        libraries=libs,
                        library_dirs=libdirs,
                        f2py_options=f2pyopts,
                        sources=['model_builder/Bayes/flib.pyf','model_builder/Bayes/flib.f']
                        )

setup(name = 'Model-Builder',
      version = '0.3.2',
      author = 'Flavio Codeco Coelho',
      author_email = 'fccoelho@fiocruz.br',
      url = 'http://model-builder.sourceforge.net',
      download_url = 'http://sourceforge.net/project/showfiles.php?group_id=164374',
      description='Model Builder is a graphical ODE simulator',
      long_description='Model Builder is a graphical tool for designing, simulating and analyzing Mathematical model consisting of a system of ordinary differential equations(ODEs).',
      include_package_data=True,
      entry_points = {'gui_scripts':['PyMB = model_builder.PyMB:main',]},
      packages = ['model_builder','model_builder/Bayes'],
      datafiles=[('share/model-builder/examples',['model_builder/Examples/*.ode','model_builder/Examples/*.spec'])],
      ext_modules = [flib]
     )
