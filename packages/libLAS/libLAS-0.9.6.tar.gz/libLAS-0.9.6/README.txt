==============================================================================
libLAS - LAS 1.0/1.1 ASPRS LiDAR data translation
==============================================================================

libLAS is a BSD library for reading and writing ASPRS LAS version 1.0 and 1.1 
data.  LAS-formatted data is heavily used in `LiDAR`_ processing operations, and 
the LAS format is a sequential binary format used to store data from sensors 
and as intermediate processing storage by some applications.  

libLAS is available under the terms of the `BSD License`_. It builds on work 
by `Martin Isenburg and Jonathan Shewchuk`_ of the  University of North 
Carolina in their `LAStools`_ project.  The base C++ library that reads 
and writes LAS 1.0/1.1 data was replaced with new development, and Martin's 
tools were ported to use this new code.

libLAS' initial development was supported by the `IGSB`_ of the Iowa DNR 
for use in its state-wide `LIDAR`_ project.

------------------------------------------------------------------------------
LAS Format Specifications
------------------------------------------------------------------------------

The LAS Format Standard is maintained by `ASPRS Standards Committee`_. LAS 
format standard documents are available in PDF format:

* `LAS 2.0 Format Standard`_ (2007-08-17) - *Proposed*
* `LAS 1.2 Format Standard`_ (2008-05-02) - *Proposed*
* `LAS 1.1 Format Standard`_ (2005-05-07)
* `LAS 1.0 Format Standard`_ (2003-05-09)

------------------------------------------------------------------------------
Authors
------------------------------------------------------------------------------

The libLAS development team are:

 * `Howard Butler`_
 * `Mateusz Loskot`_
 * `Phil Vachon`_

Special thanks to `Martin Isenburg and Jonathan Shewchuk`_ for their
`LAStools`_ pioneering implementation of the ASPRS LAS standard that made 
development of the libLAS library possible.



.. _`LIDAR`: http://en.wikipedia.org/wiki/LIDAR
.. _`IGSB`: http://www.igsb.uiowa.edu/
.. _`Martin Isenburg`: http://www.cs.unc.edu/~isenburg/
.. _`LAStools`: http://www.cs.unc.edu/~isenburg/lastools/
.. _`Martin Isenburg and Jonathan Shewchuk`: http://www.cs.unc.edu/~isenburg/lastools/
.. _`LAS Format`: http://www.lasformat.org/
.. _`LAS 2.0 Format Standard`: http://liblas.org/raw-attachment/wiki/WikiStart/incitsl1_las_format_v20.pdf
.. _`LAS 1.2 Format Standard`: http://liblas.org/raw-attachment/wiki/WikiStart/LAS1_2_Final.pdf
.. _`LAS 1.1 Format Standard`: http://liblas.org/raw-attachment/wiki/WikiStart/asprs_las_format_v11.pdf
.. _`LAS 1.0 Format Standard`: http://liblas.org/raw-attachment/wiki/WikiStart/asprs_las_format_v10.pdf
.. _`ASPRS Standards Committee`: http://www.asprs.org/society/divisions/ppd/standards/standards_comm.htm
.. _`Howard Butler`: http://hobu.biz
.. _`Mateusz Loskot`: http://mateusz.loskot.net
.. _`Phil Vachon`: http://www.geoscan.info
.. _`BSD License`: http://www.opensource.org/licenses/bsd-license.php