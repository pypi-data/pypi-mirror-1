#!/usr/bin/env python

__version__ = "$Revision: 1.42 $"

import itertools
import os
import random
import re
import sys

from Bio import Wise
from Bio.Wise import psw

from autolog import autolog
import blastdb
from path import path
import poly
import tabdelim
import tools2

from metascript._glob import glob

LOG = autolog()

INTRON_CODES = "PQWXYZBDEFHIJKLMO"
INTRON_CODES_INTERESTING = "WXYZBDEFHIJKLMO"
INTRON_SCORES = "introns_complex.bla"
PENALTY_GAP_START = "23"
PENALTY_GAP_EXTENSION = "5"

NA_EXT = "fna"
MAP_EXT = "map"

CLUSTER_DIRNAME_SPLIT_POINT = 3
CLUSTER_DIRNAME_LENGTH = 5

PATTERN_METASCRIPT_LEAF = "%s/%s" % ("?" * CLUSTER_DIRNAME_SPLIT_POINT, "?" * (CLUSTER_DIRNAME_LENGTH - CLUSTER_DIRNAME_SPLIT_POINT))
PATTERN_GENE = os.extsep.join(["%s/%s/%%s%s.metascript", NA_EXT]) # double % because we don't want it replaced until later
PATTERN_TRANSLATION = os.extsep.join(["%s/%s/?%s.translation", NA_EXT])

def map_file(gene_filename):
    return poly.localfile(gene_filename[:-len(NA_EXT)] + MAP_EXT)

def make_pattern(pattern, cluster_name):
    return pattern % (cluster_name[:CLUSTER_DIRNAME_SPLIT_POINT], cluster_name[CLUSTER_DIRNAME_SPLIT_POINT:], "*")

def make_cluster_names():
    LOG[".make_cluster_names"].debug("start")
    filenames = glob(PATTERN_METASCRIPT_LEAF)
    return sorted(filename.replace("/", "") for filename in filenames)

def light_iterator(filename):
    return tools2.LightIterator(file(filename))

def save_mappings():
    # this was somewhat experimental
    
    import fixme
    raise fixme.Generic, "arguments not passed in correctly"
    
    mappings = [eval(''.join(map_file(gene_filename))) for gene_filename in gene_pair] # XXX: INSECURE

    try:
        introns_zipped_list = zip(*introns)

        for mapping, intron_set, introns_zipped, gene_index in itertools.izip(mappings,
                                                                              itertools.imap(set, introns_zipped_list),
                                                                              introns_zipped_list,
                                                                              itertools.count()):
            introns_zipped = list(introns_zipped)
            for intron_index, mapping_node in enumerate(mapping):
                if not mapping_node or intron_index in intron_set:
                    continue

                distances = [(abs(intron_index-mapping_intron_index), mapping_intron_index)
                             for mapping_intron_index in mapping_node
                             if mapping_intron_index in intron_set
                             if not intron_set.intersection(xrange(min(intron_index+1, mapping_intron_index+1),
                                                                   max(intron_index, mapping_intron_index)))]

                if distances:
                    introns_index = introns_zipped.index(distances[0][1])
                    try:
                        introns[introns_index][gene_index].append(intron_index)
                    except AttributeError:
                        introns[introns_index][gene_index] = [introns[introns_index][gene_index], intron_index]

        for pair in introns:
            for pair_list in pair:
                try:
                    pair_list.sort()
                except AttributeError:
                    pass
    except TypeError:
        pass

def pairup_pair_metascripts(gene_pair, use_mappings):
    """
    align:
    
    seq                  0              1     2          3
     0         ..........W..............Y.....Z..........Y
     1      X............W..............Y.....Z.......
            0            1              2     3

    introns=[(0, 1), (1, 2), (2, 3)]
    """
    print ">>%s %s" % gene_pair
    LOG[".pairup_pair_metascripts"].info("%s %s", *gene_pair)

    gene_pair_local = map(poly.localfilename, gene_pair)

    print >>sys.stderr, "DEBUG cmdline: ", 
    columns = psw.align(gene_pair_local, INTRON_SCORES, PENALTY_GAP_START, PENALTY_GAP_EXTENSION, debug=True)

    seqs = [seq for defline, seq in itertools.chain(*itertools.imap(light_iterator, gene_pair_local))]

    seq_intron_indexes = [[index for index, nucleotide in enumerate(seq)
                           if nucleotide in INTRON_CODES] for seq in seqs]

    introns = []
    interesting = [INTRON_CODES_INTERESTING, INTRON_CODES][options.non_interesting]
    for column_seq_indexes in columns:
        if column_seq_indexes.kind != "SEQUENCE":
            continue

        column_intron_indexes = [intron_indexes.index(column_seq_index)
                                 for seq, column_seq_index, intron_indexes
                                 in itertools.izip(seqs, column_seq_indexes, seq_intron_indexes)
                                 if seq[column_seq_index] in interesting]

        if len(column_intron_indexes) == 2:
            introns.append(column_intron_indexes)

    if use_mappings:
        save_mappings()
        
    print map(tuple, introns)

class NotEnoughIntronsException(Exception):
    """
    also includes where the Metascript is not defined -- certainly not enough introns ;-)
    """
    pass

def random_pair_metascripts(gene_pair):
    # XXX: duplicate code!!!! Yuck!
    
    print ">>%s %s" % gene_pair
    LOG[".random_pair_metascripts"].info("%s %s", *gene_pair)

    gene_pair_local = map(poly.localfilename, gene_pair)

    seqs = [seq for defline, seq in itertools.chain(*itertools.imap(light_iterator, gene_pair_local))]

    seq_intron_indexes = [[index for index, nucleotide in enumerate(seq)
                           if nucleotide in INTRON_CODES] for seq in seqs]

    if [] in seq_intron_indexes:
        raise NotEnoughIntronsException

    intron = [random.choice([intron_index for intron_index, seq_index in enumerate(seq_intron_indexes_side)])
              for seq_intron_indexes_side in seq_intron_indexes]

    print [tuple(intron)]

def cluster_gene_glob(cluster_name, prefix="?"):
    return map(path, glob(make_pattern(PATTERN_GENE, cluster_name) % prefix))

def is_rejected(pair, reject):
    return pair in reject

def is_accepted(pair, accept):
    if not accept:
        return True

    # filepath.name gets the path without the directory, the rest gets rid of two extensions
    return tuple(filepath.name.split(os.extsep)[0] for filepath in pair) in accept

def pairup_cluster_metascripts(cluster_name, accept, reject, use_mappings):
    sys.stdout.flush()
    print ">>>%s" % cluster_name

    for gene_pair in Wise.all_pairs(cluster_gene_glob(cluster_name)):
        if is_accepted(gene_pair, accept) and not is_rejected(gene_pair, reject):
            pairup_pair_metascripts(gene_pair, use_mappings)

def random_gene(cluster_name, prefix="?"):
    genes = cluster_gene_glob(cluster_name, prefix)
    if genes:
        return random.choice(genes)
    else:
        raise NotEnoughIntronsException

def random_cluster_metascripts(*cluster_names):
    sys.stdout.flush()
    print ">>>%s/%s" % tuple(cluster_names)

    gene_pair = tuple(map(random_gene, cluster_names, options.random_prefixes))
    
    random_pair_metascripts(gene_pair)

def load_accept(filename):
    res = set()

    if not filename:
        return res
    
    for row in tabdelim.ListReader(file(filename)):
        res.add((row[0], row[1]))
        res.add((row[1], row[0]))

    return res

re_pair = re.compile(r"^>>([^> ]+) ([^> ]+)$")
def load_reject(filename):
    """
    Eliminate duplication
    """
    res = set()

    if not filename:
        return res

    try:
        infile = poly.localfile(filename)
    except TypeError:
        return res
    
    for line in tools2.irstrip(infile):
        print line
        try:
            pair = re_pair.match(line).groups()
            res.add(pair)
            res.add(tuple(reversed(pair)))
        except AttributeError: # no match
            pass
        
    return res

def get_cluster_translations(cluster_name):
    for gene_pair in Wise.all_pairs(glob(make_pattern(PATTERN_TRANSLATION, cluster_name))):
        yield gene_pair

def get_cluster_names():
    res = poly.superglobal("cluster_names", make_cluster_names)
    LOG[".get_cluster_names.n_clusters"].debug(len(res))
    return res

def get_all_translation_pairs(accept=set(), reject=set(), skip=0):
    cluster_names = get_cluster_names()

    res = []
    for cluster_name in poly.chunk(cluster_names[skip:]):
        # efficient place for poly sectioning point, shared files among groups
        for pair in get_cluster_translations(cluster_name):
            res.append(pair)

    return res

def save_all_metascript_pairs(accept=set(), reject=set(), skip=0, use_mappings=None):
    cluster_names = get_cluster_names()
    
    for cluster_name in poly.chunk(cluster_names[skip:]):
        # efficient place for poly sectioning point, shared files among groups
        pairup_cluster_metascripts(cluster_name, accept, reject, use_mappings)

def save_random_metascript_pairs(count):
    cluster_names = poly.superglobal("cluster_names", make_cluster_names)
    LOG[".save_random_metascript_pairs.n_clusters"].debug(len(cluster_names))

    for i in xrange(count):
        while True:
            try:
                random_cluster_names = map(random.choice, [cluster_names, cluster_names])
                random_cluster_metascripts(*random_cluster_names)
                break
            except NotEnoughIntronsException:
                LOG[".save_random_metascript_pairs.NotEnoughIntronsException"].info("repeating")
                pass

def pairup(random, accept_filename, reject_filename, skip, use_mappings):
    if random:
        save_random_metascript_pairs(random)
    else:
        save_all_metascript_pairs(load_accept(accept_filename),
                                  load_reject(reject_filename),
                                  skip,
                                  use_mappings)
        
    # order of operation:        #
    ##############################
    # save_all_metascript_pairs  #
    # pairup_cluster_metascripts #
    # pairup_pair_metascripts    #

def parse_options(args):
    from optparse import OptionParser

    global options

    usage = "%prog [OPTION]..."
    version = "%%prog %s" % __version__
    parser = OptionParser(usage=usage, version=version)
    parser.add_option("-A", "--accept", dest="accept_filename",
                      help="file is get_homolog_pairs.py output",
                      metavar="ACCEPT")
    parser.add_option("-R", "--reject", dest="reject_filename",
                      help="file is previous output", metavar="REJECT")
    parser.add_option("-i", "--include-non-interesting-introns",
                      action="store_true", dest="non_interesting",
                      default=False)
    parser.add_option("-m", "--use-mappings", action="store_true")
    parser.add_option("-r", "--random", type=int)
    parser.add_option("", "--random-prefixes", default="??",
                      metavar="PREFIXES")
    parser.add_option("-s", "--skip", type=int, default=0)
    
    options, args = parser.parse_args(args)

    return args

def main(args):
    args = parse_options(args)

    pairup(options.random, options.accept_filename, options.reject_filename, options.skip, options.use_mappings)

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
