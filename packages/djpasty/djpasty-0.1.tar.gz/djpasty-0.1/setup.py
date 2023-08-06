import os

from setuptools import setup, find_packages

version = '0.1'

def read_file(*path):
    return open(os.path.join(os.path.dirname(__file__),
                             *path)).read()

readme = read_file('README.txt')

setup(name='djpasty',
      version=version,
      description=("Djpasty makes it easy to run Django with"
                   " the Paste webserver."),
      long_description=readme,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Framework :: Django",
        ],
      author='Jeroen Vloothuis',
      author_email='jeroen.vloothuis@xs4all.nl',
      url='https://launchpad.net/djpasty',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'paste',
        ],
      )
