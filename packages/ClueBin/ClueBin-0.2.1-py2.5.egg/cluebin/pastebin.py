import webob
from StringIO import StringIO
import pygments
from pygments import lexers
from pygments import formatters
from pygments import util
from xml.sax import saxutils
from cluebin import paste as pastebase
from cluebin import utils


class PasteBinApp(object):
    """WSGI app representing a pastebin.

      >>> app = PasteBinApp()
    """

    def __init__(self):
        self.pmanager = pastebase.PasteManager()

    def __call__(self, environ, start_application):
        request = webob.Request(environ)
        response = webob.Response(content_type='text/html')

        out = StringIO()

        handler = self.index
        pieces = [x for x in environ['PATH_INFO'].split('/') if x]
        if pieces and hasattr(self, pieces[0]):
            handler = getattr(self, pieces[0])

        redirect = handler(request, response, out, *pieces[1:])
        if redirect:
            start_application('301 Moved Permanently',
                              [('Location', redirect)])
            return ''

        # Lazy man's templating
        top = u'''
        <html>
          <head>
            <title>PasteBin</title>
            <style>
             PRE { margin: 0; }
            .code, .linenos { font-size: 90%; }
            .source { border: 1px #999 dashed; margin: 0; padding: 1em }
            .left { width: 70%; float: left; }
            .right { margin-left: 2em; width: 20%; float: left; }
            .field { margin-bottom: 1em; }
            .field LABEL { font-weight: bold; width: 20%; display: block; float: left; }
            .field INPUT { width: 80% }
            .field TEXTAREA { width: 100%; height: 10em }
            .previous_paste DD { margin-left: 0; }
            .clear { display: block; clear; both; }
            .header { font-size: 90%; float: right; }
            </style>
          </head>
          <body><div id="main"><div class="header">ClueBin v0.2.1 by <a href="http://www.serverzen.com">ServerZen Software</a></div>
          '''

        #footer = dist.name + ' v' + dist.version
        footer = ''
        bottom = u'<div class="footer">%s</div><div class="clear"><!-- --></div></div></body></html>' % footer

        response.unicode_body = top + out.getvalue() + bottom
        return response(environ, start_application)

    def paste_listing(self, request, response, out):
        print >> out, u'<fieldset><legend>Previous Pastes</legend><ul>'

        for pobj in self.pmanager.get_pastes():
            if pobj.date is not None:
                pdate = pobj.date.strftime('%x at %X')
            else:
                pdate = 'UNKNOWN'
            print >> out, u'<li><a href="%s">Post by: %s on %s</a></li>' % \
                  (utils.url(request, 'pasted/%i' % pobj.pasteid),
                   pobj.author_name, pdate)

        print >> out, u'</ul></fieldset>'

    def index(self, request, response, out, msg=u'', paste_obj=None):
        if msg:
            msg = u'<div class="message">%s</div>' % msg

        author_name = request.params.get('author_name', u'')
        if not author_name:
            author_name = request.cookies.get('cluebin.author_name', u'')
        if isinstance(author_name, str):
            author_name = unicode(author_name, 'utf-8')
        language = request.cookies.get('cluebin.language', u'')
        if isinstance(language, str):
            language = unicode(language, 'utf-8')

        paste = u''
        if paste_obj is not None:
            paste = paste_obj.paste or u''
            try:
                if paste_obj.language:
                    l = lexers.get_lexer_by_name(paste_obj.language)
                else:
                    l = lexers.guess_lexer(paste_obj.paste)
                language = l.aliases[0]
            except util.ClassNotFound, err:
                # couldn't guess lexer
                l = lexers.TextLexer()
            formatter = formatters.HtmlFormatter(linenos=True, cssclass="source")
            formatted_paste = pygments.highlight(paste, l, formatter)

            print >> out, u'''
              <style>%s</style>
              <dl class="previous_paste">
              <dt>Previous Paste</dt>
              <dd>Format: %s</dd>
              <dd>%s</dd>
              </dl>
            ''' % (formatter.get_style_defs(), l.name, formatted_paste)

        lexer_options = u'<option value="">-- Auto-detect --</option>'
        all = [x for x in lexers.get_all_lexers()]
        all.sort()
        for name, aliases, filetypes, mimetypes_ in all:
            selected = u''
            if language == aliases[0]:
                selected = u' selected'
            lexer_options += u'<option value="%s"%s>%s</option>' % (aliases[0],
                                                                    selected,
                                                                    name)

        print >> out, u'''
            %s
            <div class="left">
            ''' % msg

        print >> out, u'''
            <form action="%(action)s" method="POST">
              <fieldset>
                <legend>Paste Info</legend>
                <div class="field">
                  <label for="author_name">Name</label>
                  <input type="text" name="author_name" value="%(author_name)s" />
                </div>
                <div class="field">
                  <label for="language">Language</label>
                  <select name="language">
%(lexers)s
                  </select>
                </div>
                <div class="field">
                  <label for="paste">Paste Text</label>
                  <textarea name="paste">%(paste)s</textarea>
                </div>
                <input type="submit" />
              </fieldset>
            </form>
            </div>
        ''' % {'action': utils.url(request, 'paste'),
               'paste': saxutils.escape(paste),
               'lexers': lexer_options,
               'author_name': author_name}

        print >> out, u'<div class="right">'
        self.paste_listing(request, response, out)
        print >> out, u'</div>'

    def pasted(self, request, response, out, *args):
        pobj = self.pmanager.get_paste(args[0])
        self.index(request, response, out, paste_obj=pobj)

    def paste(self, request, response, out):
        if not request.params.get('paste', None):
            self.index(request, response, out, msg=u"* You did not fill in body")
        else:
            paste = request.params['paste']
            author_name = request.params['author_name']
            language = request.params['language']
            response.set_cookie('cluebin.author_name', author_name)
            response.set_cookie('cluebin.language', language)

            if isinstance(author_name, str):
                author_name = unicode(author_name, 'utf-8')
            if isinstance(language, str):
                language = unicode(language, 'utf-8')
            if isinstance(paste, str):
                paste = unicode(paste, 'utf-8')

            pobj = self.pmanager.save_paste(author_name, paste, language)

            newurl = utils.url(request, 'pasted/%s' % str(pobj.pasteid))
            return newurl


def make_app(global_config, datastore=None):
    app = PasteBinApp()
    if datastore is not None:
        app.pmanager.datastore = datastore
    return app


def build_datastore(datastore_name, *datastore_args):
    f = utils.importattr(datastore_name)
    return f(*datastore_args)


def main(cmdargs=None):
    from wsgiref import simple_server
    import sys
    import optparse
    logger = utils.setup_logger()

    if cmdargs is None:
        cmdargs = sys.argv[1:]

    storages = ['cluebin.googledata.GooglePasteDataStore',
                'cluebin.sqldata.SqlPasteDataStore']

    parser = optparse.OptionParser()
    parser.add_option('-i', '--interface', dest='interface',
                      default='0.0.0.0',
                      help='Interface to listen on (by default it is '
                           '0.0.0.0 which '
                           'is shorthand for all interfaces)')
    parser.add_option('-p', '--port', dest='port',
                      default='8080',
                      help='Port to listen on (by default 8080)')
    parser.add_option('-s', '--storage', dest='storage_name',
                      default='',
                      help='Storage to use for pastes (by default '
                           'non-persistent), cluebin-provided options are: %s'
                           % str(storages))
    (opts, args) = parser.parse_args(cmdargs)

    appargs = [{}]

    datastore = None
    if opts.storage_name:
        datastore = build_datastore(opts.storage_name, *args)
        logger.info('Using storage: %s' % (opts.storage_name))
        logger.info('Using storage arguments: %s' % str(args))
    app = make_app(datastore)
    server = simple_server.make_server(opts.interface, int(opts.port), app)

    logger.info("ClueBin now listening on %s:%s using non-persistent datastore"
                % (opts.interface, opts.port))
    server.serve_forever()

    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
