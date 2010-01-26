#!/usr/bin/env python

# Site regenerator script for strobe.cc.

import os
import sys
import subprocess
import datetime

try:
    import docutils.core
    from docutils.transforms.frontmatter import DocTitle
    from docutils.parsers.rst import directives
    import beaker
    import pygments_rst_directive
    from mako.template import Template
    from mako.lookup import TemplateLookup
    from BeautifulSoup import BeautifulSoup, Tag
except ImportError:
    print "Import error. Check dependencies."
    sys.exit(0)

class SiteProcessor:
    def __init__(self, root):
        self.root = root
        self.template_lookup = TemplateLookup(
                directories=[os.path.join(root, 'code/templates')],
                output_encoding='utf-8', default_filters=['decode.utf8'])
        self.published = []
        with open('/dev/null', 'w') as null:
            if subprocess.Popen(['which', 'itex2MML'],
                                stderr=null, stdout=null).wait() == 0:
                self.itex2MML_avail = True
            else:
                print "Warn: itex2MML not found. MathML will not be rendered."
                self.itex2MML_avail = False

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
        if self.itex2MML_avail and mathml and 'MathML' in doc.get('tags', ''):
            # Gotta process through itex2MML. oh, and screw you, WebKit
            itex = subprocess.Popen('itex2MML',
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            (stdout, stderr) = itex.communicate(cleaned_body)
            cleaned_body = stdout

        return cleaned_body

    def _write_doc(self, doc, path):
        """Writes a document to the filesystem as HTML."""
        # set the document permalink path, using a solid guess
        relpath = os.path.relpath(path, self.root)
        if relpath.endswith('index.html'):
            relpath = relpath[:-10]
        doc['path'] = relpath

        tmpl = self.template_lookup.get_template("article.html")
        cleaned = self._clean_html(doc)
        with open(path, 'w') as f:
            out = tmpl.render_unicode(doc=doc, cleaned_body=cleaned)
            f.write(out.encode('utf-8'))

    def _process_doc(self, path):
        """Processes a reStructuredText document. Writes the processed
        version to disk. If the document is published, adds it to
        self.published."""
        with open(path) as f:
            contents = f.read()
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
            return datetime.date(y, m, d)
        if 'published' in doc:
            doc['published'] = todate(doc['published'])
        if 'updated' in doc:
            doc['updated'] = map(todate, doc['updated'].split(','))
        doc['html'] = html
        self._write_doc(doc, path[:-4] + '.html')
        if 'published' in doc:
            self.published.append(doc)

    def _build_index(self):
        """Rebuilds the site index from the stored article list."""
        self.published.sort(key=lambda doc: doc['published'])
        tmpl = self.template_lookup.get_template("index.html")
        with open(os.path.join(self.root, 'index.html'), 'w') as f:
            out = tmpl.render_unicode(article_list=self.published)
            f.write(out.encode('utf-8'))

    def process_dir(self):
        for root, dirs, files in os.walk(self.root):
            for file in files:
                if file.endswith('.rst'):
                    print "Processing " + os.path.join(root, file)
                    self._process_doc(os.path.join(root, file))
        self._build_index()


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sp = SiteProcessor(root)
    sp.process_dir()

