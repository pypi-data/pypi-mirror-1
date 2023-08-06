met.py
Multinomial Exact Tests

met.py is a Python module that allows you to define a pair of
multinomial distributions (conceptually 'control' and 'test'
distributions) and then compute one- and two-sided p values to test
whether the 'test' distribution is equivalent to the 'control'
distribution. The likelihood of all possible 'control' distributions can
be evaluated and the distribution of p values can be expressed in terms
of the likelihood of the observed 'control' distribution.


Contents
======================

  Installation
  Purpose
  Notes
  Copyright and License


Installation
======================

You can install the module either manually or using Python's installation tools.


Manual Installation
--------------------

Because the met module consists of a single Python script, you can
simply extract the met.py script from the zipped package file, and put
this module code wherever you want.


Automated Installation
-----------------------

The automated installation process uses Python's standard setup tool to
place the program in the standard location for third-party modules.
Follow these steps to perform an automated installation:

1. Unzip the package file.  The file can be unzipped in a temporary location,
   such as C:\Temp.  The contents of the package will be placed in a
   subdirectory named for the program and release version.
2. Open a command window in the subdirectory containing the unzipped files and
   type the following command at the prompt:

		python setup.py install

If you want to install to a non-standard location, instructions for a
customized installation can be found at
http://docs.python.org/install/index.html#inst-alt-install.


Purpose
======================

Perform exact tests of a (site or test) distribution of multinomial
count data against a distribution of equivalent ordered multinomial
count data from another (reference or control) data set. Both two-sided
and one-sided tests can be performed. One-sided tests require that
categories be ordered.

A practical example of relevant data (and the motivation for writing
this module) arises from the use of Sediment Profile Imaging to evaluate
the benthic macroinvertebrate community at site and reference locations,
and characterization of each sample in terms of the benthic successional
stage presen. These categorical data are ordered, and so a one-sided
exact multinomial test can be applied.


Notes
======================

Exact Tests
--------------------

Whereas most statistical tests compute p values based on the parameters
of a continuous distribution, and those p value are therefore
estimates, calculation of exact p values is possible when every
possible rearrangement of the data can be enumerated. Each 
rearrangement of the data must have a specific probability of
occurrence, which is computed based on a theoretical or reference
distribution of probabilities.  Summing of the probabilities of
occurrence for the observed data and for all more extreme arrangments of
the data produces an exact p value--hence, the result of an exact test.

For two-sided tests, "more extreme" means that the probability of an alternative
arrangement of site data has a lower probability than the observed arrangement.

For one-sided tests, "more extreme" means a data arrangement in which
one or more observations is shifted from a 'better' category to a
'worse' one. Therefore, to carry out one-sided exact tests, the
categories must be ordered from 'better' to 'worse'.

Issues
--------------------

When reference area sample sizes are small relative to site sample
sizes, the accuracy of the probabilities calculated from the reference
area samples may be questionable.  In particular, some categories that
are represented in the site data may not be represented in the reference
data, and so have zero reference aera probabilities.  Whenever a
reference area probability for any category is zero, the probability of
any arrangement of site data with a non-zero count in that category is
also zero.  Small reference area sample sizes may therefore lead to
underestimation of true reference probabilities for some categories, and
consequently to an underestimation of p values in the exact tests.

The met module contains two features to help evaluate and account for
uncertainties related to relatively small reference area sample sizes. 
The first of these allows assignment of small non-zero probabilities to
categories with no reference area observations, and the second allows
evaluation of the likelihood of different p values based on possible
reference area probabilities that could have led to the observed
reference data.


Copyright and License
======================

Copyright (c) 2009, R.Dreas Nielsen

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details. The GNU General Public License is available at
http://www.gnu.org/licenses/.
