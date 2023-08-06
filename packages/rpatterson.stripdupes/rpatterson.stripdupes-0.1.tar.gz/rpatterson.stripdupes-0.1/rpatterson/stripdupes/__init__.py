"""Strip duplicated sequences of lines."""

import sys
import itertools
import optparse
import logging
import difflib
import re

from rpatterson import listfile

def compile_value(option, opt, value, parser):
    value = re.compile(value)
    setattr(parser.values, option.dest, value)

parser = optparse.OptionParser(description=__doc__)
parser.add_option(
    "-m", "--min", metavar="NUM", default=0.01, type="float",
    help="Minimum length of duplicated sequence.  "
    "If NUM is less than one, use a proportion of the total "
    "number of lines, otherwise NUM is a number of lines.  "
    "[default: %default]")
parser.add_option(
    "-p", "--pattern", metavar="REGEXP", default=re.compile(r'\s+'),
    action="callback", type="string", callback=compile_value,
    help="Regular expression pattern used to normalize strings in "
    "sequences of strings.  The default matches all whitespace.  "
    "Use an empty string to disable.  [default: '\s+']")
parser.add_option(
    "-r", "--repl", metavar="STRING", default=' ',
    help="String to replace matches of pattern with for normalizing "
    "strings in sequences of strings.  [default: '%default']")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('rpatterson.stripdupes')

class ReSubString(str):

    def __new__(self, object_, pattern=parser.defaults['pattern'],
                 repl=parser.defaults['repl'], **kw):
        return super(ReSubString, self).__new__(self, object_, **kw)

    def __init__(self, object_, pattern=parser.defaults['pattern'],
                 repl=parser.defaults['repl'], **kw):
        super(ReSubString, self).__init__(**kw)
        self.sub = pattern.sub(repl, self)

    def __hash__(self):
        return hash(self.sub)

    def __eq__(self, other):
        return self.sub.__eq__(other.sub)

class SeqWrapper(object):

    def __init__(self, seq, factory=ReSubString):
        self.seq = seq
        self.factory = factory

    def __getitem__(self, key):
        return self.factory(self.seq[key])

    def __len__(self):
        return len(self.seq)

class SequenceMatcher(difflib.SequenceMatcher, object):

    def __init__(self, min_=parser.defaults['min'],
                 pattern=parser.defaults['pattern'],
                 repl=parser.defaults['repl'], **kw):
        self.min = min_
        self.pattern = pattern
        self.repl = repl
        super(SequenceMatcher, self).__init__(**kw)

    def set_seq2(self, b):
        if self.pattern:
            b = SeqWrapper(
                b, factory=lambda object_: ReSubString(
                    object_, pattern=self.pattern, repl=self.repl))
        super(SequenceMatcher, self).set_seq2(b)

    def get_matching_blocks(self):
        sorted_ = self.get_sorted_duplicates()
        matches = []
        append = matches.append
        if sorted_:
            logger.info('Finding longest from %s duplicated sequences'
                        % len(sorted_))
        else:
            logger.info('No duplicated sequences found')
        # prefer longest matches, then latter matches
        for k, j in sorted_:
            i = j-k+1
            for match_i, match_j in matches:
                if match_i <= j < match_j:
                    break
            else:
                append((i, j+1))
        return matches

    def get_sorted_duplicates(self):
        if self.min < 1:
            min_ = int(round(len(self.b)*self.min))
        else:
            min_ = int(round(self.min))
        return sorted(
            itertools.imap(tuple, itertools.imap(
                reversed, (
                    item for item in
                    itertools.chain(*itertools.imap(
                        dict.iteritems,
                        self.get_duplicates_by_len().itervalues()))
                    if item[1] >= min_)
                )),
            reverse=True)

    def get_duplicates_by_len(self):
        # optimizations
        islice = itertools.islice
        b, b2j, i2j2k = self.b, self.b2j, {}
        b2j_get = b2j.get
        i2j2k_pop = i2j2k.pop
        b_len = len(b)
        info = logger.info

        default = []
        for i, item in enumerate(b):
            n = i+1
            if n%10000 == 0:
                info('Processing #%s of %s (%s%%)'
                     % (n, b_len, n*100/b_len))
            
            js = b2j_get(item, default)
            if len(js) <= 1:
                continue
            
            # we have at least one match, advance i2j2k
            j2k = i2j2k[i] = i2j2k_pop(i-1, {}) # per i

            # optimizations
            j2k_pop = j2k.pop

            new_j2k = {}
            # the first item is i itself, skip
            for j in islice(js, 1, None):
                # prev is used to avoid doing two dict lookups
                prev = j2k_pop(j-1, default)
                if prev is default:
                    k = 1
                else:
                    k = prev + 1
                if j < i+k:
                    # ignore duplicates that overlap with the first
                    if prev is not default:
                        j2k[j-1] = prev
                    continue
                new_j2k[j] = k
            j2k.update(new_j2k)

        return i2j2k

def omit_ranges(seq, ranges):
    i = 0
    for j, k in ranges:
        yield seq[i:j]
        i = k
    yield seq[i:]

def strip(seq, min_=parser.defaults['min'],
          pattern=parser.defaults['pattern'],
          repl=parser.defaults['repl']):
    matcher = SequenceMatcher(min_=min_, pattern=pattern, repl=repl)
    matcher.set_seq2(seq)
    matches = sorted(matcher.get_matching_blocks())
    if matches:
        logger.info(
            ('Removing the following %s duplicate sequences: '
             % len(matches)) +
            ' '.join(repr(match) for match in matches))
    return itertools.chain(*omit_ranges(seq, matches))

def main(args=None):
    options, args = parser.parse_args(args=args)
    if args:
        parser.error(
            'Does not accept arguments, use standard input and outpt')
    sys.stdout.writelines(
        strip(listfile.ListFile(sys.stdin), options.min))

if __name__ == '__main__':
    main()
