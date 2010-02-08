The Codec Game
==============

:Author: Steven Robertson
:Contact: steven@strobe.cc
:Copyright: 2010 Steven Robertson. CC Attribution 3.0 US.
:Tags: Video, Algorithm, Article
:Abstract:
    Evaluating the quality of a video codec analytically is both a critical
    part of the coding process and rather difficult to do. This might help.

**Article's definitely far from finished. Come back later.**

Image quality evaluation in video coding
----------------------------------------

Image quality metrics are algorithms—usually purely mathematical, although
there are a few which are best expressed as code rather than math—which
establish a quantitative scale for rating the quality of an image or sequence
of images. The great majority of them are designed to model how a human might
rate the quality of an image, although not all of them do so directly; some
algorithms do no more than measure the energy (in the signal-processing sense)
of the difference between two images, while others attempt to model the entire
human visual system directly.

Video coding makes use of image quality metrics in at least three distinct
capacities.  The first happens during coding, where a simple metric like PSNR_
or MSE_ will be used to estimate the loss in fidelity associated with the
removal of image information from a video stream. These metrics often inform
rate-distortion optimization techniques, which are designed to help the encoder
decide which pieces of visual information are the most important, and therefore
should be allocated the largest number of bits. Image-quality metrics used in
RDO are usually chosen to be simpler, as optimizations against higher-order
surfaces can be mathematically challenging and computationally intense.

.. _PSNR: http://en.wikipedia.org/wiki/PSNR
.. _MSE: http://en.wikipedia.org/wiki/Mean_squared_error

More advanced metrics can be employed to provide post-compression feedback to
the user (or automated system) performing the compression. This is
particularly useful in real-time or batch processing, where visual
verification of the total collection is impractical, although there's no
accounting for users who feel compelled to obsessively watch
the automated quality evaluation metrics while a video is coded\ [#]_.

.. [#]  The same condition drives geeks to watch the pieces
        of a torrent slot into place, or the accurate but meaningless
        visualizations of many cloud-computing projects like SETI@Home.
        It doesn't have to be informative to be mesmerizing.

Another use for video quality metrics, and the one we'll be considering most
particularly here, is in providing feedback for optimization of the video
coding process as a whole, for use by both video coding researchers and
individuals performing video coding. In this capacity, the entire video is
considered, both as a collection of individual frames and as a whole entity,
and is assessed on an apparently simple but analytically quite complex
question: "How good is it?"

Not labeled for individual sale
-------------------------------

Let us assume for a moment that we have an *oracle* that can reliably,
consistently, and accurately assess the quality of any video sample we
throw at it. What do we do with it?

The first use we'll consider is optimizing existing video coding techniques.
Given a source video, the result typically required is to produce a coded
video which either has the highest quality for a given bitrate, or conversely
the lowest bitrate for a given filesize, subject to constraints on both total
and differential CPU time\ [#]_. To achieve this, a number of parameters
exposed by the video encoding software can be adjusted; each parameter can
affect the quality and bitrate of the resulting video, as well as the
computational complexity of the encoding process.

.. [#]  That is, the video can't take a year to encode, and an option that
        gives a 1% boost in coding efficiency at the cost of a 50% increase
        in time to encode is probably inappropriate for most uses.

An experienced user may be guided by familiarity and knowledge of the
underlying properties of each parameter to manually tap out an effective
sequence of parameters, and this one-shot intuitive process is often
sufficient. But there are situations in which the considerable effort of
finding the most optimal encoder configuration is warranted. Those who process
massive amounts of video (YouTube) could save on infrastructure by finding the
best tradeoff between the three factors of quality, bitrate, and CPU time
across general classes of videos; those who distribute a few large videos many
times (Netflix) or over low-bandwidth links (for HD video, nearly everyone)
might not care about the encoding time but could still gain efficiency by
focusing on the first two criteria. Codec developers themselves could also use
the raw data for tasks ranging from constructing default profiles for user
convenience to creating new techniques based on a concrete analysis of what
works and what doesn't.

There are many approaches to tackle this problem; some of the best are (or are
related to) `mathematical optimization`_ techniques, in which maxima or minima
of a function are found, possibly subject to constraints on the parameter
sets. If we recast a subset of the available parameters as dimensions in a
*parameter space*, and apply both the encoding process and subsequent oracle
analysis of video quality as functions operating over the domain of the
parameter space, we generate real-valued functions for CPU usage, file size /
bitrate, and perceptual video quality that can be optimized either separately
or, by combining the parameters, simultaneously.

.. _mathematical optimization:
    http://en.wikipedia.org/wiki/Optimization_%28mathematics%29

Reducing the problem to a mathematical description has certain advantages—not
least of which that academic papers describing the work become easier to
write—but are by no means the only approach to the problem. They're also not
magical. While a "real" optimization technique might be more effective than
human-driven guess-and-check, any general solution using the oracle is going
to require encoding and testing a *lot* of videos, perhaps too many for a
single human operator to create, process and analyze. In other words, for
parameter optimization to be practical, the oracle needs to be able to handle
a high volume of comparisons and must support automated querying and
analysis.

Asking the right question
-------------------------

Optmization of a limited number of parameters is, well, nice and all, but not
really that exciting. What I *really* want, and what I suspect you, dear
reader, want as well, is a way to try out new ideas, rather than fiddle with
the knobs on the old ones.

In some ways this task is considerably simpler. Let us compare "Technique A"
and "Technique B" to find out which one has the higher quality, constrained to
a particular bitrate: encode, call the oracle, done. Bonus points for running
the experiment on a diverse corpus of videos.

For quick tests of smaller changes within an existing coding framework, this
kind of constrained analysis is rather useful; it allows fast iteration and
fine-tuning where laborious and inaccurate manual testing would normally be
required. A codec normally takes many years to move from early research to
widespread adoption; this technique has the potential to shave *whole months*
off of that time. Incredible, right?

But if you were hoping to use automated testing to ensure you can download
video in the new codec of your choice by 2019 instead of 2020, you should
know: when you're developing new coding techniques, a simple A-to-B comparison
is often insufficiently detailed. To make advances, developers need to know
both what works and *why*; this leads to questions that are directed and
nuanced, such as: Which technique's distortion is more discernible if you're
looking for it? Which is more obvious if you're not?  Which type of
artifacting induces more fatigue when watching longer videos?  How much of a
difference does sound quality make in the perception of image quality?

It's essentially the reverse of the previous use case for the oracle: instead
of tweaking a coding system in response to algorithmic feedback, we're
tweaking the quality metric to answer questions posed by a human operator. The
questions we're interested in asking are fairly specific, and therefore this
oracle must be highly adaptable. They also must be able to assess the
responses of a wide range of human stimuli across both tested and untested
forms of distortion. Currently, simulating a full model of the human visual
system and the cognitive tasks that make use of it is untenable; the only
system powerful enough to serve as the oracle's comparison engine is, alas, an
actual human.

Feedback from our viewers
-------------------------

We want our oracle to be capable of a sufficiently large volume of video
quality assessments to run automated optimization tasks, with a relatively
fast (but not necessarily real-time) turnaround, but to have the accuracy and
flexibility of a human. This is mostly an engineering problem, but we need to
continue with the science for a moment longer to ensure the system is properly
designed.

One of the challenges involved in using humans for image quality assessment is
in getting consistent, useful answers out of them. Perhaps the most intuitive
approach is to ask a user to "rate this on a scale from one to ten," and
aggregate the responses, but it turns out that this technique is among the
most challenging to analyze. Since video quality assessment is not a typical
activity, there is no cultural norm for absolute scale VQA\ [#]_, and it's not
possible to simply renormalize individual users as the assessments of
individual subjects will drift dramatically within a session and between
sessions. In a controlled lab with carefully monitored subjects, it may be
possible to produce enough experimental metadata to renormalize the
results[cite], but I strongly doubt that the processing could be automated
against self-reported data from anonymous internet contributors.

.. [#]  For an example of a system that does have a norm, check out the
        product ratings on Newegg_. In almost every case, a five-star
        rating is synonymous with "worked as advertised", and lower scores are
        awarded for products that fail, depending on the magnitude of the
        failure. This partly reflects expectations of failure rates for tech,
        where a product that *doesn't* fail is as much of a surprise as one
        that does, but also reflects the evaluator establishing norms for
        assessment by reading other reviews. This has the effect of making
        Newegg ratings more a direct assessment of *value* than of
        quality, which is useful but also not what we asked for.

.. _Newegg: http://newegg.com

A more robust method is the `ABX test`_, a favorite of the professional and
very-high-end consumer audio markets. The test is delightfully simple to
perform and analyze, to the point where both software and hardware
implementations are readily available which allow a user to self-administer a
double-blind experiment. This ability is contingent on the test being an
objective evaluation of a user's ability to perceive small distortions, rather
than a subjective evaluation of the significance of such distortions; on its
face, this makes an ABX test insufficiently flexible for our purposes, but it
is still worth investigating in order to

A single trial of an ABX test generally goes like this: a user is presented
with two samples, A and B, each of the same sound but subjected to different
processing. The user is told that a third sample, X, is the same as either A
or B, and must choose which.In most cases, one source will be more expensive
(in some sense) than the other; the test is designed assist in deciding
whether


Here's how it goes: a device is given to the user, with three controls,
labeled A, B, and X. The device is prepared with two samples of audio, both
from the same source but subjected to different treatments (in the case of
software testing, one is typically an uncompressed version, the other
compressed; hardware tests might compare an expensive amplifier to a *really*
expensive one). It labels the samples A and B; these typically stay fixed
throughout the test, but don't have to. For each round of the test, the device
randomly chooses either A or B to *also* be labeled as X.  A user can play A,
B, and X as often as they'd like, but may only play them all the way through,
and may only play one at a time. Their goal is to pick whether sample A or B
was also labeled as X.

.. _ABX test: http://en.wikipedia.org/wiki/ABX_test

The results are graded based on the number of times the user correctly
identified sample X. The results form a binomial sample, which can easily be
assessed for the statistical likelihood that random choices produced a result
at least as accurate as the user at this task. This gets turned in to a
yes-or-no question by picking a threshold
