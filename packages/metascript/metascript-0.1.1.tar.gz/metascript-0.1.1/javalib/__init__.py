#!/usr/bin/env jython

__version__ = "$Revision: 1.41 $"

import exceptions
import fileinput
import operator
import os
import sys
import types
from compatibility import *

import ensembl
import enstag

import org.ensembl.datamodel

import metatranslation
from metatranslation import Metatranslation

# actually destroys the whole transcript where this occurs
DESTROY_INTRONS_OVERLAPPING_EXONS = 1

FILENAME_NO_SUBINDEX = "%03d/%02d/%s.%s.%s"
FILENAME_SUBINDEX = "%03d/%02d/%s_%03d.%s.%s"

FILENAME_BAD_FEATURE = "bad_features.txt"
INDEX_SPLIT_POINT = 3

_ASSERT_TEXT_CMP_OVERLAP = "compared Metaexons must not overlap"

_PHASE_CODES = ".WXBYDEFZHIJKLMO"
############ =  0123456789ABCDEF
############ =   W W W W W W W W
############ =    XX  XX  XX  XX
############ =      YYYY    YYYY
############ =          ZZZZZZZZ

_PHASESHIFT_LENGTH = 6
_FUZZY_LENGTH = 50
_PHASESHIFT_CODE = "P" # length < PHASESHIFT_LENGTH
_FUZZY_CODE = "Q" # length < FUZZY_LENGTH

MASK_INTRON_5PRIME = 10
MASK_INTRON_3PRIME = 30
INTRON_SIZE_CUTOFF = 1000000

_UNION_ACCUMULATORS = min, max
_INTERSECTION_ACCUMULATORS = max, min

OUTPUT_SPACES = 7

class CantFillGapException(exceptions.ValueError): pass

class FileExistsException(exceptions.Exception): pass
class GeneNotFoundException(exceptions.Exception): pass

class BadFeatureException(exceptions.ValueError): pass

class IncompatibleStrandsException(BadFeatureException): pass

class BadIntronException(BadFeatureException): pass
class IntronContainsExonFromOtherGeneException(BadIntronException): pass
class OversizedIntronException(BadIntronException): pass

def phase_code2string(phase_code):
    phase_bitstring = _PHASE_CODES.index(phase_code)
    return ''.join([".#"[(phase_bitstring & 2**x) > 0] for x in xrange(4)])

def all(seq, pred):
    "Returns 1 if pred(x) is 1 for every element in the sequence"
    return 0 not in map(pred, seq)

def _is_metaexon(obj):
    return isinstance(obj, Metaexon)

class LinearFeature:
    def __init__(self, feature):
        self.driver = feature.driver
        self.location = feature.location

        try:
            self.gene = feature.gene
        except AttributeError:
            pass

    def __cmp__(self, other):
        """
        sorts based on raw chromsomal start, end; not on strand
        """
        LinearFeature.assert_compatible(self, other)

        res = cmp(self.location.start, other.location.start)

        # assert that compared exons do not overlap:
        assert res == cmp(self.location.end, other.location.end), _ASSERT_TEXT_CMP_OVERLAP

        return res # 0 result for pure comparisons

    def __repr__(self):
        return self.__class__.__name__ + self._locrepr()

    def _locrepr(self):
        return ensembl.ensrepr(self.location)

    def _set_phase_bitstring(self, phase):
        self.phase_bitstring = phase_bitstring(phase)

    def _make_location(self, start, end):
        return ensembl.datamodel.Location(self.location.coordinateSystem,
                                          self.location.seqRegionName,
                                          max(1, start), # so it's not < 1
                                          max(1, end),
                                          self.location.strand)

    def get_sequence(self):
        return self.driver.sequenceAdaptor.fetch(self.location).string

    def get_phase_code(self):
        return _PHASE_CODES[self.phase_bitstring]

    def assert_compatible(self, other):
        assert self.driver == other.driver

        self_loc = self.location
        other_loc = other.location

        assert self_loc.coordinateSystem == other_loc.coordinateSystem
        assert self_loc.seqRegionName == other_loc.seqRegionName

        if self_loc.strand != other_loc.strand:
            raise IncompatibleStrandsException

    _get_metascript_sequence = get_sequence

class Metascript(LinearFeature):
    def __init__(self, feature):
        LinearFeature.__init__(self, feature)
        self.metaexons = []
        self.metaintrons = []

        feature.accessionID

        self.dirty = True
        if isinstance(feature, org.ensembl.datamodel.Gene):
            self._init_from_gene(feature)
        elif isinstance(feature, org.ensembl.datamodel.Transcript):
            # will not catch BadFeatureException
            self._init_from_transcript(feature)
        else:
            raise TypeError

        self.sort()

        # this is necessary because of the discrepancy from introns
        # containing exons from other genes
        if DESTROY_INTRONS_OVERLAPPING_EXONS:
            self.location.start = self._current_start
            self.location.end = self._current_end

        self._assert_features()

    def __repr__(self):
        return "Metascript%s" % repr(self._features())

    def _init_from_transcript(self, transcript):
        self.metaexons = [Metaexon(exon) for exon in transcript.exons]
        self.metaintrons = self._make_metaintrons()

        self._current_start = transcript.location.start
        self._current_end = transcript.location.end
        self.dirty = True

    def _init_from_gene(self, gene):
        transcript_uninited = 1
        self.gene = gene

        for transcript in list(gene.transcripts):
            try:
                if transcript_uninited:
                    self._init_from_transcript(transcript)
                    transcript_uninited = 0
                else:
                    new_metascript = Metascript(transcript)
                    self.add_metascript(new_metascript)
            except BadFeatureException:
                pass

        if transcript_uninited: # nothing worked
            raise BadFeatureException

        self.dirty = True

    def assert_compatible(self, feature):
        LinearFeature.assert_compatible(self, feature)
        self.dirty = True

    def _boundaries(self):
        return [self._make_location(point, point)
                for point in [self._current_start-1, self._current_end+1]]

    def _add_if_overlaps(self, metaintron, location, start, end):
        if metaintron.location.overlaps(location):
            new_location = self._make_location(start, end)
            self.metaintrons.append(Intron(new_location,
                                           metaintron.phase_bitstring,
                                           self.driver, self.gene.accessionID))

    def _add_if_overhanging(self, metaintron, boundaries):
        current_start = boundaries[0].start
        current_end = boundaries[1].end

        self._add_if_overlaps(metaintron, boundaries[0],
                              metaintron.location.start,
                              min(metaintron.location.end, current_start))
        self._add_if_overlaps(metaintron, boundaries[1],
                              max(metaintron.location.start, current_end),
                              metaintron.location.end)
        if (metaintron.location.end < current_start
            or metaintron.location.start > current_end):
            self.metaintrons.append(metaintron)

    def _add_if_overhanging_all(self, metaintrons, boundaries):
        for metaintron in metaintrons:
            self._add_if_overhanging(metaintron, boundaries)

    def _add_metaintrons(self, new_metascript, old_metaintrons):
        for new_metaintron in new_metascript.metaintrons:

            for old_metaintron in old_metaintrons:
                if old_metaintron.location.overlaps(new_metaintron.location):
                    self.metaintrons.append(Metaintron([old_metaintron,
                                                        new_metaintron]))

    def add_metascript(self, new_metascript):
        self.assert_compatible(new_metascript)

        for new_metaexon in new_metascript.metaexons:
            self._add_metaexon(new_metaexon)

        old_metaintrons = self.metaintrons
        self.metaintrons = []

        self._add_if_overhanging_all(old_metaintrons,
                                     new_metascript._boundaries())
        self._add_if_overhanging_all(new_metascript.metaintrons,
                                     self._boundaries())

        self._add_metaintrons(new_metascript, old_metaintrons)

        gap_metaintrons = self._gap_metaintrons()
        map(self.metaintrons.append, gap_metaintrons)

        # must be last:
        #self._add_metaintrons(new_metascript, self._gap_metaintrons())

        self._current_start = min(self._current_start,
                                  new_metascript.location.start)
        self._current_end = max(self._current_end, new_metascript.location.end)

        self.dirty = True

    def _features(self):
        res = []
        res.extend(self.metaexons)
        res.extend(self.metaintrons)
        res.sort()
        return res

    def _gap_metaintrons(self):
        """
        fill in gaps
        """
        res = []

        if len(self.metaexons) - 1 == len(self.metaintrons):
            return res

        features = self._features()
        for feature_window in zip(features, features[1:]):
            if feature_window[0].__class__ == feature_window[1].__class__:
                assert all(feature_window, _is_metaexon)

                gap_location = self._make_location(feature_window[0].location.end+1,
                                                   feature_window[1].location.start-1)
                try:
                    gap_filler = GapIntron(gap_location, self.driver,
                                           self.gene.accessionID)
                    res.append(gap_filler)
                except BadFeatureException:
                    raise CantFillGapException

        return res

    def _assert_features(self):
        features = self._features()

        assert self._current_start == self.location.start
        assert self._current_start == features[0].location.start

        assert len(self.metaexons) - 1 == len(self.metaintrons)

        for feature0, feature1 in zip(features, features[1:]):
            assert feature0.location.end+1 == feature1.location.start

        for feature in features:
            if isinstance(feature, GapIntron):
                if DESTROY_INTRONS_OVERLAPPING_EXONS:
                    raise BadIntronException
                else:
                    raise AssertionError, "there shouldn't be gaps if DESTROY_INTRONS_OVERLAPPING_EXONS... is turned off"

        assert self._current_end == features[-1].location.end
        assert self._current_end == self.location.end

    def _add_metaexon(self, new_metaexon):
        self.assert_compatible(new_metaexon)

        overlapping = [new_metaexon]

        old_index = 0
        while old_index < len(self.metaexons):
            old_metaexon = self.metaexons[old_index]

            comparison_start = new_metaexon.location.start-1
            comparison_end = new_metaexon.location.end+1
            comparison_location = self._make_location(comparison_start,
                                                      comparison_end)

            if old_metaexon.location.overlaps(comparison_location):
                overlapping.append(self.metaexons.pop(old_index))
            else:
                old_index += 1

        self.metaexons.append(Metaexon(overlapping))
        self.dirty = True

    def sort(self):
        """
        sorts Metaexons' and Metaintrons' start, end
        (along chromsome, not within gene)
        """
        if True: # self.dirty:
            self.dirty = False
            self.metaexons.sort()
            self.metaintrons.sort()
        else:
            return

    def _get_couplets(self):
        """
        list of exons surrounding each metaintron

        does so in GENE order, not chromosome order
        """
        self.sort()
        if self.location.strand == -1:
            singlets = self.metaexons[::-1], self.metaexons[-2::-1]
            if len(singlets[0]) == len(singlets[1]):
                # special case due to Jython stupidity!
                # different from CPython 2.3
                singlets[1].pop()
        else: # if it is 0, 1
            singlets = self.metaexons, self.metaexons[1:]

        singlets[1].append(None)

        return zip(*singlets)

    def _make_triplets(self):
        make_intervening_metaintron = self._make_intervening_metaintron 

        res = []
        for metaexon0, metaexon1 in self._get_couplets():
            metaintron = make_intervening_metaintron(metaexon0, metaexon1)
            res.append((metaexon0, metaintron, metaexon1))

        return res

    def _make_intervening_metaintron(self, metaexon0, metaexon1):
        if metaexon1 is None:
            return None

        if self.location.strand == -1:
            location_tuple = (metaexon1.location.end+1,
                              metaexon0.location.start-1)
        else:
            location_tuple = (metaexon0.location.end+1,
                              metaexon1.location.start-1)

        return Intron(self._make_location(*location_tuple),
                      metaexon1.phase_bitstring,
                      self.driver, self.gene.accessionID)

    def _make_metaintrons(self):
        res = []

        for metaexon0, metaintron, metaexon1 in self._make_triplets():
            if metaintron is None:
                break
            res.append(metaintron)

        return res

    def get_sequence(self):
        features = self._features()

        if self.location.strand == -1:
            features.reverse()

        return ''.join([feature._get_metascript_sequence()
                        for feature in features])

    def get_connections(self):
        self.sort()
        basis_introns_list = [metaintron.basis_introns
                              for metaintron in self.metaintrons]
        basis_intron_ids_list = [metaintron.basis_intron_ids
                                 for metaintron in self.metaintrons]
        results = [[] for metaintron in self.metaintrons]

        for basis_intron_ids0, result0, index0 in \
                zip(basis_intron_ids_list, results, xrange(len(results))):
            for basis_intron_ids1, result1, index1 in \
                    zip(basis_intron_ids_list[index0+1:],
                        results[index0+1:],
                        xrange(index0+1, len(results))):
                for basis_intron_id1 in basis_intron_ids1:
                    if basis_intron_id1 in basis_intron_ids0:
                        result0.append(index1)
                        result1.append(index0)
                        break

        return results

class CombinableLinearFeature(LinearFeature):
    def __init__(self, features):
        if not isinstance(features, types.ListType):
            raise ValueError
        if len(features) == 1:
            return self.__init__(features[0])
        else:
            self._set_driver(features)
            self._set_location(features)
            self._set_accessionID(features)
            self._set_phase_bitstring(features)
            self.assert_compatible(features)

    def _set_driver(self, features):
        self.driver = features[0].driver

    def _set_location(self, features):
        coord_system = features[0].location.coordinateSystem
        seq_region_name = features[0].location.seqRegionName
        start = self.start_accumulator(map(_feature_start, features))
        end = self.end_accumulator(map(_feature_end, features))
        strand = features[0].location.strand

        self.location = ensembl.datamodel.Location(coord_system,
                                                   seq_region_name, start,
                                                   end, strand)

    def _set_accessionID(self, features):
        self.accessionID = []

        try:
            for feature in features:
                for accessionID in feature.accessionID:
                    if accessionID not in self.accessionID:
                        self.accessionID.append(accessionID)

        except AttributeError:
            pass

    def _set_phase_bitstring(self, features):
        self.phase_bitstring = phase_bitstring(map(_feature_phase_bitstring,
                                                   features))

    def assert_compatible(self, features):
        for feature in features:
            LinearFeature.assert_compatible(self, feature)

class Metaexon(CombinableLinearFeature):
    start_accumulator, end_accumulator = _UNION_ACCUMULATORS

    def __init__(self, source):
        try:
            source.accessionID
        except AttributeError:
            pass

        if isinstance(source, Metaexon):
            LinearFeature.__init__(self, source)
            self.phase_bitstring = source.phase_bitstring
            self.accessionID = source.accessionID
        elif isinstance(source, org.ensembl.datamodel.Exon):
            LinearFeature.__init__(self, source)
            LinearFeature._set_phase_bitstring(self, source.phase)
            self.accessionID = [source.accessionID]
        else:
            CombinableLinearFeature.__init__(self, source)

    def __repr__(self):
        return "+".join(self.accessionID) + LinearFeature._locrepr(self)

class Metaintron(CombinableLinearFeature):
    start_accumulator, end_accumulator = _INTERSECTION_ACCUMULATORS

    def __init__(self, metaintrons):
        self.mask_locs = []
        CombinableLinearFeature.__init__(self, metaintrons)
        self._set_basis_introns(metaintrons)

    def _set_basis_introns(self, metaintrons):
        self.basis_introns = []
        self.basis_intron_ids = []
        self.mask_locs = []

        for metaintron in metaintrons:
            for basis_intron, basis_intron_id in zip(metaintron.basis_introns,
                                                     metaintron.basis_intron_ids):
                if basis_intron_id not in self.basis_intron_ids:
                    self.basis_introns.append(basis_intron)
                    self.basis_intron_ids.append(basis_intron_id)

                    for mask_loc in basis_intron.mask_locs:
                        for compare_mask_loc in self.mask_locs:
                            if mask_loc == compare_mask_loc:
                                break
                        else:
                            self.mask_locs.append(mask_loc)

    def get_phase_code(self):
        if self.location.length < _PHASESHIFT_LENGTH:
            return _PHASESHIFT_CODE
        elif self.location.length < _FUZZY_LENGTH:
            return _FUZZY_CODE
        else:
            return LinearFeature.get_phase_code(self)

    def _mask_sequence(self, seq):
        loc = self.location
        seq_length = len(seq)
        assert loc.strand

        for mask_loc in self.mask_locs:
            if not loc.overlaps(mask_loc):
                continue

            assert mask_loc.coordinateSystem == loc.coordinateSystem
            assert mask_loc.seqRegionName == loc.seqRegionName
            assert mask_loc.strand != 0

            mask_overlap_start = max(loc.start, mask_loc.start)
            mask_overlap_end = min(loc.end, mask_loc.end)

            if loc.strand == 1:
                mask_seq_start = mask_overlap_start - loc.start
                mask_seq_end = mask_overlap_end - loc.start + 1
            else:
                mask_seq_start = loc.end - mask_overlap_end
                mask_seq_end = loc.end - mask_overlap_start + 1

            seq = (seq[:mask_seq_start]
                   + "N" * (mask_seq_end - mask_seq_start)
                   + seq[mask_seq_end:])
            assert seq_length == len(seq)

        return seq

    def get_sequence(self):
        # this is a string not a list because a pseudoexon is so unlikely
        # therefore mutability is unlikely to be needed
        res = CombinableLinearFeature.get_sequence(self)

        if self.mask_locs:
            return self._mask_sequence(res)
        else:
            return res

    _get_metascript_sequence = get_phase_code

class Intron(Metaintron):
    def __init__(self, location, phase_bitstring, driver, gene_ensid):
        if location.length > INTRON_SIZE_CUTOFF:
            raise OversizedIntronException

        self.mask_locs = []

        internal_exons = exons_in_intron(location, driver, gene_ensid)
        if internal_exons:
            # if they are all pseudogenes
            if 0 not in [exon.gene.type == "pseudogene"
                         for exon in internal_exons]:
                self.mask_locs = [exon.location for exon in internal_exons]
            elif DESTROY_INTRONS_OVERLAPPING_EXONS:
                raise IntronContainsExonFromOtherGeneException

        self.location = location
        self.phase_bitstring = phase_bitstring
        self.driver = driver

        self._set_basis_introns()

    def _set_basis_introns(self):
        self.basis_introns = [self]
        self.basis_intron_ids = [id(self)]

class GapIntron(Intron):
    """
    Ensembl genes do not contain gaps so this should not get called
    unless DESTROY_INTRONS_OVERLAPPING_EXONS is 1
    """
    def __init__(self, location, driver, gene_ensid):
        return Intron.__init__(self, location, 0, driver, gene_ensid)

    def _set_basis_introns(self):
        self.basis_introns = []
        self.basis_intron_ids = []

def _feature_start(feature):
    return feature.location.start

def _feature_end(feature):
    return feature.location.end

def _feature_phase(feature):
    return feature.phase

def _feature_phase_bitstring(feature):
    return feature.phase_bitstring

def phase_bitstring(phase):
    try:
        return 2**(phase+1) # -1 => 0x1; 0 => 0x2; 1 => 0x4; 2 => 0x8
    except TypeError:
        return reduce(operator.or_, phase)

def exons_in_intron(location, driver, gene_ensid):
    location = location.copy()
    location.strand = 0

    exons = driver.exonAdaptor.fetch(location)
    return [exon for exon in exons
            if exon.gene.accessionID != gene_ensid]

def split_index(index):
    index_all = "%05d" % index
    return index_all[:INDEX_SPLIT_POINT], index_all[INDEX_SPLIT_POINT:]

def output_filename(gene_enstag, feature_type, index,
                    subindex=None, suffix="fna"):
    index_split = split_index(index)

    if subindex is None:
        return FILENAME_NO_SUBINDEX % (index_split[0], index_split[1],
                                       gene_enstag, feature_type, suffix)
    else:
        return FILENAME_SUBINDEX % (index_split[0], index_split[1],
                                    gene_enstag, subindex, feature_type,
                                    suffix)

def makedirs(filename):
    filename_dir = os.path.split(filename)[0]
    try:
        os.makedirs(filename_dir)
    except OSError:
        pass

def open_output(gene_enstag, feature_type, index, subindex=None, suffix="fna",
                decorators=[], global_options={}):
    filename = output_filename(gene_enstag, feature_type,
                               index, subindex, suffix)
    makedirs(filename)

    if os.path.exists(filename):
        raise FileExistsException, filename

    output = open(filename, "w")

    if decorators:
        pipe = " /%s|" % " /".join(decorators)
    else:
        pipe = "|"

    if subindex is None:
        print >>output, ">%s %s%s%s" % (gene_enstag, feature_type, pipe,
                                        filename)
    else:
        print >>output, ">%s %s %03d%s%s" % (gene_enstag, feature_type,
                                             subindex, pipe, filename)

    return output

def save_output(text, *args, **keywds):
    output = open_output(*args, **keywds)
    print >>output, text
    output.close()

def save_metascript_sequence(index, gene_enstag, metascript, global_options):
    save_output(metascript.get_sequence(), gene_enstag,
                "metascript", index, global_options=global_options)

def save_metatranslation_sequence(index, gene_enstag, gene, global_options):
    try:
        save_output(Metatranslation(gene).get_sequence(), gene_enstag,
                    "metatranslation", index, global_options=global_options)
    except metatranslation.IncompatiblePhaseException:
        print_spaced_out(" # incompatible phase", sys.stderr)

def save_metascript_connections(index, gene_enstag, metascript,
                                global_options):
    output = open(FILENAME_NO_SUBINDEX % (index, "metascript", "map"), "w")
    print >>output, metascript.get_connections()
    output.close()

def save_metascript_metaintrons(index, gene_enstag, metascript,
                                global_options):
    metaintrons = metascript.metaintrons

    if metascript.location.strand == -1:
        metaintrons.reverse()

    for metaintron, subindex in zip(metaintrons, xrange(len(metaintrons))):
        if (metaintron.location.end - metaintron.location.start
            > INTRON_SIZE_CUTOFF):
            continue
        sequence = metaintron.get_sequence()

        if global_options["hardmask"]:
            # sequence is always 5'->3'
            sequence = sequence[MASK_INTRON_5PRIME:-MASK_INTRON_3PRIME]
            decorators = ["hardmask"]
        else:
            decorators = []

        save_output(sequence, gene_enstag, "metaintron", index, subindex,
                    decorators=decorators, global_options=global_options)

def save_translation_peptide(index, gene_enstag, translation, translation_seq,
                             global_options):
    save_output(translation.peptide, gene_enstag, "peptide", index,
                suffix="faa", global_options=global_options)

def save_translation_sequence(index, gene_enstag, translation, translation_seq,
                              global_options):
    save_output(translation_seq.string, gene_enstag, "translation", index,
                global_options=global_options)

def save_translation_exons(index, gene_enstag, translation, translation_seq,
                           global_options):
    for subindex, exon in enumerate_list(list(translation.transcript.exons)):
        save_output(exon.sequence.string, exon.accessionID, "exon", index,
                    subindex, global_options=global_options)

def translation_length(translation):
    return sum([location.length for location in translation.codingLocations])

def save_longest_translation(index, gene, gene_enstag, processors,
                             global_options):
    longest_translation = None
    longest_translation_len = 0
    for transcript in gene.transcripts:
        try:
            Metascript(transcript) # just to throw the exception if needed
        except (BadFeatureException, CantFillGapException):
            continue

        translation = transcript.translation
        translation_len = translation_length(translation)

        if translation_len > longest_translation_len:
            longest_translation = translation
            longest_translation_len = translation_len

    if longest_translation is not None:
        for processor in processors:
            processor(index, gene_enstag, longest_translation,
                      longest_translation.sequence, global_options)

def save_metascript(index, gene, gene_enstag, processors, global_options,
                    bad_feature_filename):
    try:
        metascript = Metascript(gene)
        for processor in processors:
            processor(index, gene_enstag, metascript, global_options)
    except (BadFeatureException, CantFillGapException), e:
        # append so the file is not created unless there is output
        output_bad_features = open(bad_feature_filename, "a")

        # XXX: dump leftover singlets
        # XXX: also dump genes that are wholly within pseudogenes
        bad_filename = output_filename(gene_enstag, "metascript", index)
        bad_feature_data = (bad_filename, e.__class__.__name__)
        print >>output_bad_features, "%s\t%s" % bad_feature_data
        output_bad_features.close()
        # this might mean there is only 0 or 1 metascripts in the directory

def save_gene(index, gene, gene_enstag, processors, global_options):
    for processor in processors:
        processor(index, gene_enstag, gene, global_options)

def init_bad_feature(filename):
    try:
        os.remove(filename)
    except OSError:
        pass

def print_spaced_out(text, outfile=sys.stdout, num_spaces=OUTPUT_SPACES):
    print >>outfile, " " * num_spaces + text

def print_gene_enstag(gene_enstag, first_column):
    if first_column:
        print gene_enstag
    else:
        print_spaced_out(gene_enstag)

def process_column(gene_enstag, line_index, gene_processors,
                   metascript_processors, translation_processors,
                   global_options, bad_feature_filename, first_column):
    print_gene_enstag(gene_enstag, first_column)

    gene = enstag.fetch(gene_enstag)
    if not gene:
        raise GeneNotFoundException

    if gene.type == "pseudogene":
        print_spaced_out(" # pseudogene")
        return

    if gene_processors:
        save_gene(line_index, gene, gene_enstag, gene_processors,
                  global_options)

    if metascript_processors:
        save_metascript(line_index, gene, gene_enstag, metascript_processors,
                        global_options, bad_feature_filename)

    # XXX: metascript should be saved for both of these instead of
    #      generating twice!
    if translation_processors:
        save_longest_translation(line_index, gene, gene_enstag,
                                 translation_processors, global_options)

def process_genes(filename, gene_processors, metascript_processors,
                  translation_processors, global_options, skip,
                  bad_feature_filename):
    line_index = -1
    init_bad_feature(bad_feature_filename)

    for line in file(filename):
        line_index += 1
        if line_index < skip:
            continue

        columns = line.rstrip().split("\t")

        print "%05d " % line_index,
        first_column = 1

        for gene_enstag in columns:
            if gene_enstag != " ":
                try:
                    process_column(gene_enstag, line_index,
                                   gene_processors, metascript_processors,
                                   translation_processors,
                                   global_options, bad_feature_filename,
                                   first_column)
                except FileExistsException, e:
                    text = " # file exists: %s; skipping rest of enstag" % e
                    print_spaced_out(text, sys.stderr)
                except GeneNotFoundException:
                    text = " # gene not found"
                    print_spaced_out(text, sys.stderr)

                first_column = 0

def main():
    pass

if __name__ == "__main__":
    main()
