from zope.interface import implements
from collective.singing.interfaces import IFormatItem
from Products.CMFCore.utils import getToolByName

class DancingEventFormatter(object):
    implements(IFormatItem)
    template = """
            <div class="item">
            <img class="eventimage" src="%(portal)s/event_icon.gif" />
            <h2><a href="%(url)s">%(title)s</a></h2>
            <div class="dates">
            %(start_date)s - %(end_date)s
            </div>
            <p>%(description)s</p>
            </div>
            """

    def _toLocalizedTime(self, time, long_format=None):
        tool = getToolByName(self.item, 'translation_service')
        return tool.ulocalized_time(time, long_format=long_format)

    def __init__(self,item,request):        
        self.request = request
        self.item = item

    def __call__(self): 
        #check if it has an image
        return self.template % dict(
                portal = self.item.portal_url(),
                start_date = self._toLocalizedTime(self.item.startDate,long_format=1),
                end_date = self._toLocalizedTime(self.item.endDate,long_format=1),
                url = self.item.absolute_url(),
                title = self.item.Title(),
                description = self.item.Description(),
                )
