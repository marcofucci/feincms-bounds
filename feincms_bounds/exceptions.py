class UniqueTemplateException(Exception):
    """
        Manages Exceptions related to unique templates being
        used more than once.
    """
    pass


class FirstLevelOnlyTemplateException(Exception):
    """
        Manages Exceptions related to first-level-only templates
        being used in level of navigation > 1
    """
    pass


class NoChildrenTemplateException(Exception):
    """
        Manages Exceptions related to no-children templates being
        used as children of other templates.
    """
    pass
