"""
Toolkit to convert ROOT histograms to matplotlib figures.
"""

################ Import python libraries

import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import ROOT
import re
import copy


################ Define constants

_all_whitespace_string = re.compile(r'\s*$')


################ Define classes

class Hist(object):
    """A container to hold the parameters from a ROOT histogram."""
    def __init__(self, hist, label="__nolabel__", title=None,
                 xlabel=None, ylabel=None):
        try:
            if not hist.InheritsFrom("TH1"):
                print hist, "does not inherit from TH1, so cannot make a Hist"
                return
        except:
            print hist, "is not a ROOT object, so cannot make a Hist"
            return
        array = np.array
        self.nbins  = n = hist.GetNbinsX()
        self.xedges = array([hist.GetBinLowEdge(i) for i in range(1, n + 2)])
        self.x      = array([(self.xedges[i+1] + self.xedges[i])/2
                             for i in range(n)])
        self.xerr   = array([(self.xedges[i+1] - self.xedges[i])/2
                             for i in range(n)])
        self.y      = array([hist.GetBinContent(i) for i in range(1, n + 1)])
        self.yerr   = array([hist.GetBinError(  i) for i in range(1, n + 1)])
        self.underflow = hist.GetBinContent(0)
        self.overflow  = hist.GetBinContent(self.nbins + 1)
        self.title  = hist.GetTitle()
        self.xlabel = hist.GetXaxis().GetTitle()
        self.ylabel = hist.GetYaxis().GetTitle()
        if title : self.title  = title
        if xlabel: self.xlabel = xlabel
        if ylabel: self.ylabel = ylabel
        self.label  = label
        self.binlabels = array([hist.GetXaxis().GetBinLabel(i)
                                for i in range(1, n + 1)])
        if not any(self.binlabels): self.binlabels = None
    def show_titles(self, replace=None):
        """Add the titles defined in the ROOT histogram to the figure."""
        plt.title( _parse_latex(self.title , replace))
        plt.xlabel(_parse_latex(self.xlabel, replace))
        plt.ylabel(_parse_latex(self.ylabel, replace))
    def errorbar(self, xerr=False, yerr=False,
                 replace=None, **kwargs):
        """
        Generate a matplotlib errorbar figure.

        All additional keyword arguments will be passed to pyplot.errorbar.
        """
        if xerr:
            kwargs['xerr'] = self.xerr
        if yerr:
            kwargs['yerr'] = self.yerr
        errorbar = plt.errorbar(self.x, self.y, label=self.label, **kwargs)
        self.show_titles(replace)
        if self.binlabels:
            plt.xticks(np.arange(self.nbins), self.binlabels)
        plt.xlim(self.xedges[0], self.xedges[-1])
        return errorbar
    def bar(self, yerr=False, replace=None, **kwargs):
        """
        Generate a matplotlib bar figure.

        All additional keyword arguments will be passed to pyplot.bar.
        """
        if yerr:
            kwargs['yerr'] = self.yerr
        width = np.array([self.xedges[i+1] - self.xedges[i]
                          for i in range(self.nbins)])
        bar = plt.bar(self.xedges[0:-1], self.y, width, label=self.label,
                      **kwargs)
        self.show_titles(replace)
        return bar
    def TH1F(self, name=""):
        """Return a ROOT.TH1F object with the contents of this Hist"""
        th1f = ROOT.TH1F(name, "", self.nbins, self.xedges)
        th1f.SetTitle("%s;%s;%s" % (self.title, self.xlabel, self.ylabel))
        for i in range(self.nbins):
            th1f.SetBinContent(i + 1, self.y[i])
        return th1f
    def __div__(self, denominator):
        """Return an efficiency plot with Wilson score interval errors."""
        eff = []
        upper_err = []
        lower_err = []
        for i in range(self.nbins):
            n = denominator.y[i]
            if n == 0:
                eff.append(0)
            else:
                eff.append(float(self.y[i]) / denominator.y[i])
            s = math.sqrt(eff[i] * (1 - eff[i]) / n + 1 / (4 * n * n))
            t = (1/(1 + 1/n) * (eff[i] + 1/(2*n) + s))
            upper_err.append(t - eff[i])
            lower_err.append(eff[i] - t)
        quotient = copy.deepcopy(self)
        quotient.y = np.array(eff)
        quotient.yerr = np.array([upper_err, lower_err])
        return quotient


class HistStack(object):
    """
    A container to hold Hist objects for plotting together.

    When plotting, the title and the x and y labels of the last Hist added
    will be used unless specified otherwise in the constructor.
    """
    def __init__(self, hists=None, title=None, xlabel=None, ylabel=None):
        self.hists  = []
        self.kwargs = []
        self.title  = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        if hists:
            for hist in hists:
                self.add(hist)
    def add(self, hist, label=None, **kwargs):
        """
        Add a Hist object to this stack.

        Any additional keyword arguments will be added to just this Hist 
        when the stack is plotted.
        """
        if label is not None:
            hist.label = label
        self.hists.append(hist)
        self.kwargs.append(kwargs)
    def plot_barstack(self, replace=None, **kwargs):
        """
        Make a matplotlib bar plot, with each Hist stacked upon the last.

        Any additional keyword arguments will be passed to pyplot.bar.
        """
        bottom = [0 for i in range(self.hists[0].nbins)]
        for i, hist in enumerate(self.hists):
            if self.title  is not None: hist.title  = self.title
            if self.xlabel is not None: hist.xlabel = self.xlabel
            if self.ylabel is not None: hist.ylabel = self.ylabel
            hist.label = _parse_latex(hist.label, replace)
            all_kwargs = copy.copy(kwargs)
            all_kwargs.update(self.kwargs[i])
            hist.bar(replace=replace, bottom=bottom, **all_kwargs)
            bottom = [sum(pair) for pair in zip(bottom, hist.y)]
    def plot_errorbar(self, replace=None, **kwargs):
        """
        Make a matplotlib errorbar plot, with all Hists in the stack overlaid.

        Any additional keyword arguments will be passed to pyplot.errorbar.
        """
        for i, hist in enumerate(self.hists):
            if self.title  is not None: hist.title  = self.title
            if self.xlabel is not None: hist.xlabel = self.xlabel
            if self.ylabel is not None: hist.ylabel = self.ylabel
            hist.label = _parse_latex(hist.label, replace)
            all_kwargs = copy.copy(kwargs)
            all_kwargs.update(self.kwargs[i])
            hist.errorbar(replace=replace, **all_kwargs)
    def plot_bar(self, replace=None, **kwargs):
        """
        Make a matplotlib bar plot, with all Hists in the stack overlaid.

        Any additional keyword arguments will be passed to pyplot.bar.  You will
        probably want to include an transparency value (i.e. alpha=0.5).
        """
        for i, hist in enumerate(self.hists):
            if self.title  is not None: hist.title  = self.title
            if self.xlabel is not None: hist.xlabel = self.xlabel
            if self.ylabel is not None: hist.ylabel = self.ylabel
            hist.label = _parse_latex(hist.label, replace)
            all_kwargs = copy.copy(kwargs)
            all_kwargs.update(self.kwargs[i])
            all_kwargs.pop('fmt', None)
            hist.bar(replace=replace, **all_kwargs)

class RootFile:
    """A wrapper for TFiles, allowing easier access to methods."""
    def __init__(self, file_name):
        self.name = file_name[0:-5]
        self.file = ROOT.TFile(file_name, 'read')
        if self.file.IsZombie():
            print "Error opening %s" % file_name
            return None
    def cd(self, directory):
        """Make directory the current directory."""
        self.file.cd(directory)
    def get(self, object_name):
        """Return a Hist object from the given path within this file."""
        return Hist(self.file.Get(object_name))


################ Define functions for navigating within ROOT

def ls(directory=""):
    """Return a python list of ROOT object names from the given directory."""
    keys = ROOT.gDirectory.GetDirectory(directory).GetListOfKeys()
    key = keys[0]
    names = []
    while key:
        obj = key.ReadObj()
        key = keys.After(key)
        names.append(obj.GetName())
    return names

def pwd():
    """Return ROOT's present working directory."""
    return ROOT.gDirectory.GetPath()

def get(object_name):
    """Return a Hist object with the given name."""
    return Hist(ROOT.gDirectory.Get(object_name))


################ Define additional helping functions

def _parse_latex(string, replacements):
    """Modify a string based on a dictionary of replacements."""
    if not replacements:
        return string
    for key, value in replacements:
        string = string.replace(key, value)
    # print "LaTeX string: ", string
    if re.match(_all_whitespace_string, string):
        return ""
    return string

def prepare_efficiency(axes, lower_bound=0.69):
    """
    Set up a figure with breakmarks to indicate a suppressed zero.

    The y axis limits will be set to lower_bound and 1.0, as appropriate for
    an efficiency plot.  You must have already drawn a figure on the axes
    passed to the function, so the the x axis limits will be defined.
    """
    def breakmarks(axes, position):
        plt.axes(axes)
        xwidth = 0.005 * (plt.xlim()[1] - plt.xlim()[0])
        ywidth = 0.001
        if position == 'bottom': j = 0
        if position == 'top': j = 1
        for i in range(2):
            line = matplotlib.lines.Line2D(
                [plt.xlim()[i] - xwidth, plt.xlim()[i] + xwidth],
                [plt.ylim()[j] - ywidth, plt.ylim()[j] + ywidth],
                linewidth=1, color='black', clip_on=False)
            axes.add_line(line)
    def newbreakmarks(axes, spacing, height):
        plt.axes(axes)
        gap_height = spacing / (height + spacing) * (1.0 - plt.ylim()[0])
        seg_height = gap_height / 3
        xwidth = 0.008 * (plt.xlim()[1] - plt.xlim()[0])
        xoffsets = [0, +xwidth, -xwidth, 0]
        yvalues  = [plt.ylim()[0] - i * seg_height for i in range(4)]
        for i in range(2):
            line = matplotlib.lines.Line2D(
                [plt.xlim()[i] + offset for offset in xoffsets], yvalues,
                linewidth=1, color='black', clip_on=False)
            axes.add_line(line)

    # Backgrounds must be transparent for this to work correctly
    axes.set_axis_bgcolor('None')
    # Set constants
    breakmark_spacing = 0.02
    lower_axes_height = 0.02
    # Raise the bottom of axes to allow room for breakmarks and lower_axes
    box = axes.get_position()
    points = box.get_points().copy()
    newpoints = points.copy()
    newpoints[0, 1] += lower_axes_height + breakmark_spacing
    box.set_points(newpoints)
    axes_height = newpoints[1,1] - newpoints[0,1]
    axes.set_position(box)
    axes.set_ylim(lower_bound, 1.)
    # Erase the bottom edge of axes
    for loc, spine in axes.spines.iteritems():
        if loc in ['bottom']:
            spine.set_color('none')
    # Create lower_axes
    newpoints = points.copy()
    newpoints[1,1] = points[0,1] + lower_axes_height
    box.set_points(newpoints)
    lower_axes = plt.axes(box, axisbg='None', sharex=axes)
    for loc, spine in lower_axes.spines.iteritems():
        if loc in ['top']:
            spine.set_color('none')
    # Set only top ticks for axes and only bottom ticks for lower_axes
    axes.get_xaxis().set_ticks_position('top')
    lower_axes.get_xaxis().set_ticks_position('bottom')
    # Set ylim for lower_axes so it has the same scale as axes
    lower_axes.set_ylim(0., (1 - lower_bound) * (lower_axes_height/axes_height))
    lower_axes.set_yticks([])
    plt.setp(axes.get_xticklabels(), visible=False)
    # Draw the breakmarks
    # breakmarks(axes, 'bottom')
    # breakmarks(lower_axes, 'top')
    newbreakmarks(axes, breakmark_spacing, axes_height)
