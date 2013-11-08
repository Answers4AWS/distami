DistAMI
=======

.. image:: https://travis-ci.org/Answers4AWS/distami.png?branch=master
   :target: https://travis-ci.org/Answers4AWS/distami
   :alt: Build Status

Distributes an Amazon Machine Image (AMI) by making it public in multiple regions

Usage
-----

::

    usage: distami [-h] [--region REGION] [--to REGIONS] [--non-public] [-p] [-v]
                   [--version]
                   AMI_ID

    Distributes an AMI by copying it to one, many, or all AWS regions, and by
    optionally making the AMIs and Snapshots public.

    positional arguments:
      AMI_ID           the source AMI ID to distribute. E.g. ami-1234abcd

    optional arguments:
      -h, --help       show this help message and exit
      --region REGION  the region the AMI is in (default is current region of EC2
                       instance this is running on). E.g. us-east-1
      --to REGIONS     comma-separated list of regions to copy the AMI to. The
                       default is all regions. E.g. us-east-1,us-west-1,us-west-2
      --non-public     Copies the AMIs to other regions, but does not make the
                       AMIs or snapshots public. Bad karma, but good for AMIs that
                       need to be private/internal only
      -p, --parallel   Perform each copy to another region in parallel. The
                       default is in serial which can take a long time
      -v, --verbose    enable verbose output (-vvv for more)
      --version        display version number and exit


Examples
--------

Copy an AMI to all regions in parallel from an EC2 instance such as
Aminator:

::

    distami -p ami-abcd1234

Copy AMI in ``us-east-1`` to ``us-west-1``

::

    distribute --region us-east-1 ami-abcd1234 --to us-west-1

Copy an AMI in ``eu-west-1`` to ``us-west-1`` and ``us-west-2``, but do not make the AMI or its copies public

::

    distribute --region eu-west-1 ami-abcd1234 --to us-west-1,us-west-2 --non-public
    

Installation
------------

You can install DistAMI using the usual PyPI channels. Example:

::

    sudo pip install distami
    
You can find the package details here: https://pypi.python.org/pypi/distami

Alternatively, if you prefer to install from source:

::

    git clone git@github.com:Answers4AWS/distami.git
    cd distami
    python setup.py install


Source Code
-----------

The Python source code for DistAMI is available on GitHub:

https://github.com/Answers4AWS/distami


About Answers for AWS
---------------------

This code was written by `Peter
Sankauskas <https://twitter.com/pas256>`__, founder of `Answers for
AWS <http://answersforaws.com/>`__ - a company focused on
helping business get the most out of AWS. If you are looking for help
with AWS, please `contact us <http://answersforaws.com/contact/>`__.


LICENSE
-------

Copyright 2013 Answers for AWS LLC

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0 Unless required by applicable
law or agreed to in writing, software distributed under the License is
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied. See the License for the specific
language governing permissions and limitations under the License.
