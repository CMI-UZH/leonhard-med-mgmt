from os import path
from setuptools import setup

# Project
NAME = 'leotools'
VERSION = '0.0.1'

# Authors and maintainers
AUTHORS = 'Laura Kinkead'
MAINTAINER = 'Laura Kinkead'
MAINTAINER_EMAIL = 'laura.kinkead@uzh.ch'

# License
LICENSE = 'MIT'

# Project URLs
REPOSITORY = 'https://github.com/uzh-dqbm-cmi/leonhard-med-mgmt'
HOMEPAGE = 'https://github.com/uzh-dqbm-cmi/leonhard-med-mgmt'
PROJECT_URLS = {
    'Bug Tracker': f'{REPOSITORY}/issues',
    'Documentation': HOMEPAGE,
    'Source Code': REPOSITORY,
}
DOWNLOAD_URL = ''

# Long description
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), mode='r', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

# Install requirements
with open(path.join(this_directory, 'requirements/production.txt'), mode='r', encoding='utf-8') as f:
    INSTALL_REQUIREMENTS = f.read().splitlines()

# Classifiers
CLASSIFIERS = [
    "Development Status :: 2 - Pre-Alpha",
    "Environment :: Console",
    "Operating System :: OS Independent",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License"
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.7",
    "Framework :: Pytest",
    "Framework :: Flake8",
]

# Package definition
setup(name=NAME,
      version=VERSION,
      description='',
      url=HOMEPAGE,
      packages=[
          NAME,
      ],
      author=AUTHORS,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      license=LICENSE,
      long_description=LONG_DESCRIPTION,
      long_description_content_type='text/markdown',
      download_url=DOWNLOAD_URL,
      project_urls=PROJECT_URLS,
      python_requires='>3.5.0',
      install_requires=INSTALL_REQUIREMENTS,
      entry_points={
          'console_scripts': [
              'code_sync = leotools.code_sync:main'
          ]
      },
      include_package_data=True,
      zip_safe=False)
