# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: fieldproperty.py 236 2008-06-10 20:28:23Z crocha $
#
# end: Platecom header
"""Field properties based on Archetypes schema
"""

from zope.app.component.hooks import getSite

class ATFieldProperty(object):
    """Field properties based on Archetypes schema

    These properties can only be used on Archetypes objects. They delegate
    to schema.getField(fieldname).get() and set().

    You can use it in your type as follows. The name of the field does
    not need to conincide with the field-property name, but this is probably
    sensible. However, AttributeStorage will interfere here, so we explicitly
    use annoation storage.

        >>> import string
        >>> from Products.Archetypes.atapi import *
        >>> from iccommunity.core.fieldproperty import ATFieldProperty

        >>> class MyContent(BaseObject):
        ...     portal_type = meta_type = 'MyContent'
        ...     schema = Schema((
        ...         StringField('some_field', storage=AnnotationStorage()),
        ...         StringField('_other_field'),
        ...         ))
        ...
        ...     some_field = ATFieldProperty('some_field')
        ...     other_field = ATFieldProperty('_other_field')
        ...     upper_lower = ATFieldProperty('_other_field',
        ...         get_transform=string.upper, set_transform=string.lower)

        >>> registerType(MyContent, 'Archetypes')

    Now, get and set operations on the fieldproperty behave the same way as
    the mutator and accessor.

        >>> foo = MyContent('foo')
        >>> foo.some_field
        ''
        >>> foo.some_field = "Bar"
        >>> foo.some_field
        'Bar'
        >>> foo.getField('some_field').get(foo)
        'Bar'

    The old-style mutator and accessors still work, of course

        >>> foo.getSome_field()
        'Bar'

        >>> foo.setSome_field("Baz")
        >>> foo.some_field
        'Baz'

    Here is an example using the default AttributeStorage. In this case, we
    need different names for the AT field name and the properity, because
    AttributeStorage will use the field name as the attribute name. If
    you don't do this, you may get infinite recursion!

        >>> foo.other_field = "Hello"
        >>> foo.other_field
        'Hello'
        >>> foo.get_other_field()
        'Hello'
        >>> foo.set_other_field("Good bye")
        >>> foo.other_field
        'Good bye'

    Finally, the get_transform and set_transform arguments can be used to
    perform transformations on the retrieved value and the value before it
    is set, respectively. The field upper_lower uses string.upper() on the
    way out and string.lower() on the way in.

        >>> foo.upper_lower = "MiXeD"
        >>> foo.upper_lower
        'MIXED'
        >>> foo.get_other_field()
        'mixed'
        >>> foo.set_other_field('UpPeRaNdLoWeR')
        >>> foo.upper_lower
        'UPPERANDLOWER'

    A less frivolous example of this functionality can be seen in the
    ATDateTimeFieldProperty class below.
    """

    def __init__(self, name, get_transform=None, set_transform=None):
        self._name = name
        self._get_transform = get_transform
        self._set_transform = set_transform

    def __get__(self, inst, klass):
        if inst is None:
            return self
        field = inst.getField(self._name)
        if field is None:
            raise KeyError("Cannot find field with name %s" % self._name)
        value = field.get(inst)
        if self._get_transform is not None:
            value = self._get_transform(value)
        return value

    def __set__(self, inst, value):
        field = inst.getField(self._name)
        if field is None:
            raise KeyError("Cannot find field with name %s" % self._name)
        if self._set_transform is not None:
            value = self._set_transform(value)
        field.set(inst, value)

class ATToolDependentFieldProperty(ATFieldProperty):
    """A version of the field property type which is able to acquire
    tools. This uses a not-very-nice acquisition hack, and is not
    generalisable to all acquisition-dependent operations, but should work
    for tools in the portal root.

        >>> from Products.Archetypes.atapi import *
        >>> from iccommunity.core.fieldproperty import ATToolDependentFieldProperty
        >>> from zope.app.component.hooks import setSite
        >>> setSite(portal)

        >>> class MyContent(BaseContent):
        ...     portal_type = meta_type = 'MyContent'
        ...     schema = Schema((
        ...         ReferenceField('some_field', multiValued=True,
        ...                        relationship='foo', storage=AnnotationStorage()),
        ...         ))
        ...
        ...     some_field = ATToolDependentFieldProperty('some_field')

        >>> registerType(MyContent, 'Archetypes')

        >>> self.portal._setOb('foo', MyContent('foo'))
        >>> foo = getattr(self.portal, 'foo')

    These lines would fail with AttributeError: reference_catalog if it used
    the standard accessor.

        >>> foo.some_field
        []
        >>> foo.some_field = [self.folder.UID()]
        >>> foo.some_field
        [<ATFolder at /plone/Members/test_user_1_>]
    """

    def __init__(self, name, get_transform=None, set_transform=None):
        self._name = name
        self._get_transform = get_transform
        self._set_transform = set_transform

    def __get__(self, inst, klass):
        if inst is None:
            return self
        field = inst.getField(self._name)
        if field is None:
            raise KeyError("Cannot find field with name %s" % self._name)
        value = field.get(inst.__of__(getSite()))
        if self._get_transform is not None:
            value = self._get_transform(value)
        return value

    def __set__(self, inst, value):
        field = inst.getField(self._name)
        if field is None:
            raise KeyError("Cannot find field with name %s" % self._name)
        if self._set_transform is not None:
            value = self._set_transform(value)
        field.set(inst.__of__(getSite()), value)

class ATReferenceFieldProperty(ATToolDependentFieldProperty):
    """A more friendly/use-case-specific name for ATReferenceFieldProperty.
    """

class ATFieldMultilingualProperty(object):
    """Field properties based on Archetypes schema

    These properties can only be used on Archetypes objects. They delegate
    to schema.getField(fieldname).get() and set().

    You can use it in your type as follows. The name of the field does
    not need to conincide with the field-property name, but this is probably
    sensible. However, AttributeStorage will interfere here, so we explicitly
    use annoation storage.

        >>> import string
        >>> from Products.Archetypes.atapi import *
        >>> from iccommunity.core.fieldproperty import ATFieldProperty

        >>> class MyContent(BaseObject):
        ...     portal_type = meta_type = 'MyContent'
        ...     schema = Schema((
        ...         StringField('some_field', storage=AnnotationStorage()),
        ...         StringField('_other_field'),
        ...         ))
        ...
        ...     some_field = ATFieldProperty('some_field')
        ...     other_field = ATFieldProperty('_other_field')
        ...     upper_lower = ATFieldProperty('_other_field',
        ...         get_transform=string.upper, set_transform=string.lower)

        >>> registerType(MyContent, 'Archetypes')

    Now, get and set operations on the fieldproperty behave the same way as
    the mutator and accessor.

        >>> foo = MyContent('foo')
        >>> foo.some_field
        ''
        >>> foo.some_field = "Bar"
        >>> foo.some_field
        'Bar'
        >>> foo.getField('some_field').get(foo)
        'Bar'

    The old-style mutator and accessors still work, of course

        >>> foo.getSome_field()
        'Bar'

        >>> foo.setSome_field("Baz")
        >>> foo.some_field
        'Baz'

    Here is an example using the default AttributeStorage. In this case, we
    need different names for the AT field name and the properity, because
    AttributeStorage will use the field name as the attribute name. If
    you don't do this, you may get infinite recursion!

        >>> foo.other_field = "Hello"
        >>> foo.other_field
        'Hello'
        >>> foo.get_other_field()
        'Hello'
        >>> foo.set_other_field("Good bye")
        >>> foo.other_field
        'Good bye'

    Finally, the get_transform and set_transform arguments can be used to
    perform transformations on the retrieved value and the value before it
    is set, respectively. The field upper_lower uses string.upper() on the
    way out and string.lower() on the way in.

        >>> foo.upper_lower = "MiXeD"
        >>> foo.upper_lower
        'MIXED'
        >>> foo.get_other_field()
        'mixed'
        >>> foo.set_other_field('UpPeRaNdLoWeR')
        >>> foo.upper_lower
        'UPPERANDLOWER'

    A less frivolous example of this functionality can be seen in the
    ATDateTimeFieldProperty class below.
    """

    def __init__(self, name, get_transform=None, set_transform=None):
        self._name = name
        self._get_transform = get_transform
        self._set_transform = set_transform

    def __get__(self, inst, klass):
        if inst is None:
            return self
        field = inst.getField(self._name)
        if field is None:
            raise KeyError("Cannot find field with name %s" % self._name)
        value = field.get(inst)
        if not value:
            es_inst = inst.getTranslations()['es'][0]
            field = es_inst.getField(self._name)
            if field is None:
                raise KeyError("Cannot find field with name %s" % self._name)
            value = field.get(es_inst)
        if self._get_transform is not None:
            value = self._get_transform(value)
        return value

    def __set__(self, inst, value):
        field = inst.getField(self._name)
        if field is None:
            raise KeyError("Cannot find field with name %s" % self._name)
        if self._set_transform is not None:
            value = self._set_transform(value)
        field.set(inst, value)

_marker = object()

class ToolDependentFieldProperty(object):
    """A version of the field property type for zope schemas which is
    able to acquire tools. This uses a not-very-nice acquisition hack,
    and is not generalisable to all acquisition-dependent operations,
    but should work for tools in the portal root.

        >>> from zope.interface import Interface, implements
        >>> from zope import schema
        >>> from OFS.SimpleItem import SimpleItem
        >>> from iccommunity.core.fieldproperty import ToolDependentFieldProperty
        >>> from zope.app.component.hooks import setSite
        >>> setSite(portal)

        >>> class IToolFields(Interface):
        ...     field1 = schema.List(title = u"field1",
        ...                          required = False,
        ...                          default = [],
        ...                          description = u"Tool dependent field",
        ...                          value_type=schema.Choice(vocabulary="plone.content_types"))

        >>> class ToolFields(SimpleItem):
        ...    implements(IToolFields)
        ...    field1 = ToolDependentFieldProperty(IToolFields['field1'])

        >>> self.portal._setOb('foo', ToolFields())
        >>> foo = getattr(self.portal, 'foo')
        >>> foo.field1
        []
        >>> foo.field1 = ['ATEvent',]
        >>> foo.field1
        ['ATEvent']

    """

    def __init__(self, field, name=None, get_transform=None, set_transform=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name
        self._get_transform = get_transform
        self._set_transform = set_transform

    def __get__(self, inst, klass):
        if inst is None:
            return self

        value = inst.__dict__.get(self.__name, _marker)
        if value is _marker:
            site = getSite()
            if not site:
#                import pdb;pdb.set_trace()
                raise AttributeError(self.__name)
            field = self.__field.bind(inst.__of__(site))
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)

        if self._get_transform is not None:
            value = self._get_transform(value)
        return value

    def __set__(self, inst, value):
        field = self.__field.bind(inst.__of__(getSite()))
        field.validate(value)
        if field.readonly and inst.__dict__.has_key(self.__name):
            raise ValueError(self.__name, 'field is readonly')
        if self._set_transform is not None:
            value = self._set_transform(value)
        inst.__dict__[self.__name] = value

    def __getattr__(self, name):
        return getattr(self.__field, name)

class AnnotatableFieldProperty(object):

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name

    def __get__(self, inst, klass):
        if inst is None:
            return self

        value = inst._metadata.get(self._AnnotatableFieldProperty__name, _marker)
        #value = inst.__dict__.get(self.__name, _marker)
        if value is _marker:
            field = self._AnnotatableFieldProperty__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self._AnnotatableFieldProperty__name)

        return value

    def __set__(self, inst, value):
        field = self._AnnotatableFieldProperty__field.bind(inst)
        field.validate(value)
        if field.readonly:
            raise ValueError(self._AnnotatableFieldProperty__name, 'field is readonly')
        inst._metadata[self._AnnotatableFieldProperty__name] = value
        #inst.__dict__[self.__name] = value

    def __getattr__(self, name):
        return getattr(self._AnnotatableFieldProperty__field, name)

class PMFieldProperty(object):

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name

    def __get__(self, inst, klass):
        if inst is None:
            return self

        value = inst.getProperty(self._PMFieldProperty__name, _marker)
        if value is _marker:
            field = self._PMFieldProperty__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self._PMFieldProperty__name)

        return value

    def __set__(self, inst, value):
        field = self._PMFieldProperty__field.bind(inst)
        field.validate(value)
        if field.readonly:
            raise ValueError(self._PMFieldProperty__name, 'field is readonly')
        if not inst.hasProperty(self._PMFieldProperty__name):
            # Create the property
            assignments._setProperty(self._PMFieldProperty__name, value)

        # Override assigments value (old or new created)
        assignments._updateProperty(self._PMFieldProperty__name, value)

    def __getattr__(self, name):
        return getattr(self._PMFieldProperty__name, name)

class AuthenticatedMemberFieldProperty(object):

    def __init__(self, field, name=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name

    def __get__(self, inst, klass):
        portal = getSite()
        if not portal:
            raise AttributeError(self._AuthenticatedMemberFieldProperty__name)
        inst = portal.portal_membership.getAuthenticatedMember()

        value = inst.getProperty(self._AuthenticatedMemberFieldProperty__name, _marker)
        if value is _marker:
            field = self._AuthenticatedMemberFieldProperty__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self._AuthenticatedMemberFieldProperty__name)

        return value

    def __set__(self, inst, value):
        field = self._AuthenticatedMemberFieldProperty__field.bind(inst)
        field.validate(value)

        portal = getSite()
        if not portal:
            raise AttributeError(self._AuthenticatedMemberFieldProperty__name)
        inst = portal.portal_membership.getAuthenticatedMember()

        if field.readonly:
            raise ValueError(self._AuthenticatedMemberFieldProperty__name, 'field is readonly')

        inst.setProperties({self._AuthenticatedMemberFieldProperty__name: value})

    def __getattr__(self, name):
        return getattr(self._AuthenticatedMemberFieldProperty__name, name)
