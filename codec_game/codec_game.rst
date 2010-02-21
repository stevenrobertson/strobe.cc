The Codec Game
==============

:Author: Steven Robertson
:Contact: steven@strobe.cc
:Copyright: 2010 Steven Robertson. CC Attribution 3.0 US.
:Tags: Video, Algorithm, Article
:Abstract:
    Evaluating the quality of a video codec analytically is both a critical
    part of the development process and rather difficult to do.
    This might help.

.. role:: raw-math(raw)
    :format: latex html

.. default-role:: raw-math

.. contents::

Introduction
------------

Perceived video quality is a subjective and very context-sensitive property,
and as such it can be surprisingly difficult to nail down a valid quantitative
system for describing it. As an example, consider this experimental setup:

    Pick a YouTube_ video you've never seen before. Mute the sound, fullscreen
    it, and watch it straight through. Now rate the quality of the video on a
    scale of 1 to 100. Be accurate, as you'll be graded on how close you came
    to the real answer.

.. _YouTube: http://youtube.com

This is a flat-out stupid test design. The rating scale is so arbitrary as to
be useless; a viewer could legitimately use "number of ponies in video" as the
basis for their evaluation. Even if users employed common sense and were
earnest, the results of a bunch of ratings of a *single* video could be
expected to vary haphazardly across many users, much less a *random* one. And
the bit about a "real answer" presupposes an established absolute rating scale
for video quality, but provides no evidence for such a thing.

So that one's a bust. Consider this instead:

    Pick a YouTube_ video available in HD. Show the video to a friend,
    fullscreen, sound off, in either 720p quality or 480p quality, without
    letting the friend know which version is playing. Immediately follow that
    with a screening of the other quality setting, in the same conditions. Now
    ask the friend to pick which video was of a higher quality.

Here's a test we can sink our teeth into. It has a definite method for
evaluation, and doesn't rely on any outside context aside from a common-sense
understanding of what "video quality" means; furthermore, the only thing it
presupposes is that you have a friend willing to entertain your predilection
for running weird little experiments like this one.

On its own, this test may not seem like it provides much information about the
quality of either video — for most videos on YouTube, and for most friends,
the answer's pretty much always going to be the 720p version — but by
carefully running many trials of this test using different videos, it's
possible to use this test to build a thorough and accurate "1 to 100"-type
scale for video quality.

Running one of these trials might be simple, but running enough of them to
draw conclusions from is a surprisingly complex and costly endeavor. It can
take years for a comprehensive test to be planned, executed, and analyzed; the
`Video Quality Experts Group`_, for instance, has been hammering out the
details of the *plan* to test HDTV-resolution clips for almost six years.
Furthermore, these tests are very general, which is to say, vague; they are
targeted at evaluating objective algorithms which are intended to perform the
task of rating video quality for us, which is a very nice goal but is
insufficient until such algorithms can do as well as humans in these tasks.

.. _Video Quality Experts Group: http://vqeg.org/

For video coding developers and researchers, this means there is no simple way
to quantify the subjective effectiveness of new and existing strategies for
compressing video. This impedes teams working on production-ready open-source
encoders available today, like Dirac_, Theora_, and x264_; it also hampers
those working on experimental coding techniques which might power the next
generation of video codecs.

.. _Dirac: http://diracvideo.org/
.. _Theora: http://www.theora.org/
.. _x264: http://www.videolan.org/developers/x264.html

Let's fix that.

Pairwise comparison
-------------------






Pairwise comparison
```````````````````


It is common, and not altogether inaccurate\ [#]_, to model the value of a
conscious assessment of a particular attribute of a stimulus as a
stochastic variable having a vaguely Gaussian distribution [Wick2002]_.
This model is particularly useful when we can treat the variance of the
distribution as remaining fixed across a portion of the perceptual dynamic
range. There is significant evidence that this is approximately correct
over a substantial fraction of the total dynamic range for visual signals
in carefully controlled testing environments [Keel2002]_, but for this
section we ensure fixed variances by constraining the range over which a
given variance must be estimated per sample. This will be discussed further
in the next section.

.. [#]  Justifying this requires a certain amount of standing with your head
        in a corner, covering your ears with your hands, and singing "LA LA LA
        CENTRAL LIMIT THEOREM LA LA LARGE SAMPLE SIZE LA LA LA LA" at
        the top of your voice. Not an elegant approach, but effective.

A typical experimental apparatus for determining the perceptual strength of
one stimulus in relation to each other within a narrow dynamic range is a
`two alternative forced choice` test. 2AFC tests are conducted essentially
as in the second YouTube experiment above: a user is presented with two
stimuli in a random order and is asked to choose between them based on a
particular criterion. This test setup is valued in part because it is
resilient to user bias towards a particular outcome, and proper test design
can eliminate or at least expose ordering effects [Wick2002]_.

.. _`two alternative forced choice`:
    http://en.wikipedia.org/wiki/Two_alternative_forced_choice

.. [#]  The results are insensitive to the choice of sample to call "correct".
        We use the term to agree with literature (and because in most cases
        our expectations won't be contradicted, which is kind of the point
        of expectations).

Consider a 2AFC experiment in which a user must choose which of two
photographs is less blurry. In each trial, two versions of the same image
will be displayed, each of which has been blurred by a certain amount. Each
image will be displayed by itself for 10 seconds, with a 5-second delay
between blanking the screen after the first image and presenting the
second. The subject will then be asked to identify whether the first or
second sample was more heavily blurred.

If the images presented are quite different in level of blur, we would
expect a competent and earnest user who understood the task to respond
correctly without challenge. This should be consistent over several trials


By contrast, a setup in which two identical
images were presented (with one randomly selected to be considered
"correct')




In one set of trials, the subject is presented with an unmodified print and ; in another, the two swatches appear to be in
every way identical (although only one is considered "correct"). The
swatches are presented individually, in a random order for each trial, and
a decision is asked for after both samples have been presented and
withdrawn. We would expect an earnest, competent user who understood the
instructions to get a trial of the first kind right every time, such that
`$p_c = 1$`, but a user who had no outside knowledge would be forced to
guess which sample to call correct in the second case, yielding `$p_c =
0.5$`.

A more interesting pairing could involve samples that are slightly but
detectably different when compared side-by-side. In a simultaneous-stimulus
2AFC experiment, where both samples are available to be inspected and
compared, this could result in a large `$p_c$`; however, the experimental
procedure outlined above forces the subject to compare his or her memories of
the stimuluses in order to make a judgment. One can imagine that this
complicates the task, making an incorrect assessment more likely. Keen
observers may still be able to make the correct decision regularly, and
bumbling ones may be forced to guess, but we expect the average user to make
the right call most but not all of the time.

.. figure:: fig1.pdf
    :width: 100%
    :figwidth: 40%
    :align: right

    Figure 1: Expected results for two-alternative forced choice tasks when
    stimuli are extremely dissimilar, essentially identical, and similar but
    distinguishable, respectively. The shaded area represents the probability
    of a correct choice `$p_c$`.

Figure 1 roughly illustrates these situations using the "measurement plus
noise" model described at the start of this section.



Measuring experience
````````````````````

The example of brightness evaluation highlights one of the more remarkable and dangerous aspects of pariwise comparison activities: it's possible 


test might task requires the subject to compare the *memories* of the values of the perceptual quality being evaluated for each object.

are a measure of "user confusion", as Stevens petulantly puts it [Stev1986]_. If the difference in the attribute being measured is vast between the two stimuli, the results will be concentrated


.. [Stev1986]   Stevens, S. S., & Stevens, G. (1986). *Psychophysics:
                Introduction to its perceptual, neural, and social
                prospects.* New Brunswick, U.S.A.: Transaction Books.
                `Google Books`__.

.. __: http://books.google.com/books?id=r5JOHlXX8bgC

.. [Bair1997]   Baird, J. C. (1997). *Sensation and judgment:
                Complementarity theory of psychophysics.* Scientific
                psychology series.  Mahwah, N.J.: Lawrence Erlbaum
                Associates. `Google Books`__, where the work is
                delightfully classified as 'Juvenile Nonfiction'.

.. __: http://books.google.com/books?id=huh-AAAAMAAJ

.. [Keel2002]   Keelan, Brian W. *Handbook of Image Quality*, 2002.  Marcel
                Dekker, Inc. `Google Books`__.

.. __: http://www.google.com/books?id=E45MTZn17gEC

.. [Wick2002]   Wickens, T. D. (2002). *Elementary signal detection
                theory*.  Oxford: Oxford University Press. `Google
                Books`__.

.. __: http://www.google.com/books?id=s3pGN_se4v0C

.. [Shei2006]   Sheikh, H.R.; Sabir, M.F.; Bovik, A.C., "A Statistical
                Evaluation of Recent Full Reference Image Quality
                Assessment Algorithms," Image Processing, IEEE Transactions
                on , vol.15, no.11, pp.3440-3451, Nov.  2006. DOI:
                `10.1109/TIP.2006.881959`_

.. _10.1109/TIP.2006.881959: http://dx.doi.org/10.1109/TIP.2006.881959

