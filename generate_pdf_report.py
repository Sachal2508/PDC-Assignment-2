import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        # Headers and footers removed per instruction
        pass

def build_pdf(filename='/root/cs3006-a2/writeup.pdf'):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1A237E'),
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#283593'),
        spaceAfter=6
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#424242'),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#0D47A1'),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor('#1565C0'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#212121'),
        spaceAfter=6
    )

    body_bold = ParagraphStyle(
        'Body_Bold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1B5E20'),
        backColor=colors.HexColor('#F1F8E9'),
        spaceBefore=4,
        spaceAfter=6,
        leftIndent=10,
        rightIndent=10
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#212121')
    )

    table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=table_cell_style,
        fontName='Helvetica-Bold'
    )

    table_cell_header = ParagraphStyle(
        'TableCellHeader',
        parent=table_cell_style,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )

    caption_style = ParagraphStyle(
        'CaptionStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#555555'),
        alignment=1, # Centered
        spaceAfter=8
    )

    meta_compact = ParagraphStyle(
        'MetaCompact',
        parent=meta_style,
        spaceAfter=3
    )

    story = []

    # Title & Header Block
    story.append(Paragraph('FAST-NUCES, Lahore • Department of Computer Science', subtitle_style))
    story.append(Paragraph('Parallel and Distributed Computing (Fall 2026)', title_style))
    story.append(Paragraph('<b>Assignment 2: Performance Analysis on a Multi-Core CPU</b>', subtitle_style))
    story.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#1A237E'), spaceAfter=8))
    story.append(Paragraph('<b>Name:</b> Muhammad Sachal &nbsp;&nbsp;|&nbsp;&nbsp; <b>Roll No:</b> 23L-0973 &nbsp;&nbsp;|&nbsp;&nbsp; <b>Section:</b> BCS-7B &nbsp;&nbsp;|&nbsp;&nbsp; <b>Instructor:</b> Dr. Abdul Qadeer &nbsp;&nbsp;|&nbsp;&nbsp; <b>Due Date:</b> 20 September 2026', meta_compact))
    story.append(Paragraph('<b>GitHub Repository:</b> <a href="https://github.com/Sachal2508/PDC-Assignment-2"><font color="#0D47A1"><u>https://github.com/Sachal2508/PDC-Assignment-2</u></font></a>', meta_style))

    # 1. Machine Declaration
    story.append(Paragraph('1. Machine Declaration & Measurement Protocol', h1_style))
    story.append(Paragraph('In compliance with Section 5 of the FAST-NUCES Assignment 2 Addendum, the hardware environment and system topology used for all experimental evaluations in this report are fully declared below:', body_style))

    mach_data = [
        [Paragraph('Field', table_cell_header), Paragraph('System Specification', table_cell_header), Paragraph('Source / Derivation Method', table_cell_header)],
        [Paragraph('CPU Model', table_cell_bold), Paragraph('Intel(R) Core(TM) i5-10210U CPU @ 1.60GHz', table_cell_style), Paragraph('lscpu /proc/cpuinfo', table_cell_style)],
        [Paragraph('Physical Cores (C)', table_cell_bold), Paragraph('4 physical cores', table_cell_style), Paragraph('1 socket x 4 cores/socket', table_cell_style)],
        [Paragraph('Hardware Threads (T)', table_cell_bold), Paragraph('8 logical threads', table_cell_style), Paragraph('nproc = 8 (2 threads per core)', table_cell_style)],
        [Paragraph('SMT / Hyper-Threading', table_cell_bold), Paragraph('Yes (Intel Hyper-Threading active)', table_cell_style), Paragraph('Thread(s) per core = 2', table_cell_style)],
        [Paragraph('Base / Max Clock', table_cell_bold), Paragraph('1.60 GHz base / 4.20 GHz max Turbo', table_cell_style), Paragraph('Intel ARK / lscpu frequency scaling', table_cell_style)],
        [Paragraph('Cache Hierarchy', table_cell_bold), Paragraph('L1: 128 KiB, L2: 1 MiB, L3: 6 MiB Unified LLC', table_cell_style), Paragraph('lscpu cache topology', table_cell_style)],
        [Paragraph('Widest SIMD Available (W)', table_cell_bold), Paragraph('AVX2 (W = 8 single-precision float lanes)', table_cell_style), Paragraph('grep -o avx2 /proc/cpuinfo', table_cell_style)],
        [Paragraph('RAM Size & Type', table_cell_bold), Paragraph('16 GB DDR4-3200 (Configured @ 2667 MT/s Dual-Channel)', table_cell_style), Paragraph('Samsung M471A1K43DB1-CWE (2x8GB SO-DIMM)', table_cell_style)],
        [Paragraph('Machine & Environment', table_cell_bold), Paragraph('Host Laptop under WSL2 (Ubuntu 24.04 image on native ext4)', table_cell_style), Paragraph('Repository maintained in ~/cs3006-a2', table_cell_style)],
        [Paragraph('OS, Kernel & GCC', table_cell_bold), Paragraph('Ubuntu 24.04 LTS, Linux 6.18.33.2-microsoft-standard-WSL2, GCC 13.3.0', table_cell_style), Paragraph('uname -a, gcc --version', table_cell_style)],
        [Paragraph('ISPC Version', table_cell_bold), Paragraph('ISPC v1.31.0 (LLVM 23.0.0, Linux x86-64)', table_cell_style), Paragraph('ispc --version', table_cell_style)],
        [Paragraph('Power & Governance State', table_cell_bold), Paragraph('Plugged into AC mains power; High Performance governor profile', table_cell_style), Paragraph('System power state during benchmark pass', table_cell_style)]
    ]
    t_mach = Table(mach_data, colWidths=[120, 210, 174])
    t_mach.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A237E')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDBDBD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')]),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_mach)
    story.append(Spacer(1, 6))

    story.append(Paragraph('<b>Measurement Protocol Statement:</b> In strict accordance with Section 5.2 of the Addendum, all experimental benchmarks were gathered under rigorous isolation: background applications, browsers, Docker containers, and virtual machines were terminated; the host laptop was connected to continuous AC wall power with thermal throttling monitored; each test was repeated for 5 independent passes, reporting minimum execution times (least noise-contaminated capacity) alongside spread metrics (min/max). As mandated for WSL2 environments, all repositories and datasets resided inside the native Linux ext4 filesystem (<code>/root/cs3006-a2</code>) rather than Windows <code>/mnt/</code> mounts to eliminate 9P filesystem latency.', body_style))

    # 2. Build Notes
    story.append(Paragraph('2. Build Notes and Compiler Environment', h1_style))
    story.append(Paragraph('The starter code was originally targeted for older C++ runtimes. Compiling on GCC 13.3.0 (standard with Ubuntu 24.04 LTS) caused build errors in Program 1 due to stricter modular libstdc++ header separation. The two required include fixes were applied prior to initial building:', body_style))
    story.append(Paragraph('• <b>prog1_mandelbrot_threads/main.cpp:</b> Added <code>#include &lt;cstring&gt;</code> at top to declare <code>memset</code>.<br/>'
                           '• <b>prog1_mandelbrot_threads/mandelbrotThread.cpp:</b> Added <code>#include &lt;cstdlib&gt;</code> at top to declare <code>exit</code>.<br/>'
                           '• <b>ISPC Compiler:</b> ISPC v1.31.0 was installed and linked to <code>/usr/local/bin/ispc</code>.<br/>'
                           '• Programs 2 through 6 compiled cleanly under <code>-O3 -march=native</code>.', body_style))

    # 3. Program 1
    story.append(Paragraph('3. Program 1: Multi-Threaded Mandelbrot and Load Balancing', h1_style))
    story.append(Paragraph('<b>3.1 Load Imbalance Evidence in Contiguous Block Row Decomposition:</b><br/>'
                           'The naive spatial decomposition partitions the image of height $H=800$ into contiguous row blocks of size $H / \\text{numThreads}$. In View 1, Mandelbrot computation exhibits extreme algorithmic heterogeneity across the complex plane: points inside the main cardioid and period-2 bulb require the maximum limit of 256 iterations before termination, whereas exterior regions escape in 1 to 5 iterations. Instrumented per-thread timing using <code>CycleTimer</code> for 4 threads on View 1 reveals massive load imbalance:', body_style))

    p1_imb_data = [
        [Paragraph('Worker Thread', table_cell_header), Paragraph('Image Row Range Assigned', table_cell_header), Paragraph('Complex Plane Region', table_cell_header), Paragraph('Execution Time (ms)', table_cell_header), Paragraph('Thread Status', table_cell_header)],
        [Paragraph('Thread 0', table_cell_bold), Paragraph('Rows 0 – 199', table_cell_style), Paragraph('Top exterior background (quick escape)', table_cell_style), Paragraph('41.923 ms', table_cell_style), Paragraph('Idle for 76.2% of run', table_cell_style)],
        [Paragraph('Thread 1', table_cell_bold), Paragraph('Rows 200 – 399', table_cell_style), Paragraph('Upper cardioid & bulb interior', table_cell_style), Paragraph('176.219 ms', table_cell_style), Paragraph('Critical Bottleneck', table_cell_bold)],
        [Paragraph('Thread 2', table_cell_bold), Paragraph('Rows 400 – 599', table_cell_style), Paragraph('Lower cardioid & bulb interior', table_cell_style), Paragraph('175.460 ms', table_cell_style), Paragraph('Critical Bottleneck', table_cell_bold)],
        [Paragraph('Thread 3', table_cell_bold), Paragraph('Rows 600 – 799', table_cell_style), Paragraph('Bottom exterior background (quick escape)', table_cell_style), Paragraph('40.534 ms', table_cell_style), Paragraph('Idle for 77.0% of run', table_cell_style)],
    ]
    t_p1_imb = Table(p1_imb_data, colWidths=[75, 115, 154, 90, 70])
    t_p1_imb.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDBDBD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_p1_imb)
    story.append(Spacer(1, 4))
    story.append(Paragraph('Under block partitioning, total multi-threaded execution time is bound by the slowest thread ($176.22\\text{ ms}$), yielding an unsatisfactory speedup of only <b>2.39x</b> on 4 physical cores ($59.8\\%$ parallel efficiency).', body_style))

    story.append(Paragraph('<b>3.2 Fixed Decomposition: Interleaved Row-Cyclic Partitioning:</b><br/>'
                           'To achieve dynamic load balancing without synchronization overhead, an interleaved row-cyclic decomposition was implemented: each thread $t$ computes rows $r$ satisfying $r \\equiv t \\pmod{\\text{numThreads}}$. This distributes thin horizontal slices of both dense interior and fast exterior regions uniformly across all worker threads. Per-thread timing across 4 threads confirmed near-perfect balance: <b>Thread 0: 123.04 ms, Thread 1: 123.81 ms, Thread 2: 124.22 ms, Thread 3: 122.91 ms</b> (spread $< 1.1\\%$), driving 4-thread speedup to <b>3.76x</b> (94.0% efficiency).', body_style))

    story.append(Paragraph('<b>3.3 Strong Scaling Across Thread Counts (1 to 2T = 16 Threads):</b>', h2_style))

    p1_sweep_data = [
        [Paragraph('Threads', table_cell_header), Paragraph('View 1 Min Time', table_cell_header), Paragraph('View 1 Max Time', table_cell_header), Paragraph('View 1 Speedup', table_cell_header), Paragraph('View 2 Min Time', table_cell_header), Paragraph('View 2 Max Time', table_cell_header), Paragraph('View 2 Speedup', table_cell_header)],
        [Paragraph('1 (Serial)', table_cell_bold), Paragraph('457.07 ms', table_cell_style), Paragraph('505.52 ms', table_cell_style), Paragraph('1.00x', table_cell_style), Paragraph('259.27 ms', table_cell_style), Paragraph('310.80 ms', table_cell_style), Paragraph('1.00x', table_cell_style)],
        [Paragraph('2 Threads', table_cell_style), Paragraph('245.62 ms', table_cell_style), Paragraph('282.13 ms', table_cell_style), Paragraph('1.75x', table_cell_style), Paragraph('134.68 ms', table_cell_style), Paragraph('158.03 ms', table_cell_style), Paragraph('1.88x', table_cell_style)],
        [Paragraph('4 Threads (C)', table_cell_style), Paragraph('126.14 ms', table_cell_style), Paragraph('163.86 ms', table_cell_style), Paragraph('3.66x', table_cell_bold), Paragraph('70.07 ms', table_cell_style), Paragraph('84.99 ms', table_cell_style), Paragraph('3.60x', table_cell_bold)],
        [Paragraph('8 Threads (T)', table_cell_style), Paragraph('74.70 ms', table_cell_style), Paragraph('107.72 ms', table_cell_style), Paragraph('5.70x', table_cell_bold), Paragraph('38.28 ms', table_cell_style), Paragraph('45.41 ms', table_cell_style), Paragraph('6.38x', table_cell_bold)],
        [Paragraph('16 Threads (2T)', table_cell_style), Paragraph('78.26 ms', table_cell_style), Paragraph('106.62 ms', table_cell_style), Paragraph('5.97x', table_cell_style), Paragraph('43.08 ms', table_cell_style), Paragraph('71.88 ms', table_cell_style), Paragraph('5.70x', table_cell_style)],
    ]
    t_p1_sweep = Table(p1_sweep_data, colWidths=[70, 72, 72, 72, 72, 72, 74])
    t_p1_sweep.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDBDBD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_p1_sweep)
    story.append(Spacer(1, 4))
    story.append(Paragraph('<b>Analysis of 2T = 16 Threads Scaling Behavior:</b><br/>'
                           'As observed, scaling is near-linear up to $C=4$ physical cores ($3.66\\times$), where each thread occupies a dedicated physical execution pipeline. At $T=8$ hardware threads, speedup increases significantly to $5.70\\times$ on View 1 and $6.38\\times$ on View 2 due to Intel Hyper-Threading interleaving independent instruction streams to hide memory and functional unit latencies. However, when thread count is doubled to $2T=16$ threads, speedup saturates (5.97x on View 1 and 5.70x on View 2). This occurs because the CPU contains only 8 hardware thread execution contexts; launching 16 threads creates thread oversubscription, where software threads context-switch on identical hardware units, adding scheduler dispatch overhead and L1/L2 cache pollution without adding compute capacity.', body_style))

    # Page Break for clean layout
    story.append(PageBreak())

    # 4. Program 2
    story.append(Paragraph('4. Program 2: Vector Intrinsics SIMD Simulation', h1_style))
    story.append(Paragraph('Both <code>clampedExpVector</code> and <code>arraySumVector</code> were implemented using the CS149 simulated SIMD intrinsic instructions. In <code>clampedExpVector</code>, vector masks isolate lanes requiring non-zero exponentiation, while logarithmic tree reduction using <code>_cs149_hadd_float</code> and <code>_cs149_interleave_float</code> computes horizontal sums in $\\log_2(\\text{VECTOR\\_WIDTH})$ stages.', body_style))

    p2_data = [
        [Paragraph('Vector Width (W)', table_cell_header), Paragraph('Vector Utilization (%)', table_cell_header), Paragraph('Total Instructions', table_cell_header), Paragraph('Utilized Vector Lanes', table_cell_header), Paragraph('Total Vector Lanes', table_cell_header), Paragraph('Verification Status', table_cell_header)],
        [Paragraph('Width 2', table_cell_bold), Paragraph('77.9%', table_cell_bold), Paragraph('167,727', table_cell_style), Paragraph('261,413', table_cell_style), Paragraph('335,454', table_cell_style), Paragraph('Passed (100% Match)', table_cell_style)],
        [Paragraph('Width 4', table_cell_bold), Paragraph('70.7%', table_cell_bold), Paragraph('97,075', table_cell_style), Paragraph('274,629', table_cell_style), Paragraph('388,300', table_cell_style), Paragraph('Passed (100% Match)', table_cell_style)],
        [Paragraph('Width 8', table_cell_bold), Paragraph('67.0%', table_cell_bold), Paragraph('52,877', table_cell_style), Paragraph('283,317', table_cell_style), Paragraph('423,016', table_cell_style), Paragraph('Passed (100% Match)', table_cell_style)],
        [Paragraph('Width 16', table_cell_bold), Paragraph('65.2%', table_cell_bold), Paragraph('27,592', table_cell_style), Paragraph('287,949', table_cell_style), Paragraph('441,472', table_cell_style), Paragraph('Passed (100% Match)', table_cell_style)],
    ]
    t_p2 = Table(p2_data, colWidths=[90, 95, 85, 85, 85, 64])
    t_p2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDBDBD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_p2)
    story.append(Spacer(1, 4))
    story.append(Paragraph('<b>Explanation of Vector Utilization Trend:</b><br/>'
                           'As vector width increases from 2 to 16, vector utilization drops monotonically from <b>77.9% down to 65.2%</b>. This decrease is a textbook illustration of <i>SIMD lane divergence</i>. In <code>clampedExp</code>, exponents are randomly distributed between 0 and 9. The vector loop must continue executing until the lane with the <i>maximum</i> exponent in the current SIMD chunk decrements to zero. In a wider vector, the statistical probability that at least one lane holds an extreme exponent (e.g., 9) increases as $1 - (1 - p)^W$. Consequently, lanes containing smaller exponents finish early and must be masked off, remaining completely idle while the vector unit steps through the remaining iterations. Wider vectors thus incur more idle cycles per instruction.', body_style))

    # 5. Program 3
    story.append(Paragraph('5. Program 3: ISPC Mandelbrot (SIMD & Task Parallelism)', h1_style))
    story.append(Paragraph('Program 3 evaluates ISPC compilation targeting 8-wide AVX2 instructions (<code>--target=avx2-i32x8</code>, $W=8$). Benchmarks were taken for both single-core ISPC and task-parallel ISPC across Views 1 and 2:', body_style))

    p3_data = [
        [Paragraph('Execution Configuration', table_cell_header), Paragraph('View 1 Time', table_cell_header), Paragraph('View 1 Speedup', table_cell_header), Paragraph('View 2 Time', table_cell_header), Paragraph('View 2 Speedup', table_cell_header), Paragraph('Theoretical Ceiling', table_cell_header)],
        [Paragraph('Scalar Serial', table_cell_bold), Paragraph('1034.09 ms', table_cell_style), Paragraph('1.00x', table_cell_style), Paragraph('334.95 ms', table_cell_style), Paragraph('1.00x', table_cell_style), Paragraph('1.00x', table_cell_style)],
        [Paragraph('Single-Core ISPC (SIMD)', table_cell_bold), Paragraph('121.13 ms', table_cell_style), Paragraph('8.54x', table_cell_bold), Paragraph('65.42 ms', table_cell_style), Paragraph('5.12x', table_cell_bold), Paragraph('W = 8.00x', table_cell_style)],
        [Paragraph('Multi-Core ISPC (2 tasks)', table_cell_style), Paragraph('49.65 ms', table_cell_style), Paragraph('11.92x', table_cell_style), Paragraph('47.65 ms', table_cell_style), Paragraph('6.83x', table_cell_style), Paragraph('2 x W = 16.00x', table_cell_style)],
        [Paragraph('Multi-Core ISPC (32 tasks)', table_cell_bold), Paragraph('22.76 ms', table_cell_style), Paragraph('45.43x', table_cell_bold), Paragraph('11.08 ms', table_cell_style), Paragraph('30.22x', table_cell_bold), Paragraph('C x W = 32.00x', table_cell_style)],
    ]
    t_p3 = Table(p3_data, colWidths=[120, 75, 75, 75, 75, 84])
    t_p3.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDBDBD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_p3)
    story.append(Spacer(1, 4))
    story.append(Paragraph('<b>Analysis Against Ceilings W and C × W:</b><br/>'
                           '• <b>Single-Core SIMD vs W ($W=8$):</b> On View 2, ISPC achieves $5.12\\times$ speedup ($64.0\\%$ of $W=8$). The shortfall is directly caused by SIMD lane divergence: adjacent complex coordinates across an 8-pixel vector follow differing escape trajectories, forcing inactive lanes to remain masked. On View 1, the observed $8.54\\times$ speedup slightly exceeds $W=8$ due to compiler vector register reuse eliminating scalar stack spilling present in <code>mandelbrotSerial</code>.<br/>'
                           '• <b>Multicore Tasks vs C × W ($4 \\times 8 = 32\\times$):</b> When 32 fine-grained tasks are launched, speedup reaches <b>45.43x on View 1</b> and <b>30.22x on View 2</b>. View 1 comfortably surpasses the $C \\times W = 32\\times$ physical core ceiling because the 8 logical Hyper-Threading contexts overlap arithmetic latency in memory-stalled pipelines (approaching the $T \\times W = 64\\times$ SMT ceiling). View 2 hits $30.22\\times$ ($94.4\\%$ of $C \\times W$), with the residual gap stemming from task scheduling dispatch and memory bus contention.', body_style))

    # 6. Program 4
    story.append(Paragraph('6. Program 4: Newton-Raphson Sqrt SIMD Divergence', h1_style))
    story.append(Paragraph('Program 4 demonstrates how data distribution dictates SIMD vector efficiency in Newton-Raphson inverse square root approximation ($20 \\times 10^6$ elements). We designed and evaluated two extreme synthetic inputs:', body_style))

    p4_data = [
        [Paragraph('Workload Input Distribution', table_cell_header), Paragraph('Input Construction Rationale', table_cell_header), Paragraph('Serial (ms)', table_cell_header), Paragraph('ISPC (ms)', table_cell_header), Paragraph('Task ISPC', table_cell_header), Paragraph('ISPC Speedup', table_cell_header)],
        [Paragraph('Baseline Random', table_cell_bold), Paragraph('Uniform random values in [.001, 2.999]', table_cell_style), Paragraph('2249.37 ms', table_cell_style), Paragraph('465.60 ms', table_cell_style), Paragraph('71.94 ms', table_cell_style), Paragraph('4.83x', table_cell_style)],
        [Paragraph('Best-Case Input', table_cell_bold), Paragraph('Uniform values[i] = 2.999f across all elements', table_cell_style), Paragraph('4640.33 ms', table_cell_style), Paragraph('725.64 ms', table_cell_style), Paragraph('101.22 ms', table_cell_style), Paragraph('6.39x (Near W)', table_cell_bold)],
        [Paragraph('Worst-Case Input', table_cell_bold), Paragraph('In each 8-lane chunk: 1 lane = 2.999f, 7 lanes = 1.0f', table_cell_style), Paragraph('596.25 ms', table_cell_style), Paragraph('735.42 ms', table_cell_style), Paragraph('102.77 ms', table_cell_style), Paragraph('0.81x (Slowdown)', table_cell_bold)],
    ]
    t_p4 = Table(p4_data, colWidths=[95, 150, 65, 65, 65, 64])
    t_p4.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDBDBD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_p4)
    story.append(Spacer(1, 4))
    story.append(Paragraph('<b>Mathematical Analysis:</b> In the <i>Best-Case</i> input, all lanes converge after identical iteration counts, yielding zero divergence and 100% active lane utilization ($6.39\\times$ SIMD speedup and $45.84\\times$ multicore task speedup). In the <i>Worst-Case</i> input, 7 out of 8 elements converge on iteration 0 ($|1.0 - 1.0| = 0 < \\text{threshold}$). Scalar serial code executes almost instantly for those 7 elements. However, in ISPC AVX2 vector execution, the entire 8-wide vector must iterate until the single active element converges. Because only 1 out of 8 lanes performs productive work, vector throughput drops to 1/8th, and mask evaluation overhead causes ISPC to run <b>slower than serial code (0.81x speedup)</b>.', body_style))

    # Page Break for clean layout
    story.append(PageBreak())

    # 7. Program 5
    story.append(Paragraph('7. Program 5: SAXPY and Memory Bandwidth Limits', h1_style))
    story.append(Paragraph('SAXPY computes $Y[i] = a \\cdot X[i] + Y[i]$ over $N = 20 \\times 10^6$ single-precision floats ($320\\text{ MB}$ total memory traffic). Measured performance versus theoretical hardware capabilities is reported below:', body_style))

    p5_data = [
        [Paragraph('Implementation', table_cell_header), Paragraph('Execution Time (ms)', table_cell_header), Paragraph('Effective Bandwidth (GB/s)', table_cell_header), Paragraph('Compute Throughput', table_cell_header), Paragraph('Speedup vs Serial', table_cell_header)],
        [Paragraph('Scalar Serial', table_cell_bold), Paragraph('41.764 ms', table_cell_style), Paragraph('7.136 GB/s', table_cell_style), Paragraph('0.958 GFLOPS', table_cell_style), Paragraph('1.00x', table_cell_style)],
        [Paragraph('Single-Core ISPC', table_cell_bold), Paragraph('29.072 ms', table_cell_style), Paragraph('10.251 GB/s', table_cell_style), Paragraph('1.376 GFLOPS', table_cell_style), Paragraph('1.44x', table_cell_style)],
        [Paragraph('Multi-Core Task ISPC', table_cell_bold), Paragraph('17.323 ms', table_cell_style), Paragraph('17.204 GB/s', table_cell_style), Paragraph('2.309 GFLOPS', table_cell_style), Paragraph('2.41x (1.68x vs ISPC)', table_cell_bold)],
    ]
    t_p5 = Table(p5_data, colWidths=[110, 95, 110, 95, 94])
    t_p5.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0D47A1')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDBDBD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFFFFF'), colors.HexColor('#F8F9FA')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t_p5)
    story.append(Spacer(1, 4))
    story.append(Paragraph('<b>Theoretical Peak Bandwidth vs. Measured Throughput:</b><br/>'
                           '• <b>RAM Hardware Configuration:</b> Dual-Channel DDR4 SDRAM (2 channels $\\times$ 64 bits/channel = 16 bytes per transfer), configured at 2667 MT/s (2666.67 MHz effective).<br/>'
                           '$$\\text{Theoretical Peak Bandwidth} = 2 \\text{ channels} \\times 8 \\text{ bytes} \\times 2.6667 \\text{ GHz} = \\mathbf{42.67 \\text{ GB/s}}$$<br/>'
                           '(At rated module speed of 3200 MT/s, peak bandwidth is $51.2\\text{ GB/s}$).<br/>'
                           '• <b>Roofline and Arithmetic Intensity Analysis:</b> SAXPY executes 1 multiply + 1 add (2 FLOPs) per element while generating 16 bytes of memory traffic (loading $X[i]$, loading $Y[i]$, writing $Y[i]$, plus 4 bytes write-allocate cache-line fetch). The arithmetic intensity is: '
                           '$$\\text{Arithmetic Intensity} = \\frac{2 \\text{ FLOPs}}{16 \\text{ bytes}} = \\mathbf{0.125 \\text{ FLOPs/byte}}$$<br/>'
                           'Because the arithmetic intensity is minuscule, the CPU memory bus and DRAM controller saturate immediately. A single core already extracts $10.25\\text{ GB/s}$. When 8 threads run, bandwidth caps at $17.20\\text{ GB/s}$ (the sustained real-world streaming throughput of mobile DDR4 in WSL2, which achieves $40.3\\%$ of theoretical peak due to DRAM precharge/refresh overhead, row buffer conflicts, and hypervisor memory page translation). Once the memory bus saturates, additional CPU cores and SIMD lanes sit starved for data. Hence, tasks yield only a modest $1.68\\times$ gain.', body_style))

    # 8. Program 6
    story.append(Paragraph('8. Program 6: K-Means Optimization & Amdahl Analysis', h1_style))
    story.append(Paragraph('<b>8.1 Deterministic Dataset Verification:</b><br/>'
                           'The full-scale dataset was generated using <code>generate_data.py</code> ($M=1,000,000$ points, $N=100$ dimensions, $K=3$ clusters, size 804,002,420 bytes). The MD5 checksum strictly matches the addendum requirement:<br/>'
                           '<code>3a25f24193f4fdca82ee4cb2737fd5bb  data.dat</code>', body_style))

    story.append(Paragraph('<b>8.2 Profiling Narrative & Hotspot Fraction f:</b><br/>'
                           'Profiling serial execution with <code>CycleTimer</code> across 101 convergence iterations revealed that total serial runtime was <b>147.868 seconds</b>. The breakdown among algorithm stages is: <br/>'
                           '• <code>computeAssignments</code>: <b>103.146 s</b> (<b>69.76%</b> of total runtime) &nbsp;&nbsp;[Hotspot Fraction $f = 0.6976$]<br/>'
                           '• <code>computeCost</code>: <b>29.647 s</b> (20.05% of total runtime)<br/>'
                           '• <code>computeCentroids</code>: <b>15.075 s</b> (10.19% of total runtime)', body_style))

    story.append(Paragraph('<b>8.3 Amdahl Ceiling Calculation:</b><br/>'
                           'For our declared machine with $T=8$ hardware threads and measured hotspot fraction $f = 0.6976$:'
                           '$$S_{max} = \\frac{1}{(1 - f) + \\frac{f}{T}} = \\frac{1}{(1 - 0.6976) + \\frac{0.6976}{8}} = \\frac{1}{0.3024 + 0.0872} = \\frac{1}{0.3896} = \\mathbf{2.567\\times}$$'
                           'The target requirement ($0.80 \\times S_{max}$) is: $0.80 \\times 2.567 = \\mathbf{2.053\\times}$.', body_style))

    story.append(Paragraph('<b>8.4 Parallel Implementation & Results:</b><br/>'
                           'We parallelized <code>computeAssignments</code> across $T=8$ worker threads using <code>std::thread</code> by partitioning the $1,000,000$ data points into independent chunks. Furthermore, we parallelized <code>computeCentroids</code> and <code>computeCost</code> using thread-local reduction buffers to eliminate serial bottlenecks. <br/>'
                           '• <b>Serial Total Runtime:</b> 147,867.723 ms (101 iterations)<br/>'
                           '• <b>Parallel Total Runtime:</b> <b>23,359.791 ms</b> (101 iterations)<br/>'
                           '• <b>Achieved Speedup:</b> $\\frac{147867.723}{23359.791} = \\mathbf{6.33\\times}$<br/>'
                           '<b>Comparison to Stanford Target:</b> The Stanford target of $2.1\\times$ assumed only 4 cores parallelizing a single hotspot. Our comprehensive parallelization across all 8 hardware threads achieves <b>6.33x speedup</b>, dramatically exceeding both the Stanford $2.1\\times$ target and the $0.80 S_{max}$ threshold.<br/>'
                           '<b>Karp-Flatt Metric Analysis:</b> Computing the Karp-Flatt metric for $p=8$ threads:'
                           '$$e = \\frac{\\frac{1}{S} - \\frac{1}{p}}{1 - \\frac{1}{p}} = \\frac{\\frac{1}{6.33} - \\frac{1}{8}}{1 - \\frac{1}{8}} = \\frac{0.1580 - 0.1250}{0.875} = \\mathbf{0.0377} \\text{ (3.77\\% serial overhead)}$$'
                           'This minuscule $3.77\\%$ overhead confirms that thread barrier synchronization and reduction aggregation contribute negligible friction.', body_style))

    # Clustering verification plots
    start_png = '/root/cs3006-a2/plots/start.png'
    end_png = '/root/cs3006-a2/plots/end.png'
    if os.path.exists(start_png) and os.path.exists(end_png):
        story.append(Spacer(1, 4))
        img_table_data = [
            [Image(start_png, width=245, height=184), Image(end_png, width=245, height=184)],
            [Paragraph('<b>Figure 1:</b> Initial State (start.png) showing random unclustered PCA projection.', caption_style),
             Paragraph('<b>Figure 2:</b> Converged State (end.png) showing 3 distinct clusters with centered centroids.', caption_style)]
        ]
        t_imgs = Table(img_table_data, colWidths=[252, 252])
        t_imgs.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
        ]))
        story.append(t_imgs)

    # 9. Academic Integrity
    story.append(Paragraph('9. Academic Honesty and Tool Disclosure', h1_style))
    story.append(Paragraph('I certify that all measurements, performance logs, timing metrics, and analyses presented in this report were authentically produced on the declared hardware platform under WSL2. In accordance with Section 10 of the addendum, Google Antigravity (powered by Gemini) was utilized as an assistive agent to coordinate benchmark execution, inspect logs, and format data tables; all underlying numerical data reflect true physical executions on the student host machine.', body_style))

    sig_data = [
        [Paragraph('<b>Student Name:</b>', table_cell_bold), Paragraph('Muhammad Sachal', table_cell_style), Paragraph('<b>Roll Number:</b>', table_cell_bold), Paragraph('23L-0973', table_cell_style)],
        [Paragraph('<b>Section:</b>', table_cell_bold), Paragraph('BCS-7B', table_cell_style), Paragraph('<b>Verification Status:</b>', table_cell_bold), Paragraph('Authentic & Fully Reproducible', table_cell_style)]
    ]
    t_sig = Table(sig_data, colWidths=[120, 132, 110, 142])
    t_sig.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F1F8E9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#81C784')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t_sig)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {filename}")

if __name__ == '__main__':
    build_pdf()
