The Codec Game
Proposing a new method of assessing video quality based on human feedback.
























Perceptual coding is tricky business. One of the challenging aspects of
designing a lossy video (or audio) codec is determining how good it is.
Mathematical quality evaluation metrics such as PSNR or MSE exist for images,
but do not map directly to _human_ assessments of quality; for instance, PSNR
often "prefers" coded images that are less crisp when the source image
contains sharp anisotropic 1-D discontinuities, such as object outlines in
animation. [image 1] Of course, if we can't get a mathematical model of a
human, we can at least get a human to rate things manually, no?

Well, no; not directly, at least. Present two video clips, images, or audio
segments to a human, each of which has been noticeably distorted by
compression, but both by different compression schemes. Ask the human to
indicate which of the two is better, and if you're enormously fortunate you
_might_ get a statistically significant preference. Ask the human to
characterize the _degree_ by which one image is better than the other, and hoo
boy you have a mess on your hands.

[image 2: "On a scale of one to five, how satisfied are you with this coding
technique?"]

When considering the quagmire of human visual quality assessment, it's
encouraging to reflect on the audio community's success in this department.
Audio researchers have a statistical tool which can be used to compare two
samples: the "ABX test":http://en.wikipedia.org/wiki/ABX_test. It's a
self-contained double-blind experiment that can easily be self-administered.
In an ABX test, the user is given two controls, labeled A and B, that each
play a different sample[1]. At the start of a trial, a third control, X, is
randomly configured to play either A or B. The user's task is to identify X as
either A or B. If X can reliably be identified, there's a perceptible
difference between A and B; if not, the two are essentially indistinguishable,
and the user can save bits or dollars by choosing the technically inferior
version.

fn1. Audio coding researchers usually use compressed and uncompressed versions
of the same sound sample as A and B; audiophiles might place a $500 amplifier
next to a $10,000 one.

The ABX test is well-loved because it is simple to administer, easy to
interpret statistically, and quite decisive. But it's also fundamentally
limited. The question it asks—"Can you tell the difference?"—is a yes-or-no
proposition, and as much as you might want to, there's no easy way to extract
any other information out of an experimental run, such as "How large is the
difference?" On its surface, this makes the test nearly useless for video
applications. It is trivial to exceed the sensitivity of the human auditory
system with lossy-coded material at a low bitrate (relative to video); as a
result, it is often practical to store and distribute versions of audio
samples that are indistinguisable from the original content. Video, on the
other hand, requires a far larger amount of data to attain perfect
reconstruction. As a result, nearly all video distributed today would easily
fail in a side-by-side comparison, if the user was familiar with the visual
hallmarks of digital video compression. So if the answer's always going to be
yes, why bother asking?

What we need is a way to do the same test with a different question.

h3. Rate-distortion optimization

A significant amount of video coding is deciding what to keep and what to
throw away. Keeping details in an image inevitably requires more bits, as the
information about the details has to be stored somehow. But the number of bits
each detail will take to transmit, and the degree to which that detail's
presence or absence will affect 
