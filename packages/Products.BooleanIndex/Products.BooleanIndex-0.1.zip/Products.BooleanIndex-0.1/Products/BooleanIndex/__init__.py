def initialize(context):
    from Products.BooleanIndex.BooleanIndex import BooleanIndex
    from Products.BooleanIndex.BooleanIndex import manage_addBooleanIndex
    from Products.BooleanIndex.BooleanIndex import manage_addBooleanIndexForm

    context.registerClass(
        BooleanIndex,
        permission='Add Pluggable Index',
        constructors=(manage_addBooleanIndexForm,
                      manage_addBooleanIndex),
        icon='www/index.gif',
        visibility=None
    )
