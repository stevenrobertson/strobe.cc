#!/usr/bin/env python

# Site regenerator script for strobe.cc.
#
# This script is hereby released into the public domain. It's certainly not
# going to turn into a "project" and is pretty tightly coupled to my site
# anyway. The content of the site remains licensed as indicated on each page.

import os
import sys
import subprocess
import traceback
from datetime import date, datetime

try:
    import docutils.core
    from docutils.transforms.frontmatter import DocTitle
    from docutils.parsers.rst import directives
    import beaker
    import pygments_rst_directive
    from mako.template import Template
    from mako.lookup import TemplateLookup
    from BeautifulSoup import BeautifulSoup, Tag
    from mercurial import cmdutil, ui, hg
    from mercurial.error import Abort, LookupError
except ImportError:
    print "Import error. Check dependencies."
    sys.exit(0)

class SiteProcessor:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.template_lookup = TemplateLookup(
                directories=[os.path.join(root, 'code/templates')],
                output_encoding='utf-8', default_filters=['decode.utf8'])
        self.tools = {}
        self.published = []

    def _write(self, template_name, path, *args, **kwargs):
        tmpl = self.template_lookup.get_template(template_name)
        out = tmpl.render_unicode(*args, **kwargs)
        fobj = open(path, 'w')
        fobj.write(self._prettify(out))
        fobj.close()

    def _relpath(self, path):
        path = os.path.abspath(os.path.join(self.root, path))
        return path[len(self.root)+1:]

    def _has_tool(self, tool):
        """Checks if a given tool is available on the system path."""
        if tool in self.tools:
            return self.tools[tool]
        null = open('/dev/null', 'w')
        proc = subprocess.Popen(['which', tool], stderr=null, stdout=null)
        null.close()
        self.tools[tool] = (proc.wait() == 0)
        if not self.tools[tool]:
            print "Warning: Recommended tool '%s' not found." % tool
        return self.tools[tool]

    def _run_tool(self, tool, input):
        """Runs the tool ('tool' is a *list*), piping in 'in' and
        returning 'out'."""
        if self._has_tool(tool[0]):
            null = open('/dev/null', 'w')
            subp = subprocess.Popen(tool,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=null)
            (stdout, stderr) = subp.communicate(input)
            null.close()
            return stdout
        else:
            return input

    def _prettify(self, html):
        """Prettifies HTML without touching 'pre' elements."""
        # tidying does too much damage to whitespace. i'll pass.
        return html.encode('utf-8')

        soup = BeautifulSoup(html)
        prettysoup = BeautifulSoup(soup.prettify().decode('utf-8'))
        for (pre, mangled) in zip(soup.findAll('pre'),
                                  prettysoup.findAll('pre')):
            mangled.replaceWith(pre)
        return unicode(prettysoup).encode('utf-8')

    def _clean_html(self, doc, mathml=True, absolutize=False):
        """Prepares HTML for rendering. A lot of special cases."""
        bodysoup = BeautifulSoup(doc['html']['body'])
        # we need to toy with 'abstract' to get it to behave
        for abs in bodysoup.findAll(attrs={'class': 'abstract topic'}):
            doc['abstract'] = '\n'.join(map(unicode,
                                            abs.findAll('p')[1].contents))
            abs.extract()

        # and after a protracted fight with DocUtils, I've decided to do this
        # part in BeautifulSoup, too
        for hv in range(5, 0, -1):
            for hdr in bodysoup.findAll('h%d' % hv):
                newhdr = Tag(bodysoup, 'h%d' % (hv + 1), hdr.attrs)
                map(lambda chld: newhdr.insert(0, chld), reversed(hdr.contents))
                hdr.replaceWith(newhdr)

        # and come on, seriously? a table for footnotes? jeez.
        for fn in bodysoup.findAll('table',
                                   attrs={'class': 'docutils footnote'}):
            try:
                (link, text) = fn.findAll('td')
            except:
                continue
            fnwrap = Tag(bodysoup, 'div', [('class', 'fnwrap')])
            newfn = Tag(bodysoup, 'p', [('class', 'footnote')])
            fnwrap.insert(0, newfn)
            map(lambda e: newfn.insert(0, e), reversed(text.contents))
            newfn.insert(0, ' ')
            anchr = link.find('a')
            newanchr = Tag(bodysoup, 'a', anchr.attrs)
            newanchr.insert(0, unicode(anchr.find(text=True)).strip('[]'))
            newfn.insert(0, newanchr)
            fn.replaceWith(fnwrap)

        for anchr in bodysoup.findAll('a',
                attrs={'class': 'footnote-reference'}):
            sup = Tag(bodysoup, 'sup')
            newanchr = Tag(bodysoup, 'a', anchr.attrs)
            newanchr.insert(0, unicode(anchr.find(text=True)).strip('[]'))
            sup.insert(0, newanchr)
            anchr.replaceWith(sup)

        # fix some crazy Pygments nonsense
        for pre in bodysoup.findAll('pre', {'style': "line-height: 125%"}):
            del pre['style']

        # for feeds and whatnot
        def absolve(elem, name):
            href = elem[name]
            if href.startswith('/'):
                elem[name] = 'http://strobe.cc' + href
            elif '://' not in href and not href.startswith('#'):
                elem[name] = 'http://strobe.cc/' + doc['path'] + href
        if absolutize:
            map(lambda a: absolve(a, 'href'),
                bodysoup.findAll('a', {'href': True}))
            map(lambda img: absolve(img, 'src'),
                bodysoup.findAll('img', {'src': True}))

        body = unicode(bodysoup).encode('utf-8')
        if mathml and 'MathML' in doc.get('tags', ''):
            # Gotta process through itex2MML. oh, and screw you, WebKit
            body = self._run_tool(['itex2MML'], body)
        body = self._run_tool(
                ['perl', os.path.join(self.root, 'code/SmartyPants.pl')],
                body)
        return body

    def _get_changelog(self, path):
        """Grabs the changelog of a path, as a list of dicts.
        Given a file, it walks the file's directory."""
        repo = hg.repository(ui.ui(), self.root)
        if os.path.isfile(path):
            path = os.path.dirname(path)
        match = cmdutil.match(repo, ['re:^' + self._relpath(path)], {})
        paths = repo.walk(match)
        match = cmdutil.match(repo, paths, {})
        def prep(ctx, fns):
            pass
        opts = {'rev': '', 'follow': True}

        handle_ctx = lambda ctx: {
                'id': ''.join(map(lambda chr: '%x' % ord(chr), ctx.node())),
                'date': datetime.fromtimestamp(ctx.date()[0]),
                'comment': docutils.core.publish_parts(
                            ctx.description(), writer_name='html')['body']
            }
        try:
            res = map(handle_ctx,
                      cmdutil.walkchangerevs(repo, match, opts, prep))
        except Abort, LookupError:
            # Following a context can fail esp. if mq is being used
            try:
                opts.pop('follow')
                res = map(handle_ctx,
                          cmdutil.walkchangerevs(repo, match, opts, prep))
            except Abort:
                return []
        res.sort(key = lambda c: c['date'])
        return res

    def _write_history(self, doc, path):
        """Writes the history file for a document."""
        hist = os.path.join(os.path.dirname(path), 'history')
        if not os.path.isdir(hist):
            os.mkdir(hist)
        self._write("history.html", os.path.join(hist, 'index.html'), doc=doc)

    def _process_doc(self, path):
        """Processes a reStructuredText document. Writes the processed
        version to disk. If the document is published, adds it to
        self.published."""
        fobj = open(path)
        contents = fobj.read()
        fobj.close()

        # let ReST includes use relative paths when processing
        olddir = os.getcwd()
        os.chdir(os.path.dirname(path))
        docinfo = docutils.core.publish_doctree(contents).children[1]
        html = docutils.core.publish_parts(contents, writer_name='html')
        os.chdir(olddir)
        dirname = os.path.split(os.path.join(self.root, path))[0]

        doc =   {
                'html': html,
                'path': dirname[len(self.root)+1:],
                }

        # process docinfo (variables at start of article)
        if docinfo.tagname == 'docinfo':
            for child in docinfo.children:
                if child.tagname == 'field':
                    doc[child[0].astext().lower()] = child[1].astext()
                else:
                    doc[child.tagname.lower()] = child.astext()
        if 'tags' in doc:
            doc['tags'] = map(lambda s: s.strip(), doc['tags'].split(','))
        def todate(s):
            (y, m, d) = map(lambda i: int(i.lstrip('0')), s.strip().split('-'))
            return date(y, m, d)
        if 'published' in doc:
            doc['published'] = todate(doc['published'])
        if 'updated' in doc:
            doc['updated'] = map(todate, doc['updated'].split(','))

        doc['changelog'] = changelog = self._get_changelog(path)
        if changelog:
            doc['edited'] = changelog[-1]['date']
        else:
            doc['edited'] = datetime.fromtimestamp(os.path.getmtime(path))

        body = self._clean_html(doc)
        outpath = os.path.join(dirname, 'index.html')
        self._write("article.html", outpath, doc=doc, body=body)

        if 'published' in doc and 'Article' in doc.get('tags', ''):
            self.published.append(doc)
        if changelog:
            self._write_history(doc, path)

    def _build_index(self):
        """Rebuilds the site index from the stored article list."""
        path = os.path.join(self.root, 'index.html')
        self.published.sort(key=lambda doc: doc['published'])
        self._write('home.html', path, article_list=self.published)

    def _build_feed(self):
        articles = []
        for article in self.published:
            date = article['published']
            updated = ('updated' in article)
            if updated:
                date = max(article['published'], max(article['updated']))
            html = self._clean_html(article, mathml=False, absolutize=True)
            articles.append((date, updated, article, html))
        articles.sort()

        if not os.path.isdir(os.path.join(self.root, 'feeds')):
            os.mkdir(os.path.join(self.root, 'feeds'))
        path = os.path.join(self.root, 'feeds/content.xml')
        self._write("feed.xml", path, articles=articles)

    def process_dir(self):
        for root, dirs, files in os.walk(self.root):
            parent = os.path.split(root)[1]
            for file in files:
                # Only accept 'foo/foo.rst'
                if file.endswith('.rst') and file[:-4] == parent:
                    print "Processing " + os.path.join(root, file)
                    try:
                        self._process_doc(os.path.join(root, file))
                    except BaseException, e:
                        traceback.print_exc(e)
                        print "Warning: exception processing", file
        self._build_index()
        self._build_feed()

def watch(root):
    import pyinotify
    import time
    wm = pyinotify.WatchManager()
    mask = pyinotify.IN_CREATE | pyinotify.IN_MODIFY
    class HandleEvents(pyinotify.ProcessEvent):
        def __init__(self, root):
            super(HandleEvents, self).__init__()
            self.root = root
            self.timeout = time.time()
            self.process_IN_CREATE = self.process_IN_MODIFY = self.process
        def process(self, event):
            exts = ['.html', '.py', '.rst']
            if not filter(lambda e: event.name.endswith(e), exts):
                return
            if self.timeout + 10 < time.time():
                try:
                    if event.name.endswith('.py'):
                        subprocess.check_call(sys.argv)
                        sys.exit()
                    else:
                        SiteProcessor(self.root).process_dir()
                except:
                    pass
                self.timeout = time.time()
    notifier = pyinotify.Notifier(wm, HandleEvents(root))
    wdd = wm.add_watch(root, mask, rec=True)
    notifier.loop()

if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(root)
    sp = SiteProcessor(root)
    sp.process_dir()
    if 'watch' in sys.argv:
        watch(root)

