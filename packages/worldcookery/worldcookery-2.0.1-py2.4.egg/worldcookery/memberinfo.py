from persistent.dict import PersistentDict
from zope.interface import implements
from zope.component import adapts
from zope.security.interfaces import IPrincipal
from zope.annotation.interfaces import IAnnotations
from worldcookery.interfaces import IMemberInfo

KEY = "worldcookery.memberinfo"

class MappingProperty(object):

    def __init__(self, name):
        self.name = name

    def __get__(self, inst, class_=None):
        return inst.mapping[self.name]

    def __set__(self, inst, value):
        inst.mapping[self.name] = value

class MemberInfo(object):
    implements(IMemberInfo)
    adapts(IPrincipal)

    def __init__(self, context):
        annotations = IAnnotations(context)
        mapping = annotations.get(KEY)
        if mapping is None:
            blank = {'first': u'', 'last': u'', 'email': u''}
            mapping = annotations[KEY] = PersistentDict(blank)
        self.mapping = mapping

    first = MappingProperty('first')
    last = MappingProperty('last')
    email = MappingProperty('email')