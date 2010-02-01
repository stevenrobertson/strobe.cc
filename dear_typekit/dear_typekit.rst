Dear Typekit...
===============

:Author: Steven Robertson
:Contact: steven@strobe.cc
:Published: 2009-10-28
:Tags: Typography, Web, Article
:Abstract:
    If you're using a supported browser, the fonts you see on this site are
    provided by Typekit_. It's generally an awesome service, but it doesn't yet
    work for most Linux users.

.. _Typekit: http://typekit.com/

**Update**: Typekit has done one better, not only using Gecko browser
detection but also `using WOFF for Firefox 3.6 and up`_. Took a few months,
but they got it done the right way.

.. _using WOFF for Firefox 3.6 and up:
    http://blog.typekit.com/2010/01/21/typekit-supports-woff-in-firefox-3-6/

----

Dear Typekit,

Your service is currently broken. The good news: it's a one-line fix.

The JavaScript generated for each client includes the folowing regex against
``navigator.userAgent``, intended to check whether or not the browser is
compatible with @font-face and Typekit: 

.. code:: javascript

    function(D){
        var C=D.match(/Firefox\/(\d+\.\d+)/);
        if(C){
            var B=C[1];
            return parseFloat(B)>=3.5
        }
    }

The problem is that many Linux distributors `can't legally call their browser
Mozilla Firefox`_. The Debian project is a notable example; they've rebranded
their Firefox build "Iceweasel", and chosen similar names for other Mozilla
software. To avoid this dispute, other distributions have taken to using the
code-name for a particular Firefox build as the name—I'm currently posting this
from a browser called "Shiretoko". This doesn't even cover contexts in which
the Gecko engine is embedded by other applications which fully support TypeKit,
such as Mozilla SeaMonkey.

.. _can't legally call their browser Mozilla Firefox:
    http://en.wikipedia.org/wiki/Mozilla_Corporation_software_rebranded_by_the_Debian_project#Origins_of_the_issue_and_of_the_Iceweasel_name

It would be unreasonable to check for every variant of the browser name in the
JavaScript handed out by your application. Fortunately, Mozilla has made a
provision allowing the right decision to be made, regardless of browser name.
Here's the value of ``navigator.userAgent`` from the official build of
Firefox: ::

    Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20091021 Firefox/3.5.3

Here's what it looks like in my browser: ::

    Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20091021 Shiretoko/3.5.3

Note the common string component ``rv:1.9.1.3``; this identifies the Gecko
release version. Since browsers based on the Gecko rendering engine get most of
their characteristics from that engine, you can in almost all cases simply
check the Gecko version instead of the Firefox version\ [#]_.

.. [#]  Ideally, you shouldn't use the user-agent string at all to do browser
        detection; `Mozilla says why, and what to do instead`_. But often
        user-agent checking is the pragmatic solution.

.. _Mozilla says why, and what to do instead:
    https://developer.mozilla.org/en/Gecko_User_Agent_Strings

Doing so is really this simple:

.. code:: javascript

    function(D){
        var C=D.match(/rv:(\d+\.\d+).*Gecko\//);
        if(C){
            var B=C[1];
            return parseFloat(B)>=1.9
        }
    }

Since this change is a simple one, and since Gecko's user-agent strings have
been standardized for a while, I hope that you can make it soon, and enable
support for the many users using browsers whch would otherwise work flawlessly
with Typekit.

Thank you for providing an awesome and much-needed service.

Steven

PS: For users of unbranded Firefox versions who just want things to work now:
go to ``about:config`` and change the string
``general.useragent.extra.firefox`` to ``Firefox/3.5.3`` (or your current
version). But remember to update it along with your browser.

