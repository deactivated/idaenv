"""
Extracted from fixtures.py in importlib_metadata:

https://github.com/python/importlib_metadata/blob/main/tests/fixtures.py
"""
from __future__ import unicode_literals

import os
import sys
import shutil
import tempfile
import textwrap
import pytest

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

try:
    from contextlib import ExitStack, contextmanager
except ImportError:
    from contextlib2 import ExitStack, contextmanager


@contextmanager
def tempdir():
    tmpdir = tempfile.mkdtemp()
    try:
        yield pathlib.Path(tmpdir)
    finally:
        shutil.rmtree(tmpdir)


@contextmanager
def save_cwd():
    orig = os.getcwd()
    try:
        yield
    finally:
        os.chdir(orig)


@contextmanager
def tempdir_as_cwd():
    with tempdir() as tmp:
        with save_cwd():
            os.chdir(str(tmp))
            yield tmp


@contextmanager
def install_finder(finder):
    sys.meta_path.append(finder)
    try:
        yield
    finally:
        sys.meta_path.remove(finder)


@pytest.fixture(scope="function")
def fixture_stack():
    stack = ExitStack()
    yield stack
    stack.close()


@pytest.fixture(scope="function")
def site_dir(fixture_stack):
    site_dir = fixture_stack.enter_context(tempdir())
    yield site_dir


@contextmanager
def add_sys_path(dir):
    sys.path[:0] = [str(dir)]
    try:
        yield
    finally:
        sys.path.remove(str(dir))


@pytest.fixture(scope="function")
def on_sys_path(fixture_stack, site_dir):
    fixture_stack.enter_context(add_sys_path(site_dir))


@pytest.fixture(scope="function")
def distinfo_pkg(on_sys_path, site_dir):
    files = {
        "distinfo_pkg-1.0.0.dist-info": {
            "METADATA": """
                Name: distinfo-pkg
                Author: Steven Ma
                Version: 1.0.0
                Requires-Dist: wheel >= 1.0
                Requires-Dist: pytest; extra == 'test'
                Keywords: sample package
                Once upon a time
                There was a distinfo pkg
                """,
            "RECORD": "mod.py,sha256=abc,20\n",
            "entry_points.txt": """
                [entries]
                main = mod:main
                ns:sub = mod:main
            """,
        },
        "mod.py": """
            def main():
                print("hello world")
            """,
    }
    build_files(files, prefix=site_dir)


@pytest.fixture(scope="function")
def distinfo_pkg_with_dot(on_sys_path, site_dir):
    files = {
        "pkg_dot-1.0.0.dist-info": {
            "METADATA": """
                Name: pkg.dot
                Version: 1.0.0
                """,
        },
    }
    build_files(files, prefix=site_dir)


@pytest.fixture(scope="function")
def distinfo_pkg_with_dot_legacy(on_sys_path, site_dir):
    files = {
        "pkg.dot-1.0.0.dist-info": {
            "METADATA": """
                Name: pkg.dot
                Version: 1.0.0
                """,
            "entry_points.txt": """
                [entries]
                main = mod:main
            """,

        },
        "pkg.lot.dist-info": {
            "METADATA": """
                Name: pkg.lot
                Version: 1.0.0
                """,
            "entry_points.txt": """
                [entries]
                main = mod:main
            """,

        },
    }
    build_files(files, prefix=site_dir)


@pytest.fixture(scope="function")
def egginfo_pkg(on_sys_path, site_dir):
    files = {
        "egginfo_pkg.egg-info": {
            "PKG-INFO": """
                Name: egginfo_pkg
                Author: Steven Ma
                License: Unknown
                Version: 1.0.0
                Classifier: Intended Audience :: Developers
                Classifier: Topic :: Software Development :: Libraries
                Keywords: sample package
                Description: Once upon a time
                        There was an egginfo package
                """,
            "SOURCES.txt": """
                mod.py
                egginfo_pkg.egg-info/top_level.txt
            """,
            "entry_points.txt": """
                [entries]
                main = mod:main
            """,
            "requires.txt": """
                wheel >= 1.0; python_version >= "2.7"
                [test]
                pytest
            """,
            "top_level.txt": "mod\n",
        },
        "mod.py": """
            def main():
                print("hello world")
            """,
    }
    build_files(files, prefix=site_dir)


def build_files(file_defs, prefix=pathlib.Path()):
    """Build a set of files/directories, as described by the
    file_defs dictionary.  Each key/value pair in the dictionary is
    interpreted as a filename/contents pair.  If the contents value is a
    dictionary, a directory is created, and the dictionary interpreted
    as the files within it, recursively.
    For example:
    {"README.txt": "A README file",
     "foo": {
        "__init__.py": "",
        "bar": {
            "__init__.py": "",
        },
        "baz.py": "# Some code",
     }
    }
    """
    for name, contents in file_defs.items():
        full_name = prefix / name
        if isinstance(contents, dict):
            full_name.mkdir()
            build_files(contents, prefix=full_name)
        else:
            with full_name.open('w', encoding='utf-8') as f:
                f.write(dals(contents))


def dals(s):
    "Dedent and left-strip"
    return textwrap.dedent(s).lstrip()
