from django.contrib import admin, messages
from django.conf import settings as django_settings
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.forms.util import ErrorList
from django.http import HttpResponse

from feincms.module.page.models import Page
from feincms.module.page.modeladmins import PageAdmin as PageAdminOld
from feincms.module.page.forms import PageAdminForm as PageAdminFormOld

from .exceptions import UniqueTemplateException, \
    FirstLevelOnlyTemplateException, NoChildrenTemplateException


def get_max_navigation_level():
    """
        @return int: max level of navigation as defined by the value of
            FEINCMS_NAVIGATION_LEVEL in settings.py if defined, None
            otherwise.
    """
    return getattr(django_settings, 'FEINCMS_NAVIGATION_LEVEL', None)


def is_navigation_level_valid(level):
    """
        @return bool: True if the level 'level' is valid, False otherwise.
    """
    max_level = get_max_navigation_level()
    return not max_level or max_level >= level


def check_template(model, template, instance=None, parent=None):
    """
        Checks that the template 'template' is valid, throws the following
        exceptions otherwise:
         * UniqueTemplateException: if 'template' is defined as unique and it has
            been used already somewhere else
         * FirstLevelOnlyTemplateException: if 'template' is defined as
            first-level-only and the user is trying to use it in a level of
            navigation > 1
         * NoChildrenTemplateException: if the user is trying to add 'model' as
            child of a page defined as no-children template or he's trying to
            change the template of this instance to no-children but the contains
            already some children.
    """
    def get_parent(parent):
        if not parent:
            return None
        if isinstance(parent, Page):
            return parent
        return Page.objects.get(id=parent)

    if template.unique and model.objects.filter(
                                template_key=template.key
                            ).exclude(id=instance.id if instance else -1).count():
        raise UniqueTemplateException()

    parent_page = get_parent(parent)
    if template.first_level_only and parent_page:
        raise FirstLevelOnlyTemplateException()

    if parent_page and model._feincms_templates[parent_page.template_key].no_children:
        raise NoChildrenTemplateException()

    if instance and template.no_children and instance.children.count():
        raise NoChildrenTemplateException()


def is_template_valid(model, template, instance=None, parent=None):
    """
        @return bool: True if the 'template' can be associated to 'instance' of
            time 'model', False otherwise.
    """
    try:
        check_template(model, template, instance=instance, parent=parent)
        return True
    except (
            UniqueTemplateException, FirstLevelOnlyTemplateException,
            NoChildrenTemplateException
        ):
        pass

    return False


class PageAdminForm(PageAdminFormOld):
    """
        Overridden version of feincms.module.page.forms.PageAdminForm which
        checks for template properties.
    """
    def __init__(self, *args, **kwargs):
        super(PageAdminForm, self).__init__(*args, **kwargs)

        instance = kwargs.get('instance')
        parent = kwargs.get('initial', {}).get('parent')
        if not parent and instance:
            parent = instance.parent
        templates = self.get_valid_templates(instance, parent)

        choices = []
        for key, template in templates.items():
            if template.preview_image:
                choices.append((template.key,
                    mark_safe(u'<img src="%s" alt="%s" /> %s' % (
                        template.preview_image, template.key, template.title))))
            else:
                choices.append((template.key, template.title))

        self.fields['template_key'].choices = choices
        if choices:
            self.fields['template_key'].default = choices[0][0]

    def clean(self):
        """
            Adds extra validation against the new template properties.
        """
        cleaned_data = super(PageAdminForm, self).clean()

        # No need to think further, let the user correct errors first
        if self._errors:
            return cleaned_data

        parent = cleaned_data.get('parent')
        if parent:
            template_key = cleaned_data['template_key']
            template = self.Meta.model._feincms_templates[template_key]

            parent_error = None
            try:
                check_template(
                    self.Meta.model, template, instance=self.instance, parent=parent
                )
            except UniqueTemplateException:
                parent_error = _('Template already used somewhere else')
            except FirstLevelOnlyTemplateException:
                parent_error = _("This template can't be used as a subpage")
            except NoChildrenTemplateException:
                parent_error = _("This parent page can't have subpages")
            else:
                if not is_navigation_level_valid(parent.level+2):
                    parent_error = _(
                        "Only %d levels allowed" % get_max_navigation_level()
                    )

            if parent_error:
                self._errors['parent'] = ErrorList([parent_error])
                del cleaned_data['parent']
        return cleaned_data

    def get_valid_templates(self, instance=None, parent=None):
        """
            @return dict: dict containing all the templates valid for this instance
                (excluding unique ones already used etc.)
        """
        templates = self.Meta.model._feincms_templates.copy()

        return dict(
            filter(
                lambda (key, template): is_template_valid(
                    self.Meta.model, template, instance=instance, parent=parent
                ), templates.items()
            )
        )


class PageAdmin(PageAdminOld):
    """
        Overridden version of feincms.module.page.models.PageAdmin which
        uses a custom version of PageAdminForm.
    """
    form = PageAdminForm

    def _move_node(self, request):
        """
            Checks for validation before moving the pages around.
        """
        cut_item = self.model._tree_manager.get(pk=request.POST.get('cut_item'))
        pasted_on = self.model._tree_manager.get(pk=request.POST.get('pasted_on'))
        position = request.POST.get('position')

        if position in ('last-child', 'left'):
            cut_item_template = self.model._feincms_templates[cut_item.template_key]
            parent = pasted_on if position == 'last-child' else pasted_on.parent

            try:
                check_template(
                    self.model, cut_item_template, instance=cut_item, parent=parent
                )
            except FirstLevelOnlyTemplateException:
                msg = unicode(_(u"This page can't be used as subpage."))
                messages.error(request, msg)
                return HttpResponse(msg)
            except NoChildrenTemplateException:
                msg = unicode(_(u"This page can't have subpages"))
                messages.error(request, msg)
                return HttpResponse(msg)
            except:
                msg = unicode(_(u"Server Error."))
                messages.error(request, msg)
                return HttpResponse(msg)
            else:
                if parent and not is_navigation_level_valid(parent.level+2):
                    msg = unicode(_(u"Only %d levels allowed" % get_max_navigation_level()))
                    messages.error(request, msg)
                    return HttpResponse(msg)

        return super(PageAdmin, self)._move_node(request)

    def _actions_column(self, page):
        """
            Removes the add icon if the user can't add any subpages.
        """
        actions = super(PageAdmin, self)._actions_column(page)

        template = self.model._feincms_templates.get(page.template_key)
        no_children = template and template.no_children
        valid_navigation = is_navigation_level_valid(page.level+2)

        if (no_children or not valid_navigation) and getattr(page, 'feincms_editable', True):
            actions[1] = u'<img src="%spages/img/actions_placeholder.gif">' % django_settings.STATIC_URL
        return actions
