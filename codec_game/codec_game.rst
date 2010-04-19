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

If we, oh Internet reader, want to answer questions about video quality in
a way that is scientific and absolute, we have two choices.

1. We get together as an Internet, rent some lab space, buy
   reference-quality hardware, and run a painfully tedious test for each
   question, choosing to overlook the fact that there's no real evidence
   that the results mean what we think they do.

2. We find a new way of doing video quality analysis which is affordable
   and Internet-ready, and try to prove that it works.

I'm picking option two.

The Codec Game is a free (GPL) game for Linux, Mac OS, and Windows designed
to be the first foray into answering this question. The gameplay, on its
surface, is simple: the player is shown short video clips and asked to rate
them somehow. While the basic principle remains the same, the exact details
of each trial may vary; different evaluation methods, new widget styles,
short inter-clip visual activities, changing questions, and an increasingly
competitive rating system (among many other things) will hopefully provide
enough challenge and novelty to keep users engaged.

The variations aren't there for their own sake





sits at the heart of both questions of video quality measurement for its
own sake, and for making judgments about video
















A thought experiment:

    Gather pen and paper, and seat yourself at a table. Place the pen at
    the start of the page and shut your eyes. Write a few paragraphs about
    whatever happens to be on your mind without opening your eyes. After
    completing this, examine the legibility of the writing.

For most individuals, the results of this exercise would be substantially
poorer than handwriting produced with the aid of vision\ [#]_. Continuous,
accurate feedback can improve the quality of the results of many tasks,
from keeping time with band-mates during a song (if you are a musician) to
stabilizing the closed-loop gain (if you are an op-amp).

.. [#]  For me, the handwriting went from "completely illegible" to
        "completely illegible", although I suspect that this is something
        of a corner case.

Lossy video coding is intended to reduce the number of bits required to
represent a given video sequence in such a way as to minimize the perceived
difference between the original and coded versions. The most directly
useful source of feedback for those who are working with such tools,
therefore, is human measurement of the perceived difference. Getting
direct, quantitative, scientifically valid feedback from humans is a
notoriously difficult process [Shei2006]_; as a result, many developers and
researchers working in the field of video coding do not have access to this
kind of valuable, on-demand feedback.

This is not to say that video codec developers lack any means of testing
during development. The impact of smaller tweaks and bug-fixes can be
quantified by simple metrics such as PSNR_ and SSIM_, and any code
can be subjected to a certain extent of traditional software testing.

.. _PSNR: http://en.wikipedia.org/wiki/PSNR
.. _SSIM: http://en.wikipedia.org/wiki/SSIM

Nevertheless, the more fundamental questions in the field remain beyond the
capacity of such simple analytical tools to definitively answer.  We can
witness this in the method of `comparing different codecs`_ used in the
open-source world (the "see for yourself" approach) as well as in the
method of `evaluating new techniques`_ (informal polls in an Internet
forum).  The lack of a valid subjective comparison tool is also evident in
research, where opinionated phrases like this are popping up in published
works with alarming frequency:

    We can see that the PSNR values for both schemes are comparable.
    However, our experiments indicated that the proposed scheme is superior
    in preserving textures and details in the coded images. This
    observation is not effectively captured by the PSNR metric.

    -- [Esla2004]_

.. _comparing different codecs:
    http://people.xiph.org/~greg/video/ytcompare/comparison.html
.. _evaluating new techniques: http://forum.doom9.org/showthread.php?t=141249

The practice of quantifying perception has been the subject of active
research for more than a century and a half [Stev1986]_, and have been used
in a limited number of studies to deterministically answer questions akin
to those mentioned above, but because they require human subjects,
controlled laboratory environments, and reference-quality equipment, these
studies tend to be expensive and time-consuming. In short, open developers
and independent researchers don't have access to subjective video
comparisons simply because they're unaffordable.

Let's fix that.



A brief tour of psychophysics
-----------------------------

Quality is by definition a holistic measure, synthesized from a typically
unknown and probably quite large set of individual assessments, judgments,
and other frustratingly vague factors. Jumping straight in to a proposal
for a novel measurement technique is likely to get us in to rhetorical
trouble, so we spend the next few sections dithering about in the land of
first principles before explaining the larger problems and their potential
solutions.

We'll start with a short look at some relevant parts of psychophysics_, the
study of how subjective perceptions of a sensory stimulus are affected by
changes of the physical characteristics of the stimulus. While
psychophysical methods are not entirely adapted for use in subjective video
quality assessment, as we shall explore later, they do form the basis of
many of the published assays of SVQ determination.

Indirect measurement
````````````````````

For a time, the notion that a human could consciously assess the magnitude
of a given stimulus was considered obviously false. Objections lodged
against it tended to be philosophical, if available at all, but the belieif
was persistent enough to persuade generations of psychologists that direct
measures of perception were beyond the reach of science [Stev1986]_.

In his 1860 work *Elemente der Psychophysik*, Gustav Fenchner described a
clever hack to obtain limited but still important amounts of information
about perception without requiring subjects to make direct evaluations of
stimulus magnitude. The proposed methodology did not involve measuring
stimulus magnitude at all; instead, a subject's *sensitivity* to a
difference in stimulus magnitude would be measured across a significant
dynamic range.

These ideas were extended by

















"Define 'quality'..."
---------------------

The task of crafting an axiomatic definition for subjective phenomena that
is both meaningful and relatively complete is a Sisyphean one.  If the
definition for relatively clinical terms such as "subjective" and
"measurement" is enough to stymie a group of researchers for years at a
time [Stev1986]_, it seems rather fruitless to have a go at a concept as
holistic as video quality. I have faith, dear reader, that you'll know it
when you see it.

Fortunately, it is quite possible to reliably and meaningfully measure
phenomena without a complete definition, as is readily apparent by the fact
that we can measure, well, anything. Since any proof or axiom can disarmed
by simply questioning the nature of experience, to get any work done we
need to agree to ignore the annoying kid in the class who keeps pointing
out that everyone's perceptions could be systematically biased [#]_ and
assume that things are, to a certain extent, as they seem.

.. [#]  "Or we could all be in a giant simulation of a universe which
        actually behaves inconsistently on a fundamental level, but in such
        a way that we aren't able to detect it!" I actually postponed a
        geometry test for two days using this kind of argument back in high
        school.  I'm not proud.












Virtually all lossy video compression techniques in widespread deployment
are designed to minimize the perceived difference between the original and
coded versions. This constraint helps to make the problem of video
compression tractable, but it excludes the possibility of changes to a
video stream which can improve video quality, such as post-processing
filters, such as `this one`_ which aims to remove `ringing artifacts`_ in
animated material.

To avoid this and other pitfalls of specificity, we will simply ignore the
issue of what exactly subjective video quality *means*, and instead focus
only on

Instead,



    An assessment of the subjective video quality of a video segment is a
    random variable with a distribution that is dependent upon an
    individual's sensorineural capability, cognitive state, and evaluation
    environment, as well as the video under evaluation.




instead on
characterizing the
















It's necessarily equivocal in expressing what subjective video quality
*means*. The task of constructing definitions which satisfy in this regard,
particularly of terms related to human experience, is largely philosophical
and rather onerous, and as an engineer I wish to avoid the kind of
boondoggle wherein an interdisciplinary committee spends seven years
fruitlessly debating the meanings of the terms "sensation" and
"measurement" [Stev1986]_.

Despite dodging



Instead of focusing on intuitive meaning, we identify the

"measurement"


If this definition seems weak, it's because it was intended to be. The task
of defining


If you're thinking that this definition is pretty spineless, you're
dead-on; it was chosen to be as wimpy as possible, and for good reason.
Stevens recounts how an interdisciplinary committee spent *seven years*
attempting to define the terms "sensation" and "measurement", to no avail
[Stev1986]_; in fact, this issue is of considerable debate even today
[Bair1997]_. This entire project is expected to be an interesting
*appendix* in my undergraduate thesis. You bet your bitrate I'm going with
a weak definition.

It's more useful than it might appear at first, though. In most studies of
subjective quality, be it of audio, video, still images, or what have you,
the ultimate goal is to increase our understanding of what drives our
subjective evaluations of that quality, usually with the intent to
produce a generalized objective model which can predict subjective scores
for arbitrary inputs [see, yeah, *every single work cited*]. The goal of the
project is to determine subjective video quality for many video samples
associated with particular configurations of processing systems;
everything else is a nuisance variable. While I hope to present (hopefully)
pretty charts and (possibly) insightful commentary about trends detected in
the nuisance variables — for instance, I'm going to try to craft specific
test sequences which can assess characteristics of the viewing environment,
like the monitor's resolution, color profile, and viewing distance without
relying on the user to accurately report these things — the only thing
I'm interested in documenting academically (with all the attendant effort
in proving the validity of the approach analytically) is the ability to
decorrelate sensorineural state and evaluation environment from video
quality. No effort will be made to prove anything about the meaning or
cause of the numbers that get extracted, just that they're consistent with
other studies. In that sense, the definition is precise and complete, even
if it is cowardly.




Direct measurement
------------------


* We'll start by taking a look at some of the existing techniques for
  measuring video quality, and why they aren't appropriate for the task we
  have in mind. Perhaps you should skip down?

Objective metrics
`````````````````

* One of the most straightforward approaches to measuring video quality is
  the application of an objective metric: an algorithm which will evaluate
  a test sequence and produce one or more scores that indicate the quality
  of the video. The performance of an objective metric is usually
  characterized by their effectiveness at predicting human scores in
  subjective video quality evaluation tasks.

* The most commonly used metrics are "full-reference", meaning they measure
  the perceived *difference* in quality between a particular source video
  and a degraded version of that video, rather than attempt to create an
  abstract assessment of video quality.

  * The simplest methods are pixel-based, like PSNR_ and MSE_. These
    methods are perhaps best described as information-theoretical, and
    don't take much about the human visual system into account.

  * Another family of techniques includes the popular MS-SSIM_. I refer to
    this family as "tuned philosophy": techniques in this family involve
    making abstract statements about subjective video quality in terms of
    particular image characteristics ("users prefer images that are less
    blurry"), finding a metric to evaluate those characteristics, and
    weighting the results based on empirical measurements.

  * A third family includes coders developed using direct assessment of the
    human visual system. [must look into these further]

* In many cases, these techniques are sufficient. For example, a patch to
  an existing coder which increases PSNR is almost always a good thing
  [cite], and SSIM can provide a quick estimate of the quality of a video
  video without requiring visual inspection.

* But they're not sufficient for all purposes. Here's why:

  * Even the best models aren't correlated that strongly with human
    measurements. PSNR has a [whatever] correlation rate, and the current
    champion metric [name] has at best a [whatever] rate. [cite]

  * All studies which measure the correlation have been performed to
    measure the effectiveness of these schemes have been performed *against
    samples including these schemes*. There's no evidence to indicate that
    these tests will continue to accurately assess performance when we
    switch to a different scheme.

* Since video coding development is all about switching to new schemes, we
  need to be able to evaluate these schemes with real human viewers.

Mean Opinion Score
``````````````````

How do existing studies do it?

* The most common approach is to employ a family of techniques related to
  the `Mean Opinion Score`_. The principle of an MOS assessment is simple:
  present the user with a video, and have them rate it on a scale from 1
  (poor) to 5 (excellent). Average this rating across many runs, possibly
  applying a scaling factor. This technique is codified in ITU-T BT-500
  [cite].

.. _mean opinion score: http://en.wikipedia.org/wiki/Mean_opinion_score

* A challenging aspect of MOS measurement techniques is that they depend
  heavily on context. The meanings of '1 to 5' on this scale are not fixed.

  * This can partly be solved by careful ordering of the presentation to
    include videos that scale the full range of quality at the start of the
    presentation, to get the viewer in the right frame of mind, but even
    using this, data can be unusably variable.

  * Another technique, more easily employed with scales that have many more
    possible positions ('1 to 100'), is to include sample clips in the mix,
    and use complex statistical post-processing to adjust the results of
    individual programmers (see [cite] for some background, [cite] for an
    implementation), but this is still pretty fragile.

* Alterations to the measurement system yield more focused results.

  * Difference in Mean Opinion Score and Mean Impairment Score use a
    reference segment against a degraded one. This is less sensitive to
    context and ordering, but the magnitude of a difference is still a
    comparison with history, and so it's still sensitive to environment.

* Controlled studies using direct assessment successfully compensate for
  this by carefully controlling conditions, and their results are quite
  reproducible [cite], which indicates that these techniques work. But the
  process of ensuring that these caveats are respected is expensive and
  slow [cite?]

* We can't afford lab space; we probably don't have enough subjects. We
  want to enlist the Internet at large. To do that, though, we're going to
  need a test that's a *lot* more robust.

Indirect measurement
--------------------


* This section is also rather abstract; perhaps you should skip down?

Psychophysics (vaguely)
```````````````````````

* A bit of history. Extremely glossing.

* Psychophysics: measurement of perception of magnitude of stimulus in
  relation to actual magnitude. Gateway to sensation and perception.

* Fenchner assumed that self-reported measurements of magnitude weren't
  valid, and instead came up with the ingeniously simple method of pairwise
  comparison. This was refined to become signal detection theory.

* Stevens challenged the assumption that self-reported statistics aren't
  valid. He demonstrated that direct assessments were possible.

* The upshot is this: Fenchner didn't trust his subjects to self-report
  accurately. Stevens argued that you can, provided you could keep their
  attention and control their environment. I'm only covering a fraction of
  the debate, see [cite] for more details.

* We want to use the Internet to gather information — the opposite of "keep
  their attention and control their environment". Those Fenchnerian methods
  are suddenly rather attractive.

* One in particular is well-suited for this system. In a `two-alternative
  forced choice` task, a user is presented with two stimuli and asked to
  choose which one possesses more of some characteristic. For instance, a
  user might be shown two videos, and must select the video that is of
  higher quality.

* Over the next few sections, we'll build a statistical basis for 2AFC
  tasks.

Forced choice assessment
````````````````````````

* These next sections are derived in large part from [Keel2002]_ and
  [Wick2002]_. I am not a statistician, and haven't yet vetted this brief
  analysis. If you notice any errors, please comment; I'll update or
  supersede the page if it's necessary.

* The direct result of a single run of a 2AFC task is a true/false
  variable: did the user choose correctly? Over multiple runs, this can be
  aggregated into the proportion of correct responses, `$p_c$`.

* `$p_c$` includes both instances where the user detected the difference,
  and where they got lucky. What we really want to know is the proportion
  of times they actually detected the difference, `$p_d$`.

  * If they detect the difference, we assume they make the correct choice
    each time; in this case, `$p_{c|d} = 1$`.

  * If they do not detect the difference, they are forced to guess which
    sample was correct; in this case, `$p_{c|n} = 0.5$`.

  * The chance that they detected the signal is `$p_d$`; that they did
    not, `$p_n = 1 - p_d$`.

  * Combining these terms and applying a little algebra, we get:

  `$$p_c = p_d \cdot p_{c|d} + p_n \cdot p_{c|n} = p_d + (1 - p_d) \cdot
  0.5 \Rightarrow p_d = 2\cdot p_c - 1$$`

* It's somewhat inconvenient to sling these proportions around all the
  time, so we define a shorthand expression: the `just-noticeable
  difference`_. One JND is defined as a perceptual difference which results
  in `$p_d = 0.5$`.

.. _just-noticeable difference: http://en.wikipedia.org/wiki/JND

* Merely defining a unit doesn't get us anywhere. We could make grand
  assumptions, akin to those made by Fenchner, Weber, Thurstone, and simply
  start trying to build a scale, but there's little basis to believe that
  this is correct and much evidence to indicate that it is not.

* We would like to anchor JNDs to a scale and a probability distribution.

----

* Let us consider a particular viewer, in a particular environment, with a
  particular mental state, evaluating a particular pair of test sequences.
  We assume the following:

  * The only change between the assessment of the first video and the
    second is caused by the assessment activity [#], and that we can either
    remove the effects of this change via stats, or determine that it's
    small enough to ignore.

* We model the value of an internal assessment of video quality as a random
  variable. For ease of explanation, we assume that this variable follows a
  Gaussian distribution; we'll discard this assumption soon.

* Let's label the samples A and B. For this example, we will choose our
  labels such that B has a higher subjective quality than A, and is in that
  sense the correct choice, but it doesn't matter as long as we apply the
  consistent labels to pairs of samples.

* The axis along which we are working is currently completely arbitrary.
  For illustrative purposes, we therefore assign sample A's distribution to
  be the standard normal distribution: `$P_A = N(0, 1)$`. Sample B's
  distribution can be expressed relative to that without any loss of
  generality.

* We can now describe the 2AFC experiment as follows: the user evaluates
  the quality of both test sequences — they sample the two distributions of
  quality — and selects the video that has the higher quality value [#]_.

.. [#]  This ignores the difference between a trial in which the user
        misjudges the quality of the samples, but still chooses a sample
        perceived to be better, and one in which the user believes that
        there is no difference in quality and simply guesses. We'll address
        this in a later section.

* (Figure: stacked graphs, one showing the PDFs of the two samples, another
  showing the convoluted difference PDF)

* In this formulation, the proportion of events in which a change was
  correctly discriminated `$p_d$` corresponds to the probability that the
  value of B was detected as being higher than A. In other words, `$p_d$`
  corresponds to the probability that the difference between the perceived
  quality of the samples is positive.

* We are therefore interested in the distribution of the differences in the
  subjective video qualities assessed for each sample in the study. This
  distribution can be found as the convolution of the distribution of
  quality evaluations for the individual samples. For Gaussian
  distributions, this process simply yields another Gaussian distribution
  with a larger variance.

* Here's the point of all of this. We now have a probability distribution
  which relates a measurable characteristic to the underlying quality
  assessment function in a meaningful way. We are able to extract salient
  characteristics about the quality assessment distributions without
  measuring them; all we need to do is to characterize the difference
  distribution, which can be done easily using the collected data.

* We can now discard the imposition that the underlying quality
  distributions follow a Gaussian distribution. In its place, we add two
  much weaker assumptions:

  * The shape of the distribution of quality assessment for an individual
    sample is not significantly non-Gaussian. (For example, a strongly
    bimodal distribution could compromise the quality of this assessment.)

  * The shape of the individual distributions of quality assessments for a
    pair of samples that are very similar in subjective quality are
    similar.

  * These assumptions are easy to justify when the two samples in a paired
    comparison experiment are from the same source sequence and have been
    degraded by the same coding process. It's possible, however, that these
    assumptions could be violated, particularly where viewer preference
    becomes a concern (e.g. when comparing two videos from different
    sources, or two different coding processes). We'll look at these
    possibilities in a later section.

* With the assumption of a Gaussian distribution of individual values
  lifted, we are free to choose a more effective distribution to model the
  difference ratios.  Evidence suggests that at smaller sample sizes, the
  angular (or 'arcsine') distribution is a better fit at reasonable sample
  sizes [Keel2002]_. We will consider this when we have raw data.


Scaling
```````

*


----

* The 2AFC test design provides a number of benefits for the

* Existing testing methods are challenging because

  * The test environment needs to be carefully controlled for MOS to work
    *on its own*.  Variability not easy to extract across scales? Nonlinear
    behavior follows a different curve for each setup. This all makes it
    harder to decorrelate nuisance variables.

  * Lab space, subjects, physical interaction. Not easy for everyone.

  * Subject procurement and conditions. [#] Experts rate higher.

  * Fatigue vs inter-session variability, plus priming time

* DMOS is too contextual on its own; in fact, ITU-T Rec. B-500.11
  techniques are all too finicky to employ here without prior evidence of
  their effectiveness in highly variable test environments.




* Study of "user confusion", but turns out it's still quite effective
  for local phenomena. [cite]

* This solves some problems:

  * Less affected by context events

  * Less priming time required

  * Independence of most trials, users, variables, etc.

* On its own, independence doesn't do much for us. However, using
  multivariate analysis techniques, we can decorrelate many nuisance
  variables from scores.

* Basic approach: bin users based on performance on certain test samples.

  * Test samples can be natural, or artificially designed to highlight a
    certain characteristic of the test setup (e.g. color balance,
    sensitivity to very dark images)

  * Within a bin, we fit the "quality sensitivity function" to
    compensate for nonlinearities, and rescale it to match a normalized
    reference

  * Testing of correctness of binning is both easy and automatic: just
    throw in extra test segments but don't use them in the binning
    calculations

  * Binning will be done discretely (best-fit bin) at first, but later
    explore other decorrelation techniques

* This system is in theory able to remove the effects of hardware
  differences, most contextual effects, even possibly personal preference
  in cross-video situations (provided that personal preference is not
  simply another Gaussian variable; f.ex, preference for blur in images
  could well be bimodal [cite])

* Plus, it is (in my totally subjective personal opinion) just more fun,
  which is a relevant concern when trying to get internet people to do it.

----

Well, if you love it so much...

* It *is* used, but only in some procedures, and only on a local scale (to
  calibrate rescaling experiments).

* It's not often employed any more in wider studies because:

  * It requires a lot of tests. I mean a *lot*.

  * Unit basis doesn't necessarily scale. (See Stevens, Fenchner argument).

* This makes it less desirable for laboratory-scale video quality
  assessment for the purposes of evaluating and constructing objective
  metrics. But this is not what we're going for here. We prefer "robust" to
  "generalized", and this affects our decision to start by using paired
  comparisons.


Works cited
-----------

.. _psychophysics: http://en.wikipedia.org/wiki/Psychophysics

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

