import os
import sys
from distutils.core import setup

setup(
    name="metamake",
    packages=['metamake'],
    version="1.1.5",
    license="BSD",
    author="Matt Pizzimenti",
    author_email="mjpizz+metamake@gmail.com",
    url="http://pypi.python.org/pypi/metamake/",
    description="Metamake is a dead-simple task-based automation tool written in Python.",
    long_description=open(os.path.join(os.path.dirname(__file__), "README.txt")).read(),
    entry_points='''
[console_scripts]
mm = metamake:metamake_bin
metamake = metamake:metamake_bin
''',
    zip_safe = False,
    )
