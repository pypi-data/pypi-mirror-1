Overview
--------

This package provides a schema field that combines an internal and
external link representation. It's relatively low-tech.

It provides a widget that lets users enter links on the format:

  "Title":internal path or URI:"Description"

Both title and description are optional. If an internal path is given,
the field tries to resolve the object and stores only its UID.

Requirements
------------

* Zope 2.10.4+

Usage
-----

Include the ZCML-slug for the package to register the widget with formlib. 

A schema definition for a field carrying a single link:
   
   >>> from collective.formlib.link.field import Link
   >>> field = Link(title=u"Link")

A list of link fields:

   >>> from zope import schema
   >>> field = schema.List(
   ...     title=u"Links",
   ...     value_type=Link)

To render the link from a page template:

      <a tal:attributes="href link/@@absolute_url;
			 title link/description"
	 tal:content="link/pretty_title_or_uri" />
