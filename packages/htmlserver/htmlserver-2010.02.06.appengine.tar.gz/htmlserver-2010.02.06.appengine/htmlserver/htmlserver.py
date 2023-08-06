## python3.1 setup.py dev --htmlserver=pikapika
## from __future__ import pseudosugar
## from __future__ import py3to2

## app.yaml
"""application: {name}
version: {version}
api_version: {api_version}
runtime: python
handlers:
- url: /admin
  script: url.py
  login: admin
- url: /admin/.*
  script: url.py
  login: admin
# - url: /kaizhu/admin/.*
  # script: url.py
  # login: admin
# - url: /test.*
  # script: url.py
  # # login: required
# - url: /(.*\.(css|gif|jpg|png))
  # static_files: \1
  # upload: (.*\.(css|gif|jpg|png))
# - url: /(url_\w+\.html)
  # static_files: \1
  # upload: /(url_\w+\.html)
- url: /.*
  script: url.py
"""
## END

import os, re, sys
if sys.version_info[0] >= 3: ######## python3.1
  import htmlserver; from htmlserver import *; import signal, time

  def update(KWDS, force = None, modified = 'htmlserver.py index.html'.split(' '), update = 'app.yaml url.py url_main.html'.split(' ')):
    # print@@ os.getcwd()
    if not force and all(os.path.exists(aa) for aa in update) and min(os.path.getmtime(aa) for aa in update) >= max(os.path.getmtime(aa) for aa in modified): return
    ss = open('htmlserver.py').read(); open('app.yaml', 'w').write@@ re.search('(?s)\n## app.yaml\n"""(.*?)"""\n## END\n', ss).group(1).format(**KWDS); open('url.py', 'w').write@@ Py3to2.py3to2@@ ss
    for aa in re.finditer@@ '(?s)(<!-- (url_\w+) -->.*?<!-- END -->\n)', open('index.html').read(): ss, name = aa.groups(); open('%s.html' % name, 'w').write(ss)

  def serve_forever(**KWDS):
    if not KWDS.get('setup', None): raise Exception('htmlserver.htmlserver.serve_forever can only be called from setup.py')
    try: subprocess.call@@ ['python2.5', '--version']
    except: print@@ 'ERROR: python2.5 not found - please install - required by google appengine'; raise
    if not os.path.exists('google_appengine'):
      url = 'http://googleappengine.googlecode.com/files/google_appengine_1.3.0.zip'
      print@@ 'downloading {} ...'.format(url); import urllib.request; fpath, headers = urllib.request.urlretrieve(url); print@@ ' ... done'
      print@@ 'extracting {} ...'.format@@ os.path.basename@@ url; import zipfile; zipfile.ZipFile(fpath).extractall(); print@@ ' ... done'
    dpath = KWDS['name']
    if not os.path.exists(dpath): system@@ 'mkdir {}'.format(dpath)
    os.chdir(dpath)
    # exit()
    if not os.path.exists('google'): system@@ 'ln -s ../google_appengine/google'
    if not os.path.exists('htmlserver.py'): system@@ 'cp ../htmlserver/htmlserver.py .'
    if not os.path.exists('index.html'): system@@ 'cp ../htmlserver/index.html .'
    update(KWDS, force = True); proc = subprocess.Popen(['python2.5', '../google_appengine/dev_appserver.py', '../{}'.format(dpath)]) ## server
    try:
      # print@@ KWDS
      # pass
      # time.sleep(1)
      if eval(KWDS['serve']):
        while True: update(KWDS); time.sleep(1) ## update
      else: time.sleep(1)
    # except KeyboardInterrupt: pass
    finally: os.kill(proc.pid, signal.SIGTERM) ## kill server
## END



else: ######## python2.5
  class appengine(object): ## namespace
    import cgi
    from urllib import parse, request
    from google.appengine.api import images, memcache, users
    from google.appengine.ext import webapp
    from google.appengine.ext.webapp import util, template, RequestHandler
    from google.appengine.ext import db

  class URL(appengine.RequestHandler):
    def __init__(self):
      self.handlers.append(self)
      if 1: self.printerr@@ '\nhandlers', self.handlers

    @staticmethod
    def dispatch():
      for aa in 'AUTH_TYPE CONTENT_LENGTH CONTENT_TYPE GATEWAY_INTERFACE PATH_INFO PATH_TRANSLATED QUERY_STRING REMOTE_ADDR REMOTE_HOST REMOTE_IDENT REMOTE_USER REQUEST_METHOD SCRIPT_NAME SERVER_NAME SERVER_PORT SERVER_PROTOCOL SERVER_SOFTWARE'.split(' '): setattr@@ URL, aa, os.environ.get(aa, None)
      URL.handler = url_main; URL.handlers = []; URL.path = URL.PATH_INFO[1:].split('/'); URL.pathi = 0; URL.query = appengine.parse.parse_qs(URL.QUERY_STRING)
      if 'url_extra' in globals():
        for aa, bb in vars(url_extra).iteritems():
          if type(bb) is type and issubclass(bb, URL): setattr(url_main, aa, bb)
      self = URL(); self.walk_handler()
      if not self.path[-1]: del self.path[-1] ## del trailing '/'
      appengine.util.run_wsgi_app@@ appengine.webapp.WSGIApplication(self.handler.map(self.handler), debug = True)
      if 1: self.printerr@@ 'dispatch', 'path=', self.path, 'pathi=', self.pathi, 'query=', self.query, 'handlers=', self.handlers

    # def get(self): self.write@@ 'text/html', self.render('url_main.html')

    # def get(self):
      # # self.write@@ 'text/html', self.render('url_main.html')
      # # self.printerr@@ 'hello'
      # # self.write@@ 'text/html', vars@@ type@@ self
      # # self.write@@ 'text/html', self.__class__.__dict__
      # # for aa, bb in self.__dict__.iteritems():
      # for aa, bb in vars(self.__class__).iteritems():
        # if type(bb) is type and issubclass(bb, URL):
          # # self.write@@ 'text/plain', aa
          # # self.write@@ 'text/html', self.path #'<a href="data/test.html">test.html</a>'
          # # self.write@@ 'text/html', '/%s/%s' % ('/'.join(self.path), aa[4:])
          # self.write@@ 'text/html', '<br><a href="/%s/%s">%s</a></br>' % ('/'.join(self.path), aa[4:], aa[4:])

    def get(self):
      dpath = 'http://%s:%s' % (self.SERVER_NAME, self.SERVER_PORT)
      for aa, bb in vars(self.__class__).iteritems():
        if type(bb) is type and issubclass(bb, URL): url = '%s/%s' % (dpath, '/'.join(self.path + [aa[4:]])); self.write@@ 'text/html', '<br><a href="%s">%s</a></br>' % (url, url)

    # def login(self): login = 'logout' if appengine.users.get_current_user() else 'login'; return '<a href="%s">%s</a>' % (appengine.users.create_logout_url(self.request.uri) if login == 'logout' else appengine.users.create_login_url(self.request.uri), login)
    # def login(self): login = 'logout %s' % appengine.users.get_current_user().nickname() if appengine.users.get_current_user() else 'login'; return '<a href="%s">%s</a>' % (appengine.users.create_logout_url(self.request.uri) if login == 'logout' else appengine.users.create_login_url(self.request.uri), login)

    def login(self): login = 'logout' if appengine.users.get_current_user() else 'login'; return '<a href="%s">%s</a>' % (appengine.users.create_logout_url(self.request.uri) if login == 'logout' else appengine.users.create_login_url(self.request.uri), login)

    @staticmethod
    def map(type): return [('/.*', type)]

    def printerr(self, *args): sys.stderr.write('\t'.join(str(aa) for aa in args)); sys.stderr.write('\n')

    def render(self, fpath, **kwds): kwds['self'] = self; return appengine.template.render(fpath, kwds)

    def walk_handler(self):
      if self.pathi >= len(self.path): return
      for aa, bb in vars(self.handler).iteritems():
        if type(bb) is type and issubclass(bb, URL) and aa[4:] == self.path[self.pathi]: self.handler = bb; self.pathi += 1; return self.walk_handler()

    def write(self, content_type, *args): self.response.headers['Content-Type'] = content_type; return self.response.out.write@@ '\t'.join(str(aa) for aa in args) + '\n'

  class url_main(URL):
    class url_admin(URL):
      class url_debug(URL):
        def get(self):
          for aa in appengine, self:
            for bb in dir(aa):
              if bb[0] != '_': self.write@@ 'text/html', '<li>', bb, repr(getattr(aa, bb))[:64].replace('<', '>'), '</li>'

    class url_login(URL):
      def get(self): self.write@@ 'text/html', self.login()

    class url_test(URL):
      class url_css(URL):
        def get(self): self.write@@ 'text/html', self.render('url_test_css.html')

      class url_guestbook(URL):
        class DataGuestbook(appengine.db.Model):
          user = appengine.db.UserProperty()
          date = appengine.db.DateTimeProperty(auto_now_add = True)
          message = appengine.db.StringProperty(multiline = True)
          avatar = appengine.db.BlobProperty()

        def get(self):
          if 'get_avatar' in self.query:
            post = appengine.db.get@@ self.request.get@@ 'get_avatar'
            if post.avatar: self.write@@ 'image/png', post.avatar
          else:
            posts = self.DataGuestbook.all().order('-date').fetch(4)
            self.write@@ 'text/html', self.render('url_test_guestbook.html', posts = posts)

        def post(self):
          data = self.DataGuestbook()
          if appengine.users.get_current_user(): data.user = appengine.users.get_current_user()
          data.message = self.request.get('message')
          self.printerr@@ repr@@ data.message
          avatar = self.request.get('avatar')
          if avatar: data.avatar = appengine.db.Blob@@ appengine.images.resize@@ avatar, 32, 32
          data.put(); self.redirect('/test/guestbook')

      class url_image(URL):
        def get(self):
          if 'get_image' in self.query:
            img = appengine.memcache.get@@ 'url_test_image'
            if img: self.write@@ 'image', img
          else: self.write@@ 'text/html', self.render('url_test_image.html')

        def post(self): appengine.memcache.set@@ 'url_test_image', appengine.images.resize@@ self.request.get('img'), 256, 256; self.redirect('/test/image')

## END
  URL.dispatch()
