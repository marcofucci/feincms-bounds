=============================
feincms-bounds
=============================

.. image:: https://travis-ci.org/marcofucci/feincms-bounds.png?branch=master
        :target: https://travis-ci.org/marcofucci/feincms-bounds


FeinCMS add-on which adds extra admin Page validation:

- Unique templates: templates that can be used only once (e.g. home page)
- First-Level-Only templates: templates that can be used in the first level - of navigation only (e.g. home page)
- No-Children templates: templates that can't have subpages (e.g. home page)
- Level of Navigation: max levels of navigation allowed


Quickstart
----------

Install feincms-bounds::

    pip install -e git@github.com:marcofucci/feincms-bounds.git#egg=feincms-bounds

Add feincms-bounds to your ``settings.INSTALLED_APPS``::

	INSTALLED_APPS = (
		...
	    'feincms_bounds',
	    ...
	)

When registering a FeinCMS template, use ``feincms_bounds.models.Template``
and specify whether it's unique, first-level only or can't have subpages.

In ``models.py``::

	from feincms.module.page.models import Page

	from feincms_bounds.models import Template


	Page.register_templates(
	    Template(
	        key='internalpage',
	        title='Internal Page',
	        path='pages/internal.html',
	        regions=(
	            ('main', 'Main Content'),
	            ('sidebar', 'Sidebar'),
	        )
	    ), Template(
	        key='homepage',
	        title='Home Page',
	        path='pages/home_page.html',
	        regions=(
	            ('main', 'Main Content'),
	        ),
	        unique=True,
	        first_level_only=True,
	        no_children=True
	    )
	)


Finally, use ``feincms_bounds.admin.PageAdmin`` when registering the Page
(you need to unregister the feinCMS default one first).

In ``admin.py``::

	from django.contrib import admin

	from feincms.module.page.models import Page

	from feincms_bounds.admin import PageAdmin


	# We have to unregister it, and then reregister
	admin.site.unregister(Page)
	admin.site.register(Page, PageAdmin)


Optionally, you can specify a max level of navigation using ``settings.FEINCMS_NAVIGATION_LEVEL``.

Done! You can now take advantage of the extra admin Page validation provided by
feincms-bounds.


Example
-------

* Sample project: https://github.com/marcofucci/feincms_extended
* Original Blog: http://www.marcofucci.com/tumblelog/19/may/2010/customizing-feincms-part-1/
