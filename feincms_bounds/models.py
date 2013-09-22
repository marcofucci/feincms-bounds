from feincms.models import Template as FeinCMSTemplate


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
