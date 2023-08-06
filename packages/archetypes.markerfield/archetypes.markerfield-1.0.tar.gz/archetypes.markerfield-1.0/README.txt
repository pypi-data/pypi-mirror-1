Introduction
============

This packages contains a single Archetypes field that can manage one or
more marker interface on an object. 

It is most often used with `archetypes.schemaextender`_ to add a field to
a type which controls new optional behaviour.

Example
=======

This example adds a new item to the settings fieldset for an object
which controls an ICategory marker interface::


    class FolderExtender(object):
        """Add a new 'category' field to all Archetypes based folder types.
        """
        adapts(IBaseFolder)
        implements(ISchemaExtender)

        fields = [
                InterfaceMarkerField("category",
                    schemata = "settings",
                    interfaces = (ICategory,),
                    widget = BooleanWidget(
                        title = _(u"label_category",
                                    default=u"Is this folder a category."),
                        description = _(u"help_category",
                                    default=u"This should briefly explain what "
                                            u"categories are used for."),
                        ),
                    ),
                ]


        def __init__(self, context):
            self.context = context


        def getFields(self):
            return self.fields

.. _archetypes.schemaextender: http://pypi.python.org/pypi/archetypes.schemaextender
