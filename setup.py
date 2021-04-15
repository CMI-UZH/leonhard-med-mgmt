from setuptools import setup

setup(name='leotools',
      version='0.0.3',
      description='',
      url='https://github.com/uzh-dqbm-cmi/leonhard-med-mgmt',
      packages=['leotools'],
      python_requires='>3.6.0',
      install_requires=[
          'code-sync'
      ],
      entry_points={
          'console_scripts': [
              'build_image = leotools.build_image:main',
          ]
      },
      zip_safe=False)
