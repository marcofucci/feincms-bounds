from feincms.models import Base, Template as FeinCMSTemplate
from feincms.module.page.models import Page
from feincms.content.richtext.models import RichTextContent


class Template(FeinCMSTemplate):
    """
        Custom version of feincms.models.Template which adds support for
        unique, first-level-only and no-children properties.
    """
    def __init__(
        self, title, path, regions, key=None, preview_image=None, unique=False,
        first_level_only=False, no_children=False
    ):
        super(Template, self).__init__(
            title, path, regions, key=key, preview_image=preview_image
        )
        self.unique = unique
        self.first_level_only = first_level_only
        self.no_children = no_children


Page.register_templates(
    Template(
        key='internalpage',
        title='Internal Page',
        path='pages/internal.html',
        regions=(
            ('main', 'Main Content'),
        )
    ), Template(
        key='homepage',
        title='Home Page',
        path='pages/home_page.html',
        regions=(
            ('home_main', 'Main Content'),
        ),
        unique=True,
        first_level_only=True,
        no_children=True
    )
)

Page.create_content_type(RichTextContent)
