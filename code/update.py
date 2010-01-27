#!/usr/bin/env python

# Site regenerator script for strobe.cc.
#
# This script is hereby released into the public domain. It's certainly not
# going to turn into a "project" and is pretty tightly coupled to my site
# anyway. The content of the site remains licensed as indicated on each page.

import os
import sys
import subprocess
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
except ImportError:
    print "Import error. Check dependencies."
    sys.exit(0)

class SiteProcessor:
    def __init__(self, root):
        self.root = root
        self.template_lookup = TemplateLookup(
                directories=[os.path.join(root, 'code/templates')],
                output_encoding='utf-8', default_filters=['decode.utf8'])
        self.tools = {}
        self.published = []

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
        soup = BeautifulSoup(html)
        prettysoup = BeautifulSoup(soup.prettify().decode('utf-8'))
        for (pre, mangled) in zip(soup.findAll('pre'),
                                  prettysoup.findAll('pre')):
            mangled.replaceWith(pre)
        return unicode(prettysoup).encode('utf-8')

    def _clean_html(self, doc, mathml=True):
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
            newfn.insert(0, link.find('a'))
            fn.replaceWith(fnwrap)

        # fix some crazy Pygments nonsense
        for pre in bodysoup.findAll('pre', {'style': "line-height: 125%"}):
            del pre['style']

        cleaned_body = unicode(bodysoup)
        if mathml and 'MathML' in doc.get('tags', ''):
            # Gotta process through itex2MML. oh, and screw you, WebKit
            cleaned_body = self._run_tool(['itex2MML'], cleaned_body)
        return cleaned_body

    def _write_doc(self, doc, path):
        """Writes a document to the filesystem as HTML."""
        # set the document permalink path, using a solid guess
        relpath = os.path.join(self.root, path)[len(self.root)+1:]
        if relpath.endswith('index.html'):
            relpath = relpath[:-10]
        doc['path'] = relpath

        tmpl = self.template_lookup.get_template("article.html")
        cleaned = self._clean_html(doc)
        out = tmpl.render_unicode(doc=doc, cleaned_body=cleaned)
        fobj = open(path, 'w')
        fobj.write(self._prettify(out))
        fobj.close()

    def _get_changelog(self, path):
        """Grabs the changelog of a path, as a list of dicts.
        Given a file, it walks the file's directory."""
        repo = hg.repository(ui.ui(), self.root)
        if os.path.isfile(path):
            path = os.path.dirname(path)
        paths = []
        for root, dirs, files in os.walk(path):
            map(lambda fn: paths.append(os.path.join(root, fn)), files)
        match = cmdutil.match(repo, paths, {})
        def prep(ctx, fns):
            pass
        res = []
        for ctx in cmdutil.walkchangerevs(repo, match, {'rev': ''}, prep):
            id = ''.join(map(lambda chr: '%x' % ord(chr), ctx.node()))
            res.append({
                'id': id,
                'date': datetime.fromtimestamp(ctx.date()[0]),
                'comment': ctx.description()
            })
        res.sort(key = lambda c: c['date'])
        return res

    def _write_history(self, doc, path):
        """Writes the history file for a document."""
        hist = os.path.join(os.path.dirname(path), 'history')
        if not os.path.isdir(hist):
            os.mkdir(hist)
        tmpl = self.template_lookup.get_template("history.html")
        out = tmpl.render_unicode(doc=doc)
        fobj = open(os.path.join(hist, 'index.html'), 'w')
        fobj.write(self._prettify(out))
        fobj.close()

    def _process_doc(self, path):
        """Processes a reStructuredText document. Writes the processed
        version to disk. If the document is published, adds it to
        self.published."""
        fobj = open(path)
        contents = fobj.read()
        fobj.close()

        olddir = os.getcwd()
        os.chdir(os.path.dirname(path))
        docinfo = docutils.core.publish_doctree(contents).children[1]
        html = docutils.core.publish_parts(contents, writer_name='html')
        os.chdir(olddir)
        doc = {}
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
        doc['html'] = html
        self._write_doc(doc, path[:-4] + '.html')
        if 'published' in doc:
            self.published.append(doc)
        if changelog and path.endswith('index.rst'):
            self._write_history(doc, path)

    def _build_index(self):
        """Rebuilds the site index from the stored article list."""
        self.published.sort(key=lambda doc: doc['published'])
        tmpl = self.template_lookup.get_template("home.html")
        out = tmpl.render_unicode(article_list=self.published)
        fobj = open(os.path.join(self.root, 'index.html'), 'w')
        fobj.write(self._prettify(out))
        fobj.close()

    def _build_feed(self):
        articles = []
        for article in self.published:
            date = article['published']
            updated = ('updated' in article)
            if updated:
                date = max(article['published'], max(article['updated']))
            html = self._clean_html(article, mathml=False)
            articles.append((date, updated, article, html))
        tmpl = self.template_lookup.get_template("feed.xml")
        out = tmpl.render_unicode(articles=articles)
        fobj = open(os.path.join(self.root, 'feeds/content.xml'), 'w')
        fobj.write(BeautifulSoup(out).prettify())
        fobj.close()

    def process_dir(self):
        for root, dirs, files in os.walk(self.root):
            for file in files:
                if file.endswith('.rst'):
                    print "Processing " + os.path.join(root, file)
                    self._process_doc(os.path.join(root, file))
        self._build_index()
        self._build_feed()

if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sp = SiteProcessor(root)
    sp.process_dir()

