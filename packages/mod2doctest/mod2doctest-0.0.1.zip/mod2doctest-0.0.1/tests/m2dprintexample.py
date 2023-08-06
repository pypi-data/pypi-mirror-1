if __name__ == '__main__':
    import mod2doctest
    mod2doctest.convert(src=None, 
                        target='m2dprintexample_test.py', 
                        run_doctest=True, 
                        add_testmod=True)
    
from mod2doctest import m2d_print

#===============================================================================
m2d_print.h1('TEST_SETUP')
#===============================================================================
import pickle
import os


m2d_print.h2('GOING TO DO IT')
#-------------------------------------------------------------------------------
print 'foobar'
