Ending the video quality debate: The Codec Game
===============================================

:Author: Steven Robertson
:Contact: steven@strobe.cc
:Copyright: 2010 Steven Robertson. CC Attribution 3.0 US.
:Tags: Video, Algorithm, Article
:Abstract:
    Evaluating the quality of a video codec analytically is a surprisingly
    challenging task. This might help.

`TL;DR`__ version: I'm writing a free game where players perform video
quality evaluations. The data will help answer questions about existing
video codecs and drive the development of new ones.

.. __: http://www.urbandictionary.com/define.php?term=tl%3Bdr

.. contents::

Introduction
------------

Which one is better: x264, Theora, VP8? Despite a disheartening amount of
discussion (tiny sample: 1__ 2__ 3__ 4__ 5__ 6__), nobody has a conclusive
answer. The surveys which use objective video quality metrics like PSNR_
can be justifiably dismissed as irrelevant, because many objective metrics
have been shown to be only loosely related to the perception of video
quality by humans, and the "codec shootout" comparisons each contain a
disclaimer that the test method is not scientific and shouldn't be taken as
an absolute measure of a codec's quality [#]_.

.. [#]  Or at least they *should*.

.. __: http://www.osnews.com/story/19019/Theora-vs.-h.264
.. __: http://people.xiph.org/~maikmerten/youtube/
.. __: http://grack.com/blog/2010/01/24/comparing-theora-1-1-1-with-x264/
.. __: http://x264dev.multimedia.cx/?p=292
.. __: http://www.on2.com/index.php?599
.. __: http://multimedia.cx/eggs/vp8-the-savior-codec/

"So there's a method that *is* scientific and *can* be taken as absolute?"

Uh, er, well... not really. I mean there's a few ITU recommendations on the
matter ([BT500]_ [ITUR#TODO]_), and the VQEG_ keeps riffing on the
methodology (CITE). And there is some evidence that the methods they
specify are *internally consistent*. But current thinking is that internal
consistency doesn't really count for much in human trials, and there's
not much evidence apart from that to indicate that the either test designs
of the VQEG studies or the data that results are entirely faithful in
representing video quality.

Trouble is, there's not nearly enough published information about the way
humans evaluate video quality (or the way other humans measure it) to do
anything more than checks of internal consistency. This self-perpetuating
dearth of data stands in the way of video quality measurement for its own
sake and for the purposes of making judgments about video coding, and its
root cause is simple: to preserve internal consistency, current test
methods rely on carefully specifying as much as possible about a test
setup. This results in tests that involve careful subject screening,
elaborate and expensive equipment, controlled physical spaces,
time-consuming subject supervision, and manual statistical
post-processing.

In other words, these tests are *expensive*.

If we, dear Internet reader, want to answer questions about video quality
in a way that is scientific and absolute, we have two choices.

1. We get together as an Internet, rent some lab space, buy
   reference-quality hardware, and run a painfully tedious test for each
   question, choosing to overlook the fact that there's no real evidence
   that the results mean what we think they do.

2. We find a new way of doing video quality analysis which is affordable
   and Internet-ready, and try to prove that it works.

I'm picking option two.

The Codec Game is a free (GPL) game for Linux, Mac OS, and Windows designed
to be the first foray into answering this question. The gameplay is simple:
the player is shown short video clips and asked to rate them. The exact
details of each trial, however, will vary: different evaluation methods,
new widget styles, short inter-clip visual activities, changing questions,
and an increasingly competitive rating system (among many other things)
will hopefully provide enough challenge and novelty to keep users
engaged.

The variations aren't there for the sake of user retention, though. Each
change will be instigated by the server, and the effects on user
performance will be tracked. Initially, these changes will be made at the
hands of the researchers and developers submitting code and samples to the
system, but statistical analysis and machine learning algorithms will take
over later to explore and cross-reference the most significant changes.
Over time — a couple of months, if my estimates are right — the system will
let us confidently answer both very specific and very general questions
about video quality.

Scaling the game will be a challenge. This project will need CPU time to do
encoding, bandwidth to do distribute the videos, and tons of source
material to keep analysis interesting for both users and researchers — and,
of course, enough players to get results at a sufficient rate.  If you're
interested, I could really use your help.


----

Who cares about video quality metrics?
--------------------------------------

* Not users, by and large.

* Video codec (and postprocessing, and display) developers: engineers
  working on existing hardware, to optimize within constraints

    * x264's psy_rd

* Video researchers: scientists exploring new techniques. Can't rely on
  existing metrics, because those metrics haven't been tested against the
  new techniques to make sure they match, ipso facto. Example quote:

    We can see that the PSNR values for both schemes are comparable.
    However, our experiments indicated that the proposed scheme is superior
    in preserving textures and details in the coded images. This
    observation is not effectively captured by the PSNR metric.

    -- [Esla2004]_

    * Sure, it's a 6-year-old quote, but you get the point. Not much has
      changed in the intervening years [CITE].

* Content delivery networks. Ensure quality of experience.

* Research has focused on OVQM

    * Perceptual techniques were less common, as we hadn't finished pushing
      the boundaries of naïve methods yet

    * CDN's need real-time data, can't wait to collect it from humans

* OVQM is gaining ground, but is not there yet.


PSNR sucks
----------

* PSNR is the de facto standard. It also seriously blows.

    * Topic given much treatment elsewhere; I direct you thence.

    * In short: PSNR is completely unaware of HVS processing, only looks at
      differences.

* Modern replacements like MS-SSIM do a lot better, but not well enough.
  New proprietary methods are doing slightly better than even that, but
  still insufficient.

* "Optimizing for SSIM" is better than "optimizing for PSNR", but exactly
  how much better? It's difficult to say; not nearly enough data has been
  collected, and the stuff that is out there is of questionable value.


The (fool's) gold standard of video quality measurement
-------------------------------------------------------

* The standard for video quality measurement is BT.500-11 #(the -11 is the
  update suffix; there's a -12, but it's not public) (and others, I forget)

* This standard specifies several kinds of measurement techniques:

  * DSIS, HR, etc (discrete models)

  * SSCQS, SSCIS, DSCQS, etc (continuous models)

* Results of these studies have historically been interpreted as Mean
  Opinion Score, and roughly conflated.

* Evidence that the tests are comparable exists, but evidence that they are
  valid? Not so much.

* Digging deeper, we see that existing tests have a number of theoretical
  flaws:

    * A single unified metric, instead of individual points of analysis

        [#] Although professional studies may do this kind of thing,
        they're not public, and therefore not useful to us

    * Improper application of scaling [cite]

    * No CFA, not even PCA [cite?]

    * These complaints are also true of speech quality metrics, which are
      similar [cite]

* What are possible causes for not addressing this?

    * Ignorance. Psychometricians have been lamenting the widespread
      ignorance of the techniques they champion, despite (or perhaps
      because of) the fascinating and in some cases revolutionary data they
      turn up [cite many]

    * Informed disregard. Since OVQ researchers do most of the studies into
      video quality, and since current metrics can't — and arguably don't
      need to — beat SVQ studies in their weakened form in order to fulfill
      the roles required of them by the institutions writing the research
      grants[#], these techniques might consciously be skipped.

        [#] From the researchers' CVs, most of these are CDNs [cite].

        * In fact, it should be noted that I'm not expecting revolutionary
          results here. While the *theoretical* basis for these tests is
          tenuous, the practical value is pretty obvious. I *am* hoping to
          use these techniques to increase the precision, accuracy, and
          depth of the results, but I'd be surprised and worried if the
          experiment did something other than color in the fuzzy outlines
          of previous works.

    * Cost. This one seems the most likely: PCA/CFA have only recently
      become a thing, and the cost of running a BT.500 experiment means the
      pressure of wanting to do right has never outweighed limited
      resources.


The cost of subjective video quality
------------------------------------

* Why are subjective studies so expensive to run, anyway?

  * The BT.500 methodology seems to be inherited, rather than devised. Like
    most traditions, the details become important.

  * Since BT.500 doesn't really have any proof, there's no "proof by
    extension" possible; simply put, the closer tests are to each other,
    the more "valid" they are, because the results of one test derive their
    meaning from the results of other tests.

  * Most of the cost comes from the process of ensuring that each test is
    so entirely controlled that as few as possible of the sources of
    variance we haven't explored yet begin to affect the data

* How can we reduce the cost?

  * Find a cheaper way to control everything -> ha! unlikely.

  * Expand our knowledge of the other sources of variance so that we can
    filter them out or study them in their own right -> yes.

* I plan to do this using The Codec Game; we trade control for data. A lot
  of data.


Sources of variance
-------------------

* In BT.500 tests, there are usually only a few sources of variance that
  are considered: the HRC under test (usually selected from a handful of
  possibilities), the video samples, and to a very limited extent the
  subject.

* In our expanded tests, we have quite a few more. These are the ones I've
  identified so far, but PCA may turn up more, and CFA may indicate that
  some of these aren't in fact all that relevant.

    * The hardware. Monitor, computer, graphics card, video settings.
      Expected to remain fixed (we'll try to detect changes).

    * The testing environment. Spatial location of head relative to
      monitor, lighting, sources of distraction. Parameters may be
      recovered indirectly; should it prove necessary, we'll ask the user
      to create "profiles" for each location the game is played at, where
      the recovered parameters will be stored.

    * Individual "invariants". Eyesight, preference for explosions in
      videos, etc.

    * Individual long-term variants. Learning effects, consistency
      training.

    * Individual session-length variants. Mood, alertness, short-term
      memory of rating scale, day of week.

    * Sample video source. Both as a free variable and in terms of its
      similarity (semantic content, color, activity, compressibility, type)
      with other samples.

    * Hypothetical reference circuit (video codec) and parameters.

    * Test style (2AFC vs DSIS, for instance), widgets

    * Variable under test (quality, naturalness, sharper, colorfulness)

    * User motivation (scoring system, bonus-point timer, no. of replays)


Understanding the results
-------------------------

* It is on this section that I've made the least progress; forgive my
  inexpert ramblings. I promise I will be more up to speed soon, and
  possibly come back and update this section.

* The general idea is to use PCA to figure out what components are
  important, and CFA to verify that they are indeed what we think they are.

* PCA is a mainstay of the data mining community [cite], and is
  increasingly gaining prevalence in the psychological community [cite].
  It's useful for extracting the underlying causes of variance in a
  particular context, so that new tests can be devised which explicitly
  target these sources of variance instead of getting caught in a
  crosswinds.

    * However, PCA is an exploratory technique only! In data mining, where
      experiments aren't always a possibility, it's often used to gain
      insight to determine what to change, but then A/B tests need to be
      run to be sure [cite]. The situation in psychology is similar; PCA
      should always be followed by CFA [cite].

* CFA is... well, quite frankly I have no idea, let me read up a bit more.

* Because the system is to be implemented quite flexibly, there are tons of
  opportunities for CFA to work its magic.

Implementation
--------------

* The (first) client will be written using Python and Clutter; currently
  wondering if the convenience of GStreamer is worth the performance hit
  and



.. _psnr:
.. _bt500:
.. _vqeg:


.. [Stev1986]   Stevens, S. S., & Stevens, G. (1986). *Psychophysics:
                Introduction to its perceptual, neural, and social
                prospects.* New Brunswick, U.S.A.: Transaction Books.
                `Google Books`__.

.. __: http://books.google.com/books?id=r5JOHlXX8bgC

.. [Bair1997]   Baird, J. C. (1997). *Sensation and judgment:
                Complementarity theory of psychophysics.* Scientific
                psychology series.  Mahwah, N.J.: Lawrence Erlbaum
                Associates. `Google Books`__, which to my great amusement
                classifies the work as 'Juvenile Nonfiction'.

.. __: http://books.google.com/books?id=huh-AAAAMAAJ

.. [Keel2002]   Keelan, Brian W. *Handbook of Image Quality*, 2002.  Marcel
                Dekker, Inc. `Google Books`__.

.. __: http://www.google.com/books?id=E45MTZn17gEC

.. [Wick2002]   Wickens, T. D. (2002). *Elementary signal detection
                theory*.  Oxford: Oxford University Press. `Google
                Books`__.

.. __: http://www.google.com/books?id=s3pGN_se4v0C

.. [Wink2006]   Winkler, S. (2005). Digital video quality: Vision models
                and metrics. Chichester, West Sussex: J. Wiley & Sons.
                `Google Books`__.

.. __: http://books.google.com/books?id=NDNfMaht37cC


.. [Esla2004]   Eslami, R.; Radha, H.; , "Wavelet-based contourlet transform
                and its application to image coding," *Image Processing, 2004.
                ICIP '04. 2004 International Conference on*, vol.5, no., pp.
                3189- 3192 Vol. 5, 24-27 Oct. 2004. DOI:
                `10.1109/ICIP.2004.1421791`__

.. __: http://dx.doi.org/10.1109/ICIP.2004.1421791

.. [Shei2006]   Sheikh, H.R.; Sabir, M.F.; Bovik, A.C., "A Statistical
                Evaluation of Recent Full Reference Image Quality
                Assessment Algorithms," Image Processing, IEEE Transactions
                on , vol.15, no.11, pp.3440-3451, Nov.  2006. DOI:
                `10.1109/TIP.2006.881959`__

.. __: http://dx.doi.org/10.1109/TIP.2006.881959

