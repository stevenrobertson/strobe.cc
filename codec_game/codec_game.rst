The Codec Game
==============

:Author: Steven Robertson
:Contact: steven@strobe.cc
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
the automated quality evaluation metrics while a video is coded [#]_.

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

-------------------------

Let us assume for a moment that we have an *oracle* that can reliably,
consistently, and accurately assess the quality of any video sample we
throw at it. What do we do with it?

The first use we'll consider is optimizing existing video coding techniques.
Given a source video, the result typically required is to produce a coded
video which either has the highest quality for a given bitrate, or conversely
the lowest bitrate for a given filesize, subject to constraints on both total
and differential CPU time\ [#]_. For the sake of mathematics, let's define the 



.. [#]  That is, the video can't take a year to encode, and an option that
        gives a 1% boost in coding efficiency at the cost of a 50% increase
        in time to encode is probably inappropriate for most uses.

Many video coders have staggering numbers of options, each with their own effec








The first group of individuals have a set of videos they would like to
encode.  They also have an encoder which has an abundance of parameters which
can be modified at the start of the encoding process; each setting has a
different effect on both the final video, and on the time it takes to produce
that video.  The goal is to identify a combination of parameters that produces
either the highest-quality encoded video at a particular bitrate, or the
lowest-bitrate encoded video for a particular quality, while still finishing
the encoding in a reasonable time-frame.

A naïve approach is to simply try a bunch of different configurations and
evaluate the results by viewing them. One look at the manual pages for most
modern encoders is enough to understand how untenable that idea is. Even
someone who understands the likely result of certain parameter changes on the
output wouldn't have time to approach anything close to exhaustive testing.
Clearly, we need a different approach.

Lo, the oracle. As defined, the oracle takes a video and returns an index of
the video's quality; pseudo-mathematically, it can be described as a
real-valued function operating over the domain of video signals. If we treat
the video encoder as a function which takes a video and a set of parameters
and outputs a different (presumably crappier) video, chaining the two
functions yields a system which can measure the effectiveness of a given set
of parameters in terms of the goal stated above.

This roundabout definition is useful. Instead of blindly poking at the huge
number of settings available for encoding a video, we can now model the entire
set of possible settings mathematically, and apply optimization algorithms
against this parameter space to determine the points within which best satisfy
the encoding goals. This makes it possible to discover more advantageous
configurations of existing video coding software, and the results may provide
insight into developing new systems for video coding.

Of course, insight alone is insufficient to develop new coding systems. Codec developers must 

Codec developers face much the same problem, except on an infinitely larger
scale: rather than deal with a parameter space with a large but fixed number of
dimensions, someone with their hands in the source can do literally anything to
a video being coded, as long as it complies with the decoder specification.
Someone writing the spec itself is entirely unbounded. Of course, there's only
a limited number of methods that we know about which will produce viable
compression videos, but new ones, and new implementations of proven
techniques, form a set which is still unbounded for any practical purpose.
The point is that automated searches might work for parameter
optimization but a more directed set of questions is needed for developers to
obtain useful information from the oracle.

In summary, our oracle can be used both in an automated fashion to optimize
existing techniques, and in an interactive manner, given a certain kind of
question.


