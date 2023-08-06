==============================
pyCaBio - Python API for caBIO
==============================

The Cancer Bioinformatics Infrastructure Objects (caBIO) model and 
architecture is a synthesis of software, vocabulary, and metadata 
models for cancer research. The pyCaBio project provides a Pythonic
style API to caBIO via web services. 

For more information about caBIO see http://cabioapi.nci.nih.gov/


Prerequisites
-------------
Python 2.5

Latest setuptools
  To install, download and execute the following script:
  http://peak.telecommunity.com/dist/ez_setup.py

The installation uses setuptools to automatically install any 
other dependencies.


Installation
------------
System-wide install:

    python setup.py install

Single user install:

    python setup.py install --home=~

After installation the test suite may be run:
     
    python setup.py test

There is also example code available under the examples/ directory.


Mailing List
------------
https://list.nih.gov/archives/cabio_users.html


Known Issues
------------
* Sending arrays (collections) is not possible due to a conflict between AXIS 
  and ZSI. See tests/defects.py for an example.
  

Change History
--------------
0.1.0 - 05/13/2008
Initial alpha release.

0.2.0 - 06/27/2008
Regenerated with pyCaCORE 0.1.0.
Moved cabio under cabig package.

0.3.0 - 08/18/2008
Upgraded to use pyCaCORE 0.2.0 in order to fix GF16157.

0.4.0 - 01/04/2009
Upgraded to use caBIO 4.2


