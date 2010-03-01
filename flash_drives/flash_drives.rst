Filesystem Reliability on Flash Drives
======================================

:Author: Steven Robertson
:Contact: steven@strobe.cc
:Copyright: 2010 Steven Robertson. CC Attribution 3.0 US.
:Tags: Filesystems, Benchmark, Article
:Abstract:
    I put several filesystems on USB flash drives through hell to find out
    if any make it back alive.

*This benchmark is in planning only; I'm still building the test rig.*

Neuros_ sells the Link_, a commodity x86 machine with a Ubuntu variant
pre-installed, designed to be a home theater PC as well as an open platform for
"hacking TV". As sold, the Link boots from a USB flash drive, using a writable
root partition. During the development process, this setup was anywhere from
"a little bit flaky" to "disastrously unstable". Joe_ asked me to look into the
reliability of root filesystems on USB. With my traditional flair for
over-engineering, I decided to turn it into a comprehensive benchmark of
filesystem reliability.

.. _Neuros: http://open.neurostechnology.com/
.. _Link: http://www.neurostechnology.com/
.. _Joe: http://en.wikipedia.org/wiki/Joe_Born

Precedent
---------

Filesystem reliability is a critically important aspect of an operating system;
data loss is usually considered a showstopper by an OS release, and slow
filesystem development cycles ensure that such bugs are rare after a filesystem
is marked stable. That's not to say those bugs_ don't exist, or that
`competent users`_ aren't running into them, but they're rare enough that most
users can assume that a filesystem which is marked stable *is* stable. When a
bug is found that can be traced to the filesystem code, the bug is usually
fixed as soon as possible.

.. _bugs:
    http://bugzilla.kernel.org/buglist.cgi?product=File+System&bug_status=NEW&bug_status=REOPENED&bug_status=ASSIGNED&component=ext4
.. _competent users: http://www.phoronix.com/scan.php?page=news_item&px=Nzk0OA

Perhaps as a consequence of this, I haven't seen the results of any
filesystem stability benchmarks around the 'net. If such a benchmark showed
anything less than perfect scores for any filesystems involved under normal
conditions, it's quite likely that the maintainers of the filesystem would
fix those bugs as soon as possible, so rather than going through the
trouble of publishing a benchmark you might as well just submit an issue
report.

On the other hand, drives fail relatively often. Filesystems justifiably
assume that 

There are a few tools designed to expose filesystem *consistency*\ [#]_ issues,
like the simple but effective fsx_. The tool assaults a single file with random
operations, and has a history of exposing implementation bugs in many
filesystems. Because of this, though, fsx is unlikely to reveal any new bugs;
the kernel developers have most assuredly run this tool themselves. It also
operates in such a way that most reads and writes actually come from the page
cache, so it's not appropriate for this article's benchmarks.

.. _fsx: http://www.codemonkey.org.uk/projects/fsx/

.. [#]  For this article, consistency refers to a filesystem behaving correctly
        under normal conditions; reliability refers to behavior in both normal
        and degenerate circumstances.

Approach
--------

Given that the filesystems themselves are stable when run on a "proper" medium,
there are a few places worth investigating as the source of filesystem
corruption on USB flash drives. One is a failure of the flash drive itself to
store information consistently, but given the popularity and maturity of flash
technology this seems unlikely to be a persistent source of failure. Another
potential source of error is an 

