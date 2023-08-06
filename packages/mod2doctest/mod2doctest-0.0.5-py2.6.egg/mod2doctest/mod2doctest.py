"""Converts a Python module to a |doctest| testable docstring. 

The basic idea behind |mod2doctest| is provide a *snapshot* of the current
run of a module.  That is, you just point |mod2doctest| to a module and it 
will:

*  Run the module in a interperter.
*  Add all the '>>>' and '...' as needed.
*  Copy all the output from the run and put it under the correct input.
*  Add ellipses where needed like to memory ids and tracebacks. 
*  And provide other formating options. 

This allows you to quickly turn any Python module into a test that you can use
later on to test refactors / regression testing / etc. 

Attributes:

    convert (function): The public interface to |mod2doctest| is the 
    :func:`convert` function.
    
    FLAGS (class): :class:`FLAGS` provides a namespace for all option flags 
    that can be OR'd together to control output. 

    m2d_print (class): :class:`m2d_print` provides a namespace for utility 
    print functions that allow you to print to stdout when running a module 
    but then format nicely for inclusion into the docstring. 
    
    DEFAULT_DOCTEST_FLAGS (int): The default |doctest| flags used when 1) 
    running doctest (if :func:`convert` is directed to run doctest) or 
    when adding the ``if __name__ == '__main__'`` clause to an output
    ``target`` file.  The default options are::

        import doctest
        DEFAULT_DOCTEST_FLAGS = (doctest.ELLIPSIS | 
                                 doctest.REPORT_ONLY_FIRST_FAILURE |
                                 doctest.NORMALIZE_WHITESPACE)
    

"""

import sys
import os
import inspect
import subprocess
import re
import doctest
import datetime

class FLAGS(object):
    """Option flags used to control docstring output
    
    Option flags include: 

    *  ``ELLIPSE_TRACEBACK`` or ``ET``:  When set, :func:`convert` will replace
       the "middle" part of a traceback with ellipse (the part that contain 
       path references). 
    
    *  ``ELLIPSE_MEM_ID`` or ``EM``:  When set, :func:`convert` will replace
       all memory ids with ellipse (e.g. 0xABCD0120 --> 0x...)

    *  ``ELLIPSE_PATHS`` or ``EP``:  When set, :func:`convert` will replace
       all local paths with ellipse.  For example ``'C:\myfolder\myfile.txt'`` 
       or ``'/usr/myfolder/myfile.txt'`` will go to ``'...myfile.txt'``.  Note, 
       this only works on paths which are within quotes. 

    *  ``REMOVE_NAME_EQUAL_MAIN`` or ``RNM``:  When set, :func:`convert` will 
       remove all content within a ``if __name__ == '__main__':`` block.  This
       allows you to have content within the module without it ending up in 
       the output docstring. 
        
    *  ``COMMENTS TO TEXT`` or ``C2T``:  When set, :func:`convert` will replace
       # comments to be left justified text in the docstring output.     

    *  ``ALL``:  All option flags OR'd together.  
     
    """
    ELLIPSE_TRACEBACK = 1
    ELLIPSE_MEM_ID = 2
    ELLIPSE_PATHS = 4
    COMMENTS_TO_TEXT = 8
    REMOVE_NAME_EQUAL_MAIN = 16
    ET = ELLIPSE_TRACEBACK
    EM = ELLIPSE_MEM_ID
    EP = ELLIPSE_PATHS
    C2T = COMMENTS_TO_TEXT
    RNM = REMOVE_NAME_EQUAL_MAIN
    # ALL THE FLAGS
    ALL = (ET | EM | EP | C2T | RNM)

DEFAULT_DOCTEST_FLAGS = (doctest.ELLIPSIS | 
                         doctest.REPORT_ONLY_FIRST_FAILURE |
                         doctest.NORMALIZE_WHITESPACE)
    
def convert(src=None,
            target=True,
            add_testmod=False,
            python_cmd='python',
            flags=FLAGS.ALL,            
            break_on_newlines=True,
            run_doctest=True,
            doctest_flags=DEFAULT_DOCTEST_FLAGS, 
            fn_process_input=None, 
            fn_process_docstr=None, 
            fn_title_docstr=None,             
            ):
    """Runs a python module in shell, grabs output and returns a docstring.
    
    Kwargs:
    
        src (None, module, or file path): The python module to be converted.
        If None is given, the current module is used.  Otherwise, you need
        to provide either 1) a valid python module object or 2) a path (string)
        to the module to be run. 
        
        target (None, True, or file path): Where you want the output docstring
        to be placed.  If None, the docstring is not saved anywhere (but it
        is returned by this function).  If True is given, the src module is 
        used (the docstring is prepended to the file).  If a path (of type
        str) is provided, the docstr is saved to that file. 
        
        add_testmod (True or False): If True a ``if __name__ == '__main__'`` 
        block is added to the output file IF the ``target`` parameter is an
        external file (str path). 
         
        python_cmd (string): The python command to run to start the shell.
        
        flags (mod2doctest FLAG): A group of OR'd together mod2test flags.  See
        :class:`FLAGS` for valid flags. 

        break_on_newlines (True, False, or str): If True, this will convert 
        two or more newlines in the modules into two newlines in the output
        docstring.  When False, whitespace is converted to ``>>>`` in the 
        docstring.  If a string is provided, two or more newlines are 
        replaced by the provided string.  
        
        run_doctest (True or False): If True doctest is run on the resulting
        docstring. 
            
        doctest_flags (:mod:`doctest` flags): Valid OR'd together :mod:`doctest`
        flags.  The default flags are::  
 
            DEFAULT_DOCTEST_FLAGS = (doctest.ELLIPSIS | 
                                     doctest.REPORT_ONLY_FIRST_FAILURE |
                                     doctest.NORMALIZE_WHITESPACE)
 
        fn_process_input (callable): A function that is called and is passed
        the module input.  Used for preprocessing.   

        fn_process_docstr (callable): A function that is called and is passed
        the final docstring before saving.  Used for post processing. 
        You can use this function to perform your own custom regular 
        expressions replacements and remove temporal / local data from your 
        output before |doctest| is run.

        fn_title_docstr (callable): A function that is called and should return
        a string that will be used for the title. 
        
    Returns: 
        
        A docstring of type str. 
        
    """

    if src is None:
        src = sys.modules['__main__']
  
    if inspect.ismodule(src):
        input = open(src.__file__, 'r').read()
    elif isinstance(src, str) and os.path.isfile(src):
        input = open(src, 'r').read()
    elif isinstance(src, str):
        input = src
    else:
        raise SystemError, ("'src' %s must be a valid module, file path, "
                            "or string ...") % obj

    input = _input_remove_docstring(input)

    # Remove first docstring ...
    pinput = _input_escape_shell_prompt(input)       
    pinput = _input_fix_comments(pinput)
    pinput = _input_fix_ws_rstrip(pinput)
   
    if (flags & FLAGS.REMOVE_NAME_EQUAL_MAIN):
        pinput = _input_remove_name_eq_main(pinput)

    # Remove extra whitespace at end. 
    # You need to do this AFTER the removing of ``if __name__ == '__main__'``
    pinput = '\n\n' + pinput.strip() + '\n'
    
    shell = subprocess.Popen(args=[python_cmd, "-i"],
                             shell=False,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,
                             )

    output = shell.communicate(pinput)[0]

    output = _output_fixup(output)

    if (flags & FLAGS.ELLIPSE_MEM_ID):
        output = _ellipse_mem_id(output)
 
    if (flags & FLAGS.ELLIPSE_PATHS):
        output = _ellipse_paths(output)
   
    input_lines = pinput.split('\n') + ['']
    docstr = ''
        
    for output_line in output.split('\n'):
        docstr = _match_input_to_output(docstr,
                                        input_lines,
                                        output_line)
    
   
    docstr = _docstr_fix_comments(docstr)

    if (flags & FLAGS.ELLIPSE_TRACEBACK):
        docstr = _ellipse_traceback(docstr)
                 
    if break_on_newlines:
        docstr = _docstr_break_on_newlines(docstr, break_on_newlines)

    docstr = _docstr_left_shift_comments(docstr)
    docstr = _docstr_remove_m2d_print_h1(docstr)
    docstr = _docstr_remove_m2d_print_h2(docstr)
    docstr = _docstr_fixup(docstr)
    if fn_process_docstr:
        docstr = fn_process_docstr(docstr)

    if fn_title_docstr:
        doctitle = fn_title_docstr(docstr)
    else:
        doctitle = _docstr_get_title()

    docstr = '"""%s\n\n%s\n\n"""' % (doctitle, docstr.strip())

    if target:

        if target is True:
            target = src
            
        _docstr_save(docstr, src, target, input, add_testmod)
                    
        if run_doctest is not False:
            _run_doctest(target, doctest_flags)

    return docstr

class m2d_print(object):
    """Convenince fns that nicely print to both stdout and docstring output. 
    
    When you run a module, sometimes you want to delimit the output.  
    Therefore, you might use a :func:`print` statement.  However, this will
    cause your output docstring to contain many:: 
    
        >>> print 'foobar'
        foobar 
        
    like statements.  The m2d_print allows you to add the following types of 
    statements to your module::
        
        #=======================================================================
        m2d_print.h1('I AM HERE')
        #=======================================================================
        
    This will print to std out like this:: 

        ========================================================================
        I AM HERE
        ========================================================================

    And will show up in the docstring like this::

        '''
        ========================================================================
        I AM HERE
        ========================================================================
        '''
         
    See :mod:`mod2doctest.tests.m2dprint` for more examples. 
       
    """
    
    @staticmethod
    def h1(line):
        print '\n\n\n%s\n%s\n%s' %('='*80, line, '='*80)

    @staticmethod
    def h2(line):
        print '\n%s\n%s' % (line, '-'*80)

    @staticmethod
    def h3(line):
        print line
        



_ADD_TESTMOD_STR = """
if __name__ == '__main__':
    import doctest
    doctest.testmod(optionflags=%d)
"""
        
_REGEX_INPUT_PROCESS = re.compile(r'''
^\s*            # Start of file, exclude whitespace
(r|R)?          # Allow for raw-strings
"""             # First triple quote.
(.|\n)*?        # Everything in-between, but a non-greedy match   
"""             # Second triple quote.
\s*             # Get rid of all other whitespace.
''', flags=re.VERBOSE)
def _input_remove_docstring(input):
    """Strips the input and removes the first docstring from the input.
    
    .. note;:
    
       The first docstring is never treated as part of the input file.  
       Most notably, because this is when -- if directed -- mod2doctest
       will put the output docstring (at the top of the file). 
    
    """
    input = '\n\n' + _REGEX_INPUT_PROCESS.sub('', input).strip() + '\n'
    return input.replace(r'\r', r'')

def _input_escape_shell_prompt(input):    
    """Replaces `>>>` and '...' with escaped versions."""
    input = input.replace('>>>', '\>>>')
    return input.replace('...', '\...')

_REGEX_INPUT_FIX_COMMENTS = re.compile(r'^(#.*)', flags=re.MULTILINE)
def _input_fix_comments(input):
    """Puts a newline after comments -- needed for post processing."""
    return _REGEX_INPUT_FIX_COMMENTS.sub(r'\1\n', input)

_REGEX_INPUT_FIX_WS_RSTRIP = re.compile(r'(\S)[ \t]*\n')
def _input_fix_ws_rstrip(input):
    """Right strips line that contain non whitespace characters."""
    return _REGEX_INPUT_FIX_WS_RSTRIP.sub(r'\1\n', input)
    
def _docstr_get_title():
    return "\n%s\nAuto generated by mod2doctest on %s\n%s" % \
           ('='*80, datetime.datetime.now(), '='*80)

def _docstr_save(docstr, src, target, input, add_testmod):
                   
    if isinstance(target, str):
        input = ''
        file = target
    elif inspect.ismodule(target):
        file = target.__file__
    else:
        raise SystemError, "Unknown target type %s ..." % target

    if add_testmod and src is not target:
        if add_testmod is True:
            add_testmod  = _ADD_TESTMOD_STR % DEFAULT_DOCTEST_FLAGS
    else:
        add_testmod = ''
            
    output = 'r%s\n%s\n%s' % (docstr,
                              add_testmod,
                              input)
    open(file, 'w').write(output)

def _run_doctest(target, doctest_flags):
    if inspect.ismodule(target):
        doctest.testmod(target, optionflags=doctest_flags)
    else:
        doctest.testfile(os.getcwd() + os.sep + target, 
                         optionflags=doctest_flags)

_REGEX_OUTPUT_FIXUP_0 = re.compile(r'>>>[ |\t]$', flags=re.MULTILINE)
_REGEX_OUTPUT_FIXUP_1 = re.compile(r'^[ |\t]*$', flags=re.MULTILINE)
def _output_fixup(output):
    output = _REGEX_OUTPUT_FIXUP_0.sub(r'>>> <BLANKLINE>', output)
    return _REGEX_OUTPUT_FIXUP_1.sub(r'<BLANKLINE>', output).replace('\r', '')

def _match_input_to_output(docstr, input_lines, output_line):
    started = False
    while True:
        if output_line.startswith('>>> '):
            docstr += '>>> ' + input_lines.pop(0) + '\n'
            started = True
            output_line = output_line[4:]
        elif started and output_line.startswith('... '):
            docstr += '... ' + input_lines.pop(0) +'\n'
            output_line = output_line[4:]
        else:
            return docstr + output_line +'\n'

_REGEX_DOCSTR_FIX_COMMENTS = re.compile(r'(\n>>>\s*#.*)\n... ')
def _docstr_fix_comments(docstr):
    return _REGEX_DOCSTR_FIX_COMMENTS.sub(r'\1', docstr)
           
_REGEX_NEM = re.compile(r"""
^if\s+__name__\s*==\s*['"]__main__['"]\s*:.*
(\n[ \t].*)*""", flags=re.MULTILINE | re.VERBOSE)
def _input_remove_name_eq_main(input):
    return _REGEX_NEM.sub('', input)

_REGEX_LEFT_SHIFT_COMMENTS = re.compile(r'^>>>\s*#[ |\t]*', 
                                       flags=re.MULTILINE)
def _docstr_left_shift_comments(docstr):
    return _REGEX_LEFT_SHIFT_COMMENTS.sub(r'', docstr)
   
_REGEX_THREE_NEWLINES = re.compile(r'\n{2,}')
_REGEX_END_STUFF = re.compile(r'(\n\s*(>>>|<BLANKLINE>)[ |\t]*)*$')
def _docstr_fixup(docstr):
    docstr = docstr.replace(r'"""', r"'''")
    docstr = _REGEX_THREE_NEWLINES.sub(r'\n\n\n', docstr)
    return _REGEX_END_STUFF.sub(r'\n', docstr)
           
_REGEX_NEWLINE_TO_WS = re.compile(r'(\\?>>>\s*\n){2,}')
def _docstr_break_on_newlines(docstr, replace=True):
    if replace is True:
        replace = r'\n\n'
    return _REGEX_NEWLINE_TO_WS.sub(replace, docstr)

_REGEX_ELLIPSE_MEM_ID = re.compile(r'(?<=<)(?:(?:.*\.)*)(.* at 0x).*(?=>)')
def _ellipse_mem_id(output):
    return _REGEX_ELLIPSE_MEM_ID.sub(r'...\1...', output)

_REGEX_ELLIPSE_TRACEBACK = re.compile(r"""
                                    (Traceback.*)
                                    (?:(?:\n[ |\t]+.*)*)
                                    (\n\w+.*)
                                    """, flags=re.MULTILINE | re.VERBOSE)
def _ellipse_traceback(docstr):
    return _REGEX_ELLIPSE_TRACEBACK.sub(r'\1\n    ...\2', docstr)
    
_REGEX_LOCAL_PATH = re.compile(r"""
(\s+['|\"]+)
(?:/+|[a-zA-Z]:\\+)
.*
(?:/+|\\+)
((?:\w|\.)+['|\"]+)
""", flags=re.VERBOSE)
def _ellipse_paths(output):
    return _REGEX_LOCAL_PATH.sub(r'\1...\2', output)

_REGEX_REMOVE_PRINT_H1 = re.compile(r"""
\n>>>\s*m2d_print.h1.*
\n\n\n
\n={80}
((?:\n.*)*?)
\n={80}
""", flags=re.VERBOSE)
def _docstr_remove_m2d_print_h1(docstr):
    return _REGEX_REMOVE_PRINT_H1.sub(r'\1', docstr)
    
_REGEX_REMOVE_PRINT_H2 = re.compile(r"""
\n>>>\s*m2d_print.h2.*
\n
((?:\n.*)*?)
\n-{80}
""", flags=re.VERBOSE)
def _docstr_remove_m2d_print_h2(docstr):
    return _REGEX_REMOVE_PRINT_H2.sub(r'\1', docstr)

_REGEX_REMOVE_PRINT_H3 = re.compile(r"""
\n>>>\s*m2d_print.h2.*
((?:\n.*)*?)
""", flags=re.VERBOSE)
def _docstr_remove_m2d_print_h3(docstr):
    return _REGEX_REMOVE_PRINT_H3.sub(r'\1', docstr)
    
    
