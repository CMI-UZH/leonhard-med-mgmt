from setuptools import setup

setup(name='leotools',
      version='0.0.2',
      description='',
      url='https://github.com/uzh-dqbm-cmi/leonhard-med-mgmt',
      packages=['leotools'],
      python_requires='>3.5.0',
      install_requires=[
            'watchdog',
            'pyyaml',
            'argh'
      ],
      extras_requires={
          'code_sync': 'watchdog',
      },
      entry_points={
          'console_scripts': [
              'code_sync = leotools.code_sync:main',
              'build_image = leotools.build_image:main',
          ]
      },
      zip_safe=False)
