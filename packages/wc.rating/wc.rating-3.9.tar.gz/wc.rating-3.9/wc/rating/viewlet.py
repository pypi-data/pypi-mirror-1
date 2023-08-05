from zope.viewlet.viewlet import ViewletBase
from zope.app.pagetemplate import ViewPageTemplateFile
from wc.rating.interfaces import IRating

class RatingViewlet(ViewletBase):

    ratingChoices = (1, 2, 3, 4, 5)

    def update(self):
        self.rating = IRating(self.context)
        userinput = self.request.form.get('wc.rating')
        if userinput is not None:
            self.rating.rate(userinput)

    render = ViewPageTemplateFile('viewlet.pt')
