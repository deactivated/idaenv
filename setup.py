import sys
from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()


# Install a backport of importlib-metadata when available.
requires = []
py_major, py_minor = sys.version_info[:2]
if (py_major == 2 and py_minor == 7) or (py_major == 3 and 5 <= py_minor <= 8):
    requires.append("importlib-metadata>=2.1.3")


setup(
    name="idaenv",
    version="0.5.0",
    description="IDA Pro plugin manager.",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["ez_setup"]),
    zip_safe=False,
    license="MIT",
    install_requires=requires,
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    entry_points={
        "console_scripts": [
            "idaenv=idaenv.command_line:main",
        ]
    },
)
