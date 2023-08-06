#!/usr/bin/env python

from setuptools import setup, find_packages

from ekg.commands import commands

def command_funcs(cs):
    return ['ekg-%s = %s:%s' % 
            (c.__name__.replace('_', '-'),
             c.__module__,
             c.__name__) for c in cs]

setup(name='ekg',
      version='0.4.0pre1',
      description='Collect and display statistics about open source projects',
      long_description=
'''EKG will scan such diverse sources as mailing lists, version control repositories, wikis to collect information about open source projects to determine the health of a community''',

      author='Yaakov M. Nemoy',
      author_email='ekg@hexago.nl',
      url='https://fedorahosted.org/ekg/',
      license='GPLv2+',

      packages=find_packages(),
      install_requires=['ConfigObj>=4.5.3', 'SQLAlchemy >= 0.5.2', 'python-dateutil',
                        'urlgrabber', 'sqlalchemy-migrate'],
      include_package_data=True,

      entry_points= {
        'console_scripts': command_funcs(commands),
        }
      )
