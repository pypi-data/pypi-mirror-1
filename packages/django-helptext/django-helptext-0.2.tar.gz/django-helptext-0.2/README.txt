======================
django-helptext README
======================

This is a simple django application that makes it possible to edit the
help text associated with django models in the admin, rather than in
source code, so that it can be edited by a site's managing producer
rather than by its programmer.

Usage
=====

1. add ``"helptext"`` to your project's ``INSTALLED_APPS``.
2. ``syncdb``.
3. somewhere in your code, register the models you are interested 
   in managing with ``helptext`` with ``helptext.register_model()``.
4. Edit the FieldHelp instances in the admin.  

Issues
======

None so far.


Todo
====

* customize the admin a tad.




