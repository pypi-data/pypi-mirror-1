collective.portlet.filtersearch
===============================

This package defines a portlet that shows additional filter of current search results.
The filtering works in two modes.

1. Results grouped by a simple index/value
2. Additionally group by unique values of selected criteria


Installation
============
To install just add a collective.portlet.filtersearch to your buildout file::

	[buildout]
	...
	eggs = 
	    collective.portlet.filtersearch
	    ...

Package uses z3c.autoinclude so there is no need to add it into your zcml section.

Restart your zope instance and install it via Add/Remove product in Plone control panel.

Setting
=======
In the portlet edit form you can define which filters should appear in the portlet::

	Criteria title - The title of criteria displayed in the portlet
	Main index - Name of index which is used to group it ( it has to be in metadata too )
	Value - The value of the index that the brain has to match to group

And additional values::

	Expand list with unique values - Check box to enable the sub filtering
	Sub index - Name of index which is used for listing unique groups dynamically

You can add as many criteria as you like

Hint: To enable the portlet at the search template, just add it to your site root 
and remove the line <metal:block fill-slot="column_two_slot" /> to enable portlets at all.


TODO
====
- How to determine when display the portlet and when hide - fix the available property
- Add some tests would be nice


