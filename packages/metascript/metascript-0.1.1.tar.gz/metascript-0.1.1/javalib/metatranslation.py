#!/usr/bin/env jython

from __future__ import nested_scopes

__version__ = "$Revision: 1.6 $"

import sys

import java
from org.ensembl.datamodel import Location

import ensembl

from compatibility import *

class IncompatiblePhaseException(ValueError):
    def __init__(self, specified, calculated):
        self.specified = specified
        self.calculated = calculated

    def __str__(self):
        return "specified=%s; calculated=%s" % (self.specified, self.calculated)

class CodingFeature:
    def __init__(self, location, phase=None, endPhase=None, driver=None, constituitive=1, debuginfo=""):
        self.location = location.clone()

        self._set_phases(phase, endPhase)
        
        self.driver = driver
        self.constituitive = constituitive
        self.debuginfo = debuginfo

    def _set_phases(self, phase, endPhase):
        self.phase = phase
        self.endPhase = (phase + self.location.length) % 3
        if endPhase is not None and endPhase != self.endPhase:
            #print >>sys.stderr, "failure in: %s" % self
            #print >>sys.stderr, "length: %s" % self.location.length
            raise IncompatiblePhaseException, (endPhase, self.endPhase)

    def __cmp__(self, other):
        return self.location.compareTo(other.location)

    def __repr__(self):
        return ensembl.ensrepr(self.location)

    def overlaps(self, other):
        return self.location.overlaps(other.location)

    def get_sequence(self):
        seq = self.driver.sequenceAdaptor.fetch(self.location).string

        if self.constituitive:
            return seq # uppercase
        else:
            return seq.lower()        

def _append_non_overlapping_feature(src, dst):
    feature = src[0]
    feature.constituitive = 0
    
    dst.append(feature)
    #print >>sys.stderr, "%s _append_non_overlapping_feature (%s, %s)" % (feature, feature.phase, feature.endPhase)
    del src[0]

class _Boundary:
    def __init__(self, position, feature, src):
        self.position = position
        self.feature = feature
        self.src = src

    def tuple(self):
        return (self.position, self.feature, self.src)

    def __cmp__(self, other):
        return cmp(self.tuple(), other.tuple())

class Metatranslation:
    def __init__(self, gene):
        self.gene = gene
        self.coding_features = self._get_coding_features() # these are in chromosomal order

    def _get_coding_features(self):
        #print >>sys.stderr, "\n".join(["*" * 80] * 5)

        strand = self.gene.location.strand
        transcript = self.gene.transcripts[0]
        #print >>sys.stderr, transcript.accessionID
        old_features = self._coding_features(transcript)

        if len(self.gene.transcripts) == 1:
            return old_features

        for transcript in list(self.gene.transcripts)[1:]:
            current_features = self._coding_features(transcript)
            new_features = []

            #print >>sys.stderr, "-----"
            #print >>sys.stderr, "old: %s" % old_features
            #print >>sys.stderr, "%s: %s" % (transcript.accessionID, current_features) 
            #print >>sys.stderr, "-"

            while current_features and old_features:
                current_feature = current_features[0]
                old_feature = old_features[0]

                current_loc = current_feature.location
                old_loc = old_feature.location

                try:
                    if current_loc.start > old_loc.end:
                        _append_non_overlapping_feature(old_features, new_features)
                        continue

                    if old_loc.start > current_loc.end:
                        _append_non_overlapping_feature(current_features, new_features)
                        continue

                    assert current_feature.overlaps(old_feature)

                    starts = [_Boundary(old_loc.start, old_feature, old_features),
                              _Boundary(current_loc.start, current_feature, current_features)]

                    ends = [_Boundary(old_loc.end, old_feature, old_features),
                            _Boundary(current_loc.end, current_feature, current_features)]

                    del old_features[0]
                    del current_features[0]

                    first = min(starts), max(starts)
                    combine_boundaries(first, left=1, strand=strand)

                    last = min(ends), max(ends)
                    combine_boundaries(last, right=1, strand=strand)

                    overlap = max(starts), min(ends)
                    combine_overlap(overlap, strand, new_features)
                except IncompatiblePhaseException:
                    #print >>sys.stderr, "failed at %s/%s" % (current_feature, old_feature)
                    #print >>sys.stderr, "old_feature: (%s, %s)" % (old_feature.phase, old_feature.endPhase)
                    #print >>sys.stderr, "current_feature: (%s, %s)" % (current_feature.phase, current_feature.endPhase)
                    raise

            #print >>sys.stderr, "   -"
            #print >>sys.stderr, old_features
            #print >>sys.stderr, current_features
            for feature in old_features + current_features: 
                feature.constituitive = 0
                #print >>sys.stderr, "%s %s leftover (%s, %s)" % (feature, feature.debuginfo, feature.phase, feature.endPhase)
                new_features.append(feature)

            new_features.sort()
            old_features = new_features

        for feature_index, feature in enumerate_list(new_features):
            if feature_index > 0:
                if strand == 1:
                    endPhase = new_features[feature_index-1].endPhase
                    phase = feature.phase
                elif strand == -1:
                    endPhase = feature.endPhase
                    phase = new_features[feature_index-1].phase
                    
                #print >>sys.stderr, (endPhase, phase)
                if endPhase != phase:
                    #print >>sys.stderr, (new_features[feature_index-1].debuginfo, feature.debuginfo)
                    raise IncompatiblePhaseException, (endPhase, phase)
            
            for feature_compare in new_features[feature_index+1:]:
                ##print >>sys.stderr, feature, feature_compare
                assert not feature.overlaps(feature_compare)
                assert cmp(feature, feature_compare) == -1
        
        return new_features

    def _coding_features(self, transcript):
        res = []

        last_coding_feature = None

        for coding_loc in transcript.translation.codingLocations:
            if last_coding_feature is None:
                phase = 0
            else:
                phase = last_coding_feature.endPhase

            last_coding_feature = CodingFeature(coding_loc, phase, 
                                                driver=self.gene.driver,
                                                debuginfo=transcript.accessionID)
            res.append(last_coding_feature)

        res.sort() # get them in chromosomal order
        return res

    def __repr__(self):
        return "<Metatranslation %s>" % repr(self.coding_features)

    def get_sequence(self):
        features = self.coding_features[:]
        if self.gene.location.strand == -1:
            features.reverse()

        return "".join([feature.get_sequence() for feature in features])

def upstream_downstream(boundaries, strand):
    assert strand != 0
    upstream = boundaries[int(strand < 0)]
    downstream = boundaries[int(strand > 0)]

    return upstream, downstream

def combine_boundaries(boundaries, left=0, right=0, strand=None):
    if boundaries[0].position == boundaries[1].position:
        return

    assert not (left and right)
    side = [left, right].index(1) # throws exception if nothing is set
    location = boundaries[side].feature.location.clone()

    if left:
        location.end = boundaries[1].feature.location.start - 1
    if right:
        location.start = boundaries[0].feature.location.end + 1

    phase_side = ["phase", "endPhase"][side]

    upstream, downstream = upstream_downstream(boundaries, strand)
    
    phase = getattr(upstream.feature, phase_side)
    endPhase = getattr(downstream.feature, phase_side)

    new_feature = CodingFeature(location,
                                phase=phase,
                                endPhase=endPhase,
                                driver=upstream.feature.driver,
                                constituitive=0, debuginfo="+")
    boundaries[side].src.insert(0, new_feature)
    #print >>sys.stderr, "  %s, side=%s" % (new_feature, side)

def combine_overlap(boundaries, strand, new_features):
    location = boundaries[0].feature.location.clone()
    location.start = boundaries[0].feature.location.start
    location.end = boundaries[1].feature.location.end
    
    upstream, downstream = upstream_downstream(boundaries, strand)
    
    phase = upstream.feature.phase
    endPhase = downstream.feature.endPhase
    
    new_feature = CodingFeature(location,
                                phase=phase,
                                endPhase=endPhase,
                                driver=boundaries[0].feature.driver,
                                constituitive=min(boundaries[0].feature.constituitive,
                                                  boundaries[1].feature.constituitive),
                                debuginfo=3)
    #print >>sys.stderr, "%s overlap (%s, %s)" % (new_feature, new_feature.phase, new_feature.endPhase)
    new_features.append(new_feature)

def main(args):
    for gene in ensembl.human.all_genes():
        if len(gene.transcripts) <= 1 or gene.type == "pseudogene":
            continue

        #print gene.accessionID
        try:
            #print Metatranslation(gene)
            if gene.location.strand == -1:
                raw_input()
        except IncompatiblePhaseException, ipe:
            #print "IPE: %s" % ipe
            if gene.location.strand == -1:
                raw_input()

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
