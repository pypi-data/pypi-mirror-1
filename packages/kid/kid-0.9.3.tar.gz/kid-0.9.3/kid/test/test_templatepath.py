"""
Unit tests for the kid.TemplatePath class.

The testing directory structure looks something like this:

::
    test_templatepath0/
                      /index.kid
                      /members/
                              /index.kid
                              /stuff.kid
                              /master.kid
                      /nonmembers/
                                 /index.kid
                                 /garbage.kid
                                 /master.kid
                      /shared/
                             /message.kid
                             /error.kid
                             /errors/
                                    /error1.kid
                                    /error2.kid
                                    /error3.kid
    test_templatepath1/
                      /index.kid
                      /master.kid
                      /members/
                              /master.kid
                              /stuff.kid
"""

from os.path import join, normpath
import py
import kid

kfind = kid.path.find

tmpdir0 = None
tmpdir1 = None
files = {}

def setup_module(m):
    """Create a testing directory structure."""
    global files, tmpdir0, tmpdir1

    def _create(dir, files):
        """Create files."""
        for file in files:
            dir.join(file).write("nothing")

    # create the directory structure
    tmpdir0 = py.test.ensuretemp("test_templatepath0")
    _create(tmpdir0, ["index.kid"])

    members = tmpdir0.mkdir("members")
    _create(members, ["index.kid", "stuff.kid", "master.kid"])

    nonmembers = tmpdir0.mkdir("nonmembers")
    _create(nonmembers, ["index.kid", "garbage.kid", "master.kid"])

    shared = tmpdir0.mkdir("shared")
    _create(shared, ["message.kid", "error.kid"])

    errors = shared.mkdir("errors")
    _create(errors, ["error1.kid", "error2.kid", "error3.kid"])

    tmpdir1 = py.test.ensuretemp("test_templatepath1")
    _create(tmpdir1, ["index.kid", "indexz.kid", "master.kid"])

    members = tmpdir1.mkdir("members")
    _create(members, ["stuff.kid", "master.kid"])

    tmpdir0 = str(tmpdir0)
    kid.path.append(tmpdir0)
    tmpdir1 = str(tmpdir1)
    kid.path.append(tmpdir1)

def test_simple_file_in_root():
    assert kfind("index.kid") == normpath(join(tmpdir0, "index.kid"))
    assert kfind("indexz.kid") == normpath(join(tmpdir1, "indexz.kid"))

def test_file_in_directory():
    assert kfind("members/index.kid") == \
    		normpath(join(tmpdir0, "members/index.kid"))

    path = "shared/errors/error1.kid"
    assert kfind(path) == normpath(join(tmpdir0, path))

def test_no_exist():
    assert kfind("noexist.kid") == None

def test_find_relative():
    rel = normpath(join(tmpdir0, "shared/error.kid"))
    expected = normpath(join(tmpdir0, "shared/message.kid"))
    assert kfind("message.kid", rel=rel) == expected

def test_crawl_path():
    rel = normpath(join(tmpdir0, "nonmembers/stuff.kid"))
    expected = normpath(join(tmpdir1, "master.kid"))
    assert kfind("master.kid", rel=rel) == expected

def test_mod_python_bug():
    """This recreates the problem reported in tickit #110."""
    
    tmpdir = py.test.ensuretemp("test_templatepath")
    tmpdir.join("test.kid").write("nothing")
    tmpdir.join("base.kid").write("nothing")
    assert kfind("base.kid", rel=join(str(tmpdir), "test.kid")) \
            == join(str(tmpdir), "base.kid")
