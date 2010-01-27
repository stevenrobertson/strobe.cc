The Codec Game
==============

:Author: Steven Robertson
:Contact: steven@strobe.cc
:Published: 2009-11-12
:Updated: 2009-12-30
:Tags: Video, Algorithm, Article
:Abstract:
    Evaluating the quality of a video codec analytically is both a critical
    part of the coding process and rather difficult to do. This might help.

Image quality evaluation in video coding
----------------------------------------

Video coding makes use of image quality metrics in at least three distinct
capacities.  The first happens during coding, where a simple metric like PSNR_
or MSE_ will be used to estimate the loss in fidelity associated with the
removal of image information from a video stream. These metrics often drive
rate-distortion optimization techniques, which are designed to retain the most
important pieces of information in a video stream, given a limit on the
maximum number of bits that can be allocated to store such information. These
techniques are usually chosen to be simpler, as optimizations against
higher-order curves (or worse yet, truly nonlinear metrics) can be
mathematically challenging and computationally intense.

.. _PSNR: http://en.wikipedia.org/wiki/PSNR
.. _MSE: http://en.wikipedia.org/wiki/Mean_squared_error

More advanced metrics can be employed to provide post-compression feedback to
the user (or automated system) performing the compression. This is
particularly useful in real-time or batch processing, where visual
verification of the total collection is impractical, although there may be a
particular neurocognitive condition which compels users to obsessively watch
the automated quality evaluation metrics while a video is coded [#]_.

.. [#]  The same condition, perhaps, that draws geeks to watch the pieces
        of a torrent slot into place, or the accurate but meaningless
        visualizations of many cloud-computing projects like SETI@Home.

Another use for video quality metrics, and the one we'll be considering most
particularly here, is in providing feedback for optimization of the video
coding process as a whole, including both video coding researchers and
individuals performing video coding. In this capacity, the entire video is
considered, both as a collection of individual frames and as a whole entity,
and is assessed on an apparently simple but analytically quite complex
question: "How good is it?"

Feedback from our viewers
-------------------------

Let us assume for a moment that we have an _oracle_ that can reliably,
consistently, and accurately answer the question above for any video sample we
throw at it. What do we do with it?

Aside from the poor souls who measure their self-worth via the quality of
their home entertainment systems, this oracle would be useful to two major
classes of people: those who are using coding systems to encode video samples,
and those who are developing the coding systems.

The first group of individuals have a set of videos they would like to encode.
The goal is to identify a combination of parameters that produces either the
highest-quality encoded video at a particular bitrate, or the lowest-bitrate
encoded video for a particular quality. We refer to the set of possibilities
for encoder settings as a *parameter space*; a particular combination of
parameters describes a point within the parameter space, in much the same way
that a set of coordinates ``(x, y, z)`` describes a point in three-dimensional
space. The goal can then be expressed as wanting to find the best point(s) in
the parameter space, given a particular video and constraints on bitrate or
video quality.

Several approaches exist to search parameter spaces like this for
optimization, such as Monte Carlo methods, genetic algorithms, and even
Lagrangian optimization (given certain well-defined aspects of the parameter
space). However, it is important to consider that most users will only have a
finite amount of time; the parameter space is incredibly large, and may not be
searchable exhaustively, especially given bounds on the computational
resources and the capacity of the oracle. Thus, the user is tasked with
determining a *representative sample* of videos, and running such
optimizations on that sample, in order to generalize the results and find an
optimal set of parameters for a particular class of videos [#]_.

.. [#]  Of course, the user usually just wants to rip the DVDs they rented
        from Netflix, so this kind of optimization falls to the developer
        anyway, to be exposed to the user in the form of encoder presets.
        The distinction between *user* and *developer* here isn't that they
        be separate people, but rather that the user can't tweak the coder's
        internals.

Codec developers face much the same problem—except on an infinitely larger
scale.
