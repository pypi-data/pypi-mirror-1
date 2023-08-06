import CompositeIndex

import logging

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    context.registerClass(
        CompositeIndex.CompositeIndex,
        permission = 'Add Pluggable Index',
        constructors = (CompositeIndex.manage_addCompositeIndexForm,
                        CompositeIndex.manage_addCompositeIndex,
                        ),
        icon='www/index.gif',
        visibility=None
        )


