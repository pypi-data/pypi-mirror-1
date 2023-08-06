Installation
=============

Unfortunatly, installing pebl is not a one-stop process although it should take no longer than a few minutes. If you experience any problems, please contact me at abhikshah@gmail.com.


Install Python 2.5
-------------------

Check what version of Python you have with::


    python --version


You can download Python 2.5 from http://python.org/download

Install easy_install
--------------------

easy_install lets you install python packages and their requirements in one easy step. Unfortunately, easy_install is not distributed with python and needs to be installed separately.

1. Download ez_setup.py from http://peak.telecommunity.com/dist/ez_setup.py
2. Run :command:`python ez_setup.py` to install easy_install

Install Pebl
------------

Running the following commands will install pebl and all required dependencies::

    easy_install numpy
    easy_install pebl


Installing optional dependencies
---------------------------------

Certain features of pebl require additional dependencies. You only need to install these if you need the optional features.

For creating HTML reports of Pebl results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pebl uses Graphviz to visualize networks and matplotlib for plotting. If using Pebl on a cluster, these don't need to be installed on the worker nodes.

1. Install Graphviz from http://www.graphviz.org/Download.php
2. Install matplotlib from http://matplotlib.sourceforge.net/installing.html


For the XGrid Task Controller
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pebl use the PyXG package to access the XGrid controller. Unfortunately, the version of PyXG installable via easy_install has a bug. You need to install from svn::


    svn co http://pyxg.scipy.org/svn/pyxg/trunk PyXG
    cd PyXG
    python setup.py install


For the IPython1 Task Controller
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You will need to install both IPython and IPython1.  IPython1 is in active development and pebl requires a specific version. Once, IPython1 is oficially released, we will use that package::


    easy_install ipython

    svn co -r 2815 http://ipython.scipy.org/svn/ipython/ipython1/trunk ipython1-2815
    cd ipython1-2815
    sudo python setup.py install



For the EC2 Task Controller
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Before you can use Amazon's EC2 platform, you need to register with Amazon and create the required authentication credentials.  Consult the `Getting Started Guide <http://docs.amazonwebservices.com/AWSEC2/2008-02-01/GettingStartedGuide/>`_ at Amazon for further information.

Pebl uses the boto package to connect to EC2. Install it with::


    easy_install boto


Also see the instructions above for installing dependencies for the IPython1
Task Controller (which is required by the EC2 Task Controller).


For developing Pebl
^^^^^^^^^^^^^^^^^^^

Pebl developers will also need nose for testing and sphinx for generating html documentation::


    easy_install nose
    easy_install sphinx



