import webob
from StringIO import StringIO
import pygments
from pygments import lexers
from pygments import formatters
from pygments import util


class PasteManager(object):

    def __init__(self, datastore):
        self.datastore = datastore

    def get_paste(self, pasteid):
        return self.datastore.get_paste(pasteid)

    def get_pastes(self):
        return self.datastore.get_pastes()

    def save_paste(self, author_name, paste_text):
        p = self.datastore.gen_paste()
        p.author_name = author_name
        p.paste = paste_text
        self.datastore.save_paste(p)


class PasteBin(object):

    def __init__(self, pmanager):
        self.pmanager = pmanager

    def __call__(self, environ, start_application):
        request = webob.Request(environ)
        response = webob.Response(content_type='text/html')

        out = StringIO()

        handler = self.index
        pieces = [x for x in environ['PATH_INFO'].split('/') if x]
        if pieces and hasattr(self, pieces[0]):
            handler = getattr(self, pieces[0])

        handler(request, out, *pieces[1:])

        # Lazy man's templating
        top = u'''
        <html>
          <head>
            <title>PasteBin</title>
            <style>
            .left { width: 70%; float: left; }
            .right { margin-left: 2em; width: 20%; float: left; }
            </style>
          </head>
          <body>
          '''
        bottom = u'</body></html>'

        response.unicode_body = top + out.getvalue() + bottom
        return response(environ, start_application)

    def url(self, s):
        return '/'+s

    def paste_listing(self, request, out):
        print >> out, u'<fieldset><legend>Previous Pastes</legend><ul>'

        for pobj in self.pmanager.get_pastes():
            pdate = pobj.date.strftime('%x at %X')
            print >> out, u'<li><a href="%s">Post by: %s on %s</a></li>' % \
                  (self.url('pasted/%i' % pobj.key().id()),
                   pobj.author_name, pdate)

        print >> out, u'</ul></fieldset>'

    def index(self, request, out, msg=u'', paste=u''):
        if msg:
            msg = u'<div class="message">%s</div>' % msg

        if paste:
            try:
                l = lexers.guess_lexer(paste)
            except util.ClassNotFound, err:
                # couldn't guess lexer
                l = lexers.TextLexer()
            formatter = formatters.HtmlFormatter(cssclass="source")
            formatted_paste = pygments.highlight(paste, l, formatter)

            print >> out, u'''
              <style>%s</style>
              Your Paste:<br/>
              %s
            ''' % (formatter.get_style_defs(), formatted_paste)

        print >> out, u'''
            %(message)s
            <div class="left">
            <form action="%(action)s" method="POST">
              <fieldset>
                <legend>Paste Fields</legend>
                <div class="field">
                  <label for="author_name">Name</label>
                  <input type="text" name="author_name" />
                </div>
                <div class="field">
                  <label for="paste">Paste Text</label>
                  <textarea name="paste">%(paste)s</textarea>
                </div>
                <input type="submit" />
              </fieldset>
            </form>
            </div>
        ''' % {'action': self.url('paste'), 'message': msg, 'paste': paste}

        print >> out, u'<div class="right">'
        self.paste_listing(request, out)
        print >> out, u'</div>'

    def pasted(self, request, out, *args):
        pobj = self.pmanager.get_paste(args[0])
        self.index(request, out, paste=pobj.paste)

    def paste(self, request, out):
        if not request.params.get('paste', None):
            self.index(request, out, msg=u"* You did not fill in body")
        else:
            paste = request.params['paste']
            self.pmanager.save_paste(request.params['author_name'], paste)
            self.index(request, out, paste=paste)
