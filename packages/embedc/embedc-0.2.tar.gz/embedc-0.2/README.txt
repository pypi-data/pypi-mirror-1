embedc: Python Embedded C
ALPHA 0.2
2/12/2010

Copyright 2010 by Fernando Trias
See Artistic License in LICENSE

embedc enables Python source code to embed C/C++ snippets that seamlessly access and modify Python variables and call Python functions. 

PREREQUISITES

* GCC version 3 or higher
* Python 2.5 or higher (also compatible with Python 3)

INSTALL:

    python setup.py install
         -- OR --
    easy_install embedc
    
TEST:

You don't have to install before running the test:

    python test.py
    
If you have they python-coverage module, you can also run test-coverage to ensure all source lines are covered in the test suite.    

USAGE:

See web site, test.py and sample.py for examples and usage. More documentation is forthcoming.

Simple example:

    from embedc import C
    v = 5
    r = C("""
        v = v * 10;
        """)
    print v

Complex example:

    from embedc import C

    def myround(number):
        return round(number, 1)

    def test(data):
        datalen = len(data)
        mean = 0.0
        stddev = 0.0
        status="Calculate statistics"
        C(r"""
            #include <math.h>
            DEF double myround double
            printf("%s\n", status);
            double sum, sumsq = 0.0;
            for(int i=0;i<datalen; i++) {
                sum += data[i];
            }
            mean = sum / datalen;
            for(int i=0;i<datalen; i++) {
                sumsq += pow((data[i] - mean),2);
            }
            stddev = sqrt(sumsq / (datalen-1));
            stddev = myround(stddev);
            mean = myround(mean);
            status = "Done";
            """)
        print("Mean = %f" % mean)
        print("Stddev = %f" % stddev)
        print(status)

    samples=(10.5,15.1,14.6,12.3,19.8,17.1,6.1)
    test(samples)

SPECIAL CONSIDERATIONS

When using embed_c_precompile and inline_c_precompile, embedc will read in the source file before it is interpreted. It will look for the function name and the triple-quote """ sequence. It will also look for another triple-quote """ to end. The close parenthesis must be on the same line as the ending triple-quote """ (see examples above). This is because embedc uses line numbers to find the precompiled function at run time.

TODO:

* Allow additional compilers; allow passing GCC command line options.

* Support arrays of strings.

* Support returning strings from Python functions called from within C/C++.

* With non-precompiled code, keep a cache of the source code so if it doesn't change it, we can just reuse the DLL/so.


REFERENCES AND NOTES:

embedc makes heavy use of ctypes.

There are several alternatives to embedc. All of them have their pros and cons. Here are several:

PyInline <http://pyinline.sourceforge.net/> is a module for inlining multiple languages in Python last updated in 2001 that predates ctypes. It seeks to copy Perl Inline <http://search.cpan.org/~sisyphus/Inline-0.45/C/C.pod>.

ezpyinline <http://pypi.python.org/pypi/ezpyinline/0.1> is a fork of PyInline that provides a very simple interface for embedding C/C++ functions.

PyInline and ezpyinline do not hande arrays. I think C provides the greatest speed advantage when looping over large amounts of data and performing multiple calculations. Without arrays or the ability to return more than one number (PyInline and ezpyinline provide one return value), that advantage is hard to realize. embedc fixes these shortcoming by using ctypes to allow C/C++ to access and modify arrays.

These modules also don't provide an easy mechanism for accessing and altering Python variables from within the C/C++ code. With them, to modify variables from C, you have to code in the Python API, which is neither easy nor straightforward. 

In addition, they require a working python development environment. This can be complex on Linux if you are not using standard packages, and is also difficult in Windows. By using ctypes, embedc does not require a working Python build environment, thus simplifying deployment because there is no need to configure include paths, lib paths and so forth. The only requirement is a working compiler.

PyRex <http://wiki.python.org/moin/Pyrex> is a Python-like language that mixes C and Python to create Python modules. This is a very interesting approach, but isn't really Python and requires a great deal of expertise to use.


KNOWN ISSUES:

Cygwin:
    Cygwin has numerous problems with the test script because it quickly runs out of resources. The test script covers too many scenarios loading too many different DLLs for Cygwin to handle.

    If you get an error like this on Windows:
        *** fatal error - unable to remap tmpE9X11V.cpp.dll to same address as parent(0x2B0000) != 0x3B0000
        python 5368 fork: child 1676 - died waiting for dll loading, errno 11
    Check out http://inamidst.com/eph/cygwin for a possible solution.

    Occasionally, this error might come up in the test.py script:
        OSError: [Errno 11] Resource temporarily unavailable
    This is due to the limitations of Cygwin.
    
Local Variables: Modifying local variables is tricky and involves calling internal Python functions. It has been tested on Python 2.5, 2.6, and 3.1 but may break in future versions is the internal representation of frames and variables changes.
