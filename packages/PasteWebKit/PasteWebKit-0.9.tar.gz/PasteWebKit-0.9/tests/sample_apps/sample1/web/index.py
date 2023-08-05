from paste.deploy import CONFIG
from WebKit.Page import Page

class index(Page):

    def writeHTML(self):
        self.write('All OK; config=%s' % dict(CONFIG))
    

