#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
# author: javi santana jsantfer@gmail.com

from juno import *
from glob import glob
from os import mkdir
from os.path import join, basename, exists, realpath
from mercurial import hg,ui
from creoleparser import text2html

init({'dev_port':8000,'use_static': True, 'static_root': realpath('.'), 'use_templates': True})

# -- models

class Repo(object):
  def __init__(self, path):
    uio = ui.ui(debug=True,verbose=True)
    self.path = path
    self.repo = hg.repository(ui=uio, path='.', create=False)
    if not exists(self.path):
      mkdir(self.path)
    
  def is_under_version_control(self, f):
    return f in self.repo.status()[4]

  def all(self):
    return [Page(f, self.repo) for f in glob(join(self.path,'*')) if '.' not in f] #all files whiout extension
  
  def get_page(self, name):
    fn = join(self.path,name)
    return Page(fn, self.repo) 
    
class Page(object):
  """ repr a wiki page """
  
  def __init__(self, filename, repo):
    self.filename = filename
    self.repo = repo

  def pagename(self):
    #return basename(self.filename)
    return self.filename

  def save(self, data, comment = ''):
    open(self.filename, 'w').write(data)
    if self.pagename() in self.repo.status()[4]:  #not added
      self.repo.add([self.pagename()])
    self.repo.commit([self.pagename()], text=comment if comment else 'no comments')

  def remove(self):
    pass
  
  def to_html(self):
    s = self.to_text().decode('utf-8')
    return text2html(s, encoding='utf-8')

  def to_text(self):
    return open(self.filename).read() if exists(self.filename) else ''

 

r = None

#-- view

edit_form = """
<h1> edit %(page)s</h1>
<form action='save' method=post>
  <textarea name='content' cols=80 rows=%(lines)d>%(content)s</textarea>
  comment: <input name='comment'></textarea>
  <button type=submit>save</button>
</form>
"""

html = """
<html>
      <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>%(page)s</title>
        <style>
          hr { border: 1px solid red }
          form { display: inline; margin-right: 15px }
          p { line-height:1.5em ; margin:1em 0 ; }
          h2 { border-top:4px solid #E0E0E0; font-size:150%%; margin-top:1.5em; padding-top:0.5em; }
          a { color:#4183C4; }
          #content { margin:0 auto; padding:0 3em;  text-align:left; background-color:#F8F8F8; border:1px solid #DEDEDE;
              font-family:helvetica,arial,clean,sans-serif; width:48em; font-size:13.34px; }
          pre { background-color:#F8F8FF ; border:1px solid #DEDEDE ; color:#444444 ; font-size:90%% ;
            line-height:1.5em ; margin:1em 0 ; overflow:auto ; padding:0.5em ;
            font-family:Monaco,"Courier New",monospace; }
          .tools { text-align: right; padding-top:0.5em;}
        </style>
      </head>
      <body>
        <div id='content'>
          <div class='tools'> <a href='%(page)s/edit'> edit </a> </div>
          %(body)s 
        </div>
      </body>
</html>
"""

#-- controller

@route('/:page/edit/')
def edit(web, page):
  content = r.get_page(page).to_text()
  lines = content.count('\n') + 3
  e = edit_form % {'content':r.get_page(page).to_text(), 'page': page, 'lines': lines}
  return html % {'page': page, 'body': e }

@route('/:page/save')
def save(web, page):
  r.get_page(page).save(web.input()['content'], web.input()['comment'])
  redirect('/%s' % page)

@route('/')
def index(web): redirect('/javier-santana')
 
@route('/:page/')
def page(web, page):
  body = "%s" % (r.get_page(page).to_html())
  return html % {'page': page, 'body': body}

if __name__ == '__main__':
  import sys
  if len(sys.argv) == 2:
    r = Repo(sys.argv[1])
    config('static_root',realpath(sys.argv[1]))
    run()
  else:
    print "usage: python hg-wiki folder"



