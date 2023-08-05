from setuptools import setup
import os
requirements = ['cx_Oracle']
if os.name == 'posix':
    requirements.append('pexpect')
setup(name='sqlpython',
      version='1.3.0',
      install_requires=requirements,
      packages=['sqlpython'],
	      entry_points = {'console_scripts':['sqlpython = sqlpython.mysqlpy:run']},
      author='Luca Canali',
      author_email='luca.canali@cern.ch',
      license='MIT',
      keywords='client oracle database',
      description='Command-line interface to Oracle',
      long_description="""Customizable alternative to Oracle's SQL*PLUS command-line interface""",
      url='https://twiki.cern.ch/twiki/bin/view/PSSGroup/SqlPython'
      )