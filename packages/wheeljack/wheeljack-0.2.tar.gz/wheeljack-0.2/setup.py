import os

from setuptools import setup, find_packages

version = '0.2'

def read_file(*path):
    return open(os.path.join(os.path.dirname(__file__),
                             *path)).read()

readme = read_file('README.txt')
installation = read_file('docs', 'INSTALLATION.txt')

setup(name='wheeljack',
      version=version,
      description="Wheeljack is a build system.",
      long_description='\n\n'.join([readme, installation]),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Build Tools",
        ],
      author='Jeroen Vloothuis',
      author_email='jeroen.vloothuis@xs4all.nl',
      url='https://launchpad.net/wheeljack',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'simplejson',
        'bzr',
        'pysqlite',
        'python-dateutil',
        'httplib2',
        ],
      entry_points = {
        'console_scripts': [
            'wheeljack = wheeljack.builder:main',
        ]
    },

      )
