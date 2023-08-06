#!/usr/bin/env python
from __future__ import division, with_statement

"""
validate_external: Evaluate the characteristics of a given
segmentation with respect to a predefined set of genomic landmarks.

This tool, at least in its first incarnation, is intended to provide
spot-checking functionality, giving an overview of the characteristics
of a particular segmentation. The tool performs a series of different
types of analyses, summarizing the results in an HTML report. By
default, all validations are performed, though a subset may be
selected using the command line options listed below.

OUTDIR: A unique name associated with this evaluation. All of the results
are stored in a directory named <root>, with output filenames as
described below.

BEDFILE: The name of a file that contains a segmentation. The file must be
in BED format, and may be gzipped. The first three columns specify
genomic coordinates and the fourth column indicates the segment name.
This name is interpreted as a "state" identifier. Subsequent columns
in the segmentation BED file are ignored.

GENOMEDATADIR: A directory that contains a number of genomedata files

XXX: assumes that segmentation is non-overlapping
"""

__version__ = "$Revision: 55 $"

# Copyright 2008 Michael M. Hoffman <mmh1@washington.edu>

from collections import defaultdict
from contextlib import closing, contextmanager
from errno import ENOENT
from functools import partial
from gzip import open as _gzip_open
from itertools import repeat
from os import extsep
import sys
import time
import os
import datetime
import re   # the regular expression package, to get the tracks used for the segmentation
import math
from subprocess import check_call

from genomedata import Genome
from numpy import array, concatenate, empty, histogram, iinfo, median, NINF, PINF, isfinite
from path import path
from pkg_resources import resource_filename
from rpy2.robjects import r
import rpy2.robjects.numpy2ri # imported for side-effect
from tabdelim import DictWriter

from .bed import read_native

try:
    # Python 2.6
    PKG = __package__
except NameError:
    PKG = "segtools"

PKG_R = ".".join([PKG, "R"])

EXT_GZ = "gz"
EXT_PDF = "pdf"
EXT_PNG = "png"
EXT_TAB = "tab"
EXT_HTML = "html"
SUFFIX_GZ = extsep + EXT_GZ

FIELDNAMES_LENGTH = ["label", "num.segs", "mean.len", "median.len",
                     "stdev.len", "num.bp", "frac.bp"]
FIELDNAMES_DISTRIBUTIONS = ["label", "trackname", "lower_edge", "count"]
FIELDNAMES_TRACK_DISTRIBUTIONS = ["trackname", "lower_edge", "count"]
FIELDNAMES_TSS = ["label", "num.tss", "density.tss"]
FIELDNAMES_FREQ = ["label", "A|T", "C|G", "ambig_nucleotide", "AA|TT", "AC|GT", "AG|CT", "AT", "CA|TG", "CC|GG", "CG", "GA|TC", "GC", "TA", "ambig_dinucleotide"]
FIELDNAMES_AGGREGATION = ["label", "position", "count"]

THUMB = "_small"    # for thumbnails
NAMEBASE_SUMMARY = "summary"
NAMEBASE_LENGTH = "lengths"
NAMEBASE_TRACK_DISTRIBUTIONS = "track_distributions"
NAMEBASE_DISTRIBUTIONS = "distributions"
NAMEBASE_TSS = "tss"
NAMEBASE_FREQ = "nucleotide"
NAMEBASE_AGGREGATION = "aggregation"
#NAMEBASE_TSS_DENSITY = "tssdensity"    # not used

LABEL_ALL = "all"

PNG_WIDTH = 800
PNG_HEIGHT = 600

PNG_WIDTH_PER_PLOT = 300
PNG_HEIGHT_PER_PLOT = 200
THUMB_WIDTH = 100

PDF_WIDTH = 11
PDF_HEIGHT = 8.5

NUM_BINS = 100

COL_START = 0
COL_END = 1
COL_LABEL_KEY = 2

global QUICK
global CALC_RANGES

## classes

class Segmentation(object):
    """
    chromosomes: a dict
      key: chromosome name
      val: segments: numpy.ndarray(each row = chromStart, chromEnd, label_key)

    labels: a dict
      key: int ("label_key")
      val: printable (str or int)
      
    tracks: a list of track names that were used to obtain the segmentation
    segtool: the tool that was used to obtain this segmentation (e.g. segway)  
    """
    def __init__(self, chromosomes, labels, tracks, segtool):
        self.chromosomes = chromosomes
        self.labels = labels
        self.tracks = tracks
        self.segtool = segtool

############################# UTILITY FUNCTIONS ############################
def extjoin(*args):
    return extsep.join(args)

def make_filename(dirpath, namebase, ext):
    return dirpath / extjoin(namebase, ext)

def gzip_open(*args, **kwargs):
    return closing(_gzip_open(*args, **kwargs))

def maybe_gzip_open(filename, *args, **kwargs):
    if filename.endswith(SUFFIX_GZ):
        return gzip_open(filename, *args, **kwargs)
    else:
        return open(filename, *args, **kwargs)

def fill_array(scalar, shape, dtype=None, *args, **kwargs):
    if dtype is None:
        dtype = array(scalar).dtype

    res = empty(shape, dtype, *args, **kwargs)
    res.fill(scalar)

    return res

@contextmanager
def none_contextmanager():
    yield None

@contextmanager
def tab_saver(dirpath, namebase, fieldnames):
    outfilename = make_filename(dirpath, namebase, EXT_TAB)

    with open(outfilename, "w") as outfile:
        yield DictWriter(outfile, fieldnames, extrasaction="ignore")

## R utility functions
def r_source(resourcename):
    r.source(resource_filename(PKG_R, resourcename))
    # MA: The source function of R allows the execution of statements 
    #	from a file while running R interactively

@contextmanager
def png(dirpath, namebase, w=PNG_WIDTH, h=PNG_HEIGHT):
    # Mirela: added the option to give it the png size
    png_filename = make_filename(dirpath, namebase, EXT_PNG)
    #png_small_filename = make_filename(dirpath, "%s%s" % (namebase, THUMB), EXT_PNG)
    
    r.png(png_filename, width=w, height=h)
    png_device = r['dev.cur']()

    # Enable copying from device
    r['dev.control']("enable")
    
    yield
    
    # Close device
    r['dev.off'](png_device)
    
    # XXX: produce thumbnails
    #r['dev.copy'](device="png()", file=png_small_filename, width=THUMB_WIDTH)
     
    #command = "convert -resize %dx%d %s %s" % (THUMB_WIDTH, h*THUMB_WIDTH/w, png_filename, png_small_filename)    
    #print command
    #check_call(command)

# Using pdf (or postscript) as the device in R doesn't require X forwarding
@contextmanager
def pdf(dirpath, namebase, w=PDF_WIDTH, h=PDF_HEIGHT):
    pdf_filename = make_filename(dirpath, namebase, EXT_PDF)
    
    #Dingbats turned off because otherwise circles were being displayed as q's
    r.pdf(file=pdf_filename, width=w, height=h, useDingbats=False)
    pdf_device = r['dev.cur']()

    yield

    png_filename = make_filename(dirpath, namebase, EXT_PNG)
    
    # Close device
    r['dev.off'](pdf_device)


## Gets track/tool info from BED file header
## Assumes standard notation
def get_tracks(line):
    regexp = re.compile('description="(.*) segmentation of (.*)"')

    segtool = ""
    tracks = []

    matching = regexp.search(line)
    if matching:
        segtool = matching.group(1)
        tracks = matching.group(2).split(', ')
    return (segtool, tracks)

## input functions
def load_segmentation(filename):
    data = defaultdict(list)	# MA: a dictionary-like object

    # Give each label a unique int id (not associated with actual string
    # Thus, labels do not need to be convertable to ints in any way
    label_list = []  # stores str(label)... index is associated int

    # read in as lists of tuples
    with maybe_gzip_open(filename) as infile:
        # first get the tracks that were used for this segmentation
        # read the first line separately, I could incorporate it into read_native
        firstline = infile.readline()
        #assert "type=wiggle_0" in firstline.split()
        (segtool, tracks) = get_tracks(firstline)
        #print >>sys.stderr, "Loading data from %d tracks" % len(tracks)
        for datum in read_native(infile):
            label = datum.name
            if label in label_list:
                label_int = label_list.index(label)
            else:  # Add label to mapping
                label_int = len(label_list)
                label_list.append(label)
                #print >>sys.stderr, "Mapping label: %s -> %d" % (label, label_int)

            segment = (datum.chromStart, datum.chromEnd, label_int)
            data[datum.chrom].append(segment)

    # convert lists of tuples to array
    chromosomes = dict((chrom, array(segments))
                       for chrom, segments in data.iteritems())

    labels = dict((index, label)
                  for index, label in enumerate(label_list))

    # wrap in a Segmentation object
    return Segmentation(chromosomes, labels, tracks, segtool)

############################# LENGTH VALIDATION ############################
def make_row_length(label, lengths, num_bp, total_bp):
    return {"label": label,
            "num.segs": len(lengths),
            "mean.len": "%.3f" % lengths.mean(),     # you can customize the format by "%.2f" % lengths.mean()
            "median.len": "%.3f" % median(lengths),
            "stdev.len": "%.3f" % lengths.std(),
            "num.bp": num_bp,
            "frac.bp": "%.3f" % (num_bp / total_bp)}

def segmentation_lengths(segmentation):
    # key: label_key
    # val: list of numpy.ndarray
    lengths = defaultdict(list)

    labels = segmentation.labels

    # convert segment coords to lengths
    for chromosome_segmentation in segmentation.chromosomes.itervalues():
        for label_key in labels.iterkeys():
            labeled_row_indexes = chromosome_segmentation[:, 2] == label_key
            labeled_rows = chromosome_segmentation[labeled_row_indexes]
            lengths[label_key].append(labeled_rows[:, 1] - labeled_rows[:, 0])

    # key: label_key
    # val: int
    num_bp = {}

    # convert lengths to:
    # key: label_key
    # val: numpy.ndarray(dtype=integer)
    for label_key, label_lengths_list in lengths.iteritems():
        label_lengths = concatenate(label_lengths_list)
        lengths[label_key] = label_lengths
        num_bp[label_key] = label_lengths.sum()

    return lengths, labels, num_bp

def save_tab_length(lengths, labels, num_bp, dirpath):
    total_bp = sum(num_bp.itervalues())

    with tab_saver(dirpath, NAMEBASE_LENGTH, FIELDNAMES_LENGTH) as saver:
        for label_key, label_lengths in lengths.iteritems():
            num_bp_label = num_bp[label_key]
            label = labels[label_key]
            row = make_row_length(label, label_lengths, num_bp_label, total_bp)

            saver.writerow(row)

        all_lengths = concatenate(lengths.values())
        row = make_row_length(LABEL_ALL, all_lengths, total_bp, total_bp)

        saver.writerow(row)

def plot_length(lengths, labels, dirpath):
    r_source("external.length.R")

    # fix order for iterating through dict; must be consistent
    label_keys = labels.keys()

    # XXXopt: allocating space in advance might be faster
    lengths_array = concatenate([lengths[label_key]
                                 for label_key in label_keys])

    # creates an array that has the label repeated as many times as
    # the length
    labels_array = concatenate([[labels[label_key]] * len(lengths[label_key])
                               for label_key in label_keys])
    # XXX: convert to a factor

    data = r["data.frame"](seg=labels_array, len=lengths_array)

    with png(dirpath, NAMEBASE_LENGTH):
        r.plot(r["violinplot.length"](data=data))
    with pdf(dirpath, NAMEBASE_LENGTH):
        r.plot(r["violinplot.length"](data=data))
                           
def validate_length(segmentation, dirpath, genome, filenames):
    #(segmentation, dirpath, genome) = setup_validator(outdirname, bedfilename, genomedatadir, clobber)
    lengths, labels, num_bp = segmentation_lengths(segmentation)

    save_tab_length(lengths, labels, num_bp, dirpath)
    plot_length(lengths, labels, dirpath)


########################## DISTRIBUTION VALIDATION #########################
def constant_factory(val):
    return repeat(val).next

## Returns splice of continuous from supercontig within segment range
## datatype should be "continuous" or "sequence"
## Assumes supercontigs are non-overlapping and sorted by start ascending
## Returns empty array if no supercontig touches the given range
def get_supercontig_splice(chromosome, start, end, datatype="continuous"):
    if datatype not in ("continuous", "sequence"):
        print >>sys.stderr, "Unknown data type in 'get_supercontig_splice!"
        sys.exit()
        
    # iterate through each supercontig
    saved = array([])
    for supercontig, continuous in chromosome.itercontinuous():
        #print >>sys.stderr, "Examining supercontig [%d, %d]" % (supercontig.start, supercontig.end)

        # Select appropriate data stream
        if datatype == "continuous":
            data = continuous
        else:
            data = supercontig.seq
            
        # XXX Make sure there are no OBOBS in indexing!
        if start >= supercontig.start and end <= supercontig.end:
            # Found supercontig that completely covers range
            return data[start - supercontig.start : end - supercontig.start]
        elif start >= supercontig.start and start < supercontig.end:
            # Overlapping supercontig end
            saved = array(data[start - supercontig.start : len(data) - 1])
        elif end > supercontig.start and end < supercontig.end:
            # Overlapping supercontig start
            data_splice = data[0 : end - supercontig.start]
            # Because supercontigs in sorted order, we can return here
            if saved.shape[0] > 0:
                return concatenate((saved, data_splice))
            else:
                return data_splice
        elif end < supercontig.start:
            # We've passed the appropriate range
            break

    return saved

def remove_nans(numbers):
# by Mirela
    bool_values = isfinite(numbers)                
    numbers_nonan = numbers[bool_values]
    return numbers_nonan

def min_max_nonan(numbers):
# by Mirela
    bool_values = isfinite(numbers)                
    numbers_nonan = numbers[bool_values]
    maximum = NINF
    minimum = PINF
    if len(numbers_nonan) > 0:
        maximum = max(numbers_nonan)
        minimum = min(numbers_nonan)
    return (minimum, maximum)

def max_nonan(numbers):
# by Mirela
    bool_values = isfinite(numbers)                
    numbers_nonan = numbers[bool_values]
    if len(numbers_nonan) > 0:
        return max(numbers_nonan)
    return NINF


def seg_min_max(chromosome, segmentation, track_index):
    #print "Looking for min & max in chromosome ", chromosome.name, " for track ", track_index
    #print "segmentation: ", segmentation.chromosomes
    old_min = PINF      # MA: one min for every label, to change this for any # of labels
    old_max = NINF   
       
       
    try:
        segments = segmentation.chromosomes[chromosome.name]        
    except KeyError:
        #print "    is NOT in the segmentation"
        return (old_min, old_max)

        
    #print "    IS in the segmentation"
    #print "Segments: ", segments        

    for segment in segments:   		        
        seg_start = segment[COL_START]   
        seg_end = segment[COL_END]

        continuous = get_supercontig_splice(chromosome, seg_start, seg_end, "continuous")

        if continuous.shape[0] > 0:
            # MA: I don't think it should be -1, because array[x:y] doesn't include y
            continuous_col = continuous[:, track_index]
            
            # Mirela: continuous_col might have date NaN (missing data). 
            #   We have to ignore these from the computation of min and max
            continuous_col_all_finite = remove_nans(continuous_col)  
            
            # sanity check
            if len(continuous_col_all_finite) != 0:
                old_min = min(old_min, min(continuous_col_all_finite))
                old_max = max(old_max, max(continuous_col_all_finite))            
    
    return (old_min, old_max)        

# not used
def seg_min(chromosome, segmentation, col_index):
    if chromosome.name in segmentation.chromosomes:
        return chromosome.mins[col_index]
    else:
        return PINF
        
# not used
def seg_max(chromosome, segmentation, col_index):
    if chromosome.name in segmentation.chromosomes:
        return chromosome.maxs[col_index]
    else:
        return NINF

def get_num_tracks(genome):    
    # MA: this should really be part of the Genome class - TODO
    for chromosome in genome:    
        tracknames = chromosome.tracknames_continuous
        return len(tracknames)

def calc_ranges_for_segmentation(genome, segmentation, use_seg_tracks):
    res = defaultdict(constant_factory((PINF, NINF)))
    for chromosome in genome:    
        tracknames = chromosome.tracknames_continuous
        for col_index, trackname in enumerate(tracknames):      
                  
            # figure out if I should use this track or not                    
            if use_seg_tracks and trackname not in segmentation.tracks: continue
            if not use_seg_tracks and trackname in segmentation.tracks: continue  
                                
            #if (col_index != 4): continue
            #print >> sys.stderr, "  Calculating the boundaries for chrom ", chromosome.name, ", track ", trackname
            (minimum, maximum) = seg_min_max(chromosome, segmentation, col_index)
            old_min, old_max = res[trackname]
            res[trackname] = (min(old_min, minimum), max(old_max, maximum))
            #print "For chr ", chromosome.name, " and track ", trackname, " old min=", old_min, "new min=", minimum, " old max=", old_max, " new max = ", maximum
            #break
    return dict(res)   

def calc_ranges(genome):
    """
    returns a dict
    key: trackname
    val: (min, max) for that trackname
    """
    # start with the most extreme possible values
    res = defaultdict(constant_factory((PINF, NINF)))

    for chromosome in genome:
        tracknames = chromosome.tracknames_continuous
        for col_index, trackname in enumerate(tracknames):
            old_min, old_max = res[trackname]
            res[trackname] = (min(old_min, chromosome.mins[col_index]),
                              max(old_max, chromosome.maxs[col_index]))
            #res[trackname] = (0, 800)                              
	
    # eliminate the defaultdict behavior
    return dict(res)

def map_segments(segments, labels, chrom_size):
    """
    converts a segment mapping into labels at every nucleotide position 
        in the chromosome
        
    e.g.  segment labeled 0 at position [0,4) followed by 
          segment labeled 1 at position [4,7) gets converted into:
          0000111
    """  
    segments_dtype = segments.dtype		# MA: the data type of segments
    segments_dtype_max = iinfo(segments_dtype).max # sentinel value		
    # MA: the maximum value supported by the type
    assert segments_dtype_max not in labels.keys()

    res = fill_array(segments_dtype_max, (chrom_size,), segments_dtype)

    # will overwrite in overlapping case
    for segment in segments:
        res[segment[COL_START]:segment[COL_END]] = segment[COL_LABEL_KEY]

    return res

def calc_histogram(genome, segmentation, num_bins, use_seg_tracks):
    """
    The input parameter use_seg_tracks is:
    - 1: if we are computing the histograms only for tracks that were used for segmentation
    - 0: if we are computing the histograms only for tracks that were NOT used
    Uses global variable CALC_RANGES, if:
    - False: if we are using the precomputed ranges stored for the entire genome file
    - True: if we are calculating the segmentation ranges across the entire input
    
    returns a dict

    key: label_key
    val: dict
         key: trackname
         val: [hist, edges]
    """
    # two passes through the data to avoid running out of memory:
    
    #   If it uses CALC_RANGES, it uses the maximum across the whole genome, which is stored in the input genome file
    #       This is good if the segmentation covers the whole genome or almost the whole genome
    #   If it uses CALC_RANGES_for_segmentation instead, the maximum for the x axis is computed for this segmentation.
    #       This is good if the segmentation covers a small part of the entire genome.

    # Switch added by Orion: if CALC_RANGES is False, use ranges in database
    # else compute them from the segmentation data
    ranges = None
    if CALC_RANGES:
        print >>sys.stderr, "   calculating the ranges for the segmentation"
        ranges = calc_ranges_for_segmentation(genome, segmentation, use_seg_tracks)
    else:
        ranges = calc_ranges(genome)

    # key: trackname
    # val: histogram_func: a function that generates a histogram from data
    #                      with uniform bins within a track
    # MA: for every trackname (one of 5), there's one function that generates histograms
    histogram_funcs = dict((trackname, partial(histogram, bins=num_bins,
                                               range=track_range, new=True))
                           for trackname, track_range in ranges.iteritems())
    # MA: trackname is one the (5) track names, track_range is (min,max)
    # MA: functools.partial(func[, *args][, **keywords]) Returns a new partial 
    #	object which when called will behave like func called with the positional 
    #	arguments args and keyword arguments keywords.
    
    labels = segmentation.labels
    # return dictionary: see function docstring for specification
    # MA: now for every label (0 or 1), and for every trackname there's a histogram array of the right boundary and frequency
    res = dict((label_key, dict((trackname, list(histogram_func(array([]))))
                                for trackname, histogram_func
                                in histogram_funcs.iteritems()))
               for label_key in labels)
    
    for chromosome in genome:
        chrom = chromosome.name
        print >>sys.stderr, "  %s" % chrom

        try:
            segments = segmentation.chromosomes[chrom]
        except KeyError:
            print >>sys.stderr, "   skipping: no data"
            continue

        segment_map = map_segments(segments, labels, chromosome.end)
        # MA: segment_map has the label for each position in the entire chromosome,
        #   as obtained by the segmentation        

        # iterate through each supercontig
        for supercontig, continuous in chromosome.itercontinuous():
            print >>sys.stderr, "   %s" % supercontig.name
            supercontig_map = segment_map[supercontig.start:supercontig.end]
            # MA: supercontig_map contains 0 or 1 labels for this supercontig, 
            #   or a "sentinel value outside of the segmentation
            
            # iterate through each label
            for label_key, label in labels.iteritems():
                print >>sys.stderr, "    %s" % label

                label_rows = supercontig_map == label_key
                res_label = res[label_key]

                # iterate through each track
                for trackname, histogram_func in histogram_funcs.iteritems():                                     
                                        
                    col_index = chromosome.index_continuous(trackname)       
                    #if (col_index != 4): continue
                    print >>sys.stderr, "     %s" % trackname                                 
                    # MA: col_index is the index of the trackname (if 5 tracks, it can be 0, 1, 2, 3 or 4)

                    # only reading in here to reduce peak memory usage
                    continuous_col = continuous[:, col_index]
                    # MA: continuous_col has now the "intensity" (continuous number) from the data track
                    #  len(supercontig_map) = len(continuous_col) because they are for the same segment
                    
                    label_col = continuous_col[label_rows]

                    #print >>sys.stderr, "       length of conti col ", len(continuous_col)
                    #print >>sys.stderr, "       length of label col ", len(label_col)
                    #if (len(label_col) > 0):
                        #print "         max of label ", label, " is ", max_nonan(label_col)

                    res_trackname = res_label[trackname]

                    # MA: we need to remove the NaN's, otherwise the numpy.histogram function 
                    #   gets confused and misses some of the data 
                    label_col_nonan = remove_nans(label_col)
                    hist, edges = histogram_func(label_col_nonan)
                    # MA: edges is a list containing the left edge of every bin, hist is the frequency for every bin
                    # This calls pynum.histogram
                    #print >>sys.stderr, "Hist  = ", hist
                    #print >>sys.stderr, "Edges = ", edges

                    assert(res_trackname[1] == edges).all()
                    res_trackname[0] += hist
                    # TO CHANGE: MA: stop at the first track for now
                    
        if QUICK: break
    return res

# def save_tab_distributions_tracknames_as_rows(histogram, labels, dirpath):
#     # by Mirela
#     # hmm not sure
#     with tab_saver(dirpath, NAMEBASE_DISTRIBUTIONS,
#                    FIELDNAMES_DISTRIBUTIONS) as saver:
#         for label_key, label_histogram in histogram.iteritems():
#             label = labels[label_key]

#             for trackname, (hist, edges) in label_histogram.iteritems():
#                 for lower_edge, count in zip(edges, hist.tolist() + ["NA"]):
#                     saver.writerow(locals())
#             break;


def save_tab_distributions(histogram, labels, dirpath, use_seg_tracks, namebase=NAMEBASE_DISTRIBUTIONS, fieldnames=FIELDNAMES_DISTRIBUTIONS):
    if use_seg_tracks is None:
        filename = "%s" % namebase
    elif use_seg_tracks == 1:
        filename = "%s_inseg" % namebase
    else:
        filename = "%s_notinseg" % namebase

    with tab_saver(dirpath, filename, fieldnames) as saver:
        if labels is not None:
            for label_key, label_histogram in histogram.iteritems():
                label = labels[label_key]
                
                for trackname, (hist, edges) in label_histogram.iteritems():
                    for lower_edge, count in zip(edges, hist.tolist() + ["NA"]):
                        saver.writerow(locals())
        else:
            for trackname, (hist, edges) in histogram.iteritems():
                for lower_edge, count in zip(edges, hist.tolist() + ["NA"]):
                    saver.writerow(locals())


def plot_distributions(dirpath, num_tracks, num_labels, use_seg_tracks):
    r_source("external.distributions.R")

    if use_seg_tracks is None:
        basename = "%s" % NAMEBASE_TRACK_DISTRIBUTIONS
        use_seg_tracks = 0
    elif use_seg_tracks == 1:
        basename = "%s_inseg" % NAMEBASE_DISTRIBUTIONS
    else:
        basename = "%s_notinseg" % NAMEBASE_DISTRIBUTIONS

    if num_labels is None:
        num_labels = 0

    # load data from the file just written out
    # it's bad to remake the filename
    # XXX: rewriting everything in terms of a class would allow avoiding this
    filename = make_filename(dirpath, basename, EXT_TAB)

    print >>sys.stderr, "-Reading Distributions"
    distributions = r["read.distributions"](filename)

    # now I'm displaying the labels on the columns and the tracks on the rows
    # Modified by Orion to display the tracks on the columns and the labels on the rows
    #with png(dirpath, basename, num_labels*PNG_WIDTH_PER_PLOT, num_tracks*PNG_HEIGHT_PER_PLOT):
    print >>sys.stderr, "-Making png"
    with png(dirpath, basename, num_tracks*PNG_WIDTH_PER_PLOT, (num_labels+1)*PNG_HEIGHT_PER_PLOT):
        r.plot(r["histogram.precomp"](data = distributions, inseg=use_seg_tracks))
    print >>sys.stderr, "-Making pdf"
    with pdf(dirpath, basename, PDF_HEIGHT, PDF_WIDTH):
        r.plot(r["histogram.precomp"](data = distributions, inseg=use_seg_tracks))

def validate_distributions(segmentation, dirpath, genome, filenames):
    #(segmentation, dirpath, genome) = setup_validator(outdirname, bedfilename, genomedatadir, clobber)
    assert genome is not None

    num_tracks = get_num_tracks(genome)
    num_labels = len(segmentation.labels)    
    num_segmentation_tracks = len(segmentation.tracks)
    num_nonsegmentation_tracks = num_tracks - num_segmentation_tracks


    # generate histogram
    if num_segmentation_tracks > 0:
        # first do the histograms only for the tracks that were used for segmentation
        print >>sys.stderr, " calculating histogram for the tracks used in segmentation"
        histogram = calc_histogram(genome, segmentation, NUM_BINS, 1)
    
        print >>sys.stderr, " saving tab file for the tracks used in segmentation"
        save_tab_distributions(histogram, segmentation.labels, dirpath, 1)
    
        print >>sys.stderr, " plotting distributions for ", num_segmentation_tracks, " tracks"
        plot_distributions(dirpath, num_segmentation_tracks, num_labels, 1)

    if num_nonsegmentation_tracks > 0:
        # next, do the histograms for the tracks that were NOT used for segmentation 
        print >>sys.stderr, " calculating histogram for the tracks NOT used in segmentation"    
        histogram = calc_histogram(genome, segmentation, NUM_BINS, 0)
    
        print >>sys.stderr, " saving tab file for the tracks NOT used in segmentation"
        save_tab_distributions(histogram, segmentation.labels, dirpath, 0)

        print >>sys.stderr, " plotting distributions for ", num_nonsegmentation_tracks, " tracks"
        plot_distributions(dirpath, num_nonsegmentation_tracks, num_labels, 0)
    
    
########################## FREQUENCY VALIDATION #########################
def get_nucleotide_category(nuc, nucs):
# nuc is in integer format
    # I thought using integers directly is faster, but it seems it's even slower
    #int  65  is nuc  A
    #int  67  is nuc  C
    #int  71  is nuc  G
    #int  84  is nuc  T
    #int  97  is nuc  a
    #int  99  is nuc  c
    #int  103  is nuc  g     
    #int  116  is nuc  t
    #if nuc in (65, 84, 97, 116):
        #return 'A|T'
    #elif  nuc in (67, 71, 99, 103):
        #return 'C|G'
    #else:
        #return 'ambig_nucleotide'
    if nuc.tostring().upper() in ('A','T'):
        return nucs[0]
    if nuc.tostring().upper() in ('C','G'):
        return nucs[1]
    return nucs[2]    
                
def get_dinucleotide_category(dinuc1, dinuc2, dinucs):
# dinuc1 and dinuc2 are in integer format
    d1 = dinuc1.tostring().upper()
    d2 = dinuc2.tostring().upper()

    # XXX: this is an overly complex way to do this. better would be:
    # combine the two characters in a string. Use it as a key to a
    # dictionary.
    if ((d1 == 'A' and d2 == 'A') or (d1 == 'T' and d2 == 'T')): return dinucs[0]
    if ((d1 == 'A' and d2 == 'C') or (d1 == 'G' and d2 == 'T')): return dinucs[1]
    if ((d1 == 'A' and d2 == 'G') or (d1 == 'C' and d2 == 'T')): return dinucs[2]
    if  (d1 == 'A' and d2 == 'T'): return dinucs[3]
    if ((d1 == 'C' and d2 == 'A') or (d1 == 'T' and d2 == 'G')): return dinucs[4]
    if ((d1 == 'C' and d2 == 'C') or (d1 == 'G' and d2 == 'G')): return dinucs[5]
    if  (d1 == 'C' and d2 == 'G'): return dinucs[6]
    if ((d1 == 'G' and d2 == 'A') or (d1 == 'T' and d2 == 'C')): return dinucs[7]
    if  (d1 == 'G' and d2 == 'C'): return dinucs[8]
    if  (d1 == 'T' and d2 == 'A'): return dinucs[9]
    return dinucs[10]
          
      
def make_row_freq(label, segmentation_freq):
    row = {}
    
    for field in FIELDNAMES_FREQ:
        if field == "label": 
            row[field] = label
        else:
            if len(segmentation_freq[label][field]) == 0:
                row[field] = "NaN"
            else:
                row[field] = "%.3f" % (sum(segmentation_freq[label][field]) / len(segmentation_freq[label][field]))
    return row

# Implementation started by Mirela on Mar 2, 2009
def validate_frequency(segmentation, dirpath, genome, filenames):
    #(segmentation, dirpath, genome) = setup_validator(outdirname, bedfilename, genomedatadir, clobber)
    assert genome is not None
    
    nuc_categories = FIELDNAMES_FREQ[1:4]
    dinuc_categories = FIELDNAMES_FREQ[4:]
        
    # initialize segmentation_freq
    segmentation_freq = defaultdict(dict)
    labels = segmentation.labels
    for label_key in labels.iterkeys():
        for nuc in nuc_categories:
            segmentation_freq[label_key][nuc] = []
        for dinuc in dinuc_categories:
            segmentation_freq[label_key][dinuc] = []            

    # now count the nucleotide/dinucleotide frequencies in our segmentation
    for chromosome in genome:
        chrom = chromosome.name
        print >>sys.stderr, "  %s" % chrom

        try:
            segments = segmentation.chromosomes[chrom]
        except KeyError:
            print >>sys.stderr, "   skipping: no data"
            continue

        for segment in segments:                    
            seg_start = segment[COL_START]   
            seg_end = segment[COL_END]
            seg_label = segment[COL_LABEL_KEY]
        
            segment_counts = {}
            for nuc in nuc_categories:
                segment_counts[nuc] = 0
            for dinuc in dinuc_categories:
                segment_counts[dinuc] = 0                
            sequence = get_supercontig_splice(chromosome, seg_start, seg_end, "sequence")

            if sequence.shape[0] > 0:
                for nuc in sequence:
                    nuc_category = get_nucleotide_category(nuc, nuc_categories)
                    segment_counts[nuc_category] += 1
                               
                for i in range(len(sequence)-1):
                    dinuc_category = get_dinucleotide_category(sequence[i], sequence[i+1], dinuc_categories)
                    segment_counts[dinuc_category] += 1                               
                               
                # finished this segment, now compute the frequencies
                for nuc in nuc_categories: 
                    segmentation_freq[seg_label][nuc].append(segment_counts[nuc]/(seg_end-seg_start))
                for dinuc in dinuc_categories: 
                    segmentation_freq[seg_label][dinuc].append(segment_counts[dinuc]/(seg_end-seg_start-1))
                        
        if QUICK: break                
    #print segmentation_freq                    
                    
    with tab_saver(dirpath, NAMEBASE_FREQ, FIELDNAMES_FREQ) as saver:
        for label_key in labels.keys():
            row = make_row_freq(label_key, segmentation_freq)
            saver.writerow(row)                           


########################## TSS VALIDATION #########################
def plot_tss(num_tss, labels, dirpath, filename):
    # plot violin plots
    r_source("external.length.R")

    # fix order for iterating through dict; must be consistent
    label_keys = labels.keys()

    # XXXopt: allocating space in advance might be faster
    tss_array = concatenate([num_tss[label_key] for label_key in label_keys])

    # creates an array that has the label repeated as many times as
    # the length
    labels_array = concatenate([[labels[label_key]] * len(num_tss[label_key])
                               for label_key in label_keys])
    # XXX: convert to a factor

    data = r["data.frame"](seg=labels_array, tss=tss_array)

    with png(dirpath, filename):
        r.plot(r["violinplot.tss"](data=data))
    with pdf(dirpath, filename):
        r.plot(r["violinplot.tss"](data=data))
                               
def make_row_tss(label, num_tss, density_tss):
    return {"label": label,
            "num.tss": num_tss,
            "density.tss": "%.3f" % density_tss}

## Parses tss file and returns dict(chromosome->start_index_list)
def get_tss_data(tssfile, zero_index=False):
    tssdata = defaultdict(list)   

    # first fill up tssdata from the information in the tssfile    
    with open(tssfile) as infile:
        for line in infile:
            words = line.split()
            # words[0] is the chromosome, and words[3] is the location
            # ! I have to convert words[3] to an int, otherwise it treats it as string when I compare it
            start = int(words[3])
            if zero_index:
                start -= 1
            tssdata[words[0]].append(start) 
    
    return tssdata

# implemented by Mirela on March 6, 2009
def validate_tss(segmentation, dirpath, genome, filenames):
    #(segmentation, dirpath, genome) = setup_validator(outdirname, bedfilename, genomedatadir, clobber)
    tssfile = filenames['tss_filename']        
    print >>sys.stderr, " Using file", tssfile
    tssdata = get_tss_data(tssfile)
    
    num_tss = defaultdict(list)
    density_tss = defaultdict(list)
    labels = segmentation.labels

    for chromosome_segmentation in segmentation.chromosomes.keys():
        for segment in segmentation.chromosomes[chromosome_segmentation]:
            num = 0
            # now figure out how many of the tss are inside this segment
            # a binary search would probably be much faster, since tss are sorted already
            for tss in tssdata[chromosome_segmentation]:
                # COL_START is inclusive, COL_END is not inclusive
                if segment[COL_START] <= tss and tss < segment[COL_END]:
                    num = num+1    
            num_tss[segment[COL_LABEL_KEY]].append(num)
            density_tss[segment[COL_LABEL_KEY]].append(num*1000/(segment[COL_END]-segment[COL_START]))
            
    with tab_saver(dirpath, NAMEBASE_TSS, FIELDNAMES_TSS) as saver:
        for label_key in labels.keys():
            row = make_row_tss(label_key, sum(num_tss[label_key]), sum(density_tss[label_key]))
            saver.writerow(row)
            
    # in case we want to draw some plots, here's a start
    #plot_tss(num_tss, labels, dirpath, NAMEBASE_TSS)
    #plot_tss(density_tss, labels, dirpath, NAMEBASE_TSS_DENSITY)


########################## OVERLAP VALIDATION #########################
def validate_overlap(segmentation, dirpath, genome):
    #(segmentation, dirpath, genome) = setup_validator(outdirname, bedfilename, genomedatadir, clobber)
    raise NotImplementedError  # XXX


######################## AGGREGATION VALIDATION #######################
## Returns dict: label -> array of counts
## accepts data from dict: chr -> list of [start_index, [end_index])
## inclusive on start_index, not-inclusive on end_index
## indices should be 0-based
def calc_aggregation(genome, segmentation, features, window_size):
    labels = segmentation.labels
    # Initialize arrays
    counts = {}
    for label in labels:
        counts[label] = fill_array(0, 2*window_size)

    for chromosome in genome:
        chrom = chromosome.name
        print >>sys.stderr, "  %s" % chrom
        
        try:
            segments = segmentation.chromosomes[chrom]
        except KeyError:
            print >>sys.stderr, "   skipping: no segmentation data"
            continue

        # Map entire chromosome into a list of labels
        segment_map = map_segments(segments, labels, chromosome.end)

        relevant_features = features[chrom]
        # For each feature, tally segments in window
        for feature in relevant_features:
            # Calculate feature position as [start, end)
            try:  # List of two values
                feature_start = feature[0]
                feature_end = feature[1]
            except TypeError:  # Single value (no list)
                feature_start = feature
                feature_end = feature_start + 1
            except IndexError:  # Single value in list
                feature_end = feature_start + 1

            # Restrict to chromosome
            start = max(feature_start - window_size, 0)
            end = min(feature_end + window_size, segments.shape[0] - 1)
            # Scan window-size before and after feature (but not in)
            # XXX don't ignore segment assignments in feature
            for counti, basei in enumerate(
                    range(feature_start - window_size, feature_start) + 
                    range(feature_end, feature_end + window_size)):
                #print "\rIndices :: count:%5d, base:%10d" % (counti, basei)
                #print(segment_map[basei])
                if segment_map[basei] in labels:
                    #print(segment_map[basei])
                    counts[segment_map[basei]][counti] += 1
                
    return counts

def make_row_aggregation(label, position, count):
    return {"label": label,
            "position": position,
            "count": count}

def save_tab_aggregation(data, dirpath, window_size):
    with tab_saver(dirpath, NAMEBASE_AGGREGATION, FIELDNAMES_AGGREGATION) as saver:
        for label, counts in data.iteritems():
            for position, count in enumerate(counts):
                saver.writerow(make_row_aggregation(label, position - window_size, count))

## Plots aggregation data from dict: label -> array of counts
## Added by Orion
def plot_aggregation(counts):
#     for label, counts in counts.iteritems():
#         print "=== LABEL %s ===" % str(label)
#         for i, v in enumerate(counts):
#             print "%4d: %d" % (i, v)
#     # plot violin plots
#     r_source("external.length.R")

#     # fix order for iterating through dict; must be consistent
#     label_keys = labels.keys()

#     # XXXopt: allocating space in advance might be faster
#     tss_array = concatenate([num_tss[label_key] for label_key in label_keys])

#     # creates an array that has the label repeated as many times as
#     # the length
#     labels_array = concatenate([[labels[label_key]] * len(num_tss[label_key])
#                                for label_key in label_keys])
#     # XXX: convert to a factor

#     data = r["data.frame"](seg=labels_array, tss=tss_array)

#     with png(dirpath, filename):
#         r.plot(r["violinplot.tss"](data=data))
    return

def validate_aggregation(segmentation, dirpath, genome, filenames):
    #(segmentation, dirpath, genome) = setup_validator(outdirname, bedfilename, genomedatadir, clobber)
    tssfile = filenames['tss_filename']
    print >>sys.stderr, " Using file", tssfile
    tssdata = get_tss_data(tssfile, zero_index=True)  # dict(chr->start_index_list)

    # Calculate aggregation data
    window_size = 500
    data = calc_aggregation(genome, segmentation, tssdata, window_size)

    #XXX plot_aggregation(counts)
    save_tab_aggregation(data, dirpath, window_size)


############# GENOME-WIDE VALUE DISTRIBUTION VALIDATION ############
def calc_track_histogram(genome):
    """
    returns a dict

    key: label_key
    val: dict
         key: trackname
         val: [hist, edges]
    """
    
    ranges = calc_ranges(genome)

    # key: trackname
    # val: histogram_func: a function that generates a histogram from data
    #                      with uniform bins within a track
    # For every trackname (one of 5), there's one function that generates histograms
    # Sets the number of bins to be equal to the number of possible values
    histogram_funcs = dict((trackname,
                            partial(histogram,
                                    bins=(math.ceil(track_range[1])-math.floor(track_range[0])),
                                    range=(math.floor(track_range[0]), math.ceil(track_range[1])),
                                    new=True))
                           for trackname, track_range in ranges.iteritems())
    # MA: trackname is one the (5) track names, track_range is (min,max)
    # MA: functools.partial(func[, *args][, **keywords]) Returns a new partial 
    #	object which when called will behave like func called with the positional 
    #	arguments args and keyword arguments keywords.
    
    # return dictionary: see function docstring for specification
    # for every trackname there's a histogram array of the right boundary and frequency
    res = dict((trackname, list(histogram_func(array([]))))
                               for trackname, histogram_func
                               in histogram_funcs.iteritems())

    for chromosome in genome:
        chrom = chromosome.name
        print >>sys.stderr, "  %s" % chrom

        # iterate through each supercontig
        supercontig_num = 0
        for supercontig, continuous in chromosome.itercontinuous():
            print >>sys.stderr, "   %s" % supercontig.name
            
            # iterate through each track
            num_tracks = get_num_tracks(genome)
            track_num = 0
            for trackname, histogram_func in histogram_funcs.iteritems():
                col_index = chromosome.index_continuous(trackname)       
                print >>sys.stderr, "     Track %d/%d: %s" % (track_num, num_tracks, trackname)
                # MA: col_index is the index of the trackname (if 5 tracks, it can be 0, 1, 2, 3 or 4)

                # only reading in here to reduce peak memory usage
                continuous_col = continuous[:, col_index]
                # MA: continuous_col has now the "intensity" (continuous number) from the data track
                #  len(supercontig_map) = len(continuous_col) because they are for the same segment
                
                res_trackname = res[trackname]
                
                # MA: we need to remove the NaN's, otherwise the numpy.histogram function 
                #   gets confused and misses some of the data 
                col_nonan = remove_nans(continuous_col)
                hist, edges = histogram_func(col_nonan)
                # MA: edges is a list containing the left edge of every bin, hist is the frequency for every bin
                # This calls pynum.histogram

                assert(res_trackname[1] == edges).all()
                res_trackname[0] += hist
                track_num += 1

                ## XXX remove the lines of code below
                #if track_num >= 4:
                #    print >>sys.stderr, "EXITING after 8 tracks"
                #    return res

            supercontig_num += 1            

        if QUICK: break
    return res

def validate_track_distributions(segmentation, dirpath, genome, filenames):
    assert genome is not None

    num_tracks = get_num_tracks(genome)

    # generate histogram
    print >>sys.stderr, " calculating histogram of values for each of %d tracks" % num_tracks
    histogram = calc_track_histogram(genome)
    
    print >>sys.stderr, " saving tab file histogram of values for each track"
    save_tab_distributions(histogram, None, dirpath, None, NAMEBASE_TRACK_DISTRIBUTIONS, FIELDNAMES_TRACK_DISTRIBUTIONS)

########################## HTML FUNCTIONS #########################
def txt2html(txtfile, html):
    # if the txtfile exists, write in htmlhandle an html table
    txt = open(txtfile,"r")
    # first read the first line, and write the header
    fields = txt.readline().split()
    print >>html, '<table border="1" cellpadding="4" cellspacing="1"><tr>';
    for f in fields:
        print >>html, '<td style="background-color: rgb(204, 204, 204);">', f, "</td>"
    print >>html, "</tr>"
    for line in txt.readlines():
        print >>html, "<tr>"
        fields = line.split()
        for f in fields: 
            print >>html, "<td>", f, "</td>"        
        print >>html, "</tr>"         
    txt.close()   
    print >>html, "</table>"     
        

def write_html_length(dirpath, outfile):
    tab = "%s/%s.%s" % (dirpath, NAMEBASE_LENGTH, EXT_TAB)
    if os.path.isfile(tab):
        print >>outfile, "<hr><h2>Length statistics</h2>"
        print >>outfile, "<ul>"
        print >>outfile, '<li> Length distribution: [ <a href="lengths.pdf">PDF</a> ] <a href="lengths.png"><img src="lengths.png" width="%d"></a>  ' % THUMB_WIDTH
        print >>outfile, '<li> Summary table: [ <a href="lengths.tab">TAB</a> ]'
        txt2html(tab, outfile)
        print >>outfile, "</ul>"        


def write_html_distributions(dirpath, outfile):
    tab_inseg = "%s/%s_inseg.%s" % (dirpath, NAMEBASE_DISTRIBUTIONS, EXT_TAB)
    tab_notinseg = "%s/%s_notinseg.%s" % (dirpath, NAMEBASE_DISTRIBUTIONS, EXT_TAB)
    inseg = os.path.isfile(tab_inseg)
    notinseg = os.path.isfile(tab_notinseg)

    if inseg or notinseg:
        print >>outfile, "<hr><h2>Distributions of data intensity</h2>"
        print >>outfile, '<ul><li><table border="1" cellpadding="4" cellspacing="1"><tr>'

    if inseg:
        print >>outfile, '<td style="background-color: rgb(204, 204, 204);">Tracks used for segmentation</td>'
    if notinseg:
        print >>outfile, '<td style="background-color: rgb(204, 204, 204);">Tracks NOT used for segmentation</td></tr>'
    if inseg:
        print >>outfile, '<tr><td>[ <a href="distributions_inseg.pdf">PDF</a> ] [ <a href="distributions_inseg.tab">TAB</a> ] </td>'
    if notinseg:
        print >>outfile, '<td>[ <a href="distributions_notinseg.pdf">PDF</a> ] [ <a href="distributions_notinseg.tab">TAB</a> ]</td></tr>'
    if inseg:
        print >>outfile, '<tr><td><a href="distributions_inseg.png"><img src="distributions_inseg.png" width="%s"></a></td>' % THUMB_WIDTH
    if notinseg:
        print >>outfile, '<td><a href="distributions_notinseg.png"><img src="distributions_notinseg.png" width="%s"></a></td></tr>' % THUMB_WIDTH   
    
    if inseg or notinseg:
        print >>outfile, "</table></ul>"  

def write_html_nucleotide(dirpath, outfile):
    tab = "%s/%s.%s" % (dirpath, NAMEBASE_FREQ, EXT_TAB)
    if os.path.isfile(tab):
        print >>outfile, "<hr><h2>Nucleotide and dinucleotide content</h2>"
        print >>outfile, "<ul>"
        print >>outfile, '<li> Mean frequency of each nucleotide and dinucleotide: [ <a href="nucleotide.tab">TAB</a> ]'
        txt2html(tab, outfile)
        print >>outfile, "</ul>"        

def write_html_tss(dirpath, outfile):
    tab = "%s/%s.%s" % (dirpath, NAMEBASE_TSS, EXT_TAB)
    if os.path.isfile(tab):
        print >>outfile, "<hr><h2>Transcription start site (TSS) statistics</h2>"
        print >>outfile, "<ul>"
        print >>outfile, '<li> Number of TSS and TSS density: [ <a href="tss.tab">TAB</a> ]'
        txt2html(tab, outfile)
        print >>outfile, "</ul>" 

def write_html_aggregation(dirpath, outfile):
    tab = "%s/%s.%s" % (dirpath, NAMEBASE_AGGREGATION, EXT_TAB)
    if os.path.isfile(tab):
        print >>outfile, '<hr><h2>Aggregation data: [ <a href="aggregation.tab">TAB</a> ]</h2>' # XXX

# XXX: interleaving long file-length templates with code is not a good
# idea. better would be to use the string.Template() class along with
# data loaded from an external file using pkg_resources.resource_string()

def write_html_header(outfile, bedfilename, genomedatadirname, filenames, segmentation):
    if bedfilename is not None and os.path.isfile(bedfilename):
        time_segmentation = time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime(os.path.getmtime(bedfilename)))
    else:
        time_segmentation = None

    time_validation = time.strftime("%m/%d/%Y %I:%M:%S %p",time.localtime())
    
    print >>outfile, """
            <html>
            <head>
            <title>EvalSeg results</title>
            </head>
            
            <body>
            <h1>Results of EvalSeg (External Validation of Genome Segmentation)</h1>
            <ul>"""
    if segmentation is not None:
        print >>outfile, "<li>Software used to obtain the segmentation: <code>%s</code></li>" % segmentation.segtool

    print >>outfile, "<li>Input files<span style=\"font-weight: bold;\"></span></li>"
    print >>outfile, "<ul>"

    if bedfilename is not None:
        print >>outfile, "<li>Segmentation file: <code>%s</code>, obtained using " % bedfilename

    if segmentation is not None:
        print >>outfile, len(segmentation.tracks), " tracks:</li><ul>"
        for track in segmentation.tracks:
            print >>outfile, "<li><code>%s</code></li>" % track
    
    print >>outfile, """</ul>
                <li>Genome data directory: <code>""", genomedatadirname, """</code></li>
                <li>Other input files</li>
                <ul>
                <li>TSS file: <code>""", filenames['tss_filename'], """</code></li>
                </ul>
            </ul>"""

    if time_segmentation is not None:
        print >>outfile, "<li>Date and time when the segmentation was performed: %s</li>" % time_segmentation
    print >>outfile, "<li>Date and time when the validation was performed: %s</li>" % time_validation
    print >>outfile, "</ul>"

def write_html_footer(outfile):
    print >>outfile, "</body>"
    print >>outfile, "</html>"

def write_html_summary(dirpath, namebase, bedfilename, genomedatadirname, filenames, segmentation):
    with html_writer(dirpath, namebase, bedfilename, genomedatadirname, 
                     filenames, segmentation) as writer:
        write_html_length(dirpath, writer)
        write_html_distributions(dirpath, writer)
        write_html_nucleotide(dirpath, writer)    
        write_html_tss(dirpath, writer)                     
        write_html_aggregation(dirpath, writer)

## A generator for the html writing to allow for 
## selectively writing specific html function output
@contextmanager
def html_writer(dirpath, namebase, bedfilename, genomedatadirname, filenames, segmentation):
    outfilename = make_filename(dirpath, namebase, EXT_HTML)
    with open(outfilename, "w") as outfile:
        write_html_header(outfile, bedfilename, genomedatadirname, filenames, segmentation)
        yield outfile
        write_html_footer(outfile)

    return

########################## MAIN FUNCTIONS #########################
## Loads segmentation, genome, and sets up output directory for validator
## Useful for validate functions to call on startup
def setup_validator(outdirname, bedfilename, genomedatadirname, clobber=False):
    dirpath = path(outdirname)
    if clobber:
        try:
            dirpath.rmtree()
        except OSError, err:
            if err.errno != ENOENT:
                raise
    dirpath.makedirs()

    if bedfilename is None:
        segmentation = None
        print >>sys.stderr, "Unspecified bedfile. Not loading segmentation."
    else:
        print >>sys.stderr, "Loading segmentation from %s" % os.path.basename(bedfilename)
        segmentation = load_segmentation(bedfilename)
        print >>sys.stderr, "Found %d tracks" % len(segmentation.tracks)

    if genomedatadirname:
        genome = Genome(genomedatadirname)
    else:
        genome = none_contextmanager
    r_source("common.R")

    return (segmentation, dirpath, genome)

## main function to handle complete script
## Writes complete HTML summary after running all validators
def validate_external(outdirname, bedfilename, genomedatadirname,
                      validators=[], filenames={}, clobber=False):
    # main function: load input, prepare output directory, and run
    # validators in turn
    (segmentation, dirpath, genome) = setup_validator(outdirname, bedfilename, genomedatadirname, clobber)
    
    with genome:
        for validator in validators:	
            print >>sys.stderr, "Running %s" % validator.func_name
            validator(segmentation, dirpath, genome, filenames)
            
    write_html_summary(dirpath, NAMEBASE_SUMMARY, bedfilename, genomedatadirname, filenames, segmentation)

def parse_options(args):
    from optparse import OptionParser

    usage = "%prog [OPTION]... OUTDIR BEDFILE GENOMEDATADIR"
    version = "%%prog %s" % __version__
    parser = OptionParser(usage=usage, version=version)
    parser.add_option("--clobber", action="store_true",
                      help="Overwrite existing output files if the specified"
                      " directory already exists.")
                      
    parser.add_option("--quick", action="store_true", 
                      dest="quick", default=False,
                      help="Compute values only for one chromosome.")
    parser.add_option("--no-length", action="store_false",
                      dest="length", default=True,
                      help="Do not perform length validation.")
    parser.add_option("--track-distributions", action="store_true",
                      dest="track_distributions", default=False,
                      help="Make a histogram of the value distributions"
                      " over the whole genome for each track, independent"
                      " of segmentation. BEDFILE will be ignored.")
    parser.add_option("--no-distributions", action="store_false",
                      dest="distributions", default=True,
                      help="Do not make histograms of the distributions of"
                      " data values within each state.")
    parser.add_option("--no-frequency", action="store_false",
                      dest="frequency", default=True,
                      help="Do not make a table of nucleotide and dinucleotide"
                      " frequencies.")
    parser.add_option("--no-tss", action="store_false",
                      dest="tss", default=True,
                      help="Do not perform the TSS analysis.")
    parser.add_option("--tss-file", action="store", dest="tss_filename",
                      type="string", default="../../data/Gencode_TSS.gff",
                      help="TSS file in GFF format for the TSS/overlap analyses.")                        
    parser.add_option("--no-overlap", action="store_false",
                      dest="overlap", default=True,
                      help="Do not perform the overlap analysis.")
    parser.add_option("--no-aggregation", action="store_false",
                      dest="aggregation", default=True,
                      help="Do not perform aggregation analysis.")
    parser.add_option("--calc-ranges", action="store_true", 
                      dest="calc_ranges", default=False,
                      help="Calculate ranges for distribution plots from"
                      " segmentation data (slower) instead of using whole"
                      " genome data (default).")

    options, args = parser.parse_args(args)

    if not len(args) == 3:
        parser.print_usage()
        sys.exit(1)

    return options, args

def main(args=sys.argv[1:]):
    options, args = parse_options(args)
    outdirname = args[0]

    if options.track_distributions:
        bedfilename = None
    else:
        bedfilename = args[1]
    
    try:
        genomedatadirname = args[2]
    except IndexError:
        genomedatadirname = None

    validators = []

    # Set up list of validators to run based upon options
    # If performing track distribution validation, ignore all other validations
    if options.track_distributions:
        if genomedatadirname is None:
            print >>sys.stderr, "Missing expected genome data dir"
            sys.exit(1)
        else:
            validators.append(validate_track_distributions)
    else:
        if options.length:
            validators.append(validate_length)		# MA: validate_length is a function name

        if genomedatadirname is not None:
            if options.distributions:
                validators.append(validate_distributions)
            if options.frequency:
                validators.append(validate_frequency)

        if options.tss:
            validators.append(validate_tss)
        if options.overlap:
            validators.append(validate_overlap)
        if options.aggregation:
            validators.append(validate_aggregation)


    filenames = {}
    filenames['tss_filename'] = options.tss_filename

    # Update global flags based upon options
    global QUICK
    global CALC_RANGES
    QUICK = options.quick
    CALC_RANGES = options.calc_ranges

    # Run validators
    return validate_external(outdirname, bedfilename, genomedatadirname, 
                             validators, filenames, options.clobber)

if __name__ == "__main__":
    sys.exit(main())
