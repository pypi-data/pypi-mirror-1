from generation import createNestedStructure
from generation import createStandardContent

def setupOutOfTheBox(context):
    """This profile generates a ``typical`` out-of-the-box deployment."""
    
    portal = context.getSite()
    createNestedStructure(portal, branches=2, depth=4)
    createNestedStructure(portal, branches=2, depth=2)
    createStandardContent(portal, count=1)
