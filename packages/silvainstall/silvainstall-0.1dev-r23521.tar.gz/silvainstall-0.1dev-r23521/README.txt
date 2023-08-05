silvainstall
============

Easily install Silva >= 2.0.

To install the latest **experimental** release of Silva using
`silvainstall`, do:

  easy_install silvainstall # you might want to do this as root

  MKZO=~/lib/Zope-2.10/bin/mkzopeinstance.py
  INSTANCE_HOME=~/mysilva2.0

  silvainstall $INSTANCE_HOME -m $MKZO

That's it!  Just make sure that you set ``MKZO`` and ``INSTANCE_HOME``
according to where your ``mkzopeinstance.py`` script is and where you
want to create your instance respectively.
