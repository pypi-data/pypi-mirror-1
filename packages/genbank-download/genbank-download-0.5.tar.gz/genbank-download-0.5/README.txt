genbank-download is a small script to download nucleotide sequences from genbank 
using an accession number.

Usage:

python genbankdownload.py [options] ACCESSION-NUMBER

e.g.
    python genbankdownload.py J01415
    python genbankdownload.py J01415 > mysequence.xml
    python genbankdownload.py -m fasta J01415 > mysequence.fasta
    
    
(c) Simon J. Greenhill 2009. Contact me at <simon@simon.net.nz>