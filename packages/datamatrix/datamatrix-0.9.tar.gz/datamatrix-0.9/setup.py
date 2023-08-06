#!/usr/bin/env python

from distutils.core import setup
import sys
import os
import glob

#FIXME: Ugly hack, but as I don't use Windows there's no way I can determine
# the right install directory

docdir = os.path.join(sys.prefix,"share/doc/datamatrix") \
    if "bdist_wininst" not in sys.argv else "\Data\datamatrix"

# Grab the documentation files by globbing

pdf = glob.glob("doc/*.pdf")
#pdf.remove("doc/html")
#pdf.remove("doc/_sources")
html_sources = glob.glob("doc/html/*")
html_sources.remove("doc/html/_static")
html_sources.remove("doc/html/_sources")
data_files = [
            (docdir,pdf),
            (os.path.join(docdir,"html"),html_sources),
            (os.path.join(docdir,"html/_static"),glob.glob("doc/html/_static/*")),
            (os.path.join(docdir,"html/_sources"),glob.glob("doc/html/_sources/*")),
            (os.path.join(docdir,"_sources"), glob.glob("doc/_sources/*"))
            ]

description = """A Pythonic implementation of R's ``data.frame`` structure. This
module allows access to comma- or other delimiter separated files as if they
were tables, using a dictionary-like syntax.  ``DataMatrix`` objects can be
manipulated, rows and columns added and removed, or even transposed."""

setup(name="datamatrix",
	version="0.9",
	description=description,
	author="Luca Beltrame",
	author_email="einar@heavensinferno.net",
	packages=["datamatrix"],
    package_dir={"datamatrix":"./datamatrix"},
    data_files=data_files,
	classifiers=['License :: OSI Approved :: GNU General Public License (GPL)',
		'Operating System :: OS Independent',
		'Topic :: Text Processing'],
    url="http://www.dennogumi.org/projects/datamatrix",
    provides=["DataMatrix (0.8)"]
	)

