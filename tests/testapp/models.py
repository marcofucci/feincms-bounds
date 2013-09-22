from feincms.module.page.models import Page
from feincms.content.raw.models import RawContent

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

Page.create_content_type(RawContent)
