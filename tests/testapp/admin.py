from feincms.module.page.models import Page

from feincms_bounds.admin import PageAdmin

from django.contrib import admin


# We have to unregister it, and then reregister
admin.site.unregister(Page)
admin.site.register(Page, PageAdmin)
