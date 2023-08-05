from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

# Notes to self:
# python setup.py sdist --formats=zip
# To create the zip file

# python setup.py bdist_egg
# To create the egg file

# python setup.py register
# to register with PyPI

# create an egg and upload it 
# setup.py register bdist_egg upload 

# Test install
# setup.py develop

setup(name="wxOptParse",
    version="0.1.6",
    description="wxOptParse: run the command line options from a dialog box.",
    long_description="""\
``wxOptParse`` is a Python program that brings up a graphical representation of the options 
that another python program has for the command line, via the optparse module.

What this means is that if if you have a Python program that uses ``optparse``, 
which is a standard python
module used to parse the command line, you can click on checkboxes, 
edit boxes, combo boxes, etc. instead of passing this information on the command line.
""",
    author="Scott Kirkwood",
    author_email="scottakirkwood@gmail.com",
    url="http://wxoptparse.berlios.de/",
    download_url='http://download.berlios.de/wxoptparse/wxOptParse-0.1.6.zip',
    packages=find_packages(exclude='tests'),
    scripts=["scripts/wxoptparse", 'scripts/wxFind'],
    keywords=['wxOptParse', 'optparse', 'python', 'wxPython'],
    license='GNU GPL',
    zip_safe=True,
    platforms=['POSIX', 'Windows', 'MacOS X'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
    ],
    #    package_data={'': '*.xml'},
    install_requires=(
        'elementtree >= 1.2',
        #'wxPython'# Doesn't work on my machine,
    ), 
    )
