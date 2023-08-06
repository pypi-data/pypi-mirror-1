<<<<<<< .mine
===============
Content Ratings
===============

This is a simple python product driven by Zope 3, which is intended to make it
easy to let users (optionally including anonymous) or editors rate content.
It provides a set of interfaces, adapters and views to allow the application
of ratings to any IAnnotatable object.

Requirements:

Zope 2.8.5+ or 2.9.1+
Five 1.2.1+ or 1.3.1+

Should work with Zope 3.1 or 3.2, but the user rating views need to be fixed
to get authentication credentials.


Using it with your Product
==========================

First install it somewhere in your *python path* (not in your Products
directory), $INSTANCE_HOME/lib/python may be a good place to start using it
with zope.

You'll need to make sure the zcml for this package is loaded, so make sure 
that the configure.zcml for your product contains::

 <include package="contentratings" />

If you want to allow some content to be rated you must mark it as both
*ratable* and *annotatable*.  The standard way to do this is to add the
following to your product's configure.zcml::

 <content class=".content.MyContentClass">
   <implements
       interface="contentratings.interfaces.IEditorRatable
      			 zope.annotation.interfaces.IAttributeAnnotatable"
       />
 </content>

If you want the content to be UserRatable instead of or in addition to being
Editor ratable you just add ``contentratings.interfaces.IUserRatable`` to the
interface declaration.

To determine who gets to rate content and view ratings there are a few
permissions listed below (with their Zope2 equivalents in parentheses)::

 contentratings.EditorRate (Content Ratings: Editor Rate)
 contentratings.ViewEditorialRating (Content Ratings: View Editorial Rating)
 contentratings.UserRate (Content Ratings: User Rate)
 contentratings.ViewUserRating (Content Ratings: View User Rating)

For example to disallow anonymous users from rate objects, just remove the
``contentratings.UserRate`` permission from Anonymous in the ZMI.  By default
Anonymous is granted UserRate and all the viewing Permissions, and
``Reviewer`` and ``Manager`` are granted the EditorRate permission.

You will also need to make the ratable content object ``five:traversable`` if
you are using Zope 2 with Five, this is done by adding the following to your
zcml::

 <five:traversable class=".content.MyContentClass" />

Make sure to include the five namspace
(``xmlns:five="http://namespaces.zope.org/five"``) in your configure
directive.


Using the Views
===============

To include the views in your page layout just include the following snippet in
your template::

 <tal:editorial-view tal:on-error="nothing"
                     tal:replace="structure context/@@editorial_rating_view" />
 <tal:editorial-rate tal:on-error="nothing"
                     tal:replace="structure context/@@editorial_rating_set" />

 <tal:user-view tal:on-error="nothing"
                tal:replace="structure context/@@user_rating_view" />
 <tal:user-rate tal:on-error="nothing"
                tal:replace="structure context/@@user_rating_set" />

Including this at the end of Plone's document_byline.pt, for example, would be
appropriate.  It will only display ratings when the current content is ratable
and the user has permission to view them.  If the user has permission to edit
the rating then the edit mode will be shown below the current rating for User
ratings, or shown instead to the current rating for Editorial ratings.

Additionally, these views rely on some images provided as resources being
available at the root of the site, which may be either the zope root, or the
root of a virtual hosted portal.  In order to make these resources available
your root object must be made ``five:traversable`` as well.  To make the zope
root traversable add the following::

 <five:traversable class="OFS.Application.Application" />

To make a virtual hosted CMF or Plone portal traversable use the following:::

 <five:traversable class="Products.CMFCore.PortalObject.PortalObjectBase" />

As above, ensure that you have the Fiveconfiguration namespace available.


Working With the Plone Catalog
==============================

There are some special methods in the plone_extras sub-package to make it easy
to store ratings in plone's portal_catalog.  To enable this feature, just add
the following to your product's ``__init__.py``::

 # Add IndexableObjectWrappers for ratings:
 from contentratings.plone_extras import catalog_stuff

Which registers the adapters as indexable attributes, then add the indexes
and/or metadata to the catalog using either GenericSetup, or adding the
following to your ``Extensions/Install.py`` ``install()`` method::

 from contentratings.plone_extras.catalog_stuff import addRatingIndexesToCatalog
 from contentratings.plone_extras.catalog_stuff import addRatingMetadataToCatalog
 addRatingIndexesToCatalog(self)
 addRatingMetadataToCatalog(self)

This will add an ``user_rating_tuple`` and ``editorial_rating`` columns and
indexes to your portal_catalog.  The ``user_rating_tuple`` stores a tuple
containing the average rating and the number of ratings, for convenient
sorting and presentation.

You will also need to make sure that the catalog_stuff module is imported
whenever your product loads, so that the index methods are registered with
the catalog.  Do this by placing the following into your Product's __init__.py
or similar::

  from contentratings.plone_extras import catalog_stuff


Multiple Ratings on a Single Object
===================================

If you want to allow multiple types of ratings (so people can rate e.g. value,
quality, clarity) on a single object you can provide multiple adapters for the
object.  First you need a custom adapter class::

 from contentratings.rating import UserRating

 class MyCustomRating(UserRating):
     key='myproduct.customrating'
     scale=10

Key is required and must be unique as it's the key for the annotation in which
the rating will be stored.  Scale is optional and merely provides a ui hint
for the possible range of values.

You must then register this adapter for your class via zcml, because it is
providing the same interface as an existing adapter, you need to make it a
named adapter:

  <adapter
      for=".interfaces.IUserRatable"
      provides=".interfaces.IUserRating"
      factory="MyProduct.MyCustomRating"
      trusted="true"
      name="my_rating"
      />

For the moment you will need to provide a custom view for this rating which
looks it up by name, using ``getAdapter(obj, IUserRating, "my_rating")``.
Eventually a view may be provided by default which iterates through all
IUserRating adapters and presents them.


Using The Adapters
==================

The rating system allows users to rate objects on a continuous scale
(a discrete scale can be enforced by a view).  We distinguish
*ratable* objects which have to annotatable and implement ``IEditorRatable``
and/or ``IUserRatable`` and the ``IUserRating`` and ``IEditorialRating``
adapters for ratable objects which actually set and read the ratings.

Consider a simple object, i.e. a SampleContainer::

  >>> from zope.app.container.sample import SampleContainer
  >>> my_container = SampleContainer()

In order to mark it ratable, it also needs to annotatable, for example
attribute-annotatable::

  >>> from zope.annotation.interfaces import IAttributeAnnotatable
  >>> from contentratings.interfaces import IEditorRatable
  >>> from contentratings.interfaces import IUserRatable
  >>> from zope.interface import directlyProvides
  >>> directlyProvides(my_container, IAttributeAnnotatable, IEditorRatable, IUserRatable)

Now we can rate the object using the ``IEditorialRating`` adapter, which
stores a single rating for each object.  Anybody with permission to rate the
object overwrites the old rating::

  >>> from contentratings.interfaces import IEditorialRating
  >>> rating = IEditorialRating(my_container)
  >>> rating.rating = 5
  >>> rating.rating
  5.0
  >>> rating.rating = 10
  >>> rating.rating
  10.0

We need to make sure the rating sticks to the object::

  >>> rating = IEditorialRating(my_container)
  >>> rating.rating
  10.0

The ``IUserRating`` adapter is a bit more complicated, when a user rates an
object their rating is associated with them and they can later change it.
Anonymous users may also rate content (though this can be disabled globally).
The average of all ratings and the number of ratings can be easily obtained::

  >>> from contentratings.interfaces import IUserRating
  >>> rating = IUserRating(my_container)
  >>> rating.rate(6, 'me')
  >>> rating.rate(8, 'you')
  >>> rating.userRating('me')
  6.0
  >>> rating.userRating('you')
  8.0

We can get the average rating and number of ratings as well::

  >>> rating.averageRating
  7.0
  >>> rating.numberOfRatings
  2

We can update our user ratings, and the average will change accordingly::

  >>> rating.rate(4, 'me')
  >>> rating.userRating('me')
  4.0
  >>> rating.numberOfRatings
  2
  >>> rating.averageRating
  6.0

Anonymous ratings are a little trickier as they are averaged for all
anonymous entries::

  >>> rating.rate(9)
  >>> rating.numberOfRatings
  3
  >>> rating.averageRating
  7.0

There is only one anonymous rating, so it is the current value for anonymous::

  >>> rating.userRating()
  9.0

Once we add more anonymous ratings the value becomes the average of the
anonymous ratings::

  >>> rating.rate(7)
  >>> rating.userRating()
  8.0
  >>> rating.averageRating
  7.0
  >>> rating.numberOfRatings
  4

This of course needs to be sticky as well::

  >>> rating = IUserRating(my_container)
  >>> rating.averageRating
  7.0
  >>> rating.numberOfRatings
  4


ToDo
====

* Make the views work with Zope 3 authentication
* DHTML and AJAX-ify the views a bit
* Make the cookie that prevents anonymous users from rerating the same content
  long lived.


Credits
=======

Author:
-------

* **Alec Mitchell** <apm13@columbia.edu>

Thanks To:
----------

* **Geoff Davis** author of ATRatings from which icons and ideas were
  stolen.

* **Philipp von Weitershausen** author of
  `Web Component Development with Zope 3`_ which provides a nice example
  of an annotation based rating product, which was the starting point for
  this implementation.

.. _`Web Component Development with Zope 3`: http://www.worldcookery.com/
