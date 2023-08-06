

from zope.schema import TextLine

from ng.content.article.interfaces import IDocShort

class IProfile(IDocShort) :

  userid=TextLine(title=u"userid")
  
  


