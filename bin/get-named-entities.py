# -*- coding: utf-8 *-*
from solr import SolrConnection, SolrPaginator
from optparse import OptionParser
from collections import defaultdict
import logging
import nltk
from nltk.sem import relextract
import operator
import re
import sys

"""
Identifies named entities from the text stored in Solr

Setup code appreciatively borrowed from
https://github.com/john-kurkowski/Kilgore-Trout/blob/master/kilgoretrout/extract.py
Which means this code walked barefoot from Cohoes, NY all the way to your door.
"""

LOG = logging.getLogger(__name__)

NE_TYPES = (
    "ORGANIZATION",  # Georgia-Pacific Corp., WHO
    "PERSON",        # Eddy Bonte, President Obama
    "LOCATION",      # Murray River, Mount Everest
    "DATE",          # June, 2008-06-29
    "TIME",         # two fifty a m, 1:30 p.m.
    "MONEY",	        # 175 million Canadian Dollars, GBP 10.40
    "PERCENT",       # twenty pct, 18.75 %
    "FACILITY",      # Washington Monument, Stonehenge
    "GPE",           # South East Asia, Midlothian
)

def is_single_item(item):
    return not hasattr(item, "__iter__")


def iter_nodes(tree):
    for elem in tree:
        try:
            yield elem.node
        except AttributeError:
            pass

class NECorpus:
    def __init__(self, text):
        self._sents = self.tokenize_sentences(text)
        self._sents = self.tokenize_words(self._sents)
        self._sents = self.tag_nes(self._sents)
        self._postprocess()


    def tokenize_sentences(cls, text):
        tokenizer_url = 'nltk:tokenizers/punkt/english.pickle'
        sentence_tokenizer = nltk.data.load(tokenizer_url)
        sents = sentence_tokenizer.tokenize(text)
        return sents


    def tokenize_words(cls, sents):
        word_tokenizer = nltk.tokenize.treebank.TreebankWordTokenizer()
        tokenized_sents = [word_tokenizer.tokenize(sent) for sent in sents]
        return tokenized_sents


    def tag_nes(cls, tokenized_sents):
        tagger_url = 'nltk:taggers/maxent_treebank_pos_tagger/english.pickle'
        tagger = nltk.data.load(tagger_url)
        tagged = tagger.batch_tag(tokenized_sents)

        ne_chunker_url = 'nltk:chunkers/maxent_ne_chunker/english_ace_multiclass.pickle'
        ne_chunker = nltk.data.load(ne_chunker_url)
        nes = ne_chunker.batch_parse(tagged)
        return nes


    def _postprocess(self):
        """Perform postprocessing techniques to increase accuracy and recall."""
        # normalize choices of NE throughout the text, e.g. if "Billy Flannigan"
        # is usually a PERSON, make him always a PERSON
        def symbolize(tree):
            return '_'.join(word.lower() for word, tag in tree.leaves())

        nes = self.nes()

        counts = defaultdict(lambda: defaultdict(int))
        for sentence_no, ne in nes:
            sym = symbolize(ne)
            choice = ne.node
            counts[sym][choice] += 1

        normalized = dict()
        for sym, choices in counts.iteritems():
            if len(choices) < 2:
                continue

            choice, _ = max(choices.iteritems(), key=operator.itemgetter(1))
            normalized[sym] = choice
            LOG.debug("Normalizing NE '%s' from choices %s => %s" % (sym, choices.items(), choice))

        for sentence_no, ne in nes:
            sym = symbolize(ne)
            ne.node = normalized.get(sym, ne.node)


    def rejoin_sent(cls, tree):
        return ' '.join(word for word, tag in tree.leaves())


    def sents(self):
        """Get the sentences as split by this corpus. Note the original text
        is not saved, so rejoining the tokenized version may have slight
        differences.

        >>> text = 'The Project Gutenberg EBook of Ulysses, by James Joyce. Use this with care.'
        >>> corpus = NECorpus(text)
        >>> corpus.sents()
        ['The Project Gutenberg EBook of Ulysses , by James Joyce .', 'Use this with care .']
        """
        return [self.rejoin_sent(sent) for sent in self._sents]


    def parsed_sents(self):
        """Get sentences as parsed, tokenized, and tagged by this corpus."""
        return self._sents


    def nes(self, nes=NE_TYPES):
        """Get all NEs of the specified types in the text, or every NE if
        not specified, and the sentence they occur in."""
        if is_single_item(nes):
            nes = [nes]
        nes = set(nes)
        result = []
        for index, sent in enumerate(self._sents):
            for elem in sent:
                try:
                    if elem.node in nes:
                        result.append((index, elem))
                except AttributeError:
                    pass

        return result


    def ne_sents(self, nes=NE_TYPES, match_all=False):
        """Get sentences containing any of the specified NEs, or any NE if not specified.

        >>> text = 'The Project Gutenberg EBook of Ulysses, by James Joyce. Use this with care.'
        >>> corpus = NECorpus(text)
        >>> corpus.ne_sents('PERSON')
        ['The Project Gutenberg EBook of Ulysses , by James Joyce .']
        """
        return [self.rejoin_sent(sent) for sent in self.ne_parsed_sents(nes, match_all)]


    def ne_parsed_sents(self, nes=NE_TYPES, match_all=False):
        """Get parsed sentences containing any of the specified NEs, or any NE if not specified."""
        if is_single_item(nes):
            nes = [nes]
        nes = set(nes)
        filterfn = self._contains_all_nodes if match_all else self._contains_any_node
        return [sent for sent in self._sents if filterfn(sent, nes)]


    def _contains_all_nodes(cls, tree, nodes):
        nes = set(iter_nodes(tree))
        return nodes.issuperset(nes)


    def _contains_any_node(cls, tree, nodes):
        nes = set(iter_nodes(tree))
        return nodes.intersection(nes)


    def extract_rels(self, subj, obj):
        """Extract relationships of the given named entity subj and obj
        type."""
        return self._naive_extract(subj, obj)


    def _naive_extract(self, subj, obj):
        """Get sentences containing both subj and obj named entities."""
        # Duplicating self.ne_parsed_sents([subj, obj]) ...
        cond = set((subj, obj))
        result = []
        for index, sent in enumerate(self._sents):
            nes = [elem for elem in sent if hasattr(elem, 'node')]
            nodes = set(elem.node for elem in nes)
            if cond.issubset(nodes):
                matching_nes = [elem for elem in nes if elem.node in cond]
                result.append((index, matching_nes))

        return result


    def _nltk_extract(self, subj, obj):
        """Use NLTK's built-in relationship extractor to get subj and obj
        named entity relationships and context."""
        re_location = re.compile(".*")
        result = []
        for sent in self._sents:
            extraction = relextract.extract_rels(
                subj,
                obj,
                sent,
                pattern=re_location,
            )

            if extraction:
                result.append(extraction)

        return result

"""
Start of actual Wikia code
"""

parser = OptionParser()
parser.add_option("-w", "--wiki", dest="wiki", action="store", default=None,
                  help="Specifies the wiki to perform calculations against")
parser.add_option("-l", "--limit", dest="limit", action="store", default=None,
                  help="Specifies the document size of the calculation set")

(options, args) = parser.parse_args()

if not options.wiki:
    raise Exception('A wiki is required, passed as host name')

conn = SolrConnection('http://search-s10.prod.wikia.net:8983/solr')

ne = []

query = ["host:'%s'" % (options.wiki), 'ns:0']

response = conn.query(' AND '.join(query), fields=['html_en','nolang_txt','html'], sort='backlinks desc', limit=100)
paginator = SolrPaginator(response)

for page in paginator.page_range:
    for doc in paginator.page(page).object_list:
        try:
            text = doc.get('html_en', doc.get('nolang_txt', doc.get('html')))
            corpus = NECorpus(text)
            print corpus.nes()
        except UnicodeEncodeError:
            pass
