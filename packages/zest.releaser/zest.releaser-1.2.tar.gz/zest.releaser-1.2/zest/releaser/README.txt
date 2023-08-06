Zest release scripts
====================

Summary: package releasing made easy.

``easy_install`` this in a ``virtualenv`` or globally.  It gives you
some commands to help in releasing python packages.  They must be run
in a subversion checkout.  These are the commands:

- prerelease: ask the user for a version number (give a sane default),
  update the setup.py or version.txt and the HISTORY.txt with this and
  offer to commit those changes to subversion.

- release: copy the the trunk or branch of the current checkout and
  create a subversion tag of it.  Offer to register and upload a
  source dist of this package to PyPI (Python Package Index).  Note:
  if the package has not been registered yet, we will not do that for
  you.  You must register the package manually (``python setup.py
  register``) so this remains a conscious decision.  The main reason
  is that you want to avoid having to say: "Oops, I uploaded our
  client code to the internet; and this is the initial version with
  the plaintext root passwords."
  
- postrelease: ask the user for a version number (give a sane
  default), add a development marker to it, update the setup.py or
  version.txt and the HISTORY.txt with this and offer to commit those
  changes to subversion.

- fullrelease: all of the above in order.
