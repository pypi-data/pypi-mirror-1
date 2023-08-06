from zope import interface

class IFieldContentProvider(interface.Interface):
    def setContentFor(field, instance):
        pass
