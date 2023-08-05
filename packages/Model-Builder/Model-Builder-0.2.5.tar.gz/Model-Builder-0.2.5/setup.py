#-*- coding:iso8859-1 -*-
import ez_setup
ez_setup.use_setuptools()
try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(name = 'Model-Builder',
      version = '0.2.5',
      author = 'Flavio Codeco Coelho',
      author_email = 'fccoelho@fiocruz.br',
      url = 'http://model-builder.sourceforge.net',
      download_url = 'http://sourceforge.net/project/showfiles.php?group_id=164374',
      install_requires = ['scipy>=0.49','numpy>=0.98','matplotlib>=0.87'],
      description='Model Builder is a graphical ODE simulator',
      long_description='Model Builder is a graphcial tool for designing, simlating and analysing Mathematical model consisting of a system of ordinary differential equations(ODEs).',
      include_package_data=True,
      packages = ['model-builder','model-builder/Bayes'],
      scripts=['model-builder/PyMB.py'],
      datafiles=[('share/model-builder/examples',['model-builder/Examples/*.ode'])],
     )
