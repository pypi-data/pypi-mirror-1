##############
Testing Modulo
##############

Installation
############

Set up a Plone instance will iw.memberreplace and required
components. Please read the main `README.txt` about this.

Running the tests
#################

Old style installation::

  $ cd $INSTANCE_HOME
  $ bin/zopectl test --nowarning -s iw.memberreplace

zc.buildout based installation::

  $ cd $BUILDOUT_HOME
  $ bin/instance test --nowarning -s iw.memberreplace
