from google.appengine.ext import db


class Paste(db.Model):
    author_name = db.StringProperty()
    paste = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)


class PasteDataStore(object):

    def get_paste(self, pasteid):
        return Paste.get_by_id(int(pasteid))

    def get_pastes(self):
        return db.GqlQuery('SELECT * FROM Paste ORDER BY date DESC LIMIT 10')

    def gen_paste(self):
        return Paste()

    def save_paste(self, p):
        p.put()
