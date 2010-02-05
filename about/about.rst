Here are some facts for you
===========================

:Author: Steven Robertson
:Contact: steven@strobe.cc
:Copyright: 2010 Steven Robertson. CC Attribution 3.0 US.
:Tags: Static
:Published: 2010-02-01

Autobiographical facts
----------------------

At the risk of inundating you with my name—this makes for six instances between
the home and about pages of the site—the first fact I would like to mention is
that the author of all the content on this site is Steven Robertson. Facts two
and three are that I have some opinions on technical matters and that I share
them on this site, respectively. These facts together are important, as
opinions may provoke a strong emotional reaction, and when combined the facts
will enable you to deliver a strongly-worded commendation or rebuttal to my
face with slightly more confidence than if you did not know who I was or if I
was aware that my inflammatory opinions were exposed for the world to see,
should we ever meet at a party.

Fact four: we are unlikely to meet at a party. This is a result of facts five,
wherein I am currently living in Orlando, and six, whereby Orlando has less of
the sort of party you would go to chat with fellow hackers and more the sort of
party where you'd try aggressively to forget you're currently in Florida. Fact
seven is that I don't really care for Florida.

Fact eight: I am remarkably fond of footnotes\ [#]_.

.. [#]  If you're viewing them on the site, they're technically margin notes
        (fact 8A).

Site-related facts (not enumerated)
-----------------------------------

I write technical articles on this site, usually related to whatever I'm
currently working on. The articles tend to be longer, and to get checked in to
version control (and thus to the site) far before they're ready to "publish" by
pushing to the index and RSS feed. My current interests include massively
parallel algorithms, video coding, open consumer electronics, web design,
music, and pedagogy—a pretty typical combination—and the site's content has
thus far tracked that set pretty closely.

The site is rendered as static HTML files, using docutils_ to render
ReStructuredText_ documents, BeautifulSoup_ to do some reprocessing, itex2MML_
to render MathML_ for those documents which need it, Pygments_ for code boxes,
and Mako_ templates to bring it all together. Comments are handled off-site by
Disqus_, and fonts are provided by Typekit_. This is all running on a VPS
provided by PRGMR_, although it could of course work just as well on a shared
hosting solution if it was regenerated at my workstation instead of on the
server.

.. _docutils: http://docutils.sourceforge.net/
.. _ReStructuredText: http://docutils.sourceforge.net/rst.html
.. _BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/
.. _itex2MML: http://golem.ph.utexas.edu/~distler/blog/itex2MML.html
.. _MathML: http://www.w3.org/Math/
.. _Pygments: http://pygments.org/
.. _Mako: http://www.makotemplates.org/
.. _Disqus: http://disqus.com/
.. _Typekit: http://typekit.com/
.. _PRGMR: http://prgmr.com/xen/

The source for each article, often including code I've written to perform
benchmarks or demonstrate ideas, is all under Mercurial_ version control, as
well as the code and templates; in fact, the site is itself the actual
Mercurial repository, regenerated in-place by a commit hook. I've written a bit
about `why I believe this is the right approach`_, but in short all you need to
know is that you can get the entire history of the site (since moving to the
Mercurial backend, anyway) by simply doing::

    $ hg clone http://strobe.cc strobe_cc

.. _Mercurial: http://mercurial.selenic.com/
.. _why I believe this is the right approach: /mixing_code_and_data/

I write articles very slowly, although I'm working on that, and as a result
often make a relatively high number of edits to articles during the writing
process. The ``Published`` docinfo variable is set to display articles in the
feed and on the site index, but the pages are visible as soon as they are
uploaded regardless of whether they've been published, and will probably keep
being edited for some time thereafter as I obsessively tweak sentences that
annoy me. Rather than inundate subscribers to the `RSS feed`_ with tiny
updates, or cut them off entirely from significant updates when they happen,
the feed has an out-of-band update mechanism (using the ``Updated`` variable in
the docinfo section of each document's ReStructuredText source).

.. _RSS feed: /feeds/content.xml

The HTML and CSS aims to be as standards-compliant as possible, although I've
mostly been testing in Firefox 3.6 on Linux. I also occasionally use MathML in
my articles, which WebKit-based browsers don't touch, but I might write a
fallback system some time.

