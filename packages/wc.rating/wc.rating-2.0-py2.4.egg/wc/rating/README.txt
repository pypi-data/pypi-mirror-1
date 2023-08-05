==============
Rating objects
==============

The rating system allows users to rate objects on a continuous scale
(a discrete scale can be enforced by a view).  We distinguish

- *ratable* objects which have to annotatable and implement
  ``IRatable` on one hand

- and the ``IRating`` adapter for ratable objects which the rating of
  the latter on the other hand.

Consider a simple object, e.g. a recipe:

  >>> class Recipe(object):
  ...     pass
  >>> hamburgers = Recipe()

In order to mark it ratable, it also needs to annotatable, for example
attribute-annotatable:

  >>> from zope.annotation.interfaces import IAttributeAnnotatable
  >>> from wc.rating.interfaces import IRatable
  >>> from zope.interface import alsoProvides
  >>> alsoProvides(hamburgers, IAttributeAnnotatable, IRatable)

Now we can rate the object using the ``IRating`` adapter:

  >>> from wc.rating.interfaces import IRating
  >>> rating = IRating(hamburgers)
  >>> rating.rate(1)   # I don't like hamburgers
  >>> rating.rate(9)   # I like hamburgers

The adapter also tells about the average rating and number of ratings
that have been issued yet:

  >>> rating.averageRating
  5.0
  >>> rating.numberOfRatings
  2
