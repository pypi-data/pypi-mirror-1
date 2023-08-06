Introduction
============

Stepper is a very good Zope products. This egg is a first effort to bring some
plone relative steps availables to developpers and site administrator.

How many of you have suffer from having proxy error while trying to reindex
a new index in a catalog ?

Well now it's possible to:
- Change all members's passwords to a unique password
- Change all members's emails to a unique email
- Apply a profile without busy a zope's current thread on a production server
- Activate/Deactivate a PAS plugin: deactivate login from your website before activate a migration

So if you have any idea for any reusable migration or feature for developpers, let me know.

How to use
==========

Like Stepper, for example:

 $ ./bin/instance run parts/productdistros/Stepper/run.py -C collective.steps.config /plone dev

cf example.py to know what the dev chain do

TODO
====
- GenerateUsers into member.py to create members. convienent for stress testing purpose
- GenerateContent into content.py ""

