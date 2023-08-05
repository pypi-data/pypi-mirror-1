#!/usr/bin/env python

__version__ = "$Revision: 1.25 $"

import math
import operator
import string
import sys

## Python 2.4 compatability

try:
    dict
except NameError:
    def dict(**keywds):
        return keywds

try:
    False
except NameError:
    False = 0
    True = 1

try:
    sum
except NameError:
    def sum(iterable):
        return reduce(operator.add, iterable)

try:
    enumerate
except NameError:
    def enumerate(seq):
        return zip(xrange(len(seq)), seq)

try:
    floordiv = operator.floordiv
except AttributeError:
    def floordiv(x, y):
        return int(math.floor(x / y))

def reversed(seq):
    res = list(seq)
    res.reverse()
    return res

_ENSTAG_PREFIX = "e"

# should use string.ascii_lowercase but doesn't exist in Python 2.1:
# might be faster to use a dict but who cares?
_BASE36_DIGITS = string.digits + string.lowercase
_BASE36_RADIX = 36

# XXX: change to four letter abbreviations, SINFRU -> NEWSINFRU, abbreviate fly and Aedes stuff anyway
# XXX: handle missing species more gracefully
# XXX: 

_FEATURE_FULLTYPE_NAMES = ["exon", "gene", "peptide", "transcript"]
_FEATURE_VIEW_NAMES = ["exon", "gene", "prot", "trans"]

# in the order listed on www.ensembl.org
_SPECIES_CONF_TEXT = """Hsa	human	Homo_sapiens	ENS
Ptr	chimp	Pan_troglodytes	ENSPTR
Mml	macaque	Macaca_mulatta	ENSMMU
Mmu	mouse	Mus_musculus	ENSMUS
Rno	rat	Rattus_norvegicus	ENSRNO
Ocu	rabbit	Oryctolagus_cuniculus	ENSOCU
Cfa	dog	Canis_familiaris	ENSCAF
Bta	cow	Bos_taurus	ENSBTA
Ssc	pig	Sus_scrofa	
Dno	armadillo	Dasypus_novemcinctus	ENSDNO
Laf	elephant	Loxodonta africana	ENSLAF
Ete	tenrec	Echinops_telfairi	ENSETE
Mdo	opossum	Monodelphis_domestica	ENSMOD
Oan	platypus	Ornithorhynchus_anatinus	
Gga	chicken	Gallus_gallus	ENSGAL
Xtr	x_tropicalis	Xenopus_tropicalis	ENSXET
Dre	zebrafish	Danio_rerio	ENSDAR
Tru,Fru	fugu	Fugu_rubripes	SINFRU
Tni	tetraodon	Tetraodon_nigroviridis	GSTEN
Gac	stickleback	Gasterosteus_aculeatus	ENSGAC
Ola	medaka	Oryzias_latipes	
Cin	c_intestinalis	Ciona_intestinalis	ENSCIN
Csa	c_savignyi	Ciona_savignyi	
Dme	fruitfly	Drosophila_melanogaster	
Aga	anopheles	Anopheles_gambiae	ENSANG
Aae	aedes	Aedes_aegypti	
Ame	honeybee	Apis_mellifera	ENSAPM
Cel	c_elegans	Caenorhabditis_elegans	
Cbr	c_briggsae	Caenorhabditis_briggsae	ENSCBR
Sce	bakers_yeast	Saccharomyces_cerevisiae	
"""
_URL_BASE = "http://www.ensembl.org"

def tag36digit_to_int(place, digit):
    """
    in the tag36 0ABCD the places are:
                 43210

    >>> tag36digit_to_int(0, "0")
    0
    >>> tag36digit_to_int(0, "z")
    35
    >>> tag36digit_to_int(1, "z")
    1260
    """
    return _BASE36_RADIX**place * _BASE36_DIGITS.index(digit)

def tag36_to_int(tag36):
    """
    >>> tag36_to_int("0")
    0
    >>> tag36_to_int("z")
    35
    >>> tag36_to_int("0z0")
    1260
    >>> tag36_to_int("0za")
    1270
    >>> tag36_to_int("1az")
    1691
    """
    return sum(map(tag36digit_to_int, *zip(*enumerate(reversed(tag36)))))

def int_to_tag36(number):
    """
    tag36 format always starts with a decimal digit (even if it is zero)

    >>> int_to_tag36(0)
    '0'
    >>> int_to_tag36(35)
    '0z'
    >>> int_to_tag36(1260)
    '0z0'
    >>> int_to_tag36(1270)
    '0za'
    >>> int_to_tag36(1297)
    '101'
    """

    base36_digits = []
    div = True
    place = 1

    while div:
        div, mod = divmod(number, _BASE36_RADIX**place)
        next_int = floordiv(mod, _BASE36_RADIX**(place-1))
        base36_digits.append(_BASE36_DIGITS[next_int])
        place += 1

    res = "".join(map(str, reversed(base36_digits)))

    if res[0] not in string.digits:
        res = "0" + res
    return res

class Codec: # old-style class so it will work with Jython
    def __init__(self, prefix, key, common_name):
        self.prefix = prefix
        self.key = key[0].upper() + key[1:].lower()
        self.common_name = common_name

    def encode(self, ensid, feature_type=None):
        if feature_type is None:
            raise ValueError, "feature type not specified"

        return "".join([_ENSTAG_PREFIX, feature_type, self.key, "_", ensid])

    def decode(self, enstag):
        assert enstag[5] == "_"
        return enstag[6:]

class Tag36Codec(Codec):
    def encode(self, ensid, feature_type=None):
        try:
            feature_type_index = ensid.index(self.prefix) + len(self.prefix)

            new_feature_type = ensid[feature_type_index].lower()
            assert feature_type is None or new_feature_type == feature_type

            if (new_feature_type is not None
                and new_feature_type not in string.lowercase):
                raise ValueError

            try:
                version_point_index = ensid.rindex(".")
            except ValueError:
                version_point_index = None

            ensid_int = int(ensid[feature_type_index+1:version_point_index])
            tag36 = int_to_tag36(ensid_int)
            genus_letter = self.key[0].upper()
            species_letters = self.key[1:]

            return "".join([_ENSTAG_PREFIX, new_feature_type,
                            genus_letter, species_letters, tag36])
        except ValueError:
            if feature_type is not None:
                return Codec.encode(self, ensid, feature_type)
            else:
                raise

    def decode(self, enstag):
        if enstag[5] == "_":
            return Codec.decode(self, enstag)

        assert enstag[2:5].lower() == self.key.lower()
        feature_type = enstag[1].upper()
        ensid_int = tag36_to_int(enstag[5:])
        return "%s%s%011d" % (self.prefix, feature_type, ensid_int)

def species(enstag):
    return enstag[2:5]

def taxonomic_name(enstag):
    return _taxonomic_names[species(enstag).lower()]

def feature_type(enstag):
    return enstag[1]

def decode(enstag):
    """
    >>> decode("egHsa2zqa")
    'ENSG00000139618'
    >>> decode("egMmu0za")
    'ENSMUSG00000001270'
    >>> decode("egTni_HOXA11")
    'HOXA11'
    >>> decode("egMml66")
    'ENSMMUG00000000222'
    """
    return _codecs[species(enstag).lower()].decode(enstag)

def encode(ensid, species=None, feature_type=None):
    """
    >>> encode("ENSG00000139618")
    'egHsa2zqa'
    >>> encode("ENSG00000139618.1")
    'egHsa2zqa'
    >>> encode("ENSMUSG00000001270")
    'egMmu0za'
    >>> encode("HOXA11", "Tni", "g")
    'egTni_HOXA11'
    >>> encode("ENSMMUG00000000222")
    'egMml66'
    """
    if species is not None:
        return _codecs[species.lower()].encode(ensid, feature_type)

    for codec in _codecs.values():
        try:
            return codec.encode(ensid)
        except (ValueError, NotImplementedError):
            pass

    raise ValueError, ("none of the installed codecs are compatible "
                       "with ensid %s" % ensid)

def taxonomic_name_to_species(taxonomic_name):
    """accepts underscore or space as binomial delimiter"""

    taxonomic_name = taxonomic_name.replace("_", " ")

    # exceptional case!
    if taxonomic_name.lower().startswith("macaca mulatta"):
        return "Mml"

    space0_index = taxonomic_name.index(" ")

    genus_letter = taxonomic_name[0]
    species_letters = taxonomic_name[space0_index+1:space0_index+3]

    return genus_letter.upper() + species_letters.lower()

def feature_species(feature):
    database_name = feature.driver.configuration["database"]
    
    return taxonomic_name_to_species(database_name)

def feature_feature_type(feature):
    from ensembl import datamodel

    if isinstance(feature, datamodel.Gene):
        return "g"
    elif isinstance(feature, datamodel.Transcript):
        return "t"
    elif isinstance(feature, datamodel.Exon):
        return "e"
    elif isinstance(feature, datamodel.Translation):
        return "p"
    else:
        raise ValueError

def encode_feature(feature):
    ensid = feature.accessionID
    species = feature_species(feature)
    feature_type = feature_feature_type(feature)

    return encode(ensid, species, feature_type)

def _url_view(enstag):
    initial = feature_type(enstag)
    feature_view = _feature_views[initial]
    feature_fulltype = feature_fulltypes[initial]

    res_list = [feature_view, "view?", feature_fulltype, "=", decode(enstag)]
    return "".join(res_list)

def url(enstag):
    return "/".join([_URL_BASE, taxonomic_name(enstag), _url_view(enstag)])

def driver(enstag):
    import ensembl

    return ensembl.drivers[_codecs[species(enstag).lower()].common_name]

def adaptor(enstag):
    import ensembl

    return getattr(driver(enstag),
                   ensembl.ENSID_INFIXES[feature_type(enstag).upper()])

def fetch(enstag):
    """
    Jython only for now
    """
    return adaptor(enstag).fetch(decode(enstag))

def main(args):
    for arg in args:
        try:
            print decode(arg)
        except KeyError:
            print encode(arg)

def _init_codecs():
    global _codecs, _taxonomic_names
    _codecs = {}
    _taxonomic_names = {}

    for line in _SPECIES_CONF_TEXT.split("\n"):
        if not line:
            return

        columns = line.split("\t")
        abbreviations_text, common_name, taxonomic_name, prefix = columns
        abbreviations = [text.lower()
                         for text in abbreviations_text.split(",")]
        abbreviation_preferred = abbreviations[0]

        if prefix:
            codec = Tag36Codec(prefix, abbreviation_preferred, common_name)
        else:
            codec = Codec("", abbreviation_preferred, common_name)

        for abbreviation in abbreviations:
            _codecs[abbreviation] = codec
            _taxonomic_names[abbreviation] = taxonomic_name

def _init_unique_initial_dict(dictionary, names):
    for name in names:
        dictionary[name[0]] = name

def _init_feature_fulltypes():
    global feature_fulltypes, _feature_views
    feature_fulltypes = {}
    _feature_views = {}

    _init_unique_initial_dict(feature_fulltypes, _FEATURE_FULLTYPE_NAMES)
    _init_unique_initial_dict(_feature_views, _FEATURE_VIEW_NAMES)

def _test(*args, **keywds):
    import doctest
    doctest.testmod(sys.modules[__name__], *args, **keywds)

_init_codecs()
_init_feature_fulltypes()

if __name__ == "__main__":
    if __debug__:
        _test()
    sys.exit(main(sys.argv[1:]))
