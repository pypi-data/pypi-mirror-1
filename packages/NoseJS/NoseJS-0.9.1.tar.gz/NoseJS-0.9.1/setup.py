from setuptools import setup, find_packages
import re
version = None
for line in open("./nosejs/__init__.py"):
    m = re.search("__version__\s+=\s+(.*)", line)
    if m:
        version = m.group(1).strip()[1:-1] # quotes
        break
assert version

setup(
    name='NoseJS',
    version=version,
    description="A Nose plugin to run JavaScript tests using Rhino in a Java subprocess.",
    long_description=open("README.txt",'r').read(),
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    install_requires=['nose'],
    entry_points="""
    [nose.plugins.0.10]
    nosejs = nosejs:NoseJS
    """
) 
