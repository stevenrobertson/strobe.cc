- title: Roll your own JavaScript lambda syntax
- published: 2010-12-09
- updated: 2012-07-01
- summary:
    The syntax for anonymous functions in JavaScript sucks. I found it well
    worth the trouble to design and implement something better.

---

*Update:* The point I made here about flow being a critical part of
language design? I still totally stand by it. On the other hand, if you're
looking for an actual, practical way to make writing JavaScript less sucky
for you, I highly recommend `CoffeeScript <http://coffeescript.org>`_.

.. contents::

In my current project, I'm using the jQuery_ and Protovis_ JavaScript
libraries. Idiomatic jQuery code often uses lambdas_ for event handlers,
and Protovis essentially requires them to get anything done.

This is a problem, because the syntax for JavaScript lambdas is downright
terrible. Every time I have to type ``(function(d) { return d.tx; })``, a
baby seal dies. Because I have killed it. Out of *rage*.

So I set out to design and implement a better variant.

Why bother?
-----------

*"It's just syntax. So what if you have to type a few extra characters?"*

Between evaluating syntax options, learning a Haskell parsing library,
writing the parser, and various tests and tweaks, building my alternative
lambda syntax took about a day. Stack up the time it takes to type out
``function(...) { return ...;}`` once for each lambda in, say, a year's worth of
coding, and it's almost certainly less. So, yeah, if typing time was the
factor here, it's hard to justify building your own personal lambda syntax.

But syntax is about much more than keystrokes. It's about flow.

As `van Rossum famously noted`_, code is read more often than it is
written. The more complex an application, the more difficult it is to keep
the entire thing in memory, moreso when parts of the code aren't authored
by you. An ugly bit of syntax confronts us every time we return to
previously-written code, and when we have to claw understanding from a
steaming pile of braces for the fifth time, it can build frustration, even
resentment — or just interrupt a train of thought.

Plus, programmers are lazy creatures. If a language construct is obnoxious
to type, we'll go out of our way to avoid using it — even when the
resulting code is less clear or technically sound. After all, when I'm
holding a complicated data structure in my head, the last thing I want to
do is start counting braces.

Implementation
--------------

The sane approach to tweaking JavaScript syntax is to modify the source
before it hits the browser's script engine. This can be done client-side or
server-side.

The stock Protovis library actually includes client-side support for
rewriting function expressions (see below_) to use standard syntax on
browsers which don't support them. It does this by running a
regex-based parser\ [#]_ over the source and feeding it to eval(). To get
the source to Protovis, you can either embed it into the page, in a
``script`` tag with a special ``type`` attribute
(``text/javascript+protovis``), or load it yourself with an XHR and pass it
in.

.. [#]  I know, "eww". But it does work.

This method has a number of flaws, not least of which is elegance. Unless
you handle things manually, you can't see into the namespace of code loaded
this way from outside the eval(), and many JavaScript debuggers don't seem
to look inside such statements. Then there's the need for the XHR;
combining ``src`` and ``type`` to reprocess remote scripts doesn't seem to
work either.

Better to have your server do it. For JavaScript that gets served
statically, you can configure your parser to update the static files from
your source in your deployment script or using commit hooks. During local
development, you might consider using a utility to monitor your source
directories and trigger rebuilds (`here's mine`__) so that you can see
changes to your JavaScript instantly.

.. __: http://bitbucket.org/srobertson/watchbuildrun

If your script is inline, or served by your application, the process is
even easier — just hook your parser into your template engine, maybe add a
bit of caching, and you're all set. The specifics of this vary wildly from
framework to framework, but most provide at least one method for this to
work.

There are many valid approaches, of course. Do whatever works best for your
project.

In my case, Yesod_ allows you to depend on multiple JavaScript snippets
from page templates. On rendering a page, the framework deduplicates the
snippets, does some variable and URL substitution, and assembles the
results into a single hash-named file that gets served statically for
inclusion into a page's ``<head>``. I just tossed my parser in front of
this mechanism, which took care of everything. (Details and code in a later
article.)


Choosing a syntax
-----------------

To compare my options, I took three different functions from the source,
tried different approaches, and picked the one I liked best.  The first of
these functions, ``mkItem()``, contains a typical jQuery one-line event
handler. ::

    function mkItem(acts, node) {
      return $('<div />', {'class': 'flowItem'}).html(node.activity)
        .click(function () { $(this).replaceWith(mkSel(acts, node)); });
    }

``mkProb()`` nests one event handler inside the declaration of another.
The example is a bit pathological, and I certainly wouldn't put this in a
tutorial, but it's code that I actually wrote. Since I'm maintaining it, I
want to make sure that the new syntax works here, too. ::

    function mkProb(node, choice) {
      return $('<div />', {'class': "flowProb"}).html(choice.prob)
        .click(function () {
          $(this).replaceWith($('<div />', {'class': 'flowProbStatic'}).html(
            $('<input />', {'type': 'text', 'value': choice.prob})
              .change(function () {
                var newVal = parseFloat($(this).val());
                choice.prob = (newVal == NaN) ? 0 : newVal;
                updateChoices(node);
              })
          ));
        });
    }

Finally, ``pvscatter()``, which renders a Protovis chart\ [#]_, uses lambdas
as combinators_ in a more functional programming style.

.. [#]  The code for the axes has been removed, but this should still draw
        the actual data.

::

    function pvscatter(data, tgt_id) {
        var w = 600, h = 500,
            x = pv.Scale.linear(data, function(d) { return 0; },
                                function(d) { return d.y0 > 0 ? d.time : 0; })
                    .range(0, w).nice(),
            y = pv.Scale.linear(data, function(d) { return 0; },
                                function(d) { return d.y0; })
                    .range(0, h).nice(),
            vis = new pv.Panel().width(w).height(h).canvas(tgt_id);

        vis.add(pv.Area)
            .data(data)
            .bottom(1)
            .left(function(d) { return x(d.time); })
            .height(function(d) { return y(d.y0); })
            .fillStyle("rgb(121, 173, 210)")
          .anchor("top").add(pv.Line)
            .lineWidth(3);

        vis.render();
    };

In over half of the uses here, the lambda definition is the sole argument
of a function invocation, leading to an unpleasant ``});`` at the end of
the definition. It's important to visually denote the start and end of a
lambda expression, but for the sole-argument case, the braces are redundant
and add to the clutter.

.. _below:

Evidently Mozilla agrees. `JavaScript 1.8`_ — which refers to Mozilla's
implementation of ECMAScript, and is *not* a standard — includes a bit of
syntactic sugar to write expression closures: just drop the braces and
``return`` keyword from a lambda. Here's the third example above, written
in that style::

    function pvscatter(data, tgt_id) {
        var w = 600, h = 500,
            x = pv.Scale.linear(data, function(d) 0,
                                function(d) d.y0 > 0 ? d.time : 0)
                    .range(0, w).nice(),
            y = pv.Scale.linear(data, function(d) 0, function(d) d.y0)
                    .range(0, h).nice();
            vis = new pv.Panel().width(w).height(h).canvas(tgt_id);

        vis.add(pv.Area)
            .data(data)
            .bottom(1)
            .left(function(d) x(d.time))
            .height(function(d) y(d.y0))
            .fillStyle("rgb(121, 173, 210)")
          .anchor("top").add(pv.Line)
            .lineWidth(3);

        vis.render();
    };

This works pretty well for the sole-argument combinators on lines 13 and
14, but I find that when multiple lambdas are being used in a single
invocation (lines 3-6), I end up missing the braces. Without them, the
heaviness of the ``function(d)`` pulls the whole expression off-balance.

Of course, you could simply add extra parentheses yourself, but then you're
halfway back to the original expression. Plus I know I'd leave the extra
parentheses off most of the time, and that eventually I'd end up with an
atrocity like this in production code::

    alert((function() function() function() function() "Yay!")()()()());

(Yep, that's valid in Firefox.)

Another knock against this syntax is that it doesn't do anything for
multiple-expression statements, or single-expression statements where you
don't return the result (as in event handlers). I have more lambdas in my
Protovis code than elsewhere, so the combinator syntax is more important,
but if you're fixing something, you might as well fix it *as hard as you
can*.

So, the requirements are: lose the ``function`` keyword; require some form
of bracketing but avoid redundancy; support multiple statements, including
nested lambdas; return the contained expresson's value, or not (without
ugly boolean hacks); and look good.  After a bit of toying around, I came
up with this solution, which meets all of my goals::

    foo(d: d.time);  // foo(function(d) { return d.time; });
    bar(d| do(d));   // bar(function(d) { do(d); });

    bzzz((d: d.time), (d: d.val));
    // bzzz((function(d) { return d.time; }), (function(d) { return d.val; }));

The syntax is directly translated from the compact variant, shown
literally, to the expanded format shown in the comments. It's pure sugar;
by the time the code hits an ECMAScript interpreter, all such syntax has
been replaced. I'm quite satisfied with it.

Here's the first example with the new approach. There are pros and cons
regarding the loss of the internal semicolon (you can still use one, of
course), but I end up feeling that for any lambda longer than a few
characters but still comprising one statement, simply adding a space around
the statement is enough to set it off from the rest of the code. In fact, I
think it does a much better job than the original syntax at framing the
code, despite *removing* the visual context provided by the curly-braces.

::

    function mkItem(acts, node) {
      return $('<div />', {'class': 'flowItem'}).html(node.activity)
        .click(| $(this).replaceWith(mkSel(acts, node)) );
    }

The second example is, well, still a huge old pile of ugly. But the shorter
syntax allows statements to be indented much more intuitively. That's *not*
a fluke, or even trivial; a lot of devs, myself included, stick to
80-character line lengths, and when your syntax is so weighty that you
can't fit what is logically a line in that width, things turn ugly. The
shorter syntax makes it much more likely that you'll be able to stick a
line break where it makes the most sense. ::

    function mkProb(node, choice) {
      return $('<div />', {'class': "flowProb"}).html(choice.prob).click(|
        $(this).replaceWith(
          $('<div />', {'class': 'flowProbStatic'}).html(
            $('<input />', {'type': 'text', 'value': choice.prob}).change(|
              var newVal = parseFloat($(this).val());
              choice.prob = (newVal == NaN) ? 0 : newVal;
              updateChoices(node);
            )
          )
        )
      );
    }

Finally, the Protovis example, demonstrating multiple lambda arguments to
one function. The somewhat lighter ``:`` character causes combinator
lambdas (those that evaluate and return one statement) to stand out less
than the ``|``-separated lambdas, which is appropriate for combinator-rich
code like Protovis. Note also that the syntax is unfazed by the ternary
operator on line 3. ::

    function pvscatter(data, tgt_id) {
        var w = 600, h = 500,
            x = pv.Scale.linear(data, (d: 0), (d: d.y0 > 0 ? d.time : 0))
                        .range(0, w).nice(),
            y = pv.Scale.linear(data, (d: 0), (d: d.y0)).range(0, h).nice();
            vis = new pv.Panel().width(w).height(h).canvas(tgt_id);

        vis.add(pv.Area)
            .data(data)
            .bottom(1)
            .left(d: x(d.time))
            .height(d: y(d.y0))
            .fillStyle("rgb(121, 173, 210)")
          .anchor("top").add(pv.Line)
            .lineWidth(3);

        vis.render();
    };


"Works for me"
--------------

So far, I've loved using my syntax. It meets all of my needs. I am *not*,
however, suggesting that it meets all of yours. Syntax debates are tend to
be vigorous and (ironically) quite verbose\ [#]_. I don't mean to stir one up
here.

.. [#]  For an example about JS lambdas, see a mammoth discussion on
        Mozilla's ECMAScript mailing list that starts here__ and continues
        over two__ months__ and hundreds of messages. There are, I'm sure,
        many similar discussions out there.

.. __: https://mail.mozilla.org/pipermail/es-discuss/2008-November/008216.html
.. __: https://mail.mozilla.org/pipermail/es-discuss/2008-November/thread.html
.. __: https://mail.mozilla.org/pipermail/es-discuss/2008-December/thread.html

But, regardless of which JavaScript lambda syntax you prefer, I *do*
recommend that you go implement one in your own projects. The result should
be fully standards-compliant, and can be done with no performance overhead
in production. It's a great way to try out experimental syntax in
real-world code to see what sticks, and — since you've got a parser anyway
— trivial to change syntaxes (or even revert to standard ECMAScript) later.
And if your experience is anything like mine, the pleasure of using the
improved syntax is entirely worth the effort.



.. _jQuery: http://jquery.com/
.. _Protovis: http://vis.stanford.edu/protovis/
.. _Yesod: http://docs.yesodweb.com/
.. _van Rossum famously noted: http://www.python.org/dev/peps/pep-0008/
.. _lambdas: http://en.wikipedia.org/wiki/Anonymous_function
.. _JavaScript 1.8: https://developer.mozilla.org/en/new_in_javascript_1.8
.. _combinators: http://en.wikipedia.org/wiki/Combinator
