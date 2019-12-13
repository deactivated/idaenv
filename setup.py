from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()


setup(name='idaenv',
      version="0.4.0",
      description="IDA Pro plugin manager.",
      long_description=readme,
      long_description_content_type="text/markdown",
      packages=find_packages(exclude=['ez_setup']),
      zip_safe=False,
      license="MIT",
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
      })
