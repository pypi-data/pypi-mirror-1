from zope.viewlet.viewlet import ViewletBase
from zope.app.pagetemplate import ViewPageTemplateFile
from worldcookery.interfaces import IRating

class RatingViewlet(ViewletBase):

    def update(self):
        rating = self.request.form.get('worldcookery.rating')
        if rating is not None:
            IRating(self.context).rate(rating)

    render = ViewPageTemplateFile('rating.pt')

    def rating(self):
        return IRating(self.context)

    ratingChoices = (1, 2, 3, 4, 5)