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

If you're using IDA 7.3 or earlier, initialize a Python 2 virtual environment
and activate it:

    $ virtualenv -p python2 ida
    $ ./ida/bin/activate

If you're using IDA 7.4 or later, it is recommended to use
[venv](https://docs.python.org/3/library/venv.html), which is included in the
standard library.

    $ python3 -m venv ida
    $ ./ida/bin/activate

It is still possible to use virtualenv with Python 3, however you will encounter
an exception when starting IDA 7.4 due to a longstanding
[issue](https://github.com/pypa/virtualenv/issues/737) in virtualenv.

Once virtual environment is activated, install idaenv:

    $ pip install idaenv

Update the IDAUSR environment variable to include the idaenv plugin directory:

    $ export IDAUSR=$HOME/.idapro:$( idaenv prefix )

Install some idaenv compatible extensions using setup.py or pip. Then use the
idaenv "update" command:

    $ pip install ...
    $ idaenv update
    Writing wrapper to '/home/me/.virtualenvs/cpy2/ida/plugins/keypatch_keypatch_f265c7.py'...
    Writing wrapper to '/home/me/.virtualenvs/cpy2/ida/plugins/uemu_uemu_791c39.py'...
      Updated:
        - keypatch.keypatch
        - uemu.uemu

    ... TODO include output ...

To see what plugins are installed, use the "ls" or "status" command.

    $ idaenv ls
    Plugins:
      Active:
        - keypatch.keypatch
        - uemu.uemu

## Mechanism

idaenv takes inspiration from the established `console_scripts` mechanism in
Python. It generates and manages small wrapper scripts that import from an
installed package and then export the interface expected by IDA Pro. For
example, plugin wrappers use the following template:

```python
from %(module)s import %(attr)s

def PLUGIN_ENTRY():
    return %(attr)s()
```

## Packaging

In order for idaenv to know where plugins are located inside of a package, they
have to be called out in `setup.py` using "entry points". For example, the
declaration for a traditional plugin that consists of just a single file (like
the excellent keypatch) might look like:

```python
from setuptools import setup


setup(name='keypatch',
      version="0.0",
      py_modules=["keypatch"],
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

The structure of the entry points dictionary is described in detail by the
[setuptools documentation](https://setuptools.readthedocs.io/en/latest/setuptools.html#dynamic-discovery-of-services-and-plugins).
The general structure is:

```python
{
    "entry_point_group": [
        "plugin_name=module.submodule:PluginClass.plugin_method
    ]
}
```

idaenv supports the following entry point groups:

- `idapython_plugins`
- `idapython_procs`
- `idapython_loaders`
