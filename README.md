# idaenv - IDAPython Plugin Management

idaenv is a plugin manager for the IDA Pro disassembler. It bridges the gap
between IDA Pro and the greater Python ecosystem of setuptools/virtualenv.

Most Python packages are distributed using setuptools (or perhaps distutils) and
the PyPi package repository. However IDA Pro expects extensions to be standalone
files placed in a specific directory. Using idaenv, you can install Python
packages into a virtual environment using setuptools (or pip), run a single
"update" command, and immediately use plugins, processor modules, or loaders
contained in the package.

## Usage

Initialize a virtual environment to use with IDA Pro:

    $ mkvirtualenv -p python2 ida

Install idaenv:

    $ cd idaenv
    $ python setup.py install

Update the IDAUSR environment variable to include the idaenv plugin directory:

    $ export IDAUSR=$HOME/.idapro:$( idaenv prefix )

Install some idaenv compatible extensions using setup.py or pip. Then use the
idaenv "update" command:

    $ pip install ...
    $ idaenv update
    ... TODO include output ...

To see what plugins are installed, use the "status" command.

    ... TODO include output ...

## Mechanism

idaenv takes inspiration from the established `console_scripts` mechanism in
Python. It generates and manages small wrapper scripts that import from an
installed package and then export the interface expected by IDA Pro. For
example, plugin wrappers use the following template:

```python
import pkg_resources

def PLUGIN_ENTRY():
    ep = pkg_resources.load_entry_point(%(dist)r, %(group)r, %(name)r)
    return ep()
```

## Packaging

In order for idaenv to know where plugins are located inside of a package, they
have to be called out in `setup.py` using "entry points". For example, the
declaration for keypatch might look like:

```python
from setuptools import setup, find_packages


setup(name='keypatch',
      version="0.0",
      packages=find_packages(exclude=['ez_setup']),
      install_requires=[
          "keystone-engine"
      ],
      zip_safe=False,
      entry_points={
          "idapython_plugins": [
              "keypatch=keypatch:Keypatch_Plugin_t",
          ]
      })
```

Three different entry point groups are supported:

- `idapython_plugins`
- `idapython_procs`
- `idapython_loaders`
