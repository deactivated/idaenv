from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()


setup(name='idaenv',
      version="0.2.0",
      description="IDA Pro plugin manager.",
      long_description=readme,
      packages=find_packages(exclude=['ez_setup']),
      zip_safe=False,
      license="MIT",
      classifiers=[
          "Natural Language :: English",
          "Programming Language :: Python"
      ],
      entry_points={
          "console_scripts": [
              "idaenv=idaenv.command_line:main",
          ]
      })
