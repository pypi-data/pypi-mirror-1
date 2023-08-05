import sre_parse, sre_compile, sre_constants
from sre_constants import BRANCH, SUBPATTERN
from sre import VERBOSE, MULTILINE, DOTALL
import re

__all__ = ['Scanner', 'pattern']

FLAGS = (VERBOSE | MULTILINE | DOTALL)
class Scanner(object):
    def __init__(self, lexicon, flags=FLAGS):
        self.actions = [None]
        # combine phrases into a compound pattern
        s = sre_parse.Pattern()
        s.flags = flags
        p = []
        for idx, token in enumerate(lexicon):
            phrase = token.pattern
            try:
                subpattern = sre_parse.SubPattern(s,
                    [(SUBPATTERN, (idx + 1, sre_parse.parse(phrase, flags)))])
            except sre_constants.error:
                print "Can't parse %s" % (token.__name__,)
                raise
            p.append(subpattern)
            self.actions.append(token)

        p = sre_parse.SubPattern(s, [(BRANCH, (None, p))])
        self.scanner = sre_compile.compile(p)


    def iterscan(self, string, dead=None, idx=0, context=None):
        """
        Yield match, end_idx for each match
        """
        match = self.scanner.scanner(string, idx).search
        actions = self.actions
        i, j, k = 0, 0, 0
        end = len(string)
        while True:
            m = match()
            if m is None:
                break
            k, j = m.span()
            if i == j:
                break
            # yield for dead space
            if k != i and dead is not None:
                rval = dead(string, i, k)
                if rval is not None:
                    yield rval, j
            action = actions[m.lastindex]
            if action is not None:
                rval, next_pos = action(m, context)
                if next_pos is not None and next_pos != j:
                    # "fast forward" the scanner
                    j = next_pos
                    match = self.scanner.scanner(string, j).search
                yield rval, j
            i = j
        if i != end and dead is not None:
            rval = dead(string, i, end)
            yield rval, j
            
def pattern(pattern, flags=FLAGS):
    def decorator(fn):
        fn.pattern = pattern
        fn.regex = re.compile(pattern, flags)
        return fn
    return decorator

def InsignificantWhitespace(match, context):
    return None, None
pattern(r'\s+')(InsignificantWhitespace)
