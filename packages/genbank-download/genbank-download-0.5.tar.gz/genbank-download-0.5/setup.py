from distutils.core import setup
import sys

sys.path.append('genbank-download')
import genbankdownload


setup(name='genbank-download',
      version='0.5',
      author='Simon Greenhill',
      author_email='simon@simon.net.nz',
      url='http://simon.net.nz/code/genbank-download/',
      download_url='http://bitbucket.org/simongreenhill/genbank-download/',
      description='a small script to download nucleotide sequences from genbank using an accession number.',
      long_description=genbankdownload.__doc__,
      #package_dir={'': ''},
      py_modules=['genbankdownload'],
      provides=['genbankdownload'],
      keywords='genbank genetics mitchondria bioinformatics fasta',
      license="BSD License",
      classifiers=[
          "Programming Language :: Python", 
          "Intended Audience :: Science/Research", 
          "License :: OSI Approved :: BSD License",
          "Topic :: Scientific/Engineering",
          "Topic :: Scientific/Engineering :: Bio-Informatics",
      ],
     )