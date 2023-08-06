import commands 
import os
import time
from distutils.core import setup

#Determine & save the revision number for the ETC
warning=""
vfname=os.path.join('.','SVN_VERSION')
try:
    # Always try to determine the version using svnversion
    warning=""
    stat,revset=commands.getstatusoutput('svnversion .')
    if stat != 0:
        raise ValueError("cannot extract svnversion information")
    if revset.find('exported') >= 0 :
        raise ValueError("this copy was exported - no version information")
    if revset.find("M") >= 0 :
        warning="this copy is modified"
    if revset.find(":") >= 0 :
        warning="this copy is mixed"

    revset = revset.replace("M","")

    f=open(vfname,'w')
    f.write(revset)
    f.close()

except ValueError:
    print "couldn't run svnversion"
    #If we can't generate it, then see if the version file already
    #exists from when the source distribution was being assembled. 
    try :
        f=open(vfname,"r")
        revset=f.readline()
        f.close()
    except IOError:
        warning="cannot extract svnversion information"
        revset='unavailable'

VERSION = "1.0b."+revset

print warning
print "assuming that the version is " + VERSION

setup(name="CROC",
    version=VERSION,
    description="A package for calculating ROC curves and Concentrated ROC (CROC) curves.",
    long_description="""================
The CROC Package
================

This pure-python package is designed to be a standard implementation of performance curves 
and metrics for use either in python scripts or through a simple commandline interface. 

With this package, one can easily:

#. Compute the coordinates of both Accumulation Curves and ROC curves.
#. Handle ties appropriately using several methods.
#. Compute the BEDROC metric.
#. Vertically add and average the performance curves of several cross-validation folds.
#. Focus on the early part of the ROC curve by using several soon to be published x-axis transforms. 

Please email the author if you discover any bugs. Currently, this package is officially in BETA
status. Full documentation can be found at http://www.ics.uci.edu/~sswamida/CROC

""",
    requires=["sympy"],
    author="S. Joshua Swamidass",
    url="http://www.ics.uci.edu/~sswamida/CROC",
    author_email="swamidass@gmail.com",
    classifiers=["Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "License :: Free for non-commercial use",
        "Natural Language :: English",
        "Environment :: Console",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Scientific/Engineering :: Visualization"],
    scripts=['scripts/croc-average', 'scripts/croc-bedroc', 'scripts/croc-area', 'scripts/croc-curve'],
    packages=['croc']
)
