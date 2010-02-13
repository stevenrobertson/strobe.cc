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
task of rating video quality for us, which is a very nice goal but doesn't get
us anywhere until such algorithms can do as well as humans in these tasks.

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

What if there were a way to get a quantitative analysis of subjective video
quality with high granularity both within and across codec families, at no
cost to developers, with results in a week?

----

In the rest of this article, we'll delve into the statistical basis for video
quality assessment, look at existing large-scale video quality assessment
experiments and why they're not well-suited to codec development, and take a
glimpse at potential approaches to drawing conclusions from pairwise
comparisons performed in uncontrolled settings. I imagine that most of you
will find these sections rather dry, so unless you're either *really* curious
or my thesis advisor I recommend you skip right down to the final section,
which maps out my plan to build a game that turns pairwise comparisons (the
second kind of test described above) into a fun, challenging, and competitive
time-killer.

.. contents::

The meaning of quality
----------------------

It is common, and not altogether inaccurate\ [#]_, to model the value of a conscious assessment of a particular quality of a stimulus as a stochastic variable having an essentially Gaussian distribution with a variance that is more or less fixed across a limited dynamic range of the underlying value of the variable being assessed [Keel2002]_, [Wick2002]_.



.. [#]  Justifying this requires a certain amount of standing with your head
        in a corner, covering your ears with your hands, and singing "LA LA LA
        SAMPLING THEOREM LA LA LARGE SAMPLE SIZE LA LA LA LA" at
        the top of your voice. Not an elegant approach, but effective.








Perform this thought experiment (or, if you like, go do it):

    Go to YouTube_ and pick a video you've never seen before. Watch it only
    once, all the way through, with the sound off; then evaluate the quality
    of the video on a scale from one to ten. Be sure to answer correctly, as
    you're being graded on the response.

"No way that's fair, you vindictive sack of crap," one might respond, "you
can't grade me on my opinion!" Of course, therein lies the problem: such an
answer would be entirely subjective, and given the test description there's no
meaningful basis on which to argue that any answer is more correct than any
other. Your answer could well be a count of the number of ponies in the video
and still be valid.

In the interests of eliminating ambiguity, let's try an alternative test setup:

    Go back to YouTube, and find a video available in HD. Watch it in 720p,
    then again in 360p. Pick which video is of a higher quality.

Here's a test we can sink our teeth into. By involving a comparison between
two videos, we've provided context for the interpretation of the result; using
the same source material for both samples largely eliminates the effects of
user preference for anything other than video format. The constrained response
even allows us to reduce the variable to a single boolean value: did the user
choose the video we expected them to?

This test setup is known as a two-alternative forced choice task, or even more
generally as a pairwise comparison. Pairwise testing has been a cornerstone of
psychophysical measurement since the field's inception [Thur1927]_, and
remains one of the most effective and generalizable methods of indirectly
measuring properties which don't have a physical unit or otherwise escape
direct characterization.

As designed, however, the experiment won't reveal much useful information; we
can guess with a very high degree of confidence which video an earnest user
with normal vision will select. In order to gather more useful information, we
need to make a few adjustments to our experimental design, first among these
being to compare samples which aren't so far apart in quality.

If we represent the reduction in quality between two samples as a *distortion signal* applied to an original signal, we can model the activity described above as a signal detection problem. 

It is common, if a bit oversimplified, to model the evaluation of the quality
of a video in working memory as a stochastic variable having an underlying
probability distribution with an approximately Gaussian shape and relatively
constant variance within a limited dynamic range [Schif1982]_. In other words,
our measurement of quality is a bit noisy\ [#]_.

.. [#]  Okay, I'm mangling the theoretical basis a bit. Frankly, most texts
        I've read go something like 'assumption assumption assumption
        assumption SAMPLING THEOREM assumption assumption SAMPLING THEOREM',
        which is sound, I guess, but entirely unsatisfying, and so there's not
        much citable work to go on. I'll clean this up before actually writing
        an *academic* paper, and rest assured that I'll vet the stats
        generated from this project thoroughly before doing anything with them.

When comparing samples that differ considerably in quality, the difference is
much larger than the "assessment noise", and thus it is enormously unlikely
that a trial would result in an incorrect assessment. However, if two samples
differ very little, the noise can easily drown out that difference, allowing
the user to actually perceive the lower-quality sample as having a higher
quality, and indicating as much. Of course, it's much more likely in those situations that the user will be aware of not being able to discriminate 




tests have been a cornerstone of psychophysical measurement for the better part of 

Of course, the test doesn't really shed much light on 




are less concerned with what's 



Most individuals presented with such a task would 








1. Were you correct?
2. Why did you give it that rating?
















Although the instructions don't convey enough information to unambiguously
answer the first question, it's not entirely a trick question; if we define the
1-to-10 scale for video quality more meaningfully, an evaluation on that scale
also becomes meaningful. The goal of most existing efforts to define such a
scale is to produce a system which reflects the ratings that would be assigned
by the average viewer. This description has a clear and sensible intuitive
meaning, but from a statistical standpoint it is painfully vague.

The meaning of a scale for video quality assessment can be made much more
rigid by basing the scale on a well-defined unit of perceptual sensitivity,
the Just Noticeable Difference. Intuitively, the JND can be described as the
smallest difference between two samples that an average viewer can detect in
normal viewing conditions. The mathematical definition is a bit more verbose;
since most of the conclusions we hope to reach depend on the JND, we'll spend
the next few paragraphs establishing it.

Defining the Just Noticeable Difference
```````````````````````````````````````

Here's another thought experiment: Go back to YouTube, and find a video
available in HD. Pick either the 720p or the 480p video quality setting, and
show it to a friend one time through in full-screen mode, without letting them
know which quality setting you chose. Immediately do the same thing with the
other quality setting. Now ask them to pick which video they thought was of a
higher quality. It's easy to imagine that most people will consistently pick
the 720p version in this test.

Now imagine conducting the same experiment, except instead of using 720p and
480p, use 720p and 700p\ [#]_. This time, you might expect it to be a lot more
challenging to determine the right answer. Your most sharp-eyed and attentive
friends might be able to consistently identify the higher-quality version,
but the rest might not be able to notice any difference between the two, and
would be forced to resort to simply guessing which is which. If we move the
quality settings closer still, even the best human viewers may not be able to
notice the change in quality level.

.. [#]  Ignore aliasing. It's just an example.

This setup is known as a two-alternative forced choice task. The result of a
single round of this test is a boolean value, representing whether the user
chose the correct (expected) sample; multiple runs yield the proportion of
correct choices, `$p_c$`, for this particular viewer and pair of samples.

The result of a large number of trials of a TAFC task using two samples which
are perfectly indistinguishable—perhaps copies of the same file with different
labels—is expected to be `$p_c=0.5$`; at each trial a user would be forced to
guess which of the two identical samples was 'correct'. If instead a TAFC
experiment is conducted with samples that are easily distinguishable by a
competent member of the population under study—present users with a bright
white and a pitch black image, and ask them to identify which one is
brighter\ [#]_—the expected result of many trials is `$p_c=1.0$`.

.. [#]  We assume that a user always makes the correct choice if a difference
        is discernable, which is not always the case; this assumption will
        be explored in more detail later.

For a sample pair whose difference is neither patently obvious nor too small
to notice, we expect a user to detect the difference between the samples in
some trials but not others. If a difference is detectable, the user responds
correctly with `$p_{cd}=1.0$` for such trials; otherwise, the user responds by
guessing with `$p_{cg}=0.5$`. The sum of those values then represents the
combination of detection and guess events. Using this, we can relate the
proportion of correct responses `$p_c$` to the proportion of trials in which a
difference was detected `$p_d$` as

`$$p_c = p_d \cdot p_{cd} + (1 - p_d) p_{cg} = \frac{1 + p_d}{2} \Rightarrow
p_d = 2p_c - 1$$`



We are interested in the distribution of this f


A recent survey of full-reference\ [#]_ image quality metrics [Sheikh2006]_
revealed that a few methods have gotten quite good at matching human judgments
of the quality of still images to which certain distortions had been added.

.. [#]  Full-reference metrics reveal the loss in quality caused by introducing
        distortion into an image, while no-reference, and to a lesser extent
        reduced-reference, metrics are intended to assess an image as a human
        might without seeing the original. Full-reference methods are closer to
        the needs of video coding, and we'll consider them exclusively herein.

.. [Keel2002]   Keelan, Brian W. *Handbook of Image Quality*, 2002.
                Marcel Dekker, Inc. `Amazon link`__.

.. __: http://www.amazon.com/Handbook-Image-Quality-Characterization-Engineering/dp/0824707702/ref=sr_1_1?ie=UTF8&s=books&qid=1265961536&sr=8-1

.. [Wick2002]   Wickens, T. D. (2002). *Elementary signal detection theory*.
                Oxford: Oxford University Press. `Amazon link`__.

.. __: http://www.amazon.com/Elementary-Signal-Detection-Theory-Wickens/dp/0195092503/ref=sr_1_1?ie=UTF8&s=books&qid=1266041473&sr=8-1

.. [Thur1927]   Thurstone, L.L. (1927). A law of comparative judgement.
                *Psychological Review*, 34, 273-286.

.. [Schif1982]  Schiffman, Harvey Richard. *Sensation and Perception*, 2nd 
                ed., 1982. John Wiley & Sons, Inc. `Amazon link`__.

.. __: http://www.amazon.com/Sensation-Perception-Harvey-Richard-Schiffman/dp/0471082082/ref=tmm_hrd_title_4

.. [Sheikh2006] Sheikh, H.R.; Sabir, M.F.; Bovik, A.C., "A Statistical
                Evaluation of Recent Full Reference Image Quality Assessment
                Algorithms," Image Processing, IEEE Transactions on , vol.15,
                no.11, pp.3440-3451, Nov. 2006. DOI: `10.1109/TIP.2006.881959`_

.. _10.1109/TIP.2006.881959: http://dx.doi.org/10.1109/TIP.2006.881959

