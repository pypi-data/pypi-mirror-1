from google.appengine.ext import db
from cluebin import paste


class GooglePaste(db.Model, paste.Paste):
    author_name = db.StringProperty()
    language = db.StringProperty()
    paste = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)

    @property
    def pasteid(self):
        return self.key().id()

    @staticmethod
    def kind():
        return 'Paste'


class GooglePasteDataStore(paste.PasteDataStore):

    def get_paste(self, pasteid):
        return GooglePaste.get_by_id(int(pasteid))

    def get_pastes(self):
        return db.GqlQuery('SELECT * FROM Paste ORDER BY date DESC LIMIT 10')

    def gen_paste(self):
        return GooglePaste()

    def save_paste(self, p):
        p.put()
