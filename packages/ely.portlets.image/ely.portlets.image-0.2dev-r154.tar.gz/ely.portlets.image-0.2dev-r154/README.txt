Introduction
============

A portlet for attaching and linking a single image in plone 3

This is quite basic at present. There are some things to know:

The image is stored as an OFS.Image.Image in the portlet assignment
data - this is so we get access to get method that produces useful
headers for caching, and gives us some useful parameters for creating
a tag. However, since portlet Assignments do not provide enough
context to be Locatable in the zope sense, then we need to generate
our own tag based on an assignment path saved when the portlet was
added. Since portlet assignments can't be moved, then this is ok. It's
all transparent to you if you are simply interested in using this.

