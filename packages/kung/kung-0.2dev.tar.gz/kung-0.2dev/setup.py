from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='kung',
      version=version,
      description="more with less",
      long_description="""\
less in the browser with syntax highlighting and other nifty stuff features.""",
      classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Topic :: Utilities"
      ],
      keywords='less more read file',
      author='Travis Jeffery',
      author_email='travisjeffery@gmail.com',
      url='http://github.com/travisjeffery/kung',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          "pygments",
          "argparse"
      ],
      entry_points="""
        [console_scripts]
        kung = kung.kung:main
      """,
      )
