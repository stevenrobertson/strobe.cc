OK to Disconnect? Part 1
========================

:Author: Steven Robertson
:Contact: steven@strobe.cc
:Copyright: 2010 Steven Robertson. CC Attribution 3.0 US.
:Tags: Filesystems, Benchmark, Article
:Abstract:
    USB flash drives don't play well with non-FAT filesystems, resulting in
    data loss. In this series of articles, we'll find out why — and how to
    fix it.




Joe Born approached the Neuros_ community a few months ago with a problem.
The `Neuros Link`, a home theater PC built from commodity x86 hardware and
running a Ubuntu variant, was intended to run its operating system from a
USB flash drive.


Getting Ubuntu running on a flash drive is simple; recent versions even
include a wizard which will perform the installation process for you. With
Linux experts on staff and in the community, Neuros quickly developed a
working drive image.








This article was written with the aim of shedding a bit of light on two
related questions: which flash drive model is the most reliable, and which
filesystem is the most resistant to errors when used on flash media? As
will be stressed later, the results in this article are very connected to
the test methodology, and it is *absolutely wrong* to generalize them.
Still, the results are (well, *should be*) interesting, and answer a few
specific questions I've had about filesystems on USB Flash drives.

.. contents::

The questions arose in a discussion with Joe Born of Neuros_. The `Neuros
Link` is a commodity x86 machine with a Ubuntu variant pre-installed,
intended as both a functional home theater PC as well as an open platform
for "hacking TV". As sold, the Link boots from a USB flash drive, using a
writable root partition. In a particular configuration during testing, this
combination would be surprisingly unstable; a clean boot and shutdown would
do enough damage to the filesystem to render the USB stick unbootable.

.. _Neuros: http://open.neurostechnology.com/
.. _Neuros Link: http://www.neurostechnology.com/

Joe asked my opinion on the questions that kick off the article. I
responded with a few hunches, but wanted more reliable data to back my
answers, so I searched for measurements of the reliability of both flash
drives and filesystems — and didn't find any. I was initially surprised to
find that the nobody had tried to come up with these numbers before, but as
it turns out, there are some solid explanations as to why this benchmark
appears to be novel.


Precedent (or lack thereof)
---------------------------

*Warning: potentially obvious explanations follow. I'm still writing in
thesis mode, sorry.*

Filesystems change slowly
`````````````````````````

Filesystem consistency is a critical part of the stability of nearly every
major operating system desgined for consumer use, and has been for
generations. The bandwidth and cost of local physical media massively
outstrips that of networked storage, and the desktop metaphor, including
hierarchical file storage, is still firmly entrenched in both users and
applications; even those platforms which intentionally hide the filesystem
from users, such as iPhone OS, still have a filesystem underneath, because
both OSes themselves and the alternative application-level systems for data
storage (such as databases) which fit on anything less than a datacenter
are still built on top of a filesystem. In larger deployments, demand for
component interchangeability, fault tolerance, and data recovery provides a
significant incentive to ensure that any given filesystem in use can be
read from many platforms, and at the consumer level, portable media makes
similar demands for different reasons. These factors tend to cause the
development and deployment of new filesystems to be dramatically slower
than most computing technologies — on the order of decades, rather than
months.

In other words, most filesystems are *extremely* well-tested.

In accord with this, bugs in filesystem code which result in inconsistent
behavior under normal operating conditions are rare. They can
occasionally__ sneak into deployment, but when that happens they're usually
treated as show-stoppers and resolved as quickly as possible. When such
bugs are found, they are typically only observed under unusual conditions;
between practical testing and automated tools like fsx_,
frequently-encountered issues are usually caught long before they enter the
wild.

.. __:  https://bugs.edge.launchpad.net/ubuntu/+source/linux/+bug/330824

.. _fsx: http://www.codemonkey.org.uk/projects/fsx/

However, no single developer — perhaps not even a single *company* — could
afford to amass even a modest fraction of the hardware upon which these
filesystems will eventually be expected to work upon; no matter how much
testing one may wish to do, there will always be more system configurations
in deployment. To deal with this, component manufacturers rigidly adhere to
a hierarchy of specifications that culminates in an interface standard such
as SATA_ or `USB MSC`_.  The OS matches this with another set of
abstractions, presenting something such as a `block device`_ to the
filesystem code [#]_.

.. [#]  At the extreme ends of storage — embedded devices and datacenter
        systems — things are more varied, and the distinction between
        hardware and software gets muddled. Even some filesystems
        themselves, such as JFFS2_, are tied to particular hardware, and
        won't work with a generic block device abstraction.

As long as every component behaves as required by the interface it
fulfills, a filesystem can function independent of the medium on which it
resides. Performance considerations aside, it is *possible* to run the same
filesystem implementations on a floppy disk and a `SAN`_, and expect both
to remain consistent.

But what happens if the abstraction misbehaves?

Interfaces are guarantees
`````````````````````````

Hardware manufacturers also have considerable interest in making sure the
components they sell behave according to spec throughout their rated
lifetime, as the cost of a faulty component goes beyond replacing a single
disk. The ill-will and reputation damage done by even a small number of
faulty drives can be enough to tank a storage provider, as evidenced by
IBM's Deathstar__. One of a few countermeasures employed by modern drives
and controllers is `S.M.A.R.T.`_, a system designed to model and test the
drive to warn the user of impending drive failure.

.. __: http://en.wikipedia.org/wiki/IBM_Deskstar

But these warnings are imperfect, and often ignored or hidden from the
user. Other flaws can also remain undetected, such as a chipset which
misbehaves under a certain rare-but-not-impossible set of conditions. These
things do happen [#]_, and the naïve user might suggest that filesystems
should be designed with enough resilience to survive these incidents
unscathed.

.. [#]  Sysadmins, feel free to insert "to me, ALL THE FRIGGIN' TIME".

Suggest that to filesystem developers, however, and you're likely to get
stabbed with a mounting bracket.

They would be right to do so.





They would be right to do so. The variety
of failures that a capricious universe may inflict upon a storage subsystem
is essentially limitless [#]_, and the idea that a piece of software can
continue to operate in the face of *any* hardware fault is preposterous.

This is not to suggest that filesystem developers don't take stability in
the face of *certain kinds* of faults into account. In particular, most
modern filesystems are designed from the platter up to recover from
transient faults, like unexpected power loss or system crashes. Some of the
newer copy-on-write filesystems like ZFS_ and BtrFS_ can even recover from
less obvious errors, such as accidental deletion by a user.

Nevertheless, it is important to realize that, no matter how
well-engineered a filesystem is, it can't predict or control faults that
happe

Boring or irresponsible
```````````````````````

Since both filesystems and the storage media they run on are engineered for
stability, a benchmark which compares the reliability of filesystems on
storage media under traditional usage systems would be, well, rather dull.
*Oh, gee, every combination passed. How intriguing.* Not exactly something
that's gonna bring in the viewers.

In the unlikely event of actually finding a test that reliably failed, both
hardware and software vendors would undoubtedly work to fix it quickly;
it'd be easier to file a bug report and have done with it than go through
the trouble of writing up a benchmark and then retracting it later.

To make things more interesting, one might consider constructing a
filesystem torture test: inject faults underneath the filesystem layer. As
has been established, though,


I'm belaboring this point with good reason. It might be tempting to
generalize these benchmarks to claim "ext4 is more stable than NTFS" [#]_,
but doing so is


.. [#]  Haven't run the benchmarks yet, it might end up being the other way
        around.






Say that a drive has a few bad sectors, or that there's a bug in a
chipset's storage I/O which causes a drive to behave improperly in certain
circumstances. Ideally, we would be able to detect such failures, but
technologies like `S.M.A.R.T.`_ are only partially effective in practice
and so the is common [#]_ such a condition could occur. Should a filesystem
be expected to function correctly on faulty hardware?





Calling a filesystem "unstable" if bad sectors cause data loss is roughly
equivalent to accusing an auto manufacturer of unsafe design if a station
wagon doesn't survive orbital re-entry. It's impossible to guard against
infinite eventualities; at some point


That's not to say developers use this as an excuse to design filesystems
that will become unrecoverable the first time a system shuts down
uncleanly. Certain failures are far more likely than others, and most
filesystem teams take great pains to ensure that data loss is minimized in
the event of both transient and systemic failures of the block device
abstraction, by using preventative redundancy measures such as journaling_
and providing an fsck_ and other fault-repair utilities.

Nor are hardware manufacturers ignorant of the





.. _SATA: http://en.wikipedia.org/wiki/SATA

.. _USB MSC: http://en.wikipedia.org/wiki/USB_mass_storage

.. _block device: http://en.wikipedia.org/wiki/Device_file_system#Block_devices

.. _SAN: http://en.wikipedia.org/wiki/SAN

.. _S.M.A.R.T.: http://en.wikipedia.org/wiki/S.M.A.R.T.

.. _journaling: http://en.wikipedia.org/wiki/Journaling_file_system

.. _fsck: http://en.wikipedia.org/wiki/Fsck
