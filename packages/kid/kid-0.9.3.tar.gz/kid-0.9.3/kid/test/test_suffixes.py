"""Unit Tests for the import suffix functionality."""

__revision__ = "$Rev: 219 $"
__author__ = "David Stanek <dstanek@dstanek.com>"
__copyright__ = "Copyright 2005, David Stanek"

import sys
import ihooks
import py
import kid
import kid.importer

tmpdir = py.test.ensuretemp("test_suffixes")
sys.path = [str(tmpdir)] + sys.path

tfile = tmpdir.join("test_suffixes0.kid")
tfile.write(py.code.Source("""
<html xmlns:py="http://purl.org/kid/ns#">
    <body>
        <p>my content</p>
    </body>
</html>
"""))

def test_enable_import_empty():
    """By default *.kid files are imported."""
    kid.enable_import()
    import test_suffixes0
    py.test.raises(ImportError, "import test_suffixes1")
    kid.importer.uninstall()

def test_enable_import_with_suffixes():
    """Using suffixes any file extension can be importable."""
    kid.enable_import(suffixes=[".html", ".kid.html"])
    import test_suffixes0 # *.kid files are always importable

    dest = tmpdir.join("test_suffixes1.html")
    tfile.copy(dest)
    import test_suffixes1

    dest = tmpdir.join("test_suffixes2.kid.html")
    tfile.copy(dest)
    import test_suffixes2

    dest = tmpdir.join("test_suffixes3.xhtml")
    tfile.copy(dest)
    py.test.raises(ImportError, "import test_suffixes3")
    kid.importer.uninstall()
