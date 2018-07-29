from sys import version_info
from setuptools import setup, find_packages

if version_info.major == 3 and version_info.minor < 6 or \
        version_info.major < 3:
    print('Your Python interpreter must be 3.6 or greater!')
    exit(1)

setup(name='technical',
      version='1.0.2',
      description='Technical Indicators',
      url='https://github.com/berlinguyinca/technical',
      author='Gert Wohlgemuth and Contributors',
      author_email='berlinguyinca@gmail.com',
      license='GPLv3',
      packages=find_packages(),
      setup_requires=['pytest-runner'],
      tests_require=['pytest', 'pytest-mock', 'pytest-cov'],
      install_requires=[
          'TA-Lib',
          'pyti',
          'pandas',
          'simplejson',
          'arrow',
          'SQLAlchemy'
      ],
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Office/Business :: Financial :: Investment',
          'Intended Audience :: Science/Research',
      ])
