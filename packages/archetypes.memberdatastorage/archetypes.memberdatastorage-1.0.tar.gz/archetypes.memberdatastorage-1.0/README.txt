Introduction
============

A facade storage for Archetypes which delegates to 
a Plone site's Memberdata Tool for storing content 
item field values as memberdata properties. 

This heavily relies on name magic.
It is assumed that the correponding member and content 
instances have **exactly** the same id. 

The use case driving its development has been to support
custom Archetypes-based content types which can be used
as home folders for members and mirroring some of the
member properties. That way, people can change member 
properties by editing their home folder settings.

``archetypes.memberdata`` is used in production on http://www.incf.org.


Usage
=====

In your Archetypes schema definition you can use the ``MemberPropertyField``
instead of a regular StringField to get and set the field's value in a
corresponding member property. Per default, a property with the same
name as the field is used unless the ``member_property_id`` is set to point
to a different property.

For other field types one can use ``MemberdataStorage`` as well as long as
the data type can be handled by the member data tool.
