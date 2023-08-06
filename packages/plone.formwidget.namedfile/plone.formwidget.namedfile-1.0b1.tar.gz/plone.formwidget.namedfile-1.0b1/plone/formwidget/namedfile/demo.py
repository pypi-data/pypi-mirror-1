from plone.directives import form
from plone.namedfile.field import NamedImage, NamedFile

class IDemo(form.Schema):
    
    a = NamedImage(title=u"A", required=True)
    b = NamedImage(title=u"B", required=False)
    c = NamedFile(title=u"C", required=True)
    d = NamedFile(title=u"D", required=False)
