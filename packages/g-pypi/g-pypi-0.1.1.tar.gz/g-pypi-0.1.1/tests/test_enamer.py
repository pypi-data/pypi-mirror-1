#!/usr/bin/env python


"""

Unit tests via nose


"""


#import functions you're testing implicitly so we can get an idea of coverage
from g_pypi.enamer import is_valid_uri, get_filename, get_vars



def test_is_valid_uri():
    """Check if URI's addressing scheme is valid
     
     g-pypi will use http, ftp and mirror
    
    """

    assert is_valid_uri('http://foo.com/foo-1.0.tbz2') == True
    assert is_valid_uri('ftp://foo.com/foo-1.0.tbz2') == True
    assert is_valid_uri('mirror://sourceforge/foo-1.0.tbz2') == True
    assert is_valid_uri('http://foo.com/foo-1.0.tbz2#md5=2E3AF09') == True

def test_get_filename():
    """Return filename minus extension from src_uri"""
    assert get_filename("http://www.foo.com/pkgfoo-1.0.tbz2") == "pkgfoo-1.0"
    assert get_filename("http://www.foo.com/PKGFOO-1.0.tbz2") == "PKGFOO-1.0"
    assert get_filename("http://www.foo.com/pkgfoo_1.0.tbz2") == "pkgfoo_1.0"
    assert get_filename("http://www.foo.com/PKGFOO_1.0.tbz2") == "PKGFOO_1.0"
    assert get_filename("http://www.foo.com/pkg-foo-1.0_beta1.tbz2") == \
            "pkg-foo-1.0_beta1"
    assert get_filename("http://www.foo.com/pkg_foo-1.0lawdy.tbz2") == \
            "pkg_foo-1.0lawdy"
    assert get_filename("http://internap.dl.sourceforge.net/sourceforge/abeni/abeni-0.0.22.tar.gz") == "abeni-0.0.22"
    assert get_filename("http://internap.dl.sourceforge.net/sourceforge/dummy/StupidName_0.2.tar.gz") == "StupidName_0.2"



test_get_vars_docs = \
    """
    
    Test ``get_vars`` with all types of URI's we can come up with.

    Note:
    -----

    up_pn and up_pv are upstream's package name and package version respectively
    and not actually used in an ebuild. These are the names returned
    from yolklib/PyPI.

    
    """

def test_get_vars1():
    """
    Absolute best-case scenario determines $P from up_pn, up_pv
    We have a sanely named package and URI is perfect.

    """

    up_pn = "pkgfoo"
    up_pv = "1.0"
    uri = "http://www.foo.com/pkgfoo-1.0.tbz2"
    input_test = (uri, up_pn, up_pv)
    correct = \
        {'pn': 'pkgfoo',
         'pv': '1.0',
         'p': 'pkgfoo-1.0',
         'my_pn': '',
         'my_pv': '',
         'my_p': '',
         'my_p_raw': '',
         'src_uri': 'http://www.foo.com/${P}.tbz2',
         }
    results = get_vars(uri, up_pn, up_pv)
    _get_vars(input_test, correct, results, __doc__)


def test_get_vars2():
    """
    (up_pn == pn) but URI has wrong case

    """
    up_pn = "pkgfoo"
    up_pv = "1.0"
    uri = "http://www.foo.com/PkgFoo-1.0.tbz2"
    input_test = (uri, up_pn, up_pv)
    correct = \
        {'pn': 'pkgfoo',
         'pv': '1.0',
         'p': 'pkgfoo-1.0',
         'my_pn': 'PkgFoo',
         'my_pv': '',
         'my_p': '${MY_PN}-${PV}',
         'my_p_raw': 'PkgFoo-1.0',
         'src_uri': 'http://www.foo.com/${MY_P}.tbz2',
         }
    results = get_vars(uri, up_pn, up_pv)
    _get_vars(input_test, correct, results, __doc__)

def test_get_vars3():
    """ 
    (up_pn != pn) URI has correct case
    
    """
    up_pn = "PKGFoo"
    up_pv = "1.0"
    uri = "http://www.foo.com/pkgfoo-1.0.tbz2"
    input_test = (uri, up_pn, up_pv)
    correct = \
        {'pn': 'pkgfoo',
         'pv': '1.0',
         'p': 'pkgfoo-1.0',
         'my_pn': '',
         'my_pv': '',
         'my_p': '',
         'my_p_raw': '',
         'src_uri': 'http://www.foo.com/${P}.tbz2',
         }
    results = get_vars(uri, up_pn, up_pv)
    _get_vars(input_test, correct, results, __doc__)


def test_get_vars4():
    """
    
    up_pn is not lower case but matches uri pn
    
    """

    pn = "pkgfoo"
    up_pn = "PKGFoo"
    up_pv = "1.0"
    uri = "http://www.foo.com/PKGfoo-1.0.tbz2"
    input_test = (uri, up_pn, up_pv, pn)
    correct =\
        {'pn': 'pkgfoo',
         'pv': '1.0',
         'p': 'pkgfoo-1.0',
         'my_pn': 'PKGfoo',
         'my_pv': '',
         'my_p': '${MY_PN}-${PV}',
         'my_p_raw': 'PKGfoo-1.0',
         'src_uri': 'http://www.foo.com/${MY_P}.tbz2',
         }
    results = get_vars(uri, up_pn, up_pv, pn="pkgfoo")
    _get_vars(input_test, correct, results, __doc__)


def test_get_vars5():
    """
    up_pn is not lower case and doesn't match uri case
    """
    pn = "pkgfoo"
    up_pn = "PKGFoo"
    up_pv = "1.0"
    uri = "http://www.foo.com/pkgFOO-1.0.tbz2"
    input_test = (uri, up_pn, up_pv, pn)
    correct =\
        {'pn': 'pkgfoo',
         'pv': '1.0',
         'p': 'pkgfoo-1.0',
         'my_pn': 'pkgFOO',
         'my_pv': '',
         'my_p': '${MY_PN}-${PV}',
         'my_p_raw': 'pkgFOO-1.0',
         'src_uri': 'http://www.foo.com/${MY_P}.tbz2',
         }
    results = get_vars(uri, up_pn, up_pv, pn)
    _get_vars(input_test, correct, results, __doc__)

def _get_vars(input_test, correct, results, test_desc):
    try:
        assert results == correct
    except AssertionError:
        print
        print "Testing:", test_desc
        print 'get_vars(raw_uri, up_pn, up_pv, pn="", pv="")'
        print input_test
        print "<var> -> <result> -> <correct>"
        print
        for key in results.keys():
            if results[key] != correct[key]:
                print "*", 
            print key, "->", results[key], "->", correct[key]

        raise AssertionError
