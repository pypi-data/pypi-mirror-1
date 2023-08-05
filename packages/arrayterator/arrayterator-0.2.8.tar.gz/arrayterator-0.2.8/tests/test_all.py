import glob
import doctest

def test_docstring():
    for file in glob.glob('*.txt'):
        doctest.testfile(file)

if __name__ == '__main__':
    test_docstring()
