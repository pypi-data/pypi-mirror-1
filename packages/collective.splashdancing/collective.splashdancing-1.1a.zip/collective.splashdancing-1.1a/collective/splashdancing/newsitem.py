from zope.interface import implements
from collective.singing.interfaces import IFormatItem

class DancingNewsItemFormatter(object):
    implements(IFormatItem)
    template = """\
            <div class="item">
            <h2><a href="%(url)s">%(title)s</a></h2>
            <img src="%(url)s/image_thumb" />
            <p>%(description)s</p>
            <a href="%(url)s">more...</a>
            </div>
            """
    noimagetemplate = """\
            <div class="item">
            <h2><a href="%(url)s">%(title)s</a></h2>
            <p>%(description)s</p>
            </div>
            """
    def __init__(self,item,request):        
        self.request = request
        self.item = item

    def __call__(self): 
        #check if it has an image
        if self.item.getImage():
            return self.template % dict(
                url = self.item.absolute_url(),
                title = self.item.Title(),
                description = self.item.Description(),
                )
        return self.noimagetemplate % dict(
                url = self.item.absolute_url(),
                title = self.item.Title(),
                description = self.item.Description(),
                )
