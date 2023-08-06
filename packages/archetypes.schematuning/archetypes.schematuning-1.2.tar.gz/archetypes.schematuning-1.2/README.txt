This package speeds up Archetypes Schemas and is a patch for 
Products.Archetypes_.

.. _Products.Archetypes: http://pypi.python.org/pypi/Products.Archetypes

It uses plone.memoize to cache Archetypes Schemas instead of factoring and 
modifying them every time they're accessed. Factoring a schema is usually fast
but in an average Plone Site, the ATDocument's schema, for example, is accessed 
about 80 times per request. So caching it still makes sense, even if a single 
call is fast. With schematuning, ATDocument in PythonProfiler (which linearly slows
down whole Python) came down from 1.518s down to 0.084s for Schema calls. This 
makes it roughly 18 times faster.  

History
=======

Roché Compaan and Hedley Roos found while working on one of their projects
several performance issues. One of it was the often repeated BaseObject.Schema()
method. Read about it on the Mailing-List_.

.. _Mailing-List: http://plone.org/support/forums/core#nabble-td1303544

License
=======

GNU General Public License, GPL

Authors
=======

* Hedley Roos (tests, better cache-key, invalidation)

* Jens Klein (initial code, maintainer) <dev@bluedynamics.com> 
   
