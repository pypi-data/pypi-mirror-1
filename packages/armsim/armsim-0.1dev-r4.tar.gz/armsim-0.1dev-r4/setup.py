from setuptools import setup, find_packages, Extension
import sys, os

version = '0.1'

setup(name='armsim',
      version=version,
      description="ARM Simulator for Linux",
      long_description="""\
armsim is an ARM Simulator for Linux

Objective
---------
armsim has the objective of simulating arm based processors starting with the
at91sam9260

nonetheless, it is designed to be extensible, so you'll be able to write you
own classes to plug in you microcontroller

Is is designed for Linux and Python2.6 so be sure you have these requirements.

Current Status
--------------
Currently a total of 20 instructions are supported, even tough most of them
are recognized.

The project is being developed quickly so you can expect the complete
instruction set to be supported in a few weeks

                       """,
      classifiers=[
          'Development Status :: 1 - Planning',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: C',
          'Topic :: Software Development :: Embedded Systems',
          'Topic :: System :: Emulators',
      ], 
      author='Eduardo Diaz',
      author_email='iamedu@gmail.com',
      url='http://code.google.com/p/armdev/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'zope.component',
      ],
      entry_points={
          'console_scripts':[
              'armsim = armsim.simulator:main',
          ]
      },
      ext_modules=[
          Extension('uart', ['src/uartmodule.c'], libraries=['util'])
      ],
      platforms=['Linux'],
      package_dir={'armsim' : 'armsim'},
      package_data={'armsim' : ['controllers/*.cfg']},
      )

