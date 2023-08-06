Simple python package for Plone, whiches makes the gre(a)ybox available for images

INSTALL

Egg:
note: not yet in cheeseShop
1. svn co https://svn.plone.org/svn/collective/collective.greybox/tags/0.1 /your/local/path
2. run setup.py
3. create ftw.greybox-configure.zcml in your $INSTANCE/etc/packages-includes
    content:

        <configure>

        <include package="collective.greybox" />

        </configure>


4. Restart your Instance and choose greybox profile while creating a new Plone Site.
   Or install greybox with quickinstaller

Without easy_install:
1: go to your $INSTANCE/lib/python
$ mkdir collective
$ cd collective
$ svn co https://svn.plone.org/svn/collective/collective.greybox/tags/0.1/collective/greybox/ greybox

2. repeat step 3 and 4 from egg installation


TESTED WITH

Plone 3.0.3 / 3.0.4 / 3.0.5
Zope 2.10.5


CONTACT

info (a) 4teamwork.ch
m.leimguber (a) 4teamwork.ch
