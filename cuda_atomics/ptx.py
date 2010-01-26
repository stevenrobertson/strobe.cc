#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import math
import numpy
import scipy
import pycuda.driver as cuda
import pycuda.autoinit
import matplotlib.pyplot as plt

from tempfile import NamedTemporaryFile
from subprocess import check_call
import time

from pycuda.compiler import SourceModule
from string import Template

def stat(array):
    return "%1.7f±%1.6f" % (scipy.mean(array), scipy.stdev(array))

keys = ['b-', 'g-', 'r-', 'y-', 'k-']
colors = ['0.5', 'k', '0.25', 'y', '.75', 'g', 'r', 'm', 'b', 'c']

stdlib = """
.version 1.4
.target sm_13

.func (.reg .u32 $ret) get_gtid ()
{
    .reg .u16 tmp;
    .reg .u32 cta, ncta, tid, gtid;

    mov.u16         tmp,    %ctaid.x;
    cvt.u32.u16     cta,    tmp;
    mov.u16         tmp,    %ntid.x;
    cvt.u32.u16     ncta,   tmp;
    mul24.lo.u32    gtid,   cta,    ncta;

    mov.u16         tmp,    %tid.x;
    cvt.u32.u16     tid,    tmp;
    add.u32         gtid,   gtid,   tid;
    mov.b32         $ret,   gtid;
    ret;
}

.reg .u32 lcg_state;

.func (.reg .u32 $ret) lcg_rounds   (.reg .u32 num_iters)
{
    // hooray for crappy random numbers
    .reg .pred p;

loop:
    mad.lo.u32  lcg_state,  lcg_state, 1664525, 1013904223;
    sub.u32     num_iters,  num_iters,  1;
    setp.ne.u32 p,          num_iters,   0;
@p  bra.uni     loop;

    mov.u32     $ret, lcg_state;
    ret;
}
"""

def get_func(mod, funcname):
    fn = mod.get_function(funcname)
    print "Compiled %s: used %d regs, %d sm, %d local" % (funcname,
            fn.num_regs, fn.shared_size_bytes, fn.local_size_bytes)
    return fn

def disassemble(src):
    """Okay this absolutely sucks but whatever, ptxas runs quickly"""
    sf = NamedTemporaryFile(suffix='.ptx')
    sf.write(src)
    sf.flush()
    tf = NamedTemporaryFile(suffix='.cubin')
    check_call(['ptxas', '-o', tf.name, sf.name])
    sf.close()
    check_call(['decuda/decuda.py', tf.name])
    tf.close()

def consecutive_clocks():
    """Measures a few rounds of sampling consecutive clocks."""

    ptx = stdlib + """
    .entry consecutive_clocks ( .param .u32 out )
    {

        .reg .u32 base, off, clka, clkb, clks, iter;
        .reg .pred p;

        mov.u32         iter,   256;
        mov.u32         clks,   0;

    loop:
        mov.u32         clka,   %clock;
        mov.u32         clkb,   %clock;
        sub.u32         clka,   clkb,   clka;
        add.u32         clks,   clks,   clka;
        sub.u32         iter,   iter,   1;
        setp.ne.u32     p,      iter,   0;
    @p  bra.uni         loop;

        ld.param.u32    base,   [out];
        call.uni        (off),  get_gtid,   ();
        mad24.lo.u32    base,   off,    4,  base;

        st.global.b32   [base], clks;

    }
    """

    fn = get_func(cuda.module_from_buffer(ptx), 'consecutive_clocks')

    fig = plt.figure()
    ax = fig.add_subplot(111, title='Clocks from consecutive operations, 256 iterations/thread')
    ax.set_ylabel('Clocks')
    ax.set_xlabel('Block width')
    ax.set_xticks(range(10))
    ax.set_xticklabels([str(1 << i) for i in range(10)])

    for grid in range(5):
        gridw = 1 << grid
        allres = []
        allerr = []
        for width in range(10):
            widthw = 1 << width
            if widthw * gridw > 1024: continue
            all_calc = numpy.zeros( (gridw * 30 * widthw,) ).astype(numpy.int32)

            for run in range(5):
                a = numpy.empty( (gridw * 30 * widthw,) ).astype(numpy.int32)
                fn(cuda.InOut(a), block=(widthw, 1, 1), grid=(gridw * 30, 1))
                all_calc += a

            print "%dx%d: %f ± %f" % (gridw, widthw, scipy.mean(all_calc),
                                    scipy.std(all_calc))

            allres.append(scipy.mean(all_calc)/256/5)
            allerr.append(scipy.std(all_calc)/(256*5))

        #ax.plot(range(len(allres)), allres, keys[grid], label=str(gridw))
        ax.errorbar(range(len(allres)), allres, yerr=allerr, fmt=keys[grid],
                    label=str(gridw))
    ax.legend(loc=0, title="Blocks/SM")
    return fig

clkfig = consecutive_clocks()
#clkfig.savefig('consecutive_clocks_2.png', dpi=80, format='png')

def basic_add_performance():
    """Measures memory latency for certain operations."""

    base_src = Template("""
    .entry $FNAME ( .param .u32 out )
    {
        .reg .u32 base, off, clka, clkb, clkoa, clkob, clks, tmp, iter;
        .reg .pred p;

        mov.u32         iter,   $RUNS;
        mov.u32         clks,   0;
        mov.u32         tmp,    0;

        ld.const.u32    base,   [scratch];
        $MULT

    warmup:
        mov.u32         clka,   %clock;
        $OPER
        sub.u32         iter,   iter,   1;
        setp.ne.u32     p,      iter,   0;
    @p  bra.uni         warmup;

        mov.u32         clkoa,  %clock;
        mov.u32         iter,   $RUNS;
    loop:
        mov.u32         clka,   %clock;
        $OPER
        xor.b32         clka,   clka,   tmp;
        mov.u32         clkb,   %clock;
        xor.b32         clka,   clka,   tmp;
        sub.u32         clka,   clkb,   clka;
        add.u32         clks,   clks,   clka;
        sub.u32         iter,   iter,   1;
        setp.ne.u32     p,      iter,   0;
    @p  bra.uni         loop;
        mov.u32         clkob,  %clock;
        sub.u32         clkoa,  clkob,  clkoa;

        mov.u32         iter,   $RUNS;
    cooldown:
        $OPER
        sub.u32         iter,   iter,   1;
        setp.ne.u32     p,      iter,   0;
    @p  bra.uni         cooldown;

        ld.param.u32    base,   [out];
        call.uni        (off),  get_gtid,   ();
        shr.u32         off,    off,    5;
        mad24.lo.u32    base,   off,    8,  base;
        st.volatile.global.b32  [base], clks;

        add.u32         base,   base,   4;
        st.global.b32   [base], clkoa;
    }
    """)

    addrtypes = {
            'single': {'label': "all conflicts",  'ADDRTYPE': "single",
                       'MULT': "mov.u32 off, %smid;" +
                       "mad24.lo.u32 base, off, 128, base;"},
            'uncoa':  {'label': "uncoalesced",    'ADDRTYPE': "uncoa",
                       'MULT': "call.uni        (off),  get_gtid,   ();" +
                               "mad24.lo.u32 base, off, 128, base;"},
            'coa':    {'label': "coalesced",      'ADDRTYPE': "coa",
                       'MULT': "call.uni        (off),  get_gtid,   ();" +
                               "mad24.lo.u32 base, off, 4, base;"},
            }

    # Evil, I know, DRY and all
    addrtypesorder = ['single', 'uncoa', 'coa']

    opertypes = {
            'atomic':       "atom.global.add.u32 tmp, [base], tmp;",
            'red':          "red.global.add.u32     [base], clks;",
            'store':        "st.global.u32 [base], clks;",
            'load':         "ld.global.u32 tmp, [base];",
            'load_store': """
                ld.global.u32 tmp, [base];
                add.u32 tmp, tmp, clks;
                st.global.u32 [base], tmp;
                """
            }

    opertypesorder = ['load', 'store', 'load_store', 'red', 'atomic']

    order = []
    for va in addrtypesorder:
        for k in sorted(opertypes.keys()):
            order.append((va, k))

    runs = 512
    rounds = 8
    mod = stdlib + "\n.const .u32 scratch;"
    for (addr, oper) in order:
        c = dict(addrtypes[addr])
        c['otype'] = oper
        c['OPER'] = opertypes[oper]
        c['RUNS'] = runs
        c['FNAME'] = "%s_%s" % (addr, oper)
        mod += base_src.substitute(c)
    for i in enumerate(mod.split('\n')):
        print "%3d %s" % i
    disassemble(mod)
    mod = cuda.module_from_buffer(mod)
    figs = []
    barwidth = 0.3

    scratch = cuda.mem_alloc(1024*16*30*128)
    scratchptr = mod.get_global('scratch')
    cuda.memset_d32(scratchptr[0], int(scratch), 1)

    def plot(title, names, vals, errs):
        N=len(vals[0])
        bw=2*.9/len(names)
        fig = plt.figure()
        ax = fig.add_subplot(111, title=title)
        ax.set_ylabel('Clocks')
        ax.set_xlabel('Warps/SM')
        ax.set_xticks(range(N))
        ax.set_xticklabels([1<<i for i in range(N)])
        for idx, (name,val,err) in enumerate(zip(names, vals, errs)):
            ax.bar([i+bw*(idx/2)-.45 for i in range(N)], val, bw, yerr=err,
                     color=colors[idx], label=name, zorder=-idx)
        ax.axis(ymin=0)
        ax.legend(loc=0)
        return fig

    for addr in addrtypesorder:
        addrlbl = addrtypes[addr]['label']
        print "Access pattern:", addrlbl
        interms, interes, totalms, totales = [], [], [], []
        for operidx, oper in enumerate(opertypesorder):
            interm, intere, totalm, totale = [], [], [], []
            for dim in ((1, 1), (2, 1), (4, 1), (8, 1), (8, 2), (8, 4)):
                vals = numpy.zeros( (dim[0] * dim[1] * 30, 2) )
                fn = mod.get_function('%s_%s' % (addr, oper))
                for round in range(rounds+1):
                    a = numpy.zeros_like(vals).astype(numpy.int32)
                    fn(cuda.InOut(a), block=(32 * dim[0], 1, 1),
                                      grid=(30 * dim[1], 1))
                    if round != 0: vals += a
                    time.sleep(.005)
                means = scipy.mean(vals, axis=0) / (runs*rounds)
                stds = scipy.std(vals, axis=0) / (runs*rounds)
                # this is just gross
                interm.append(means[0])
                totalm.append(means[1])
                intere.append(stds[0])
                totale.append(stds[1])
                print "%16s: %1.7f±%1.6f" % (oper, means[0], stds[0])
                print "%16s: %1.7f±%1.6f" % (oper+' total', means[1], stds[1])
            interms.append(interm)
            interes.append(intere)
            interms.append(totalm)
            interes.append(totale)

        names = []
        for i in opertypesorder:
            names.append(i)
            names.append(i+' total')

        fig1 = plot('Basic memory latency, %s access pattern' % addrlbl,
                    names, interms, interes)
        figs.append((addr, fig1))

    return figs

basicfigs = basic_add_performance()
for name, fig in basicfigs:
    fig.savefig('basic_add_good_%s.png' % name, dpi=80, format='png')


def basic_add_performance_2():
    """Measures memory latency for certain operations."""

    base_src = Template("""
    .entry $FNAME ( .param .u32 out )
    {
        .reg .u32 base, off, clka, clkb, clkoa, clkob, clks, tmp, iter;
        .reg .pred p;

        mov.u32         iter,   $RUNS;
        mov.u32         clks,   0;
        mov.u32         tmp,    0;

        ld.const.u32    base,   [scratch];
        $MULT
        mov.u32         lcg_state,  scratch;

    warmup:
        mov.u32         clka,   %clock;
        $OPER
        sub.u32         iter,   iter,   1;
        setp.ne.u32     p,      iter,   0;
    @p  bra.uni         warmup;

        mov.u32         clkoa,  %clock;
        mov.u32         iter,   $RUNS;
    loop:
        //call.uni        (tmp),  lcg_rounds, (100);
        $LCGROUNDS
        mov.u32         clka,   %clock;
        $OPER
        xor.b32         clka,   clka,   tmp;
        mov.u32         clkb,   %clock;
        xor.b32         clka,   clka,   tmp;
        sub.u32         clka,   clkb,   clka;
        add.u32         clks,   clks,   clka;
        sub.u32         iter,   iter,   1;
        setp.ne.u32     p,      iter,   0;
    @p  bra.uni         loop;
        mov.u32         clkob,  %clock;
        sub.u32         clkoa,  clkob,  clkoa;

        mov.u32         iter,   $RUNS;
    cooldown:
        $OPER
        sub.u32         iter,   iter,   1;
        setp.ne.u32     p,      iter,   0;
    @p  bra.uni         cooldown;

        ld.param.u32    base,   [out];
        call.uni        (off),  get_gtid,   ();
        shr.u32         off,    off,    5;
        mad24.lo.u32    base,   off,    8,  base;
        call.uni        (tmp),  lcg_rounds, (1);
        st.volatile.global.b32  [base], tmp;
        st.volatile.global.b32  [base], clks;

        add.u32         base,   base,   4;
        st.global.b32   [base], clkoa;
    }
    """)

    addrtypes = {
            'single': {'label': "all conflicts",  'ADDRTYPE': "single",
                       'MULT': "mov.u32 off, %smid;" +
                               "mad24.lo.u32 base, off, 128, base;"},
            'uncoa':  {'label': "uncoalesced",    'ADDRTYPE': "uncoa",
                       'MULT': "call.uni        (off),  get_gtid,   ();" +
                               "mad24.lo.u32 base, off, 128, base;"},
            'coa':    {'label': "coalesced",      'ADDRTYPE': "coa",
                       'MULT': "call.uni        (off),  get_gtid,   ();" +
                               "mad24.lo.u32 base, off, 4, base;"},
            }

    # Evil, I know, DRY and all
    addrtypesorder = ['single', 'uncoa', 'coa']

    opertypes = {
            'atomic':       "atom.global.add.u32 tmp, [base], tmp;",
            'red':          "red.global.add.u32     [base], clks;",
            'store':        "st.global.u32 [base], clks;",
            'load':         "ld.global.u32 tmp, [base];",
            'load_store': """
                ld.global.u32 tmp, [base];
                add.u32 tmp, tmp, clks;
                st.global.u32 [base], tmp;
                """
            }

    opertypesorder = ['load', 'store', 'load_store', 'red', 'atomic']

    lcgtext = "mad.lo.u32  lcg_state,  lcg_state, 1664525, 1013904223;\n"*50

    order = []
    for va in addrtypesorder:
        for k in sorted(opertypes.keys()):
            order.append((va, k))

    runs = 512
    rounds = 4
    mod = stdlib + "\n.const .u32 scratch;"
    for (addr, oper) in order:
        c = dict(addrtypes[addr])
        c['otype'] = oper
        c['OPER'] = opertypes[oper]
        c['RUNS'] = runs
        c['FNAME'] = "%s_%s" % (addr, oper)
        c['LCGROUNDS'] = lcgtext
        mod += base_src.substitute(c)
    for i in enumerate(mod.split('\n')):
        print "%3d %s" % i
    disassemble(mod)
    mod = cuda.module_from_buffer(mod)
    figs = []
    barwidth = 0.3

    scratch = cuda.mem_alloc(1024*16*30*128)
    scratchptr = mod.get_global('scratch')
    cuda.memset_d32(scratchptr[0], int(scratch), 1)

    def plot(title, names, vals, errs):
        N=len(vals[0])
        bw=2*.9/len(names)
        fig = plt.figure()
        ax = fig.add_subplot(111, title=title)
        ax.set_ylabel('Clocks')
        ax.set_xlabel('Warps/SM')
        ax.set_xticks(range(N))
        ax.set_xticklabels([1<<i for i in range(N)])
        for idx, (name,val,err) in enumerate(zip(names, vals, errs)):
            ax.bar([i+bw*(idx/2)-.45 for i in range(N)], val, bw, yerr=err,
                     color=colors[idx], label=name, zorder=-idx)
        ax.axis(ymin=0)
        ax.legend(loc=0)
        return fig

    for addr in addrtypesorder:
        addrlbl = addrtypes[addr]['label']
        print "Access pattern:", addrlbl
        interms, interes, totalms, totales = [], [], [], []
        for operidx, oper in enumerate(opertypesorder):
            interm, intere, totalm, totale = [], [], [], []
            for dim in ((1, 1), (2, 1), (4, 1), (8, 1), (8, 2), (8, 4)):
                vals = numpy.zeros( (dim[0] * dim[1] * 30, 2) )
                fn = mod.get_function('%s_%s' % (addr, oper))
                for round in range(rounds+1):
                    a = numpy.zeros_like(vals).astype(numpy.int32)
                    fn(cuda.InOut(a), block=(32 * dim[0], 1, 1),
                                      grid=(30 * dim[1], 1))
                    if round != 0: vals += a
                    time.sleep(.005)
                means = scipy.mean(vals, axis=0) / (runs*rounds)
                stds = scipy.std(vals, axis=0) / (runs*rounds)
                # this is just gross
                interm.append(means[0])
                totalm.append(means[1])
                intere.append(stds[0])
                totale.append(stds[1])
                print "%16s: %1.7f±%1.6f" % (oper, means[0], stds[0])
                print "%16s: %1.7f±%1.6f" % (oper+' total', means[1], stds[1])
            interms.append(interm)
            interes.append(intere)
            interms.append(totalm)
            interes.append(totale)

        names = []
        for i in opertypesorder:
            names.append(i)
            names.append(i + ' total')

        fig1 = plot('Compute memory latency, %s access pattern' % addrlbl,
                    names, interms, interes)
        figs.append((addr, fig1))

    return figs

basicfigs = basic_add_performance_2()
for name, fig in basicfigs:
    fig.savefig('compute_bar_%s.png' % name, dpi=80, format='png')

plt.show()
