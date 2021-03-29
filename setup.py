from pathlib import Path
from sys import version_info

from setuptools import find_packages, setup

from technical import __version__

if version_info.major == 3 and version_info.minor < 6 or \
        version_info.major < 3:
    print('Your Python interpreter must be 3.6 or greater!')
    exit(1)

readme_file = Path(__file__).parent / "README.md"
readme_long = "Technical Indicators for Financial Analysis"
if readme_file.is_file():
    readme_long = (Path(__file__).parent / "README.md").read_text()

setup(name='technical',
      version=__version__,
      description="Technical Indicators for Financial Analysis",
      long_description=readme_long,
      long_description_content_type="text/markdown",
      url='https://github.com/freqtrade/technical',
      author='Freqtrade Team',
      author_email='berlinguyinca@gmail.com',
      license='GPLv3',
      packages=find_packages(),
      setup_requires=['pytest-runner'],
      tests_require=['pytest', 'pytest-cov', 'pytest-mock'],
      install_requires=[
          'TA-Lib',
          'pandas',
          'arrow',
      ],
      include_package_data=True,
      zip_safe=False,
      classifiers=[
          'Programming Language :: Python :: 3.6',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Topic :: Office/Business :: Financial :: Investment',
          'Intended Audience :: Science/Research',
      ])
