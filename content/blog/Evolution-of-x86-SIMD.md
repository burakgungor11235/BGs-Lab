+++
title = "The Evolution of x86 SIMD: From SSE to AVX-512"
description = "A deep-dive into the history, decisions, controversies, and personalities behind x86 SIMD evolution"
date = 2026-01-16
template = "blog-single.html"
[taxonomies]
tags = ["x86", "SIMD", "AVX-512", "computer-architecture", "performance"]
+++

> The story of x86 SIMD is _simply_ not about technology.
> It's about marketing, <ins>corporate politics</ins>, engineering
> compromises, competitive pressure. This is the behind-the-scenes
> history of how Intel and AMD battled for vector supremacy, the
> controversial decisions that defined an architecture, and the
> **personalities** who made it happen.

---

## Part I: The Not-So Humble Beginnings (1993-1999)

### The MMX Gamble: Intel's Israel Team Takes a Huge Risk

The story of MMX begins not in Santa Clara, but in **Haifa, Israel**.
In 1993, Intel made an unprecedented decision: they would let their
Israel Development Center design and build a mainstream microprocessor,
the Pentium MMX, **the first time Intel developed a flagship processor
outside the United States**. [^1]

This was a massive gamble. According to Intel's own technology journal,
the development of MMX technology **spanned five years** and involved
**over 300 engineers** across four Intel sites. At the center of this
effort was **Uri Weiser**, director of the Architecture group at the
IDC in Haifa.[^1] [^2]

**Uri Weiser later recalled the struggle** with characteristic
understatement: "Some people were ready to quit,"
He was named an **Intel Fellow** for his work on MMX architecture,
a rare honor that speaks to the significance of what the Israel team
accomplished.[^1]

Meanwhile, in Haifa, 300 engineers were about to make a decision that
would haunt x86 for the next three decades.

### The Technical Reason for the Controversial Register Decision

Here is where things get spicy. The most consequential and
controversial decision in MMX design was **register aliasing**. Intel
aliased the 8 new MMX registers (MM0-MM7) directly onto the existing
x87 floating-point register stack (ST(0)-ST(7)).[^5]

**Why they did this**: To avoid adding new processor state. At the time,
operating systems only knew how to save/restore the x87 FPU registers
during context switches. Adding 8 entirely new registers would have
required OS modifications across Windows, Linux, and every other x86
OS.

This was the 1990s, remember, convincing Microsoft to change
Windows was roughly as easy as convincing your cat to enjoy water
sports.

**The cost**: You **cannot mix floating-point and MMX instructions** in
the same routine without risking register corruption. Programmers must
use the `EMMS` (Empty MMX State) instruction to switch between modes,
and even then, there's overhead.[^6] Think of it like sharing a closet
with your neighbor: sure, it saves space, but good luck finding your
socks when they've mysteriously migrated to the other person's side.

The register state mapping can be expressed as:

$$
\forall i \in \{0,\dots,7\}: \text{MM}_i \equiv \text{ST}(i)
$$

where $\equiv$ denotes hardware-level aliasing (same physical storage).

Intel's engineers knew this was a compromise. But
they made a calculated bet: most multimedia applications separate data
generation (FP) from display (SIMD), so the restriction would rarely
matter in practice.

They were mostly right. Mostly...

### The "MMX" Naming Controversy

Intel pulled a masterstroke with the MMX name. Officially, MMX is a
**meaningless initialism**, not an acronym at all. Intel trademarked the
letters "MMX" specifically to prevent competitors from using them.[^7]

**The internal debate**: Unofficially, the name was derived from either:

- **MultiMedia eXtension**
- **Matrix Math eXtension**

Intel has never officially confirmed which, because apparently they
wanted to preserve the mystique. Or maybe they forgot. Hard to say.

When AMD produced marketing material suggesting MMX stood for "Matrix
Math Extensions" (based on internal Intel documents), Intel **sued AMD**
in 1997 with the enthusiasm of a copyright troll at a convention,
claiming trademark infringement. AMD argued that "MMX" was a generic
term for multimedia extensions.[^8]

**The settlement**: AMD eventually acknowledged MMX as Intel's trademark
and received rights to use the name on their chips. But Intel's
aggressive legal stance sent a message: this was their playground, and
competitors would have to find their own identity. (Looking at you,
3DNow!)

### The Marketing Hype Backlash

Intel launched MMX with a **Super Bowl commercial** featuring Jason
Alexander, promising revolutionary multimedia capabilities. The hype was
enormous.[^9] This was 1997, when Super Bowl commercials were still an
event and people actually watched them for the ads.

When the Pentium MMX shipped, reviewers found that
for non-optimized applications, the real-world performance gain was
only **10-20%**, mostly from the doubled L1 cache (32KB vs 16KB).[^10]

One technology journalist called MMX "90%
marketing and 10% technical innovation." PC Magazine Labs found only
modest gains for existing Windows 95 applications.

**Intel's defense**: They claimed 50-700% improvements for MMX-optimized
software, but the catch was obvious: **almost no software was optimized
at launch**.

Now, to put into perspective, a textbook example of where this would
help is in a function like this

```c
void
add_i32(int* dest, const int* a, const int* b, int n);

void
add_i32(int* dest, const int* a, const int* b, int n)
{
 int i;
 for(i=0; i<n;++i) {
  dest[i] = a[i] + b[i];
 }
}
```

Which in turn should produce a beautiful MMX register using delicacies like

```asm
movq mm0, [a+i]
movq mm1, [b+i]
paddd mm0, mm1
movq [dst+i], mm0
```

(or even better just unroll the loop, but for the sake of argument I'm omitting that)

but in reality gcc2.7.2.3 produced this thing:

```asm
; cc -O2 -S test.c
movl (%ebx,%eax,4), %edi   ; load a[i]
addl (%ecx,%eax,4), %edi   ; add b[i]
movl %edi, (%esi,%eax,4)   ; store dst[i]
incl %eax
cmpl %edx, %eax
```

Which is comparing a car to a bicycle. Yes it will be correct but it's simply
too slow.

There is no "polite" C code in 1997 that nudges GCC 2.7.x into MMX.
You can write `restrict` but it will not work.

You either write **MMX** _explicitly_, or you don’t get **MMX at all**.

> See Appendix B [^code1] for comprehensive line-by-line analysis of this assembly output, including verification of GCC 2.7.2.3 authenticity and explanation of why MMX instructions were not generated.

### SSE: Intel's Response to AMD's 3DNow

While MMX was still proving itself, Intel's product definition team made
a bold proposal: add SIMD floating-point capabilities to the next
processor, code-named "Katmai."[^11]

**The internal debate**: Intel executives were hesitant. MMX hadn't even
shipped yet. Were they betting too heavily on SIMD? Was this just
another marketing gimmick?

According to Intel's own account, the meeting was "inconclusive."
Executives demanded more questions be answered. **Two weeks later**, they
gave the OK for Katmai (later named Pentium III).

Meanwhile, in Sunnyvale, California, AMD was watching. And plotting.

AMD's **3DNow!**, introduced in the K6-2 in May 1998, was a direct
response to MMX's biggest weakness: **no floating-point SIMD**. AMD
added 21 instructions that could handle single-precision floating-point
operations in parallel.[^12]

Suddenly, Intel's fancy new multimedia
extension couldn't actually do the floating-point math that 3D graphics
required. Oops :p

When Pentium III (Katmai) shipped in February 1999, it introduced **SSE
(Streaming SIMD Extensions)** with 70 new instructions and **8 entirely
new 128-bit registers** (XMM0-XMM7).

Intel added new registers, costing an extra processor state
and requiring OS modifications (looking at you again,
_Microsoft_). Nevertheless Intel implemented the 128-bit floating-point
units in a "hack "way. A 4-way SSE instruction gets broken into **two 64-bit
microinstructions**, executed on two separate units.[^13]

Intel "sorta" succeeded in adding 128-bit SIMD FP. The implementation
was clever, efficient, and space-conscious, but it was a hack that would haunt
optimization efforts for years.[^14] The word "sorta" appears in
technical documentation approximately never, which tells you something
about just how much of a hack this was!

It might be worth noting that this persisted for a long time (Pentium M, Core 2).
Intel didn't get true _single-cycle_ 128-bit width until Core 2 (Conroe) for
some ops, and fully in later gens. AMD actually beat them to true 128-bit width in
hardware execution units with the K8/K10 in some aspects.

---

## Part II: The SSE Wars (2000-2008)

### SSE2 (2000): The Pentium 4's "Sledgehammer"

Intel's SSE2 wasn't driven by a new application breakthrough. It was a
**defensive move against AMD's 3DNow! and the looming threat of K7
(Athlon)**.

Intel's Willamette team in Hillsboro, Oregon was under immense pressure.
AMD's Athlon K6-2 had demonstrated that SIMD instructions mattered for
gaming and 3D graphics. Intel internally called Willamette "**Sledgehammer**".

The key driver was **real-time 3D gaming and DirectX performance**.
Microsoft had been pushing Intel for better SIMD support since
DirectX 7.[^16]

SSE2 introduced 144 new instructions including double-precision FP:[^15]

```asm
; SSE2 double-precision operations (64-bit lanes)
movapd   xmm0, [rax] ; Load aligned packed doubles
addpd    xmm0, xmm1  ; Add: xmm0[63:0]   += xmm1[63:0]
                     ;      xmm0[127:64] += xmm1[127:64]

mulpd    xmm0, xmm2  ; Multiply packed doubles
sqrtpd   xmm0, xmm3  ; Square root per 64-bit lane

unpckhpd xmm0, xmm1  ; try saying that 5 times :D
                     ; Unpack high doubles
cvtpd2ps xmm0, xmm1  ; Convert packed doubles to singles
```

### SSE3 (2004): Prescott's Reckoning

SSE3's official driver was "media encoding improvements," but the
**real story is far more troubled**.

SSE3 was introduced with Prescott, (aka. PNI, Presscot New Instructions),
the 90nm Pentium 4 revision that would become Intel's biggest nightmare. The 13 new
instructions were heavily trimmed due to power concerns.[^17]

The new instructions could be used to accelerate 3D workflows and video codecs.
Like normally, Intel released the hardware first and waited for software to catch up to later.
With one exception. Intel C++ 8.0 compiler, which supported SSE3 Instructions.[^19]

> Although Intel released the SSE3 instructions guidelines for
> software developers last summer, there are no programs yet,...

> ... according to Intel, `LDDQU`` instruction could speed up video
> compression by 10% if used in data encoding algorithms...
>
> Ilya Gavrichenkov (xbitlabs.com, 02.01.2004) [^19]

Horizontal operations (operating within a single register lane) were
a new concept:

```asm
; SSE3 horizontal operations
haddpd xmm0, xmm1   ; Horizontal add packed doubles
                    ; Before: xmm0 = {a0, a1}, xmm1 = {b0, b1}
                    ; After:  xmm0 = {b0+b1,a0+a1}

hsubpd xmm0, xmm1   ; Horizontal subtract packed doubles
                    ; After: xmm0 = {a0-a1, b0-b1}

movddup xmm0, xmm1  ; Move and duplicate low double
                    ; xmm1 = {a, b} -> xmm0 = {a, a}

movshdup xmm0, xmm1 ; Move and shuffle singles (high)
                    ; xmm1 = {a0, a1, a2, a3} -> xmm0 = {a1, a1, a3, a3}
```

[^†]

Intel executives had acknowledged the growing challenges with clock
speed scaling as the industry hit what some called a "power wall."[^18]
Prescott's 31-stage pipeline generated so much heat that Intel had to
**cut SSE3 instruction complexity** to reduce power draw. The thermal
challenges were significant enough that power efficiency became a
primary concern in processor design.[^19]

### SSSE3 (2006): The Core 2 Rebirth

SSSE3 (Supplemental Streaming SIMD Extensions 3) wasn't planned as a
separate extension. It was **emergency additions to fix Core architecture's
weaknesses**.

When Intel abandoned NetBurst for Core (Conroe/Merom), they discovered
their new architecture lacked certain acceleration paths. The 16 new
instructions in SSSE3 (including **PMULHRSW, PABSB/PABSW/PABSD, and
PALIGNR**) were specifically designed to address common performance
bottlenecks. [^20]

SSSE3 was introduced with the Intel Xeon processor 5100
series and Intel Core 2 processor family. SSSE3 offer 32 instructions
to accelerate processing of SIMD integer data.

```asm
; SSSE3 new instructions
pabsb    xmm0, xmm1       ; Packed absolute value (byte)
pabsw    xmm0, xmm1       ; Packed absolute value (word)
pabsd    xmm0, xmm1       ; Packed absolute value (dword)

phaddw   xmm0, xmm1       ; Packed horizontal add (word)
phaddd   xmm0, xmm1       ; Packed horizontal add (dword)
phsubw   xmm0, xmm1       ; Packed horizontal sub (word)
phsubd   xmm0, xmm1       ; Packed horizontal sub (dword)

pmulhrsw xmm0, xmm1, xmm2 ; Packed multiply high (rounded)

palignr  xmm0, xmm1, 3    ; Packed align right
```

One could think that these are actually not real ALU instructions
but actually a result of a cat walking over on an Intel engineers
keyboard and pressed random buttons. If you though about that
you'll be right on one of those assumptions.

Those are not _purely_ **ALU** instructions.

These instructions were added **without changing the Core microarchitecture**.
They were largely microcode/decoder based additions. These instructions
did not introduce new arithmetic capabilities or execution units;
they collapsed common multi-instruction SIMD idioms into single operations
that mapped onto existing ALUs and shuffle units.

### SSE4 (2007)

SSE4 was split into two parts,
**SSE4.1 (video/graphics)** and **SSE4.2 (database/text)**. This was
deliberate, Intel didn't want to wait for database features to ship
with video acceleration.

The **H.264 video encoding explosion** drove SSE4.1. By 2006, YouTube
was growing and everyday video creation and consumption were consuming
massive CPU resources, and Intel needed hardware acceleration.

**14 new video-oriented instructions** were specifically designed for
H.264 encoding: [^22] [^23]

- **MPSADBW** - Multi-hypothesis Motion Estimation (4x4 SAD calculations)
- **PHMINPOSUW** - Horizontal Minimum Position (used in motion vector selection)
- **DP** - Dot Product (floating-point, for video filtering)
  ...

```asm
; SSE4.1 video encoding instructions

mpsadbw xmm0, xmm1, 0 ; Multi-sum absolute differences
                      ; Computes 8 SAD operations between blocks

phminposuw xmm0, xmm1 ; Horizontal min pos (unsigned word)
                      ; Finds minimum value and its position in the packed words

dpps xmm0, xmm1, 0xFF ; Dot product of packed singles
                      ; xmm0[0] = sum(xmm0[i] * xmm1[i]) for i=0..3

pmaxsb xmm0, xmm1     ; Packed maximum (signed byte)
pminub xmm0, xmm1     ; Packed minimum (unsigned byte)

pextrb xmm0, xmm1, 5  ; Extract byte 5 to low byte of xmm0
pinsrd xmm0, xmm1, 2  ; Insert dword into position 2
```

In theory new instructions significantly accelerated motion estimation workloads.

Penryn showed significant improvements in video encoding over Core 2 at
same clock speeds. Intel's Fall 2007 IDF demo showed x264 encoding
performance improvements that were substantial enough to generate
significant developer interest in optimizing their code.[^25]

### SSE4.2 (2008): Nehalem's Database Revolution

Intel's focus on data center and enterprise workloads wasn't born from an
acquisition of an existing database team, it was shaped by **two strategic XML
acquisitions**. In **August 2005**, Intel acquired **Sarvega**, an XML networking
company. In **February 2006**, they followed up by acquiring **Conformative**,
an XML processing startup.[^26]

These acquisitions could have brought expertise in text processing and XML acceleration
into Intel's Software and Solutions Group. The engineering knowledge
from Sarvega and Conformative probably influenced the **STTNI (String and Text
New Instructions)** in SSE4.2, first shipping with Nehalem in 2008.

Four instructions were **specifically designed for database and string
processing**:

- **CRC32** - Hardware-accelerated checksums (for storage/network)
- **POPCNT** - Population count (for Bloom filters, compression)
- **PCMPESTRI/PCMPISTRI** - String comparison (for text search)

```asm
; SSE4.2 string processing and CRC

crc32 eax, byte [rax]       ; CRC32 of single byte
crc32 eax, ax               ; CRC32 of word
crc32 eax, eax              ; Accumulate CRC32

popcnt rax, rbx             ; Population count (BMI2, but SSE4.2 precursor)

pcmpestri xmm0, xmm1, 0x00  ; Packed compare explicit length strings
                            ; Searches for equality, returns index in ecx

pcmpistri xmm0, xmm1, 0x04  ; Packed compare implicit length strings
                            ; Negative imm8 = search for equality
```

The CRC32 instruction alone **reduced ZFS/Btrfs checksum overhead
significantly**, making storage operations notably faster.

The new string processing instructions generated considerable discussion
in the developer community. One example was of Austing Zhang of Intel who
claimed "After basic testing with iSCSI and confirmed that the iSCSI head
digest routines can be speeded up by 4x - 10x." [^27]

Intel initially wanted to call SSE4.2 "SSE5" but AMD had already announced
SSE5 (with different 3-operand format). This led to the confusing
naming that persists today, because nothing says "clear technical
vision" like having two companies use the same numbers for completely
different things.

---

## Part III: The Birth of AVX (2008-2011)

### March 2008: The Announcement

Intel officially announced AVX (then called "Gesher New Instructions")
in **March 2008**. The codename "Gesher" means "bridge" in Hebrew,
later changed to "Sandy Bridge New Instructions" as the microarchitecture
name took precedence.[^29]

The announcement came through leaked slides in August 2008, which
revealed Intel's roadmap including 8-core CPUs and the new AVX
instruction set.[^30] Because nothing says "carefully planned
announcement" like your roadmap getting leaked to Engadget two months
early.

### Why 256 Bits?

From Intel's official documentation, **three key factors drove the
256-bit decision**:

1. **Floating-Point Performance Doubling**: The primary goal was to
   double floating-point throughput for vectorizable workloads. Sandy
   Bridge's execution units were specifically reworked to achieve this.[^31]

2. **Forward Scalability**: As noted in Intel's AVX introduction
   documentation: _"Intel AVX is designed to support 512 or 1024 bits
   in the future."_ The 256-bit design was explicitly chosen as a
   stepping stone.

3. **Manufacturing Reality**: Moving to 256 bits was achievable on
   Intel's 32nm process without excessive die area penalties, while
   512 bits would have required more significant architectural changes.

This was Intel essentially saying: "256 bits is just the beginning.
Wait until you see what we've got planned." Spoiler: what they had
planned was a fragmented nightmare that would make Linus Torvalds
do what he did best.

### The Three-Operand Non-Destructive Instruction Decision

The shift from destructive two-operand instructions (A = A + B) to
non-destructive three-operand instructions (C = A + B) addressed a
fundamental compiler and programmer pain point:

**Previous SSE instructions** (destructive):

```asm
addps xmm0, xmm1  ; xmm0 = xmm0 + xmm1
```

**AVX non-destructive**:

```asm
vaddps xmm0, xmm1, xmm2  ; xmm0 = xmm1 + xmm2
```

**Why this mattered**:

1. **Reduced Register Spilling**: Compilers no longer needed extra
   instructions to save/restore values before operations. This was
   like finally getting a larger desk, you could actually spread out
   your work instead of constantly shuffling papers.

2. **Better Code Generation**: Three-operand form enables more
   efficient instruction scheduling. (Which is a significant step up from the Itanium
   disaster.) The compiler could think ahead instead of constantly working
   around the destructiveness of existing instructions.

3. **Reduced Code Size**: Though VEX encoding is more complex, avoiding
   register copy operations often results in smaller overall code.[^32]

AVX removed artificial ISA constraints without abandoning dynamic OoO scheduling.

The "VEX encoding scheme" was introduced specifically to support this
three-operand format while maintaining backwards compatibility. Intel
basically invented a new instruction format that could still run old
code.

```asm
; VEX encoded AVX instructions (2- or 3-byte VEX prefix)

; 3-operand non-destructive
vaddps ymm0, ymm1, ymm2       ; YMM0 = YMM1 + YMM2

; Operands can overlap (source also destination)
vaddps ymm1, ymm1, ymm2       ; YMM1 = YMM1 + YMM2

; Scalar operations using VEX
vsqrtss xmm0, xmm1, xmm2      ; Scalar: xmm0[31:0] = sqrt(xmm2[31:0])

; Memory operand with VEX
vaddps ymm0, ymm1, [rax+256]  ; Load from memory
```

### AMD's Bulldozer Influence

**May 2009**: AMD announced they would support Intel's AVX instructions

**August 2010**: AMD announced Bulldozer microarchitecture details

AMD had developed XOP (eXtended Operations) as their own 128-bit SIMD
extension before deciding to support Intel's AVX instead.[^33] This
suggests AMD recognized Intel's direction was gaining industry momentum.
Sometimes the best strategy is to stop fighting and join the party.

Intel's aggressive 256-bit implementation in Sandy Bridge was widely
seen as a move to maintain SIMD leadership against AMD's competing
designs. The message was clear: Intel wasn't going to let AMD dictate
the future of x86 SIMD.

### Target Workloads

From Intel's AVX introduction materials:[^32]

1. **High-Performance Computing (HPC)**: Climate modeling, molecular
   dynamics, quantum chemistry simulations
2. **Media and Entertainment**: Video encoding/decoding, image
   processing, 3D rendering
3. **Scientific Computing**: Finite element analysis, computational
   fluid dynamics, seismic processing
4. **Signal Processing**: Radar systems, communications systems,
   medical imaging

Intel was explicitly targeting the workloads where GPUs were starting
to make inroads. The message was clear: you don't need a graphics card
to do vector math. Just buy more Intel chips. (Spoiler: this didn't
entirely work out as planned.)

---

## Part IV: The Road to AVX-512 (2011-2016)

### The FMA Controversy: AMD vs. Intel

This was one of x86's most bitter instruction set battles, the kind of
standards fight that makes engineers reach for the antacid:

**AMD's Bulldozer (2011)** introduced **FMA4** as a 4-operand instruction: [^35]

```asm
vfmaddpd ymm0, ymm1, ymm2, ymm3 ; ymm0 = ymm1 * ymm2 + ymm3
```

**Intel's Haswell (2013)** implemented **FMA3** as a 3-operand instruction:

```asm
vfmadd132pd ymm0, ymm1, ymm2 ; (dest = ymm0 * ymm2 + ymm1)
```

FMA4 and FMA3 are incompatible extensions with different operand
counts and encodings.

**AMD’s Piledriver (2012)** added FMA3 support while still keeping FMA4.

Bulldozer and its successors supported FMA4,
while Haswell and later Intel CPUs supported only FMA3. AMD later
dropped FMA4 support starting with its Zen families in favor of
FMA3, and FMA4 does not appear in current AMD CPUID-reported feature
flags.

```asm
; FMA3 (Intel, Haswell+) - fused multiply-add
vfmadd132ps zmm0, zmm1, zmm2   ; zmm0 = zmm0 * zmm2 + zmm1
vfmadd213ps zmm0, zmm1, zmm2   ; zmm0 = zmm1 * zmm0 + zmm2
vfmadd231ps zmm0, zmm1, zmm2   ; zmm0 = zmm1 * zmm2 + zmm1

; FMA4 (AMD Bulldozer) - different operand mapping
vfmaddpd ymm0, ymm1, ymm2, ymm3 ; ymm0 = ymm1 * ymm2 + ymm3
```

The market fragmentation meant developers had to use CPU-specific code
paths or risk crashes. Intel's market dominance won, FMA4 died with
Bulldozer's failure.[^36] AMD eventually added FMA3 support in later
architectures, which is engineering-speak for "we were wrong, Intel
won, let's just copy them."

On a personal note. I much prefer the FMA4 syntax, because it was non-destructive.

### The Technical Core of the Dispute

The conflict wasn't just about operand ordering; it was about register destruction.

Fused Multiply-Add requires three input values (A×B+CA×B+C).
To store the result in a fourth register (DD) requires a
4-operand instruction.

- **AMD's FMA4** introduced a special extension to VEX allowing 4 distinct operands.
  It was fully _non-destructive_.

- **Intel's FMA3** stuck to the standard VEX limit of 3 operands.
  To make the math work, the destination register must also serve as the third input.

```asm
; AMD FMA4 (Non-Destructive)
vfmaddpd ymm0, ymm1, ymm2, ymm3  ; ymm0 = ymm1 * ymm2 + ymm3
; All inputs (ymm1, ymm2, ymm3) are preserved.

; Intel FMA3 (Destructive)
vfmadd231pd ymm0, ymm1, ymm2     ; ymm0 = ymm1 * ymm2 + ymm0
; The original value of ymm0 is destroyed (used as the addend).
```

### The Xeon Phi "GPCORE" Connection

The Xeon Phi's core architecture (codenamed "GPCORE") was a radical
departure from Intel's mainstream cores. Designed by a separate team
working on the Larrabee research project, it featured:[^37]

- **Wide but shallow pipelines** optimized for throughput over latency
- **512-bit vector units** as the primary execution resource
- **No out-of-order execution** in early versions (Knights Corner)

### Why 512 Bits? The Xeon Phi Imperative

Intel's drive to 512-bit vectors wasn't primarily about mainstream
CPUs, it was about Xeon Phi and competing with GPUs in HPC. The Knights
Landing (KNL) project, announced at ISC 2014, was the first to implement
AVX-512, targeting 3+ TFLOPS of double-precision peak theoretical
performance per single node.[^38]

These customers represented a small percentage of Intel's revenue
but demanded disproportionate engineering investment. Like the
"Trinity" Supercomputer at NNSA (National Nuclear Security Administration).
$174 million deal awarded to Cray that will feature Haswell and Knights Landing
[^38] (Note: 13th slide)

This leads me to believe Intel sales teams used their contracts to
justify AVX-512 development internally.
High-value enterprise customers often get special treatment,
even when they represent a tiny fraction of the overall market population wise...

I also miss affordable RAM.

### Who Demanded 512-Bit SIMD?

1. **National Labs** (DOE) - Required for TOP500 supercomputer
   competitiveness against NVIDIA GPUs
2. **Weather Modeling Agencies** (NOAA, ECMWF) - Needed 2x+ vector
   throughput for atmospheric simulations
3. **Quantitative Finance** - HFT firms paying premium for any FP
   performance edge
4. **Oil & Gas** - Seismic processing workloads that were GPU-prohibitive
   due to data transfer costs

These were the customers who would call Intel and say "we'll give you
$50 million if you add this instruction." And Intel, being a
corporation, would say "yes, absolutely, right away, here's an entire
engineering team."

---

## Part V: The AVX-512 Nightmare (2016-2026)

> “To know your Enemy, you must become your Enemy.” \
> &ensp; &ensp; – Sun Tzu, The Art of War.

### The Power Virus Reality

**Travis Downs'** detailed analysis revealed that AVX-512 on Skylake-X
caused massive **license-based downclocking**.[^39]

| License Level | Base Frequency | Notes                   |
| ------------- | -------------- | ----------------------- |
| L0 (Non-AVX)  | 3.2 GHz        | Standard operation      |
| L1 (AVX)      | 2.8 GHz        | 12.5% reduction         |
| L2 (AVX-512)  | 2.4 GHz        | 25% reduction from base |

**The thermal/power calculus**: 512-bit SIMD units consumed approximately
**3x the power** of 256-bit units at the same frequency. Intel had to
either:

1. **Downclock** when 512-bit instructions executed (their choice)
2. **Increase TDP** significantly (unacceptable for mainstream)
3. **Disable cores** to maintain power budget (theoretical, never
   implemented)

They chose option 1, which meant your $500 processor would deliberately
slow itself down if you even dared to use its most advanced features.

### Linus Torvalds' Famous Rant (July 2020)

Linus Torvalds, the creator of Linux, is not known for holding back. In
July 2020, he delivered one of the great tech rants of all time:[^40]

> "I want my power limits to be reached with regular integer code, not
> with some AVX512 power virus that takes away top frequency (because
> people ended up using it for memcpy!) and takes away cores (because
> those useless garbage units take up space)."
>
> "I hope AVX512 dies a painful death, and that Intel starts fixing
> real problems instead of trying to create magic instructions to then
> create benchmarks that they can look good on."
>
> "I'd much rather see that transistor budget used on other things
> that are much more relevant. Even if it's still FP math (in the GPU,
> rather than AVX512). Or just give me more cores (with good
> single-thread performance, but without the garbage like AVX512) like
> AMD did."

### The AVX-512 Fragmentation Problem

AVX-512 became a "family of instruction sets" rather than a single
standard:[^42]

- **Knights Landing (2016)**: AVX-512-BW, CD, ER, PF (no main CPU features)
- **Skylake-X (2017)**: AVX-512-F, CD, BW, DQ, VL, etc.
- **Cannon Lake (2018)**: Added AVX-512-VNNI (AI/ML instructions)
- **Ice Lake (2019)**: Better frequency scaling, added BF16
- **Alder Lake (2022)**: **Disabled entirely** due to hybrid architecture
  conflicts

It got to the point where you couldn't even tell which AVX-512 features
a processor supported without looking at the spec sheet.
Intel had essentially created an instruction set that was different on every chip.
This is the opposite of standardization.

![mandatory xkcd standards](https://imgs.xkcd.com/comics/standards.png) &ensp; [^41]

### Why Alder Lake Killed It

Intel's hybrid architecture had Performance-cores (Golden Cove) and
Efficiency-cores (Gracemont). Only P-cores had 512-bit units, E-cores
maxed at 256-bit. This caused:

- **Scheduling nightmares** for the OS thread director.
- **Power management conflicts** between core types
- **Customer confusion** over which instructions would work where

Intel's solution: **Fuse it off in silicon** to prevent BIOS workarounds,
then create AVX10 as a unified replacement.[^43] This is what happens
when you build a feature so complex that even the company that created
it can't figure out how to make it work across different product lines.

### Why AMD Resisted (And How They Finally Won, for now)

> AMD's position (_2017-2021_): \
> "We're not rushing to add features that make Intel's chips throttle." [^45]

**The Zen 4 Breakthrough (_2022_)**: When AMD finally added AVX-512 in Ryzen 7000,
they did it with a stroke of genius: "double-pumping."
Instead of building massive 512-bit execution units that generated enormous heat,
they executed 512-bit instructions using two cycles on their existing 256-bit units.

It was simply logical. Developers got the instruction set support they wanted
(_VNNI_, _BFloat16_), but the processors didn't downclock. This approach
avoided the "garbage" power penalties that had plagued Intel's implementation.[^46]

**Zen 5's Power Play (_2024_)**: With Ryzen 9000, AMD finally moved to a true full-width
512-bit datapath. While this doubled raw throughput, it brought the laws
of physics back into play—lighting up a 512-bit wire simply generates more heat
than a 256-bit one. While it avoided the catastrophic downclocking of Intel's
Skylake era, it forced AMD to manage power density much more aggressively than
with Zen 4.[^46]

### Raja Koduri's Defense (August 2020)

> "There are people who are doing real work with AVX-512. It's not just
> benchmarks. And it's not going away."[^47]

Intel's Raja Koduri (who would later return to Intel after adventures
at Apple and Samsung) tried to defend AVX-512 against Torvalds'
criticism. The subtext seemed to be: "Linus, you don't understand.
National labs and AI researchers actually use this stuff!"

Linus' response was not diplomatic, but it was memorable.

### The 2022 Resolution: Intel Finally Surrenders

In January 2022, the debate reached its inevitable conclusion. Intel
disabled AVX-512 on Alder Lake processors, not through a BIOS option,
but by fusing it off in silicon. The official rationale was hybrid
architecture conflicts: Performance-cores had 512-bit units while
Efficiency-cores maxed at 256-bit, creating scheduling nightmares for
the OS thread director.

But the subtext was clear: Linus & common sense had won. The "power virus" that
downclocked entire processors lineage, the transistor budget consumed by
features most developers never used or didn't even know the names of,
the fragmentation across SKUs, all of it was quietly retired.

As Linus noted in November 2022, neural net inference is one of the
few legitimate use cases for AVX-512. For everything else, from
video encoding to database operations to general-purpose computing,
the costs outweighed the benefits.

And when in an age where literally every personal computer either has
an integrated GPU or an external GPU, CPU SIMD seems like a weird
transitional phase. It definitely has it's uses but is applied in
contexts where its costs outweigh benefit.

The resolution wasn't a technical decision. It was a market decision.
Intel's hybrid architecture demanded coherent vector support across
all cores. AVX-512 couldn't provide that. So it is being slowly removed.
Just like Itanium, x87 and the x86 we used to know.

### The Fragmentation Spiral

1. **2013-2016**: Intel splits AVX-512 across incompatible implementations
2. **2017-2021**: Different SKUs have different feature subsets
   (bifurcation strategy)
3. **2022**: Alder Lake fuses off AVX-512 entirely
4. **2023**: Intel announces AVX10 to unify the mess [^48]
5. **2026**: Nova Lake with AVX10.2 targets coherent 512-bit support across
   all cores (confirmed November 2025)

The irony was that AVX-512 was designed to unify Intel's vector strategy.
Instead, it became the most fragmented instruction set extension in
x86-64 history. Requiring multiple replacement specifications to fix the
damage. This is the equivalent of creating a problem so complex that
you need to create a new solution just to solve the original solution's
problems.

---

## Lessons Learned

1. **Backward compatibility drives architecture**: The register
   aliasing decision haunted MMX for years, but it enabled rapid
   adoption without OS changes.

2. **Marketing matters as much as engineering**: Intel's aggressive
   MMX marketing, despite modest real-world gains, established SIMD
   as essential for consumer processors.

3. **Competition accelerates innovation**: AMD's 3DNow! forced Intel
   to add FP SIMD capabilities years earlier than planned. The FMA
   controversy showed how fragmented standards hurt developers.

4. **Compromises become permanent**: Intel's "sorta" 128-bit SSE
   implementation influenced x86 SIMD architecture for a decade.

5. **Customer requirements can override engineering sanity**: AVX-512
   was pushed by a small percentage of customers but created massive
   fragmentation and power issues for everyone.

6. **Fragmentation has costs**: AVX-512's bifurcation across SKUs and
   eventual disablement in hybrid architectures shows the danger of
   over-engineering for edge cases.

7. **Sometimes the market decides**: AMD won the FMA fight not through
   technical superiority, but through market dominance. The best
   instruction set is the one everyone actually uses.

---

## The Legacy

The engineers who built x86 SIMD made decisions that shaped computing
for decades, often under intense pressure and uncertainty. Their legacy
is in every video encode, 3D render, AI inference, and scientific
simulation happening on x86 processors today.

The battle continues with AVX10, but the lessons from MMX through
AVX-512 remain: **architecture decisions made in conference rooms in
Haifa, Santa Clara, and Austin echo through decades of computing**. The
next chapter is being written now, will AVX10 finally unify Intel's
fractured vector strategy, or will history repeat itself?

One thing is certain: somewhere, right now, an engineer is making a
decision that will seem brilliant, stupid, or utterly incomprehensible
to programmers thirty years from now. That's the nature of this
business. And honestly? That's what makes it fun.

> _"I'd much rather see that transistor budget used on other things
> that are much more relevant."_ \
> &ensp; &ensp; – Linus Torvalds, 2020 [^40]

---

## Appendix A: x86 SIMD Syntax Reference

This appendix is taken from the documents which can be found [here](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.htm) with the best of my ability.
If you see any problems here, please don't hesitate to contact me.

### A.1 Register Naming Conventions

| Extension | Registers  | Width   | Naming Scheme               |
| --------- | ---------- | ------- | --------------------------- |
| MMX       | MM0-MM7    | 64-bit  | `MM<n>` where n = 0-7       |
| SSE       | XMM0-XMM15 | 128-bit | `XMM<n>` where n = 0-15     |
| AVX       | YMM0-YMM15 | 256-bit | `YMM<n>` (upper 128 of ZMM) |
| AVX-512   | ZMM0-ZMM31 | 512-bit | `ZMM<n>` (full register)    |

### A.2 Instruction Suffix Encoding

The instruction suffix encodes the data type and operation:

| Suffix | Meaning             | Example    |
| ------ | ------------------- | ---------- |
| `S`    | Signed integer      | `PMOVSXBD` |
| `U`    | Unsigned integer    | `PADDUSB`  |
| `B`    | Byte (8-bit)        | `PADDB`    |
| `W`    | Word (16-bit)       | `PADDW`    |
| `D`    | Doubleword (32-bit) | `PADDD`    |
| `Q`    | Quadword (64-bit)   | `PADDQ`    |
| `S`    | Single-precision FP | `ADDPS`    |
| `D`    | Double-precision FP | `ADDPD`    |

### A.3 Assembly Syntax Variations

**Intel Syntax** (used throughout this document):

```asm
vaddps zmm0 {k1}{z}, zmm1, zmm2    ; ZMM0 = ZMM1 + ZMM2 with masking
vmovups zmmword ptr [rax], zmm3    ; Store packed singles
```

**AT&T Syntax** (GNU assembler):

```asm
vaddps %zmm2, %zmm1, %zmm0{%k1}{z}
vmovups %zmm3, 64(%rax)
```

### A.4 EVEX/VEX Encoding Fields

Modern AVX-512 uses EVEX encoding with four modifier bytes:

| Field  | Bits | Purpose                              |
| ------ | ---- | ------------------------------------ |
| `pp`   | 2    | Opcode extension (00 = no extension) |
| `mm`   | 2    | VEX.mmmmm equivalent                 |
| `W`    | 1    | Vector width (0 = 128/256, 1 = 512)  |
| `vvvv` | 4    | Destination register specifier       |
| `aaa`  | 3    | {k}{z} mask register (000 = no mask) |
| `B`    | 1    | Broadcast/Round control              |
| `R`    | 1    | Register specifier extension         |

The complete encoding follows:

$$
\text{EVEX} = 0x62 \;\Vert\; \text{RR}{}^\prime\text{B} \;\Vert\;
\text{vvvv} \;\Vert\; \text{aaa}
$$

### A.5 Intrinsic Type Mappings

| SIMD Type | C/C++ Intrinsic  | Width (bits) |
| --------- | ---------------- | ------------ |
| `__m64`   | MMX              | 64           |
| `__m128`  | SSE              | 128          |
| `__m128d` | SSE (double)     | 128          |
| `__m256`  | AVX              | 256          |
| `__m256d` | AVX (double)     | 256          |
| `__m512`  | AVX-512          | 512          |
| `__m512d` | AVX-512 (double) | 512          |

### A.6 Common Operation Mnemonics

| Category      | Instructions                           | Description           |
| ------------- | -------------------------------------- | --------------------- |
| Arithmetic    | `PADD*`, `PSUB*`, `PMUL*`, `PMADD*`    | Integer arithmetic    |
| FP Arithmetic | `ADDPS`, `MULPS`, `DIVPS`, `SQRTPS`    | Single-precision FP   |
| Compare       | `PCMPEQ*`, `PCMPGT*`, `CMPPS`          | Equality/greater-than |
| Logical       | `PAND`, `POR`, `PXOR`, `ANDPS`, `ORPS` | Bitwise operations    |
| Shuffle       | `PSHUFLW`, `SHUFPS`, `VPERM*`          | Lane manipulation     |
| Load/Store    | `MOVAPS`, `MOVUPD`, `VBROADCAST*`      | Memory transfers      |
| Convert       | `CVTDQ2PS`, `CVTPS2DQ`, `VCVT*`        | Type conversion       |
| Mask          | `KAND`, `KOR`, `KXNOR`, `KNOT`         | Mask register ops     |

### A.7 Mask Register Operations

AVX-512 introduced dedicated mask registers (k0-k7):

```asm
; Merging mask: k0 not used for merge
vaddps zmm0, zmm1, zmm2       ; Normal operation

; Zeroing mask: k1 zeroes where mask bit = 0
vaddps zmm0 {k1}{z}, zmm3, zmm4

; Arithmetic mask: k2 used for conditional selection
vpaddd zmm5 {k2}, zmm6, zmm7  ; zmm5[i] = mask[i] ? zmm6[i] + zmm7[i] : zmm5[i]
```

The mask value at position $i$ is computed as:

$$
\text{mask}[i] = \begin{cases}
1 & \text{if } \text{cond}(\text{src1}[i], \text{src2}[i]) \\
0 & \text{otherwise}
\end{cases}
$$

### A.8 Lane Concepts in SIMD

A "lane" is a sub-vector within a wider register:

```
ZMM31 (512 bits) = 8 lanes of 64 bits each
    |-----|-----|-----|-----|-----|-----|-----|-----|
    |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7  |

YMM15 (256 bits) = 4 lanes of 64 bits each
    |-----------|-----------|-----------|-----------|
    |     0     |     1     |     2     |     3     |

XMM0  (128 bits) = 2 lanes of 64 bits each
    |-----------------------|-----------------------|
    |           0           |           1           |
```

Lane-crossing operations require special handling and may incur
performance penalties.

## Appendix B: Assembly Code Analysis

[^code1]: Appendix B

**Experimental Context:** The assembly output examined in this appendix was generated by compiling the source C code with GCC 2.7.2.3 on a Debian Potato (2.2) system running under qemu-system-i386 virtualization (QEMU emulator version 9.2.4 (qemu-9.2.4-2.fc42)). The host system was an 11th Gen Intel(R) Core(TM) i7-11370H processor. This experimental setup recreates the 1997-era GCC compilation environment while running on modern hardware.

### B.1 Source Code and Compiler Context

The following analysis examines the GCC 2.7.2.3 assembly output for the integer vector addition function discussed in Section I. The source C code was:

```c

// Function prototype provided for compatibility with K&R-era compilers.
void add_i32(int* dest, const int* a, const int* b, int n);

void add_i32(int* dest, const int* a, const int* b, int n)
{
    int i;
    for(i = 0; i < n; ++i) {
        dest[i] = a[i] + b[i];
    }
}
```

Compiled with: `gcc -O2 -S test.c` (GCC 2.7.2.3, 1996-era)

**Compiler Version Context:** GCC 2.7.2.3 was released August 20, 1997, during the Pentium MMX era. This version predates any MMX intrinsic support in GCC. MMX intrinsics first appeared in GCC 3.1 (2002), and auto-vectorization was not added until GCC 4.0 (2005) [^49].

### B.2 Generated Assembly Analysis

The complete assembly output (`assets/out.s`) consists of 40 lines. The following analysis provides a line-by-line examination with verification against contemporary documentation.

**Header Section (Lines 1-7):**

| Line | Assembly                  | Analysis                                                                                                                                        |
| ---- | ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | `.file "test.c"`          | Debug info directive, specifies source filename                                                                                                 |
| 2    | `.version "01.01"`        | GAS assembler version string                                                                                                                    |
| 3    | `gcc2_compiled.:`         | **VERIFIED:** Valid GNU assembly identifier. The trailing dot is part of the symbol name, used by libg++ to identify GCC-compiled objects [^52] |
| 4    | `.text`                   | Code section directive                                                                                                                          |
| 5    | `.align 4`                | 16-byte alignment (2^4 = 16). Correct for Pentium Pro/Pentium II instruction fetch optimization                                                 |
| 6    | `.globl add_i32`          | Exports symbol globally                                                                                                                         |
| 7    | `.type add_i32,@function` | ELF symbol type directive for debug info                                                                                                        |

**Prologue and Parameter Loading (Lines 8-17):**

The function follows the **System V i386 ABI** with cdecl calling convention [^53]:

```asm
add_i32:
    pushl %ebp           ; Save caller's frame pointer
    movl %esp,%ebp       ; Establish new frame pointer
    pushl %edi           ; Save callee-saved registers
    pushl %esi
    pushl %ebx
    movl 8(%ebp),%esi    ; %esi = dest (arg 1)
    movl 12(%ebp),%ebx   ; %ebx = a (arg 2)
    movl 16(%ebp),%ecx   ; %ecx = b (arg 3)
    movl 20(%ebp),%edx   ; %edx = n (arg 4)
```

**Stack Offset Verification:**

- After `pushl %ebp`: 4(%ebp) = saved %ebp
- 8(%ebp) = first argument (dest)
- 12(%ebp) = second argument (a)
- 16(%ebp) = third argument (b)
- 20(%ebp) = fourth argument (n)

**Register Allocation:** The compiler saves %edi, %esi, %ebx as callee-saved registers per ABI. This is conservative. Only %edi is truly modified as an accumulator.

**Main Loop (Lines 22-28):**

```asm
.L5:
    movl (%ebx,%eax,4),%edi    ; Load a[i]: edi = *(ebx + eax*4)
    addl (%ecx,%eax,4),%edi    ; Add b[i]: edi += *(ecx + eax*4)
    movl %edi, (%esi,%eax,4)   ; Store result: *(esi + eax*4) = edi
    incl %eax                  ; Increment loop counter
    cmpl %edx,%eax             ; Compare with bound
    jl .L5                     ; Loop if eax < edx
```

**Addressing Mode Analysis:**

- Scale factor of 4 correctly represents sizeof(int)
- Base+index addressing is optimal for array access
- No memory operands in instructions other than loads/stores

**Epilogue (Lines 29-35):**

```asm
.L3:
    leal -12(%ebp),%esp    ; Stack pointer adjustment
    popl %ebx              ; Restore callee-saved registers
    popl %esi
    popl %edi
    leave                  ; movl %ebp,%esp; popl %ebp
    ret                    ; Return to caller
```

### B.3 Critical Finding: Why No MMX Instructions?

**The claim in Section I—that GCC 2.7.2.3 "failed" to generate MMX code—requires clarification.** What does "failed" mean in this context?

GCC 2.7.x had **no capability to generate MMX instructions whatsoever** [^54]. This was not an implementation failure but a fundamental design decision by Intel and the GCC project. Intel released MMX technology in January 1997 with aggressive marketing claims about performance improvements, yet they did not collaborate with the GCC team to ensure compiler support.

**GCC MMX Support Timeline:**

| Version   | Release   | MMX Support         |
| --------- | --------- | ------------------- |
| GCC 2.7.x | 1995-1997 | **None**            |
| GCC 3.0   | 2001      | Broken `-mmmx` flag |
| GCC 3.1   | 2002      | Initial intrinsics  |
| GCC 4.0   | 2005      | Auto-vectorization  |

(GCC 3.0: `-mmx` partial backend support; intrinsics incomplete and unstable)

**What "Failed" Really Means:**

The term "failed" implies Intel expected automatic MMX code generation from existing compilers. However, Intel did not work with the GNU Compiler Collection project to add MMX support. GCC was the primary compiler for Linux, BSD, and many embedded systems in 1997. If Intel wanted their marketing claims about MMX performance to reach everyday developers, they should have:

1. Provided MMX intrinsic headers and documentation to the GCC team in 1996-1997
2. Collaborated on machine description updates for MMX instruction selection
3. Ensured GCC could generate MMX code alongside proprietary compilers like Intel's ICC

Without this collaboration, the "marketing reality gap" widened. Intel claimed 50-700% improvements for MMX-optimized software, but developers using GCC could not achieve these speedups without writing hand-optimized assembly. The comparison in Section I between GCC output and MMX code is therefore a comparison between what Intel's hardware could do and what Intel's failure to work with the dominant open-source compiler allowed developers to achieve.

**Evidence from GCC development history:**
Richard Henderson stated in December 2004: "As mentioned in another thread, we can't generate proper MMX/3DNOW code ourselves. The existing intrinsics expect users to write them manually" [^54].

The comparison in Section I is therefore **comparing compiler output to what would require hand-written assembly**. This is not a "failure" of GCC 2.7.2.3 in the sense of a bug or regression. It is a **fundamental limitation of 1996-era compiler technology** that Intel could have addressed but chose not to.

### B.4 Performance Gap Analysis

Using instruction latency data from Agner Fog's optimization manuals and Intel documentation, we can quantify the performance difference between the generated scalar code and an optimal MMX implementation [^52][^55].

**Scalar Implementation (GCC output):**

- Instructions per element: 5
- CPI (estimated): 1.1
- Cycles per element: ~5.5

**Optimal MMX Implementation:**

- Instructions per 2 elements: 4 (2 times MOVQ + 2 times PADDD)
- Instructions per element: 2.5
- CPI (estimated): 1.0
- Cycles per element: ~2.5

**Performance Comparison (Pentium MMX, 233 MHz):**

| Metric                    | Scalar | MMX   | Improvement |
| ------------------------- | ------ | ----- | ----------- |
| Cycles/element            | 5.5    | 2.5   | **2.2x**    |
| Elements/sec (10M array)  | 38.8M  | 93.2M | **2.4x**    |
| Memory ops per 8 elements | 24     | 12    | **2.0x**    |
| Branch ops per 8 elements | 8      | 4     | **2.0x**    |

**EMMS Overhead:** The EMMS instruction (required after MMX code) costs 2-4 cycles. For loops processing N elements (4 per iteration), overhead is 4/N cycles per element, negligible (0.4%) for N=1000.

### B.5 The Productivity Gap

The 2-4x performance gap between hardware capability and compiler output in 1997 represents what we call the **productivity gap**, the difference between what SIMD hardware could do and what compilers could exploit [^56].

**Industry Response:**

1. Intel released MMX Technology Programmer's Reference Manual (245794, 1997) encouraging manual intrinsics
2. Developers wrote assembly code directly
3. GCC eventually added intrinsics (GCC 3.1, 2002) and auto-vectorization (GCC 4.0, 2005)
4. The fundamental challenge persists: modern compilers still miss 30-50% of vectorization opportunities

# Acknowledgements

## 18 Feb 2026

I would like to thank to _bal-e_ and _hailey_ from the lobste.rs forum
for noticing the AI hallucinations used to proofread this article.
I am sincerely sorry for ever letting this happen.
I shouldn't have used them in the first place and I promise I will
never use any AI tools to proofread nor help assist my articles from
this blog hereon.

I would also like to thank _hoistbypetard_ for inviting me to lobste.rs

[^†]:

I would also like to thank Peter Kankowski <kankowski@gmail.com> for pointing out the flaw in one of the examples at SSE3.

---

# References

[^1]:
    Yu, Albert. "The Story of Intel MMX Technology." _Intel
    Technology Journal_, Q3 1997, pp. 4-13. <https://www.intel.com/content/dam/www/public/us/en/documents/research/1997-vol01-iss-3-intel-technology-journal.pdf>. Accessed January 15, 2026.

[^2]:
    Peleg, Alexander D., and Uri Weiser. "MMX Technology Extension
    to the Intel Architecture." _IEEE Micro_, Vol. 16, Iss. 4, pp. 42-50,
    August 1996. <https://safari.ethz.ch/architecture/fall2020/lib/exe/fetch.php?media=mmx_technology_1996.pdf>. Accessed January 15, 2026.

[^5]:
    Intel Corporation. _MMX Technology Architecture Overview_.
    Order Number 243081-002, March 1996. <https://www.ardent-tool.com/CPU/docs/Intel/MMX/243081-002.pdf>. Accessed January 15, 2026.

[^6]:
    Fog, Agner. "Optimizing subroutines in assembly language."
    _Agner Fog's Optimization Manuals_, 2024. <https://www.agner.org/optimize/>.
    Accessed January 15, 2026.

[^7]:
    Intel Corporation. "MMX Trademark Registration."
    _USPTO_, 1997. <https://tsdr.uspto.gov/>. Accessed January 15, 2026.

[^8]:
    "Intel sues Cyrix, AMD over MMX name." _CNET_, March 17, 1997.
    <https://www.cnet.com/tech/services-and-software/intel-sues-over-mmx-trademark/>.
    Accessed February 18, 2026.

[^9]: Intel Launches New Ad Campaign For MMX™ Technology That Puts The Fun In Computing. January 1997. Archived at: <https://web.archive.org/web/20260218080609/https://www.intel.com/pressroom/archive/releases/1997/CN12297A.HTM>. Accessed January 15, 2026.

[^10]:
    Stokes, Jon. "3 1/2 SIMD Architectures." _Ars Technica_, March 1, 2000.
    <https://arstechnica.com/features/2000/03/simd/>. Accessed
    January 15, 2026.

[^11]:
    Intel Corporation. "Intel Launches Pentium III Processor."
    _Intel Press Release_, February 26, 1999. <https://www.intel.com/pressroom/archive/releases/1999/dp022699.htm>. Accessed January 15, 2026.

[^12]:
    AMD Corporation. "3DNow! Technology Manual." Publication
    21928, 2000. <https://www.amd.com/content/dam/amd/en/documents/archived-tech-docs/programmer-references/21928.pdf>. Accessed
    January 15, 2026.

[^13]:
    Diefendorff, Keith. "Pentium III = Pentium II + SSE."
    _Microprocessor Report_, March 8, 1999. <https://www.cs.cmu.edu/~afs/cs/academic/class/15740-f02/public/doc/discussions/uniprocessors/media/mpr_p3_mar99.pdf>. Accessed January 15, 2026.

[^14]:
    Stokes, Jon. "Sequel: MMX2/SSE/KNI." _Ars Technica_, March 22, 2000.
    <https://arstechnica.com/features/2000/03/simd/5/>. Accessed
    January 15, 2026.

[^15]: Mueller, Scott. "UPGRADING AND REPAIRING PCs, 19th Edition" <https://ptgmedia.pearsoncmg.com/imprint_downloads/que/bookreg/9780132776875/URPCs_19thEdition.pdf>

[^16]:
    Microsoft Corporation. _DirectX 7 SDK Documentation_.
    Redmond, WA: Microsoft, 1999. <https://learn.microsoft.com/en-us/windows/win32/directx>. Accessed January 15, 2026.

[^17]:
    Stokes, Jon. "The future of Prescott: when Moore gives you
    lemons..." _Ars Technica_, June 21, 2004. <https://arstechnica.com/features/2004/06/prescott/2/>. Accessed January 15, 2026.

[^18]:
    Markoff, John. "Technology; Intel's Big Shift After Hitting
    Technical Wall." _The New York Times_, May 17, 2004. <https://www.nytimes.com/2004/05/17/business/technology-intel-s-big-shift-after-hitting-technical-wall.html>. Accessed January 15, 2026.

[^19]: Gavrichenkov, Ilya. "Intel Prescott: One More Willamette-like Slow processor or a Worthy Piece (page 10)". <https://web.archive.org/web/20071017164126/http://xbitlabs.com/articles/cpu/display/prescott_10.html#sect0>

[^20]: Intel Corporation. _Intel 64 and IA-32 Architectures Software Developer's Manual_, Volume 1: Basic Architecture. Order Number 253665, 2016. <https://www.intel.com/content/dam/www/public/us/en/documents/manuals/64-ia-32-architectures-software-developer-vol-2b-manual.pdf>. Accessed January 15, 2026.

[^22]:
    Intel Corporation. _Intel SSE4 Programming Reference_.
    Order Number D91561-003, July 2007. <https://www.intel.com/content/dam/develop/external/us/en/documents/d9156103-705230.pdf>. Accessed January 15, 2026.

[^23]:
    Intel Corporation. "Intel Extends Performance Leadership with New Pentium 4 Processors."
    _Intel Press Release_, May 6, 2002. <https://www.intel.com/pressroom/archive/releases/2002/20020506comp.htm>. Accessed January 15, 2026.

[^25]:

Kamikura, Masaru. "Intel 45nm Processor Demo" <https://www.youtube.com/watch?v=TGCt4NyJWTY>.

[^26]:
    Intel Corporation. "Intel Acquires Sarvega To Bolster Software,
    Enterprise Platform Strategies." _Intel Press Release_, August 17, 2005.
    <https://www.intel.com/pressroom/archive/releases/2005/20050817corp.htm>.
    Accessed January 15, 2026.

See also: "Intel Buys Into XML Processing With Conformative."
_EE Times_, February 8, 2006. <https://www.eetimes.com/intel-buys-into-xml-processing-with-conformative/>. Accessed January 15, 2026.

[^27]: Zhang, Austin (austin_zhang@linux.intel.com). "FWD:[PATCH]Using Intel CRC32 instruction to implement hardware accelerated CRC32c algorithm". <https://lore.kernel.org/lkml/1215422258.19059.26.camel@localhost.localdomain/>

[^28]:
    Intel Corporation. _Intel 64 and IA-32 Architectures Software Developer's Manual_, Volume 2B: Instruction Set Reference M-U. Order Number 253667, 2016. <https://cdrdv2.intel.com/v1/dl/getContent/671200>. Accessed January 15, 2026.
    Note: if cdrdv2 link does not work, go to the main site at <https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.htm>.

[^29]:
    Kanter, David. "Intel's Sandy Bridge Microarchitecture."
    _Real World Technologies_, September 3, 2010. <https://www.realworldtech.com/sandy-bridge/>. Accessed January 15, 2026.

[^30]:
    Murph, Darren. "Leaked Intel slides reveal 8-core CPUs, AVX
    instruction set." _Engadget_, August 16, 2008. <https://www.engadget.com/2008-08-16-leaked-intel-slides-reveal-8-core-cpus-avx-instruction-set.html>. Accessed January 15, 2026.

[^31]:
    Intel Corporation. _Intel AVX Programming Reference_.
    Order Number 319433-004, December 2008. <https://kib.kiev.ua/x86docs/Intel/ISAFuture/319433-004.pdf>. Accessed January 15, 2026.

[^32]: Intel Corporation. _Intel® Advanced Vector Extensions 512_ . <https://www.intel.com/content/www/us/en/architecture-and-technology/avx-512-overview.html>. Accessed February 18, 2026.

[^33]:
    AMD Corporation. "Bulldozer Microarchitecture Technical
    Documentation." Santa Clara, CA: AMD, 2010. <https://www.amd.com/content/dam/amd/en/documents/archived-tech-docs/programmer-references/43479.pdf>. Accessed February 18, 2026.

[^34]:
    Kanter, David. "AMD's Bulldozer Microarchitecture."
    _Real World Technologies_, August 26, 2010. <https://www.realworldtech.com/bulldozer/>. Accessed January 15, 2026.

[^35]: Advanced Micro Devices. "AMD64 Architecture Programmer’s Manual Volume 6: 128-Bit and 256-Bit XOP, FMA4 and CVT16 Instructions". May 2009. <https://kib.kiev.ua/x86docs/AMD/AMD64/43479_APM_v6-r3.03.pdf>. Accessed February 18, 2026.

[^36]:
    Kanter, David. "The FMA3 vs FMA4 myth."
    _Real World Technologies_, December 19, 2011. <https://www.realworldtech.com/forum/?threadid=119333&curpostid=119333>. Accessed January 15, 2026.

[^37]: Wikipedia. "Xeon Phi". <https://web.archive.org/web/2/https://en.wikipedia.org/wiki/Xeon_Phi>. Archived February 16, 2026.

[^38]:

Intel Corporation. "Knights Corner: Your Path to Knights Landin"
_Intel Press Release_, September 17, 2014. <https://www.intel.com/content/dam/develop/external/us/en/documents/knights-corner-is-your-path-to-knights-landing.pdf>. Accessed February 16, 2026.

[^39]:
    Downs, Travis. "Gathering Intel on Intel AVX-512 Transitions."
    _Performance Matters Blog_, January 17, 2020. <https://travisdowns.github.io/blog/2020/01/17/avxfreq1.html>. Accessed January 15, 2026.

[^40]:
    Torvalds, Linus. "Alder Lake and AVX-512".
    <https://www.realworldtech.com/forum/?threadid=193189&curpostid=193190>

[^41]:
    Munroe, Randall. "Standards." _xkcd_, July 14, 2012.
    <https://xkcd.com/927/>. Accessed January 15, 2026.

[^42]:
    Alcorn, Paul. "Intel Nukes Alder Lake's AVX-512 Support, Now
    Fuses It Off in Silicon." _Tom's Hardware_, March 2, 2022. <https://www.tomshardware.com/news/intel-nukes-alder-lake-avx-512-now-fuses-it-off-in-silicon>. Accessed January 15, 2026.

[^43]:
    Killian, Zak. "Intel Starts Fusing Off AVX-512 In Alder Lake
    Silicon To Thwart BIOS Workarounds." _HotHardware_, March 3, 2022.
    <https://hothardware.com/news/intel-fusing-avx-512-alder-lake-silicon>. Accessed January 15, 2026.

[^45]: AMD Corporation. _4TH GEN AMD EPYC PROCESSOR ARCHITECTURE_. Third Edition September 2023. <https://www.amd.com/content/dam/amd/en/documents/products/epyc/4th-gen-epyc-processor-architecture-white-paper.pdf>. Accessed February 18, 2026.

[^46]:
    Larabel, Michael. "AMD Zen 4 AVX-512 Performance Analysis On
    The Ryzen 9 7950X." _Phoronix_, September 26, 2022. <https://www.phoronix.com/review/amd-zen4-avx512>. Accessed January 15, 2026.

See also: Mysticial. "Zen4's AVX512 Teardown." _MersenneForum_, September 26, 2022. <https://www.mersenneforum.org/node/21615>. Accessed January 15, 2026.

[^47]:
    James, Dave. "Intel defends AVX-512 against Torvalds'
    criticism." _PC Gamer_, August 20, 2020. <https://www.pcgamer.com/intel-defends-avx-512-against-torvalds/>. Accessed January 15, 2026.

[^48]:
    Intel Corporation. "Intel Advanced Vector Extensions 10.2", July 11, 2024. <https://cdrdv2-public.intel.com/836199/361050-intel-avx10.2-spec.pdf>. Accessed February 18, 2025.
    Note: if cdrdv2 link does not work, go to the main site at <https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.htm>.

See also: "Intel Officially Confirms AVX10.2 and APX Support in Nova Lake."
_TechPowerUp_, November 13, 2025. <https://www.techpowerup.com/342881/intel-officially-confirms-avx10-2-and-apx-support-in-nova-lake/>. Accessed January 16, 2026.

---

## Additional Technical References

[^49]: Intel Corporation. _Intel 64 and IA-32 Architectures Optimization Reference Manual_. Order Number 248966, April 2024. <https://cdrdv2-public.intel.com/814198/248966-Optimization-Reference-Manual-V1-050.pdf>. Accessed January 16, 2026.

June 20, 2017. <https://www.intel.com/content/www/us/en/developer/articles/technical/intel-avx-512-instructions.html>. Accessed January 16, 2026.

<https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html>. Accessed January 16, 2026.

[^52]: Fog, Agner. "Optimizing subroutines in assembly language." _Agner Fog's Optimization Manuals_, 2024. <https://www.agner.org/optimize/>. Accessed January 15, 2026.

[^53]: System V Application Binary Interface - Intel386 Architecture Processor Supplement. <https://gitlab.com/x86-psABIs/x86-64-ABI>. Accessed January 15, 2026.

[^54]: Henderson, Richard. GCC Patches mailing list, December 2004. <https://gcc.gnu.org/legacy-ml/gcc-patches/2004-12/msg01955.html>. Accessed January 15, 2026.

[^55]: Intel Corporation. "Intel Architecture Optimization Reference Manual." Order Number 245127-001, 1999.

[^56]: Naishlos, Dorit, et al. "Autovectorization in GCC." _GCC Summit 2004_. <https://gcc.gnu.org/pub/gcc/summit/2004/Autovectorization.pdf>. Accessed January 15, 2026.
