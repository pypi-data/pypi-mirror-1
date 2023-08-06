# PYTHON
import doctest
# MOD2DOCTEST
import mod2doctest

def run_all():
    for file in ['basicexample', 'm2d_print']:
        output = mod2doctest.convert(src='%s.py' % file, target=None)
        known_to_be_good_output = open('%s_docstr.py' % file).read().strip()[1:]
        print '\n\nTesting %s ...' % file
        print `output`
        print `known_to_be_good_output`
        print `output.replace(known_to_be_good_output[0:125], '')`
        

if __name__ == '__main__':
    run_all()

