.. contents::

.. Note to recipe author!
   ---------------------
   Update the following URLs to point to your:
   
   - code repository
   - bug tracker 
   - questions/comments feedback mail 
   (do not set a real mail, to avoid spams)

   Or remove it if not used.
   
Motivation
==================

We're deploying multiple test/staging servers using django and it's a pain to have lots of apache confs lying around which are almost exactly the same.

The only things that are different are the IP addresses, server names and, if using buildout (which is kind of the whole point of this), the python path and packages.  So a valid approach would be to put your apache conf somewhere under your buildout directory and have it built at the same time as you buildout your project.

There's already a nice recipe that does this `z3c.recipe.filetemplate <http://pypi.python.org/pypi/z3c.recipe.filetemplate>`_. So this recipe is subclassing from that and using zc.recipe.egg to add a ``python_path`` value to the options. This is done by setting the eggs and extra-paths values in the recipe.

This is just an internal project so there's no bug tracker, mailing list etc. I hope that someone finds it useful, please contact me it you do or wish to make changes to it.



