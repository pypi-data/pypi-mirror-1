#-*- coding:iso8859-1 -*-
import ez_setup
ez_setup.use_setuptools()

import setuptools
from numpy.distutils.core import setup, Extension

    
#flib = Extension(name='model-builder.Bayes.flib',sources=['model-builder/Bayes/flib.f'])

setup(name = 'Model-Builder',
      version = '0.4.5',
      author = 'Flavio Codeco Coelho',
      author_email = 'fccoelho@gmail.com',
      url = 'http://model-builder.sourceforge.net',
      download_url = 'http://sourceforge.net/project/showfiles.php?group_id=164374',
      install_requires = ['scipy>=0.6','numpy>=1','matplotlib>=0.9', 'BIP'],
      description='Model Builder is a graphical ODE simulator',
      long_description='Model Builder is a graphcial tool for designing, simlating and analysing Mathematical model consisting of a system of ordinary differential equations(ODEs).',
      include_package_data=True,
      packages = ['model_builder'],
      entry_points = {'gui_scripts':['PyMB = model_builder.PyMB:main']},
      #scripts=['model-builder/PyMB.py'],
      #datafiles=[('share/model-builder/examples',['model-builder/Examples/*.ode'])],
      #ext_modules = [flib]
     )
