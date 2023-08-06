from Products.Five.browser import BrowserView

import generation

class UserInterface(BrowserView):
    def loremipsumize(self):
        generation.loremipsumize(self.context.aq_inner)
        self.request.response.redirect(self.context.absolute_url())
        
