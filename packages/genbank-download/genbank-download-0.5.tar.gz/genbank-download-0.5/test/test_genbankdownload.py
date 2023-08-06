import unittest
import re
import os


# handle relative import from parent directory
try:
    from genbankdownload import get_accession
except ImportError:
    import sys
    sys.path.insert(0, '..')
    from genbankdownload import get_accession
    

# J01415.2 is the standard mitochondrial Cambridge Reference Sequenc
ACCESSION_NUMBER = 'J01415.2'

def load_data(ext):
    filename = os.path.join(os.path.dirname(__file__), 'testdata', 'sequences.%s' % ext)
    handle = open(filename, 'rU')
    data = handle.readlines()
    handle.close()
    return "".join(data)

class Test(unittest.TestCase):
    """Unit tests for get_accession"""
    
    def test_xml(self):
        a = get_accession(ACCESSION_NUMBER, 'nucleotide', 'xml')
        assert a.startswith('<?xml version="1.0"?>')
        assert load_data('xml') == a
        
    def test_fasta(self):
        a = get_accession(ACCESSION_NUMBER, 'nucleotide', 'fasta')
        assert a.startswith('>gi|113200490|gb|J01415.2|HUMMTCG Homo sapiens mitochondrion, complete genome')
        assert load_data('fasta') == a
        
    def test_gb(self):
        a = get_accession(ACCESSION_NUMBER, 'nucleotide', 'gb')
        assert a.startswith('LOCUS')
        assert load_data('gb') in a
    
    def test_native(self):
        a = get_accession(ACCESSION_NUMBER, 'nucleotide', 'native')
        assert a.startswith('Seq-entry ::= set {')
        assert load_data('asn1') in a, a


if __name__ == "__main__":
    unittest.main()



