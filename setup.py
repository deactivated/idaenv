from setuptools import setup, find_packages


setup(name='idaenv',
      version="0.1",
      description="IDA Pro plugin manager.",
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
