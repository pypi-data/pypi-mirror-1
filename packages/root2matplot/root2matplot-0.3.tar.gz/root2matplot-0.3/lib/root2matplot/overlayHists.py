#!/usr/bin/env python
"""Overlay the histograms from several root files with identical structure"""
__version__ = '1.1'

## Created by Jeff Klukas (klukas@wisc.edu), November 2009
## Updated February 2010

######## Import python libraries #############################################

import sys
import optparse
import shutil
import math
import os
import re

## If we actually plan to do something other than show the help menu, 
## import the PyROOT package
if '-h' not in sys.argv and len(sys.argv) > 1:
    import ROOT
    # ROOT parses options when the first ROOT command is called, so we must
    # add '-b' before that to get batch mode, but we must immediately remove
    # it to avoid interference with option parsing for this script.
    sys.argv.append('-b')
    ROOT.gErrorIgnoreLevel = ROOT.kWarning
    sys.argv.remove('-b')


######## Define classes and generators #######################################

class RootFile:
    """A wrapper for TFiles, allowing quick access to the name and Get."""
    def __init__(self, file_name):
        self.name = file_name[0:-5]
        self.file = ROOT.TFile(file_name, 'read')
        if self.file.IsZombie():
            print "Error opening %s, exiting..." % file_name
            sys.exit(1)
    def Get(self, object_name):
        return self.file.Get(object_name)

def counter_generator():
    """Incremement the counter used to number plots."""
    k = 0
    while True:
        k += 1
        yield k
next_counter = counter_generator().next



######## These functions are the meat of this program #########################

#### A recursive function to drill down through directories
def process_directory(path, files):
    """Loop through all histograms in the directory and plot them."""
    dir_to_make = '%s/%s' % (options.plot_dir, path)
    if not os.path.exists(dir_to_make):
        os.mkdir(dir_to_make)
    keys = files[0].file.GetDirectory(path).GetListOfKeys()
    key = keys[0]
    while key:
        obj = key.ReadObj()
        key = keys.After(key)
        new_path = '%s/%s' % (path, obj.GetName())
        if obj.IsA().InheritsFrom('TDirectory'):
            process_directory(new_path, files)
        #### If obj is a desired histogram, process it
        matches_path = options.regex.search(new_path)
        is_1D_histogram = (obj.IsA().InheritsFrom('TH1') and
                           not obj.IsA().InheritsFrom('TH2') and
                           not obj.IsA().InheritsFrom('TH3'))
        if (matches_path and is_1D_histogram):
            if options.use_matplotlib:
                process_hist_matplotlib(path, new_path, files, obj)
            else:
                process_hist(path, new_path, files, obj)


#### This is where all the plotting actually happens
def process_hist(path, new_path, files, obj):
    """Overlay all the instances of this plot and apply the options."""
    counter = next_counter() # used for page numbers
    name = obj.GetName()
    hist = files[0].file.GetDirectory(path).Get(name)
    title = hist.GetTitle()
    x_title = hist.GetXaxis().GetTitle()
    y_title = hist.GetYaxis().GetTitle()
    if options.title:
        if options.title[0] == '+':
            title += options.title[1:]
        else:
            title = options.title
    if options.xlabel:
        if options.xlabel[0] == '+':
            x_title += options.xlabel[1:]
        else:
            x_title = options.xlabel
    if options.ylabel:
        if options.xlabel[0] == '+':
            y_title += options.ylabel[1:]
        else:
            y_title = options.ylabel
    if options.area_normalize or (options.sticky and 'Norm' in name):
        y_title = "Fraction of Events in Bin"
    if options.normalize:
        if type(options.normalize) == type(int):
            file_name = files[options.normalize_to_file - 1].name
            y_title = "Events Normalized to %s" % file_name
        else:
            y_title = "Events Scaled by %d" % options.normalize
    hists = []
    #### Apply options to hist from each file
    for i, file in enumerate(files):
        hist = file.file.GetDirectory(path).Get(name)
        if not hist: continue
        hist.SetTitle(file.name)
        if options.efficiency_from:
            denom = file.file.Get(options.efficiency_from)
            nbins = hist.GetNbinsX();
            num = [hist.GetBinContent(j) for j in range(1, nbins + 1)]
            den = [denom.GetBinContent(j) for j in range(1, nbins + 1)]
            eff, up, down = wilson(num, den)
            for j in range(nbins):
                hist.SetBinContent(j + 1, eff[j])
                hist.SetBinError(j + 1, max(up[j], down[j]))
        color = ROOT.TColor.GetColor(*options.colors[i][0:3])
        hist.SetLineColor(color)
#         if options.fill:
#             r, g, b = plot_colors_rgb[i % len(colors)]
#             #fill_color = ROOT.TColor.GetColor(r * 1.2, g * 1.2, b * 1.2)
#             fill_color = color
#             hist.SetFillColor(fill_color)
#             hist.SetFillStyle(1001)
#             print 'Hist ', hist.GetFillColor()
        if options.markers:
            hist.SetMarkerColor(color)
            hist.SetMarkerStyle(options.marker_styles[i])
        else:
            hist.SetMarkerSize(0)
        if options.overflow or (options.sticky and 'Overflow' in name):
            nbins = hist.GetNbinsX()
            overflow = hist.GetBinContent(nbins + 1)
            hist.AddBinContent(nbins, overflow)
        if options.underflow or (options.sticky and 'Underflow' in name):
            underflow = hist.GetBinContent(0)
            hist.AddBinContent(1, underflow)
        if options.area_normalize or (options.sticky and 'Norm' in name):
            integral = hist.Integral()
            if integral: hist.Scale(1. / integral)
        hists.append(hist)
    if options.normalize:
        if type(options.normalize) == type(int):
            integral = hists[options.normalize_to_file - 1].Integral()
            if integral:
                for hist in hists:
                    hist.Scale(hist.Integral() / integral)
        else:
            hist.Scale(options.normalize)
    #### Combine hists in a THStack and draw
    pads = [canvas]
    stack = ROOT.THStack('st%.3i' % counter, title)
    legend_height = 0.04 * len(files) + 0.02
    if options.legend == 1:
        legend_loc = [0.65, 0.89 - legend_height, 0.87, 0.89]
    elif options.legend == 8:
        legend_loc = [0.22, 0.15, 0.90, 0.15 + legend_height]
    else:
        print "Invalid legend parameter for ROOT output!"
        sys.exit(1)
    legend = ROOT.TLegend(*legend_loc)
    for hist in hists:
        stack.Add(hist)
        legend.AddEntry(hist)
    stack.Draw(options.draw)
    stack.GetXaxis().SetTitle(x_title)
    stack.GetYaxis().SetTitle(y_title)
    if options.ratio or (options.sticky and 'Ratio' in name):
        pads, stack, stack_ratio = add_ratio_plot(hists, stack, counter)
        pads[1].cd()
        stack_ratio.Draw(options.draw)
        pads[0].cd()
    pads[0].SetLogx(options.logx or (options.sticky and 'Logx' in name))
    pads[0].SetLogy(options.logy or (options.sticky and 'Logy' in name))
    stack.Draw(options.draw)
    if options.efficiency or (options.sticky and 'Eff' in name):
        stack.Draw(options.draw + 'e')
        stack.SetMaximum(1.)
        stack.SetMinimum(0.)
    if options.numbering:
        display_page_number(counter)
    if options.overflow or (options.sticky and 'Overflow' in name):
        display_overflow(stack, hist)
    if options.underflow or (options.sticky and 'Underflow' in name):
        display_underflow(stack, hist)
    legend.Draw()
    save_plot(stack, options.plot_dir, path, name, counter)

#### This is where all the plotting actually happens
def process_hist_matplotlib(path, new_path, files, obj):
    """Overlay all the instances of this plot and output using matplotlib."""
    counter = next_counter() # used for page numbers
    name = obj.GetName()
    xpos = options.size.find('x')
    width = float(options.size[:xpos])
    height = float(options.size[xpos+1:])
    plt.figure(1, figsize=(width, height))
    ax = plt.axes()
    ax.cla()
    stack = r2m.HistStack()
    #### Apply options to hist from each file
    for i, file in enumerate(files):
        hist = r2m.Hist(file.file.GetDirectory(path).Get(name),
                        file.name, xlabel=options.xlabel, ylabel=options.ylabel)
        if options.title:
            if options.title[0] == "+":
                hist.title += options.title[1:]
            else:
                hist.title = options.title
        if not hist: continue
        if options.efficiency_from:
            denom = r2m.Hist(file.file.Get(options.efficiency_from))
            eff, up, down = wilson([sum(hist.y)], [sum(denom.y)])
            hist.label += (" ($%.1f \pm %.1f\\%%$)" %
                           (eff[0] * 100., max(up[0], down[0]) * 100.))
            hist.y, up, down = wilson(hist.y, denom.y)
            hist.yerr = np.array([up, down])
        stack.add(hist, color=options.colors[i], fmt=options.marker_styles[i])
    if (options.errorbar):
        stack.plot_errorbar(replace=options.replace, yerr=True)
    if options.stack:
        stack.plot_barstack(replace=options.replace)
    if options.bar:
        stack.plot_bar(replace=options.replace, alpha=0.5)
    if options.efficiency:
        plt.ylim(0, 1)
    plt.legend(numpoints=1, loc=options.legend)
    if options.numbering:
        plt.text(1.0, 1.025, counter, transform=ax.transAxes,
                 horizontalalignment='right')
    output_file_name = '%s/%s/%s' % (options.plot_dir, path, name)
    plt.savefig(output_file_name, transparent=options.transparent)
    if options.ext == "pdf":
        shutil.copy("%s.pdf" % output_file_name, "%.3i.pdf" % counter)
    report_progress(counter)



######## Define some supporting functions #####################################

def save_plot(stack, plot_dir, path, name, counter):
    """Save the canvas to the output format defined by --ext."""
    output_file_name = '%s/%s/%s.%s' % (plot_dir, path, name, options.ext)
    canvas.SaveAs(output_file_name)
    if options.ext == 'pdf':
        numbered_pdf_name = '%.3i.pdf' % counter
        shutil.copy(output_file_name, numbered_pdf_name)
    report_progress(counter)

def report_progress(counter, divisor=1):
    """Print the current number of finished plots."""
    if counter % divisor == 0:
        print "\r%i plots written to %s" % (counter, options.output),
        sys.stdout.flush()

def merge_pdf():
    """Merge together all the produced plots into one pdf file."""
    if "001.pdf" not in os.listdir('.'):
        print "No output files, so no merged pdf was made"
        return
    print "Writing merged pdf..."
    os.system('gs -q -dBATCH -dNOPAUSE -sDEVICE=pdfwrite '
              '-dAutoRotatePages=/All '
              '-sOutputFile=%s.pdf ' % options.output +
              '[0-9][0-9][0-9].pdf')
    os.system('rm [0-9]*.pdf')

def display_page_number(page_number):
    """Add a page number to the top corner of the canvas."""
    page_text = ROOT.TText()
    page_text.SetTextSize(0.03)
    page_text.SetTextAlign(33)
    page_text.DrawTextNDC(0.97, 0.985, '%i' % page_number)

def display_overflow(stack, hist):
    """Add the overflow to the last bin and print 'Overflow' on the bin."""
    nbins = hist.GetNbinsX()
    x = 0.5 * (hist.GetBinLowEdge(nbins) +
               hist.GetBinLowEdge(nbins + 1))
    y = stack.GetMinimum('nostack')
    display_bin_text(x, y, nbins, 'Overflow')

def display_underflow(stack, hist):
    """Add the underflow to the first bin and print 'Underflow' on the bin."""
    nbins = hist.GetNbinsX()
    x = 0.5 * (hist.GetBinLowEdge(1) +
               hist.GetBinLowEdge(2))
    y = stack.GetMinimum('nostack')
    display_bin_text(x, y, nbins, 'Underflow')

def display_bin_text(x, y, nbins, text):
    """Overlay TEXT on this bin."""
    bin_text = ROOT.TText()
    bin_text.SetTextSize(min(1. / nbins, 0.04))
    bin_text.SetTextAlign(12)
    bin_text.SetTextAngle(90)
    bin_text.SetTextColor(13)
    bin_text.SetTextFont(42)
    bin_text.DrawText(x, y, text)

def add_ratio_plot(hists, stack, counter):
    """Divide canvas into two parts, and plot the ratio on the bottom."""
    ## Both pads are set to the full canvas size to maintain font sizes
    ## Fill style 4000 used to ensure pad transparency because of this
    div = 0.3 # portion of canvas to use for ratio plot
    margins = [ROOT.gStyle.GetPadTopMargin(), ROOT.gStyle.GetPadBottomMargin()]
    useable_height = 1 - (margins[0] + margins[1])
    canvas.Clear()
    pad = ROOT.TPad('mainPad', 'mainPad', 0., 0., 1., 1.)
    pad.SetFillStyle(4000)
    pad.Draw()
    pad.SetBottomMargin(margins[1] + div * useable_height)
    pad_ratio = ROOT.TPad('ratioPad', 'ratioPad', 0., 0., 1., 1.);
    pad_ratio.SetFillStyle(4000)
    pad_ratio.Draw()
    pad_ratio.SetTopMargin(margins[0] + (1 - div) * useable_height)
    pad.cd()
    stack.Draw()
    stack_ratio = ROOT.THStack('stRatio%.3i' % counter,
                               ';%s;Ratio' % stack.GetXaxis().GetTitle())
    for hist in hists[1:]:
        ratio_hist = hist.Clone()
        ratio_hist.Divide(hists[0])
        stack_ratio.Add(ratio_hist)
    stack_ratio.Draw()
    stack_ratio.GetYaxis().SetNdivisions(507) # Avoids crowded labels
    stack.GetXaxis().SetBinLabel(1, '') # Don't show numbers below top plot
    stack.GetXaxis().SetTitle('')
    if stack.GetYaxis().GetTitle() == '':
        stack.GetYaxis().SetTitle('Content')
    # Avoid overlap of y-axis numbers by supressing zero
    if stack.GetMinimum() / stack.GetMaximum() < 0.25:
        stack.SetMinimum(stack.GetMaximum() / 10000)
    return [pad, pad_ratio], stack, stack_ratio

def wilson(numerator, denominator):
    nbins = len(numerator)
    eff = [numerator[i] / denominator[i] for i in range(nbins)]
    up = []
    down = []
    for i in range(nbins):
        n = denominator[i]
        sqrt = math.sqrt(eff[i] * (1 - eff[i]) / n + 1 / (4 * n * n))
        up.append(-eff[i] + (1/(1 + 1/n) * (eff[i] + 1/(2*n) + sqrt)))
        down.append(eff[i] - (1/(1 + 1/n) * (eff[i] + 1/(2*n) - sqrt)))
    return eff, up, down

def add_options_from_configuration(options, nfiles):
    """Define a set of global variables storing style information, etc."""
    exec("import %s as config" % options.config[:-3])
    for attribute in dir(config):
        if '__' not in attribute:
            attr = getattr(config, attribute)
            setattr(options, attribute, attr)
    return options

def process_options(options, nfiles):
    options.use_matplotlib = (options.stack or options.errorbar or options.bar)
    try:
        global matplotlib
        import matplotlib
        if options.ext == "png":
            matplotlib.use('AGG')
        if options.ext == "pdf":
            matplotlib.use('PDF')
        if options.ext == "ps":
            matplotlib.use('PS')
        imported_matplotlib = True
    except ImportError:
        print "Unable to load matplotlib"
        if options.use_matplotlib:
            sys.exit(1)
        imported_matplotlib = False
    if options.use_matplotlib:
        try:
            global r2m, np, plt
            import root2matplot as r2m
            import numpy as np
            from matplotlib import pyplot as plt
            options.marker_styles = options.markers_matplotlib
        except ImportError:
            print "Unable to load root2matplot"
            sys.exit(1)
    else:
        options.marker_styles = options.markers_root
    if imported_matplotlib:
        if options.colormap:
            cmap = plt.get_cmap(options.colormap)
            if options.ncolors < nfiles:
                options.ncolors = nfiles
            options.colors = [cmap(float(i)/options.ncolors)
                              for i in range(nfiles)]
        else:
            options.colors = [[value/256. for value in options.colors[i]]
                              for i in range(nfiles)]
            options.ncolors = len(options.colors)
            if nfiles > options.ncolors:
                print "Not enough colors defined!"
                sys.exit(1)
    if options.normalize:
        if '.' in options.normalize:
            options.normalize = float(options.normalize)
        else:
            options.normalize = int(options.normalize)
    if options.efficiency_from:
        options.efficiency = True
    return options


######## Define the main program #############################################

def main():
    usage="""usage: %prog [options] file1.root file2.root file3.root ...

Function: overlays corresponding histograms from several files, dumping the
  images into a directory structure that mirrors that of the ROOT file and,
  if output format is pdf, also merging all images into a single file;
  most style options can be controlled from your rootlogon.C macro"""
    
    parser = optparse.OptionParser(usage=usage, 
                                   version='%s %s' % ('%prog', __version__))
    parser.add_option('-e', '--ext', default='pdf', 
                      help="choose an output extension; default is pdf")
    parser.add_option('--draw', default='nostack p H',
                      help="pass DRAW to ROOT's Draw command; default is "
                      "'nostack p H'; try 'nostack e' for error bars")
    parser.add_option('-m', '--markers', action='store_true', default=False,
                      help="add markers to histograms")
    parser.add_option('-s', '--sticky', action='store_true', default=False,
                      help="enable name-based special plotting options "
                      "(see below)")
#     parser.add_option('-f', '--fill', action='store_true', default=False,
#                       help="Fill histograms with a color")
    parser.add_option('--output', default='overlaidHists', metavar='NAME',
                      help="name of output directory; default is "
                      "'overlaidHists'")
    parser.add_option('--numbering', action='store_true', default=False,
                      help="add a page number in the upper right of each plot")
    parser.add_option('--path', default='', 
                      help="only process plot(s) in the given location or in "
                      "subdirectories; PATH may be a regular expression (use "
                      ".* for wildcard)")
    parser.add_option('--normalize', metavar='VALUE',
                      help="if integer, normalize to the VALUEth file "
                      "(starting with 1); if float, scale by VALUE")
    parser.add_option('--stack', action="store_true", default=False,
                      help="output a matplotlib stacked bar graph")
    parser.add_option('--errorbar', action="store_true", default=False,
                      help="output a matplotlib errorbar graph")
    parser.add_option('--bar', action="store_true", default=False,
                      help="output a matplotlib bar graph")
    parser.add_option('--transparent', action="store_true", default=False,
                      help="use a transparent background for matplotlib "
                      "output")
    parser.add_option('--colormap', default=None,
                      help="Select colors from the selected matplotlib "
                      "colormap rather than the defaults")
    parser.add_option('--ncolors', type=int, default=None,
                      help="The number of colors with which to divide the "
                      "colormap")
    parser.add_option('--legend', type=int, default=1, metavar="LOC",
                      help="Place legend in LOC, according to matplotlib "
                      "location codes; for ROOT, you can use 1 (default) for "
                      "upper right or 8 for lower center")
    parser.add_option('--size', default='6x4.5',
                      help="Define the size of the matplotlib plot as "
                      "width x height in inches; default is '6x4.5'")
    parser.add_option('--title', default=None,
                      help="Add TITLE to the title of each plot")
    parser.add_option('--xlabel', default=None,
                      help="Replace the x-axis label with XLABEL")
    parser.add_option('--ylabel', default=None,
                      help="Replace the y-axis label with YLABEL")
    parser.add_option('--config', default="overlayHists_config.py",
                      help="Use the given configuration file; default is "
                      "overlayHists_config.py")
    parser.add_option('--efficiency-from', default=None, metavar="DENOM",
                      help="Divide all plots by DENOM")
    group1 = optparse.OptionGroup(
        parser,
        "special plotting options",
        "Use the command line options given below to apply changes to all "
        "plots.  If you only wish to apply an option to a specific plot, "
        "you can use '-s' "
        "to turn on sticky keywords (such as 'Norm').  Any plot that includes "
        "the given keyword in its ROOT name will have the option applied "
        "regardless of its presence or absence on the command line."
        )
    group1.add_option('-n', '--area-normalize', action='store_true',
                      default=False,
                      help="'Norm': area normalize the histograms")
    group1.add_option('--efficiency', action='store_true', default=False,
                      help="'Eff' : force y axis scale to run from 0 to 1")
    group1.add_option('--logx', action='store_true', default=False,
                      help="'Logx': force log scale for x axis")
    group1.add_option('--logy', action='store_true', default=False,
                      help="'Logy': force log scale for y axis")
    group1.add_option('--overflow', action='store_true', default=False,
                      help="'Overflow' : display overflow content in "
                      "highest bin")
    group1.add_option('--underflow', action='store_true', default=False,
                      help="'Underflow': display underflow content in "
                      "lowest bin")
    group1.add_option('--ratio', action='store_true', default=False,
                      help="'Ratio': display a ratio plot below the normal "
                      "plot")
    parser.add_option_group(group1)
    global options
    options, arguments = parser.parse_args()
    options.plot_dir = '%s/%s' % (os.path.abspath('.'), options.output)
    options.regex = re.compile(options.path)
    files = [RootFile(filename) for filename in arguments]
    ## if no arguments provided, just display the help message
    if len(files) == 0:
        parser.print_help()
        sys.exit(0)
    ## add style options and create the canvas
    options = add_options_from_configuration(options, len(files))
    options = process_options(options, len(files))
    global canvas
    canvas = ROOT.TCanvas()
    ## here, we decend into the files to start plotting
    process_directory('', files)
    print ''
    if options.ext == 'pdf':
        merge_pdf()


if __name__ == '__main__':
    if '--timing' in sys.argv:
        sys.argv.remove('--timing')
        try:
            import cProfile
            cProfile.run('main()', 'timing')
        except ImportError:
            import profile
            profile.run('main()', 'timing')
        import pstats
        p = pstats.Stats('timing')
        p.sort_stats('cumulative').print_stats(25)
    else:
        main()

