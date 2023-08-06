# The setup script for the InsideTrac plugin

from setuptools import setup, find_packages

setup(name='InsideTrac',
      version='0.2.7',
      packages=find_packages(exclude=['*.tests*']),
      install_requires=[
        'feedparser',
        'trac>=0.11.5',
        'TracScheduler',
        'IniAdmin'
        ],
      test_suite='nose.collector',
      setup_requires=[
        'Nose',
        'coverage'
        ],
      entry_points = """
        [trac.plugins]
        insidetrac.api = insidetrac.api
        insidetrac.model = insidetrac.model
        """,
      author = "Michael J. Pedersen",
      author_email = "m.pedersen@icelus.org",
      description = "Trac plugin and Greasemonkey scripts to help monitor external projects",
      package_data = {'insidetrac': ['templates/*']},
      license = "LGPL",
      url = "http://www.insidetrac.org/"
      )
