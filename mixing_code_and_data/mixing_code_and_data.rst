On the mixing of data and code
==============================

:Author: Steven Robertson
:Contact: steven@strobe.cc
:Tags: Article
:Abstract:
    No abstract yet.

*This article is less published than most. Don't judge it / me based on it just
yet.*

The value of a strong separation between data and code is nearly self-evident.

Programs which possess a tight coupling to certain datasets are often
inflexible and difficult to test; as a result, they can easily become
bug-ridden maintenance nightmares. Even small scripts built to process a
particular chunk of data can quickly be submerged in a morass of copy-and-paste
code, undocumented "magic constants", and misleading comments as a coder grabs
the closest existing file from a bag of tricks and adapts it to a dataset that
is just dissimilar enough from the last use to require tweaking, but not so
much as to warrant generalizing and modularizing the code.

Well-designed systems, on the other hand, gleam with their sterile isolation.
Model-view-controller architectures are often called upon as examples of this,
among a tremendously wide selection of valid design patterns that rigidly
isolate not only code but realms of thought into crisp, neat sections. Not only
do components written according to such models not require adaptation, they
actually *defy* it; the inflexibility of such modularization will often prevent
the programmer from taking the wrong approach in order to get results for a
fixed scenario. It's certianly no panacea for bad code, but it usually helps.

There's a certain intrinsic beauty to the latter kind of interface. Instead of
a wall of knobs, switches, and levers, there are a few slots for passing
precise, well-formed items, and a whole bunch of white space. The imagery
sounds abstract, an emotional response to a learned set of patterns, but a lot
of it is actually present in the code itself. Hand a few pages of code, an
interface description document, or a sketch of of the call tree to a layman,
and she'll be able to spot the good code from the bad without being able to
read a lick of it. Good, well-isolated code has an aesthetic property which
mirrors its underlying construction.

These ideas—certainly not original ones—came to mind a few months ago, right after the `Climate Research Unit data leak`_. Curiosity and excessive press coverage led me to flick through a few samples of CRU's code for analysing and modeling climate data. My first thought was that the code felt ugly.

With a bit of horror, I also realized that it felt *familiar*.

.. _Climate Research Unit data leak: 
    http://en.wikipedia.org/wiki/Climatic_Research_Unit_hacking_incident

(unfinished article)

