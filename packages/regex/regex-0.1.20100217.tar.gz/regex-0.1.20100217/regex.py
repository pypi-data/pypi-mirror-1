#
# Secret Labs' Regular Expression Engine
#
# Copyright (c) 1998-2001 by Secret Labs AB.  All rights reserved.
#
# This version of the SRE library can be redistributed under CNRI's
# Python 1.6 license.  For any other use, please contact Secret Labs
# AB (info@pythonware.com).
#
# Portions of this engine have been developed in cooperation with
# CNRI.  Hewlett-Packard provided funding for 1.6 integration and
# other compatibility work.
#
# 2010-01-16 mrab Python front-end re-written as a single module

r"""Support for regular expressions (RE).

This module provides regular expression matching operations similar to
those found in Perl.  It supports both 8-bit and Unicode strings; both
the pattern and the strings being processed can contain null bytes and
characters outside the US ASCII range.

Regular expressions can contain both special and ordinary characters.
Most ordinary characters, like "A", "a", or "0", are the simplest
regular expressions; they simply match themselves.  You can
concatenate ordinary characters, so last matches the string 'last'.

The special characters are:
    "."                Matches any character except a newline.
    "^"                Matches the start of the string.
    "$"                Matches the end of the string or just before the newline
                       at the end of the string.
    "*"                Matches 0 or more (greedy) repetitions of the preceding
                       RE. Greedy means that it will match as many repetitions
                       as possible.
    "+"                Matches 1 or more (greedy) repetitions of the preceding
                       RE.
    "?"                Matches 0 or 1 (greedy) of the preceding RE.
    *?,+?,??           Non-greedy versions of the previous three special
                       characters.
    *+,++,?+           Possessive versions of the previous three special
                       characters.
    {m,n}              Matches from m to n repetitions of the preceding RE.
    {m,n}?             Non-greedy version of the above.
    {m,n}+             Possessive version of the above.
    "\\"               Either escapes special characters or signals a special
                       sequence.
    []                 Indicates a set of characters. A "^" as the first
                       character indicates a complementing set.
    "|"                A|B, creates an RE that will match either A or B.
    (...)              Matches the RE inside the parentheses. The contents are
                       captured and can be retrieved or matched later in the
                       string.
    (?flags-flags)     Sets/clears the flags for the remainder of the RE (see
                       below).
    (?:...)            Non-capturing version of regular parentheses.
    (?flags-flags:...) Non-capturing version of regular parentheses with local
                       flags.
    (?P<name>...)      The substring matched by the group is accessible by name.
    (?<name>...)       The substring matched by the group is accessible by name.
    (?P=name)          Matches the text matched earlier by the group named name.
    (?#...)            A comment; ignored.
    (?=...)            Matches if ... matches next, but doesn't consume the
                       string.
    (?!...)            Matches if ... doesn't match next.
    (?<=...)           Matches if preceded by ... (must be fixed length).
    (?<!...)           Matches if not preceded by ... (must be fixed length).
    (?(id)yes|no)      Matches yes pattern if group id matched, the (optional)
                       no pattern otherwise.

The special sequences consist of "\\" and a character from the list
below.  If the ordinary character is not on the list, then the
resulting RE will match the second character.
    \number  Matches the contents of the group of the same number.
    \A       Matches only at the start of the string.
    \b       Matches the empty string, but only at the start or end of a word.
    \B       Matches the empty string, but not at the start or end of a word.
    \d       Matches any decimal digit; equivalent to the set [0-9] when
             matching a bytestring or a Unicode string with the ASCII flag, or
             the whole range of Unicode digits when matching a Unicode string.
    \D       Matches any non-digit character; equivalent to [^\d].
    \f       Matches the formfeed character.
    \g<name> Matches the text matched by the group named name.
    \G       Matches the empty string, but only at the position where the search
             started.
    \n       Matches the newline character.
    \N{name} Matches the named character.
    \p{name} Matches the character if it has the specified property.
    \P{name} Matches the complement of \p<name>.
    \r       Matches the carriage-return character.
    \s       Matches any whitespace character; equivalent to [ \t\n\r\f\v].
    \S       Matches any non-whitespace character; equivalent to [^\s].
    \t       Matches the tab character.
    \uXXXX   Matches the Unicode codepoint with 4-digit hex code XXXX.
    \v       Matches the vertical tab character.
    \w       Matches any alphanumeric character; equivalent to [a-zA-Z0-9_]
             when matching a bytestring or a Unicode string with the ASCII
             flag, or the whole range of Unicode alphanumeric characters
             (letters plus digits plus underscore) when matching a Unicode
             string. With LOCALE, it will match the set [0-9_] plus characters
             defined as letters for the current locale.
    \W       Matches the complement of \w; equivalent to [^\w].
    \xXX     Matches the character with 2-digit hex code XX.
    \Z       Matches only at the end of the string.
    \\       Matches a literal backslash.

This module exports the following functions:
    match     Match a regular expression pattern to the beginning of a string.
    search    Search a string for the presence of a pattern.
    sub       Substitute occurrences of a pattern found in a string.
    subn      Same as sub, but also return the number of substitutions made.
    split     Split a string by the occurrences of a pattern.
    splititer Return an iterator yielding the parts of a split string.
    findall   Find all occurrences of a pattern in a string.
    finditer  Return an iterator yielding a match object for each match.
    compile   Compile a pattern into a RegexObject.
    purge     Clear the regular expression cache.
    escape    Backslash all non-alphanumerics in a string.

Some of the functions in this module take flags as optional parameters. These
flags can also be set within an RE:
    A  a  ASCII      Make \w, \W, \b, \B, \d, and \D match the corresponding
                     ASCII character categories when matching a Unicode string.
                     Default when matching a bytestring.
    D     DEBUG      Prints the parsed pattern.
    I  i  IGNORECASE Perform case-insensitive matching.
    L  L  LOCALE     Make \w, \W, \b, \B, \d, and \D dependent on the current
                     locale.
    M  m  MULTILINE  "^" matches the beginning of lines (after a newline) as
                     well as the string. "$" matches the end of lines (before a
                     newline) as well as the end of the string.
    S  s  DOTALL     "." matches any character at all, including the newline.
    X  x  VERBOSE    Ignore whitespace and comments for nicer looking RE's.
    U  u  UNICODE    Make \w, \W, \b, \B, \d, and \D dependent on the Unicode
                     locale. Default when matching a Unicode string.
    Z  z  ZEROWIDTH  Correct handling of zero-width matches.

This module also defines an exception 'error'.

"""

# Public symbols.
__all__ = ["match", "search", "sub", "subn", "split", "splititer", "findall",
    "finditer", "compile", "purge", "template", "escape", "A", "I", "L", "M",
    "S", "T", "U", "X", "Z", "ASCII", "DEBUG", "IGNORECASE", "LOCALE",
    "MULTILINE", "DOTALL", "UNICODE", "VERBOSE", "ZEROWIDTH", "TEMPLATE",
    "error"]

__version__ = "2.3.0"

# Flags.
A = ASCII = 0x80      # Assume ASCII locale.
D = DEBUG = 0x200     # Print parsed pattern.
I = IGNORECASE = 0x2  # Ignore case.
L = LOCALE = 0x4      # Assume current 8-bit locale.
M = MULTILINE = 0x8   # Make anchors look for newline.
S = DOTALL = 0x10     # Make dot match newline.
U = UNICODE = 0x20    # Assume Unicode locale.
X = VERBOSE = 0x40    # Ignore whitespace and comments.
Z = ZEROWIDTH = 0x100 # Correct handling of zero-width matches.
T = TEMPLATE = 0x1    # Template.

# re exception.
class error(Exception):
    def __init__(self, message):
        if isinstance(message, unicode):
            message = message.encode(sys.stdout.encoding)
        Exception.__init__(self, message)

# --------------------------------------------------------------------
# Public interface.

def match(pattern, string, flags=0, pos=None, endpos=None):
    """Try to apply the pattern at the start of the string, returning a match
    object, or None if no match was found."""
    return _compile(pattern, flags).match(string, pos, endpos)

def search(pattern, string, flags=0, pos=None, endpos=None):
    """Scan through string looking for a match to the pattern, returning a match
    object, or None if no match was found."""
    return _compile(pattern, flags).search(string, pos, endpos)

def sub(pattern, repl, string, count=0, flags=0):
    """Return the string obtained by replacing the leftmost non-overlapping
    occurrences of the pattern in string by the replacement repl.  repl can be
    either a string or a callable; if a string, backslash escapes in it are
    processed.  If it is a callable, it's passed the match object and must
    return a replacement string to be used."""
    return _compile(pattern, flags).sub(repl, string, count)

def subn(pattern, repl, string, count=0, flags=0):
    """Return a 2-tuple containing (new_string, number). new_string is the
    string obtained by replacing the leftmost non-overlapping occurrences of the
    pattern in the source string by the replacement repl.  number is the number
    of substitutions that were made. repl can be either a string or a callable;
    if a string, backslash escapes in it are processed. If it is a callable,
    it's passed the match object and must return a replacement string to be
    used."""
    return _compile(pattern, flags).subn(repl, string, count)

def split(pattern, string, maxsplit=0, flags=0):
    """Split the source string by the occurrences of the pattern, returning a
    list containing the resulting substrings."""
    return _compile(pattern, flags).split(string, maxsplit)

def splititer(pattern, string, maxsplit=0, flags=0):
    """Return an iterator yielding the parts of a split string."""
    return _compile(pattern, flags).splititer(string, maxsplit=maxsplit)

def findall(pattern, string, pos=None, endpos=None, flags=0, overlapped=False):
    """Return a list of all non-overlapping matches in the string if overlapped
    is False or all matches if overlapped is True .  If one or more groups are
    present in the pattern, return a list of groups; this will be a list of
    tuples if the pattern has more than one group.  Empty matches are included
    in the result."""
    return _compile(pattern, flags).findall(string, pos, endpos, overlapped=overlapped)

def finditer(pattern, string, pos=None, endpos=None, flags=0, overlapped=False):
    """Return an iterator over all non-overlapping matches in the string.  For
    each match, the iterator returns a match object.  Empty matches are included
    in the result."""
    return _compile(pattern, flags).finditer(string, pos, endpos, overlapped=overlapped)

def compile(pattern, flags=0):
    "Compile a regular expression pattern, returning a pattern object."
    return _compile(pattern, flags)

def purge():
    "Clear the regular expression cache"
    _cache.clear()

def template(pattern, flags=0):
    "Compile a template pattern, returning a pattern object."
    return _compile(pattern, flags | T)

def escape(pattern):
    "Escape all non-alphanumeric characters in pattern."
    if isinstance(pattern, unicode):
        s = []
        for c in pattern:
            if c in _ALNUM:
                s.append(c)
            elif c == u"\x00":
                s.append(u"\\000")
            else:
                s.append(u"\\")
                s.append(c)
        return u"".join(s)
    else:
        s = []
        for c in pattern:
            if c in _ALNUM:
                s.append(c)
            elif c == "\x00":
                s.append("\\000")
            else:
                s.append("\\")
                s.append(c)
        return "".join(s)

# --------------------------------------------------------------------
# Internals.

_ALPHA = frozenset("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
_DIGITS = frozenset("0123456789")
_ALNUM = _ALPHA | _DIGITS
_OCT_DIGITS = frozenset("01234567")
_HEX_DIGITS = frozenset("0123456789ABCDEFabcdef")

if __name__ != "__main__":
    import _regex
    _regex.set_exception(error)

import unicodedata
from collections import defaultdict

# The repeat count which represents infinity.
_UNLIMITED = 0xFFFFFFFF

# The names of the opcodes.
_OPCODES = """
FAILURE
SUCCESS
ANY
ANY_ALL
ANY_ALL_REV
ANY_REV
ATOMIC
BEGIN_GROUP
BITSET
BOUNDARY
BRANCH
CATEGORY
CATEGORY_REV
CHARACTER
CHARACTER_IGNORE
CHARACTER_IGNORE_REV
CHARACTER_REV
END
END_GREEDY_REPEAT
END_GROUP
END_LAZY_REPEAT
END_OF_LINE
END_OF_STRING
END_OF_STRING_LINE
GREEDY_REPEAT
GREEDY_REPEAT_ONE
GROUP
GROUP_EXISTS
LAZY_REPEAT
LAZY_REPEAT_ONE
LOOKAROUND
NEXT
RANGE
REF_GROUP
REF_GROUP_IGNORE
REF_GROUP_IGNORE_REV
REF_GROUP_REV
SEARCH_ANCHOR
SET
SET_IGNORE
SET_IGNORE_REV
SET_REV
START_OF_LINE
START_OF_STRING
STRING
STRING_IGNORE
STRING_IGNORE_REV
STRING_REV
"""

def _define_opcodes(opcodes):
    "Defines the opcodes and their numeric values."
    # The namespace for the opcodes.
    class Record(object):
        pass

    op_list = [op.strip() for op in opcodes.splitlines()]
    op_list = [op for op in op_list if op]

    _OP = Record()

    for i, op in enumerate(op_list):
        setattr(_OP, op, i)

    return _OP

# Define the opcodes in a namespace.
_OP = _define_opcodes(_OPCODES)

# The mask for the flags.
_GLOBAL_FLAGS = ASCII | DEBUG | LOCALE | UNICODE | ZEROWIDTH
_LOCAL_FLAGS = IGNORECASE | MULTILINE | DOTALL | VERBOSE

# The regular expression flags.
_REGEX_FLAGS = {"a": ASCII, "i": IGNORECASE, "L": LOCALE, "m": MULTILINE,
  "s": DOTALL, "u": UNICODE, "x": VERBOSE, "z": ZEROWIDTH}

# Unicode properties and categories.
_CATEGORIES = """
0 Cn Unassigned
1 Lu Uppercase_Letter
2 Ll Lowercase_Letter
3 Lt Titlecase_Letter
4 Mn Non_Spacing_Mark
5 Mc Spacing_Combining_Mark
6 Me Enclosing_Mark
7 Nd Decimal_Digit_Number
8 Nl Letter_Number
9 No Other_Number
10 Zs Space_Separator
11 Zl Line_Separator
12 Zp Paragraph_Separator
13 Cc Control
14 Cf Format
15 Cs Surrogate
16 Co Private_Use
17 Cn Unassigned
18 Lm Modifier_Letter
19 Lo Other_Letter
20 Pc Connector_Punctuation
21 Pd Dash_Punctuation
22 Ps Open_Punctuation
23 Pe Close_Punctuation
24 Pi Initial_Punctuation
25 Pf Final_Punctuation
26 Po Other_Punctuation
27 Sm Math_Symbol
28 Sc Currency_Symbol
29 Sk Modifier_Symbol
30 So Other_Symbol
L Letter L& Letter&
M Mark M& Mark&
Z Separator Z& Separator&
S Symbol S& Symbol&
N Number N& Number&
P Punctuation P& Punctuation&
C Other C& Other&
Alpha
Alnum
ASCII
Blank
Cntrl
Digit
Graph
Linebreak
Lower
Print
Punct
Space
Upper
Word
XDigit
0x0000 0x007F InBasic_Latin
0x0080 0x00FF InLatin-1_Supplement
0x0100 0x017F InLatin_Extended-A
0x0180 0x024F InLatin_Extended-B
0x0250 0x02AF InIPA_Extensions
0x02B0 0x02FF InSpacing_Modifier_Letters
0x0300 0x036F InCombining_Diacritical_Marks
0x0370 0x03FF InGreek_and_Coptic
0x0400 0x04FF InCyrillic
0x0500 0x052F InCyrillic_Supplementary
0x0530 0x058F InArmenian
0x0590 0x05FF InHebrew
0x0600 0x06FF InArabic
0x0700 0x074F InSyriac
0x0780 0x07BF InThaana
0x0900 0x097F InDevanagari
0x0980 0x09FF InBengali
0x0A00 0x0A7F InGurmukhi
0x0A80 0x0AFF InGujarati
0x0B00 0x0B7F InOriya
0x0B80 0x0BFF InTamil
0x0C00 0x0C7F InTelugu
0x0C80 0x0CFF InKannada
0x0D00 0x0D7F InMalayalam
0x0D80 0x0DFF InSinhala
0x0E00 0x0E7F InThai
0x0E80 0x0EFF InLao
0x0F00 0x0FFF InTibetan
0x1000 0x109F InMyanmar
0x10A0 0x10FF InGeorgian
0x1100 0x11FF InHangul_Jamo
0x1200 0x137F InEthiopic
0x13A0 0x13FF InCherokee
0x1400 0x167F InUnified_Canadian_Aboriginal_Syllabics
0x1680 0x169F InOgham
0x16A0 0x16FF InRunic
0x1700 0x171F InTagalog
0x1720 0x173F InHanunoo
0x1740 0x175F InBuhid
0x1760 0x177F InTagbanwa
0x1780 0x17FF InKhmer
0x1800 0x18AF InMongolian
0x1900 0x194F InLimbu
0x1950 0x197F InTai_Le
0x19E0 0x19FF InKhmer_Symbols
0x1D00 0x1D7F InPhonetic_Extensions
0x1E00 0x1EFF InLatin_Extended_Additional
0x1F00 0x1FFF InGreek_Extended
0x2000 0x206F InGeneral_Punctuation
0x2070 0x209F InSuperscripts_and_Subscripts
0x20A0 0x20CF InCurrency_Symbols
0x20D0 0x20FF InCombining_Diacritical_Marks_for_Symbols
0x2100 0x214F InLetterlike_Symbols
0x2150 0x218F InNumber_Forms
0x2190 0x21FF InArrows
0x2200 0x22FF InMathematical_Operators
0x2300 0x23FF InMiscellaneous_Technical
0x2400 0x243F InControl_Pictures
0x2440 0x245F InOptical_Character_Recognition
0x2460 0x24FF InEnclosed_Alphanumerics
0x2500 0x257F InBox_Drawing
0x2580 0x259F InBlock_Elements
0x25A0 0x25FF InGeometric_Shapes
0x2600 0x26FF InMiscellaneous_Symbols
0x2700 0x27BF InDingbats
0x27C0 0x27EF InMiscellaneous_Mathematical_Symbols-A
0x27F0 0x27FF InSupplemental_Arrows-A
0x2800 0x28FF InBraille_Patterns
0x2900 0x297F InSupplemental_Arrows-B
0x2980 0x29FF InMiscellaneous_Mathematical_Symbols-B
0x2A00 0x2AFF InSupplemental_Mathematical_Operators
0x2B00 0x2BFF InMiscellaneous_Symbols_and_Arrows
0x2E80 0x2EFF InCJK_Radicals_Supplement
0x2F00 0x2FDF InKangxi_Radicals
0x2FF0 0x2FFF InIdeographic_Description_Characters
0x3000 0x303F InCJK_Symbols_and_Punctuation
0x3040 0x309F InHiragana
0x30A0 0x30FF InKatakana
0x3100 0x312F InBopomofo
0x3130 0x318F InHangul_Compatibility_Jamo
0x3190 0x319F InKanbun
0x31A0 0x31BF InBopomofo_Extended
0x31F0 0x31FF InKatakana_Phonetic_Extensions
0x3200 0x32FF InEnclosed_CJK_Letters_and_Months
0x3300 0x33FF InCJK_Compatibility
0x3400 0x4DBF InCJK_Unified_Ideographs_Extension_A
0x4DC0 0x4DFF InYijing_Hexagram_Symbols
0x4E00 0x9FFF InCJK_Unified_Ideographs
0xA000 0xA48F InYi_Syllables
0xA490 0xA4CF InYi_Radicals
0xAC00 0xD7AF InHangul_Syllables
0xD800 0xDB7F InHigh_Surrogates
0xDB80 0xDBFF InHigh_Private_Use_Surrogates
0xDC00 0xDFFF InLow_Surrogates
0xE000 0xF8FF InPrivate_Use_Area
0xF900 0xFAFF InCJK_Compatibility_Ideographs
0xFB00 0xFB4F InAlphabetic_Presentation_Forms
0xFB50 0xFDFF InArabic_Presentation_Forms-A
0xFE00 0xFE0F InVariation_Selectors
0xFE20 0xFE2F InCombining_Half_Marks
0xFE30 0xFE4F InCJK_Compatibility_Forms
0xFE50 0xFE6F InSmall_Form_Variants
0xFE70 0xFEFF InArabic_Presentation_Forms-B
0xFF00 0xFFEF InHalfwidth_and_Fullwidth_Forms
0xFFF0 0xFFFF InSpecials
"""

def _create_categories(categories):
    "Creates the Unicode property masks and the categories."
    # Normalise the names.
    categories = categories.upper().replace("_", "").replace("-", "")

    # Build the tables of the categories.
    cat = {}
    prop_masks = defaultdict(int)
    script_ranges = {}
    extra_value = 32
    for line in categories.splitlines():
        if not line:
            continue
        fields = line.split()
        if fields[0].isdigit():
            # It's a Unicode property.
            value = int(fields[0])
            mask = 1 << value
            for f in fields[1 : ]:
                cat.setdefault(f, value)
                if len(f) == 2:
                    prop_masks[f] |= mask
                    if f[0] not in cat:
                        cat[f[0]] = extra_value
                        extra_value += 1
                    prop_masks[f[0]] |= mask
        elif fields[0].startswith("0X"):
            # It's a Unicode script range.
            cat[fields[2]] = extra_value
            # Without the leading "In".
            cat[fields[2][2 : ]] = extra_value
            extra_value += 1
            script_ranges[fields[2]] = int(fields[0], 16), int(fields[1], 16)
        else:
            # It's a category or property.
            if fields[0] in cat:
                value = cat[fields[0]]
                for f in fields[1 : ]:
                    cat[f] = value
            else:
                for f in fields:
                    cat[f] = extra_value
                extra_value += 1

    return cat, dict(prop_masks), script_ranges

# Build the category tables.
_categories, _property_masks, _script_ranges = _create_categories(_CATEGORIES)

# Caches for the patterns and replacements.
_cache = {}

# Maximum size of the caches.
_MAXCACHE = 1024

import sys

def _compile(pattern, flags=0):
    "Compiles a regular expression to a PatternObject. "
    # We're checking in this order because _pattern_type isn't defined when
    # _compile() is first called, with a string pattern, but only after the
    # support objects are defined.
    if isinstance(pattern, (unicode, str)):
        pass
    elif isinstance(pattern, _pattern_type):
        if flags:
            raise ValueError("cannot process flags argument with a compiled pattern")
        return pattern
    else:
        raise TypeError("first argument must be string or compiled pattern")

    # Have we already seen this regular expression?
    key = pattern, type(pattern), flags
    p = _cache.get(key)
    if p:
        return p

    # Parse the regular expression.
    source = _Source(pattern)
    info = _Info(flags)
    source.ignore_space = info.local_flags & VERBOSE
    parsed = _parse_pattern(source, info)
    if not source.at_end():
        raise error("trailing characters in pattern")

    # Global flags could be passed in 'flags' or in the pattern, so we're
    # checking after parsing.
    both_flags = UNICODE | ASCII
    if (info.global_flags & both_flags) == both_flags:
        raise ValueError("ASCII and UNICODE flags are incompatible")

    # Fix the group references.
    parsed.fix_groups()

    # Optimise the parsed pattern.
    parsed = parsed.optimise()
    parsed = parsed.pack_characters()

    # Should we print the parsed pattern?
    if flags & DEBUG:
        parsed.dump()

    # Compile the parsed pattern. The result is a list of tuples.
    code = parsed.compile() + [(_OP.SUCCESS, )]

    # Flatten the code into a list of ints.
    code = _flatten_code(code)

    # The named capture groups.
    index_group = dict((v, n) for n, v in info.group_index.items())

    # Create the PatternObject.
    #
    # Local flags like IGNORECASE affect the code generation, but aren't needed
    # by the PatternObject itself. Conversely, global flags like LOCALE _don't_
    # affect the code generation but _are_ needed by the PatternObject.
    p = _regex.compile(pattern, info.global_flags | info.local_flags, code, info.group_index, index_group)

    # Store the compiled pattern.
    if len(_cache) >= _MAXCACHE:
        _cache.clear()
    _cache[key] = p

    return p

def _flatten_code(code):
    "Flattens the code from a list of tuples."
    code = _optimise_boundary(code)
    flat_code = []
    for c in code:
        if c[0] < 0:
            # Negative opcodes are end-markers.
            flat_code.append(_OP.END)
        else:
            flat_code.append(c[0])
        flat_code.extend(c[1 : ])
    return flat_code

def _create_swap_pairs():
    "Creates the set of swap pairs for _optimise_boundary()."
    _swap_pairs = set()
    for opcode in [_OP.GROUP, _OP.ATOMIC]:
        _swap_pairs.add((opcode, _OP.BOUNDARY))
        _swap_pairs.add((-opcode, _OP.BOUNDARY))
    return _swap_pairs

_swap_pairs = _create_swap_pairs()

def _optimise_boundary(code):
    "Optimises BOUNDARY opcode placement."
    # Scan the code list. If a swappable pair is found then swap them.
    pos = 0
    try:
        while True:
            pair = (code[pos][0], code[pos + 1][0])
            if pair in _swap_pairs:
                code[pos], code[pos + 1] = code[pos + 1], code[pos]
                if pos > 0:
                    # Step backwards in case the swap has makes the previous pair swappable.
                    pos -= 1
                else:
                    pos += 1
            else:
                pos += 1
    except IndexError:
        pass
    return code

def _parse_pattern(source, info):
    "Parses a pattern, eg. 'a|b|c'."
    # Capture group names can be duplicated provided that their matching is
    # mutually exclusive.
    previous_groups = info.used_groups.copy()
    branches = [_parse_sequence(source, info)]
    all_groups = info.used_groups
    while source.match("|"):
        info.used_groups = previous_groups.copy()
        branches.append(_parse_sequence(source, info))
        all_groups |= info.used_groups
    info.used_groups = all_groups
    return _Branch(branches)

def _parse_sequence(source, info):
    "Parses a sequence, eg. 'abc'."
    sequence = []
    item = _parse_item(source, info)
    while item:
        sequence.append(item)
        item = _parse_item(source, info)
    return _Sequence(sequence)

def _parse_item(source, info):
    "Parses an item, which might be repeated. Returns None if there's no item."
    element = _parse_element(source, info)
    if not element:
        return element
    here = source.tell()
    lazy = possessive = False
    try:
        min_count, max_count = _parse_quantifier(source, info)
        if source.match("?"):
            lazy = True
        elif source.match("+"):
            possessive = True
        if min_count == max_count == 1:
            return element
    except error:
        # Not a quantifier, so we'll parse it later as a literal.
        source.seek(here)
        return element
    if lazy:
        return _LazyRepeat(element, min_count, max_count)
    elif possessive:
        return _Atomic(_GreedyRepeat(element, min_count, max_count))
    else:
        return _GreedyRepeat(element, min_count, max_count)

def _parse_quantifier(source, info):
    "Parses a quantifier."
    if source.match("?"):
        # Optional element, eg. 'a?'.
        return 0, 1
    elif source.match("*"):
        # Repeated element, eg. 'a*'.
        return 0, None
    elif source.match("+"):
        # Repeated element, eg. 'a+'.
        return 1, None
    elif source.match("{"):
        # Limited repeated element, eg. 'a{2,3}'.
        min_count = _parse_count(source)
        if source.match(","):
            max_count = _parse_count(source)
            if source.match("}"):
                # An empty minimum means 0 and an empty maximum means unlimited.
                min_count = int(min_count) if min_count else 0
                max_count = int(max_count) if max_count else None
                if max_count is not None and min_count > max_count:
                    raise error("min repeat greater than max repeat")
                if min_count >= _UNLIMITED or max_count is not None and max_count >= _UNLIMITED:
                    raise error("repeat count too big")
                return min_count, max_count
            else:
                raise error("missing }")
        elif source.match("}"):
            if min_count:
                min_count = max_count = int(min_count)
                if min_count >= _UNLIMITED:
                    raise error("repeat count too big")
                return min_count, max_count
            else:
                raise error("invalid quantifier")
        else:
            raise error("invalid quantifier")
    else:
        # No quantifier.
        return 1, 1

def _parse_count(source):
    "Parses a quantifier's count, which can be empty."
    count = []
    here = source.tell()
    ch = source.get()
    while ch in _DIGITS:
        count.append(ch)
        here = source.tell()
        ch = source.get()
    source.seek(here)
    return source.sep.join(count)

def _parse_element(source, info):
    "Parses an element. An element might actually be a flag, eg. '(?i)'."
    while True:
        here = source.tell()
        ch = source.get()
        if ch in ")|":
            # The end of a sequence. At the end of the pattern ch is "".
            source.seek(here)
            return None
        elif ch in "?*+{":
            # Looks like a quantifier.
            source.seek(here)
            try:
                _parse_quantifier(source, info)
            except error:
                # Not a quantifier, so it's a literal.
                # None of these characters are case-dependent.
                source.seek(here)
                ch = source.get()
                return _Character(ch)
            # A quantifier where we expected an element.
            raise error("nothing to repeat")
        elif ch == "(":
            # A parenthesised subpattern or a flag.
            element = _parse_paren(source, info)
            if element:
                return element
        elif ch == "^":
            # The start of a line or the string.
            if info.local_flags & MULTILINE:
                return _StartOfLine()
            else:
                return _StartOfString()
        elif ch == "$":
            # The end of a line or the string.
            if info.local_flags & MULTILINE:
                return _EndOfLine()
            else:
                return _EndOfStringLine()
        elif ch == ".":
            # Any character.
            if info.local_flags & DOTALL:
                return _AnyAll()
            else:
                return _Any()
        elif ch == "[":
            # A character set.
            return _parse_set(source, info)
        elif ch == "\\":
            # An escape sequence.
            return _parse_escape(source, info, False)
        elif ch == "#" and (info.local_flags & VERBOSE):
            # A comment.
            source.ignore_space = False
            # Ignore characters until a newline or the end of the pattern.
            while source.get() not in "\n":
                pass
            source.ignore_space = True
        else:
            # A literal.
            if info.local_flags & IGNORECASE:
                return _CharacterIgnore(ch)
            return _Character(ch)

def _parse_paren(source, info):
    "Parses a parenthesised subpattern or a flag."
    if source.match("?P"):
        # A Python extension.
        return _parse_extension(source, info)
    elif source.match("?#"):
        # A comment.
        return _parse_comment(source)
    elif source.match("?="):
        # Positive lookahead.
        return _parse_lookaround(source, info, False, True)
    elif source.match("?!"):
        # Negative lookahead.
        return _parse_lookaround(source, info, False, False)
    elif source.match("?<="):
        # Positive lookbehind.
        return _parse_lookaround(source, info, True, True)
    elif source.match("?<!"):
        # Negative lookbehind.
        return _parse_lookaround(source, info, True, False)
    elif source.match("?<"):
        # A named capture group.
        name = _parse_name(source)
        if not name:
            raise error("bad group name")
        group = info.new_group(name)
        source.expect(">")
        saved_local_flags = info.local_flags
        saved_ignore = source.ignore_space
        try:
            subpattern = _parse_pattern(source, info)
        finally:
            info.local_flags = saved_local_flags
            source.ignore_space = saved_ignore
        source.expect(")")
        return _Group(info, group, subpattern)
    elif source.match("?("):
        # A conditonal subpattern.
        return _parse_conditional(source, info)
    elif source.match("?>"):
        # An atomic subpattern.
        return _parse_atomic(source, info)
    elif source.match("?"):
        # A flags subpattern.
        return _parse_flags_subpattern(source, info)
    else:
        # An unnamed capture group.
        group = info.new_group()
        saved_local_flags = info.local_flags
        saved_ignore = source.ignore_space
        try:
            subpattern = _parse_pattern(source, info)
        finally:
            info.local_flags = saved_local_flags
            source.ignore_space = saved_ignore
        source.expect(")")
        return _Group(info, group, subpattern)

def _parse_extension(source, info):
    "Parses a Python extension."
    if source.match("<"):
        # A named capture group.
        name = _parse_name(source)
        if not name:
            raise error("bad group name")
        group = info.new_group(name)
        source.expect(">")
        saved_local_flags = info.local_flags
        saved_ignore = source.ignore_space
        try:
            subpattern = _parse_pattern(source, info)
        finally:
            info.local_flags = saved_local_flags
            source.ignore_space = saved_ignore
        source.expect(")")
        return _Group(info, group, subpattern)
    elif source.match("="):
        # A named group reference.
        name = _parse_name(source)
        if not name:
            raise error("bad group name")
        source.expect(")")
        if info.local_flags & IGNORECASE:
            return _RefGroupIgnore(info, name)
        return _RefGroup(info, name)
    else:
        raise error("unknown extension")

def _parse_comment(source):
    "Parses a comment."
    ch = source.get()
    while ch not in ")":
        ch = source.get()
    if not ch:
        raise error("missing )")
    return None

def _parse_lookaround(source, info, behind, positive):
    "Parses a lookaround."
    saved_local_flags = info.local_flags
    saved_ignore = source.ignore_space
    try:
        subpattern = _parse_pattern(source, info)
    finally:
        info.local_flags = saved_local_flags
        source.ignore_space = saved_ignore
    source.expect(")")
    return _LookAround(behind, positive, subpattern)

def _parse_conditional(source, info):
    "Parses a conditional subpattern."
    saved_local_flags = info.local_flags
    saved_ignore = source.ignore_space
    try:
        group = _parse_name(source)
        source.expect(")")
        previous_groups = info.used_groups.copy()
        yes_branch = _parse_sequence(source, info)
        if source.match("|"):
            yes_groups = info.used_groups
            info.used_groups = previous_groups
            no_branch = _parse_sequence(source, info)
            info.used_groups |= yes_groups
        else:
            no_branch = None
    finally:
        info.local_flags = saved_local_flags
        source.ignore_space = saved_ignore
    source.expect(")")
    return _Conditional(info, group, yes_branch, no_branch)

def _parse_atomic(source, info):
    "Parses an atomic subpattern."
    saved_local_flags = info.local_flags
    saved_ignore = source.ignore_space
    try:
        subpattern = _parse_pattern(source, info)
    finally:
        info.local_flags = saved_local_flags
        source.ignore_space = saved_ignore
    source.expect(")")
    return _Atomic(subpattern)

def _parse_flags_subpattern(source, info):
    "Parses a flags subpattern."
    # It could be inline flags or a subpattern possibly with local flags.
    # Parse the flags.
    flags_on, flags_off = 0, 0
    try:
        while True:
            here = source.tell()
            ch = source.get()
            flags_on |= _REGEX_FLAGS[ch]
    except KeyError:
        pass
    if ch == "-":
        try:
            while True:
                here = source.tell()
                ch = source.get()
                flags_off |= _REGEX_FLAGS[ch]
        except KeyError:
            pass
        if not flags_off or (flags_off & _GLOBAL_FLAGS):
            error("bad flags")
    # Separate the global and local flags.
    source.seek(here)
    info.global_flags |= flags_on & _GLOBAL_FLAGS
    flags_on &= _LOCAL_FLAGS
    new_local_flags = (info.local_flags | flags_on) & ~flags_off
    saved_local_flags = info.local_flags
    saved_ignore = source.ignore_space
    info.local_flags = new_local_flags
    source.ignore_space = info.local_flags & VERBOSE
    if source.match(":"):
        # A subpattern with local flags.
        try:
            subpattern = _parse_pattern(source, info)
        finally:
            info.local_flags = saved_local_flags
            source.ignore_space = saved_ignore
        source.expect(")")
        return subpattern
    else:
        # Inline flags.
        source.expect(")")
        return None

def _parse_name(source):
    "Parses a name."
    saved_ignore = source.ignore_space
    source.ignore_space = False
    name = []
    here = source.tell()
    ch = source.get()
    while ch in _ALNUM or ch == "_":
        name.append(ch)
        here = source.tell()
        ch = source.get()
    source.seek(here)
    source.ignore_space = saved_ignore
    return source.sep.join(name)

def _is_octal(string):
    "Checks whether a string is octal."
    return all(ch in _OCT_DIGITS for ch in string)

def _is_decimal(string):
    "Checks whether a string is decimal."
    return all(ch in _DIGITS for ch in string)

def _is_hexadecimal(string):
    "Checks whether a string is hexadecimal."
    return all(ch in _HEX_DIGITS for ch in string)

def _parse_escape(source, info, in_set):
    "Parses an escape sequence."
    ch = source.get()
    if not ch:
        # A backslash at the end of the pattern.
        raise error("bad escape")
    if ch == "x":
        # A 2-digit hexadecimal escape sequence.
        return _parse_hex_escape(source, info, 2, in_set)
    elif ch == "u":
        # A 4-digit hexadecimal escape sequence.
        return _parse_hex_escape(source, info, 4, in_set)
    elif ch == "U":
        # A 8-digit hexadecimal escape sequence.
        return _parse_hex_escape(source, info, 8, in_set)
    elif ch == "g" and not in_set:
        # A group reference.
        here = source.tell()
        try:
            return _parse_group_ref(source, info)
        except error:
            # Invalid as a group reference, so assume it's a literal.
            source.seek(here)
            return _char_literal(info, in_set, ch)
    elif ch == "G" and not in_set:
        # A search anchor.
        return _SearchAnchor()
    elif ch == "N":
        # A named codepoint.
        return _parse_named_char(source, info, in_set)
    elif ch in "pP":
        # A Unicode property.
        return _parse_property(source, info, in_set, ch)
    elif ch in _ALPHA:
        # An alphabetic escape sequence.
        if not in_set:
            # Positional escapes aren't allowed inside a character set.
            value = _POSITION_ESCAPES.get(ch)
            if value:
                return value
        value = _CHARSET_ESCAPES.get(ch)
        if value:
            return value
        value = _CHARACTER_ESCAPES.get(ch)
        if value:
            return _Character(value)
        return _char_literal(info, in_set, ch)
    elif ch in _DIGITS:
        # A numeric escape sequence.
        return _parse_numeric_escape(source, info, ch, in_set)
    else:
        # A literal.
        return _char_literal(info, in_set, ch)

def _char_literal(info, in_set, ch):
    "Creates a character literal, which might be in a set."
    if info.local_flags & IGNORECASE and not in_set:
        return _CharacterIgnore(ch)
    return _Character(ch)

def _parse_numeric_escape(source, info, ch, in_set):
    "Parses a numeric escape sequence."
    if in_set or ch == "0":
        # Octal escape sequence, max 3 digits.
        return _parse_octal_escape(source, info, [ch], in_set)
    else:
        # At least 1 digit, so either octal escape or group.
        digits = ch
        here = source.tell()
        ch = source.get()
        if ch in _DIGITS:
            # At least 2 digits, so either octal escape or group.
            digits += ch
            here = source.tell()
            ch = source.get()
            if _is_octal(digits) and ch in _OCT_DIGITS:
                # 3 octal digits, so octal escape sequence.
                value = int(digits + ch, 8) & 0xFF
                if info.local_flags & IGNORECASE:
                    return _CharacterIgnore(value)
                return _Character(value)
            else:
                # 2 digits, so group.
                source.seek(here)
                return _RefGroup(info, digits)
        else:
            # 1 digit, so group.
            source.seek(here)
            return _RefGroup(info, digits)

def _parse_octal_escape(source, info, digits, in_set):
    "Parses an octal escape sequence."
    here = source.tell()
    ch = source.get()
    while len(digits) < 3 and ch in _OCT_DIGITS:
        digits.append(ch)
        here = source.tell()
        ch = source.get()
    source.seek(here)
    try:
        value = int(source.sep.join(digits), 8) & 0xFF
        if info.local_flags & IGNORECASE and not in_set:
            return _CharacterIgnore(value)
        return _Character(value)
    except ValueError:
        raise error("bad escape")

def _parse_hex_escape(source, info, max_len, in_set):
    "Parses a hex escape sequence."
    digits = []
    here = source.tell()
    ch = source.get()
    while len(digits) < max_len and ch in _HEX_DIGITS:
        digits.append(ch)
        here = source.tell()
        ch = source.get()
    if len(digits) != max_len:
        raise error("bad hex escape")
    source.seek(here)
    value = int(source.sep.join(digits), 16)
    if info.local_flags & IGNORECASE and not in_set:
        return _CharacterIgnore(value)
    return _Character(value)

def _parse_group_ref(source, info):
    "Parses a group reference."
    source.expect("<")
    name = _parse_name(source)
    if not name:
        raise error("bad group name")
    source.expect(">")
    if info.local_flags & IGNORECASE:
        return _RefGroupIgnore(info, name)
    return _RefGroup(info, name)

def _parse_named_char(source, info, in_set):
    "Parses a named character."
    here = source.tell()
    ch = source.get()
    if ch == "{":
        name = []
        ch = source.get()
        while ch in _ALPHA or ch == " ":
            name.append(ch)
            ch = source.get()
        if ch == "}":
            try:
                value = unicodedata.lookup(source.sep.join(name))
                if info.local_flags & IGNORECASE and not in_set:
                    return _CharacterIgnore(value)
                return _Character(value)
            except KeyError:
                raise error("undefined character name")
    source.seek(here)
    return _char_literal(info, in_set, "N")

def _parse_property(source, info, in_set, prop_ch):
    "Parses a Unicode property."
    here = source.tell()
    ch = source.get()
    if ch == "{":
        name = []
        ch = source.get()
        while ch and (ch.isalnum() or ch.isspace() or ch in "&_-"):
            name.append(ch)
            ch = source.get()
        if ch == "}":
            # The normalised name.
            norm_name = source.sep.join(ch.upper() for ch in name if ch.isalnum())
            # The un-normalised name.
            name = source.sep.join(name)
            value = _categories.get(norm_name)
            if value is not None:
                return _Category(prop_ch == "p", value)
            raise error("undefined property name '%s'" % name)
    source.seek(here)
    return _char_literal(info, in_set, prop_ch)

def _parse_set(source, info):
    "Parses a character set."
    # Negative character set?
    saved_ignore = source.ignore_space
    source.ignore_space = False
    negate = source.match("^")
    ranges = []
    try:
        item = _parse_set_range(source, info)
        ranges.append(item)
        while not source.match("]"):
            item = _parse_set_range(source, info)
            ranges.append(item)
    finally:
        source.ignore_space = saved_ignore
    if info.local_flags & IGNORECASE:
        return _SetIgnore(not negate, ranges)
    return _Set(not negate, ranges)

def _parse_set_range(source, info):
    "Parses a range in a character set."
    # It might actually be a single value, a range, or a predefined set.
    start = _parse_set_item(source, info)
    here = source.tell()
    if isinstance(start, _Character) and source.match("-"):
        if source.match("]"):
            source.seek(here)
            return start
        end = _parse_set_item(source, info)
        if isinstance(end, _Character):
            if start.char_code > end.char_code:
                raise error("bad character ranmge")
            return _SetRange(start.char_code, end.char_code)
        source.seek(here)
    return start

def _parse_set_item(source, info):
    "Parses an item in a character set."
    if source.match("\\"):
        return _parse_escape(source, info, True)
    elif source.match("[:"):
        return _parse_character_class(source, info)
    else:
        ch = source.get()
        if not ch:
            raise error("bad set")
        return _Character(ch)

def _parse_character_class(source, info):
    name = _parse_name(source)
    source.expect(":]")
    value = _categories.get(name.upper())
    if value is not None:
        return _Category(True, value)
    raise error("undefined character class name '%s'" % name)

def _compile_replacement(pattern, template):
    "Compiles a replacement template."
    # This function is called by the _regex module.
    source = _Source(template)
    if isinstance(template, unicode):
        def make_string(char_codes):
            return u"".join(unichr(c) for c in char_codes)
    else:
        def make_string(char_codes):
            return "".join(chr(c) for c in char_codes)
    compiled = []
    literal = []
    while True:
        ch = source.get()
        if not ch:
            break
        if ch == "\\":
            # '_compile_repl_escape' will return either an int group references
            # or a string literal.
            is_group, item = _compile_repl_escape(source, pattern)
            if is_group:
                # It's a group, so first flush the literal.
                if literal:
                    compiled.append(make_string(literal))
                    literal = []
                compiled.append(item)
            else:
                literal.append(item)
        else:
            literal.append(ord(ch))
    # Flush the literal.
    if literal:
        compiled.append(make_string(literal))
    return compiled

def _compile_repl_escape(source, pattern):
    "Compiles a replacement template escape sequence."
    here = source.tell()
    ch = source.get()
    if ch in _ALPHA:
        # An alphabetic escape sequence.
        value = _CHARACTER_ESCAPES.get(ch)
        if value:
            return False, value
        if ch == "g":
            # A group preference.
            return True, _compile_repl_group(source, pattern)
        else:
            source.seek(here)
            return False, ord("\\")
    elif ch == "0":
        # An octal escape sequence.
        digits = ch
        while len(digits) < 3:
            here = source.tell()
            ch = source.get()
            if ch not in _OCT_DIGITS:
                source.seek(here)
                break
            digits += ch
        return False, int(digits, 8) & 0xFF
    elif ch in _DIGITS:
        # Either an octal escape sequence (3 digits) or a group reference (max
        # 2 digits).
        digits = ch
        here = source.tell()
        ch = source.get()
        if ch in _DIGITS:
            digits += ch
            here = source.tell()
            ch = source.get()
            if ch and _is_octal(digits + ch):
                # An octal escape sequence.
                return False, int(digits + ch, 8) & 0xFF
            else:
                # A group reference.
                source.seek(here)
                return True, int(digits)
        else:
            source.seek(here)
            # A group reference.
            return True, int(digits)
    else:
        # A literal.
        return False, ord(ch)

def _compile_repl_group(source, pattern):
    "Compiles a replacement template group reference."
    source.expect("<")
    name = _parse_name(source)
    if not name:
        raise error("bad group name")
    source.expect(">")
    try:
        index = int(name)
        if not 0 <= index <= pattern.groups:
            raise error("invalid group")
        return index
    except ValueError:
        try:
            return pattern.groupindex[name]
        except KeyError:
            raise error("unknown group")

# The regular expression is parsed into a syntax tree. The different types of
# node are defined below.

_INDENT = "  "

class _RegexBase(object):
    def fix_groups(self):
        pass
    def optimise(self):
        return self
    def pack_characters(self):
        return self
    def remove_captures(self):
        return self
    def is_empty(self):
        return False
    def is_atomic(self):
        return True
    def contains_group(self):
        return False
    def get_first(self):
        return self
    def drop_first(self):
        return _Sequence()
    def get_last(self):
        return self
    def drop_last(self):
        return _Sequence()
    def get_range(self):
        return None
    def __hash__(self):
        return hash(self._key)
    def __eq__(self, other):
        return type(self) is type(other) and self._key == other._key

class _StructureBase(_RegexBase):
    def get_first(self):
        return None
    def drop_first(self):
        raise error("internal error")
    def get_last(self):
        return None
    def drop_last(self):
        raise error("internal error")

class _Any(_RegexBase):
    _opcode = {False: _OP.ANY, True: _OP.ANY_REV}
    _op_name = {False: "ANY", True: "ANY_REV"}
    def __init__(self):
        self._key = self.__class__
    def compile(self, reverse=False):
        return [(self._opcode[reverse], )]
    def dump(self, indent=0, reverse=False):
        print "%s%s" % (_INDENT * indent, self._op_name[reverse])

class _AnyAll(_Any):
    _opcode = {False: _OP.ANY_ALL, True: _OP.ANY_ALL_REV}
    _op_name = {False: "ANY_ALL", True: "ANY_ALL_REV"}

class _Atomic(_StructureBase):
    def __init__(self, subpattern):
        self.subpattern = subpattern
    def fix_groups(self):
        self.subpattern.fix_groups()
    def optimise(self):
        subpattern = self.subpattern.optimise()
        sequence = []
        while True:
            item = subpattern.get_first()
            if not item or not item.is_atomic():
                break
            sequence.append(item)
            subpattern = subpattern.drop_first()
        if not subpattern.is_empty():
            sequence.append(_Atomic(subpattern))
        if len(sequence) == 1:
            return sequence[0]
        return _Sequence(sequence)
    def pack_characters(self):
        return _Atomic(self.subpattern.pack_characters())
    def is_empty(self):
        return self.subpattern.is_empty()
    def contains_group(self):
        return self.subpattern.contains_group()
    def get_range(self):
        return self.subpattern.get_range()
    def compile(self, reverse=False):
        return [(_OP.ATOMIC, )] + self.subpattern.compile(reverse) + [(-_OP.ATOMIC, )]
    def dump(self, indent=0, reverse=False):
        print "%s%s" % (_INDENT * indent, "ATOMIC")
        self.subpattern.dump(indent + 1, reverse)
    def __eq__(self, other):
        return type(self) is type(other) and self.subpattern == other.subpattern

class _Boundary(_RegexBase):
    _pos_text = {False: "NON-MATCH", True: "MATCH"}
    def __init__(self, positive):
        self.positive = bool(positive)
    def compile(self, reverse=False):
        return [(_OP.BOUNDARY, int(self.positive))]
    def dump(self, indent=0, reverse=False):
        print "%sBOUNDARY %s" % (_INDENT * indent, self._pos_text[self.positive])

class _Branch(_StructureBase):
    def __init__(self, branches):
        self.branches = branches
    def fix_groups(self):
        for branch in self.branches:
            branch.fix_groups()
    def optimise(self):
        branches = []
        for branch in self.branches:
            branch = branch.optimise()
            if isinstance(branch, _Branch):
                branches.extend(branch.branches)
            else:
                branches.append(branch)
        sequence = []
        while True:
            item = branches[0].get_first()
            if not item or item.contains_group():
                break
            if any(branch.get_first() != item for branch in branches[1 : ]):
                break
            sequence.append(item)
            branches = [branch.drop_first() for branch in branches]
        suffix = []
        while True:
            item = branches[0].get_last()
            if not item or item.contains_group():
                break
            if any(branch.get_last() != item for branch in branches[1 : ]):
                break
            suffix.append(item)
            branches = [branch.drop_last() for branch in branches]
        suffix.reverse()
        set_ranges = []
        for branch in branches:
            r = branch.get_range()
            if not r:
                break
            set_ranges.append(r)
        if len(set_ranges) == len(branches):
            sequence.append(_Set(True, [_SetRange(*r) for r in set_ranges]).optimise())
        else:
            char_prefixes = defaultdict(list)
            order = {}
            new_branches = []
            for branch in branches:
                first = branch.get_first()
                if type(first) is _Character:
                    char_prefixes[first.char_code].append(branch)
                    order.setdefault(first.char_code, len(order))
                else:
                    self._flush_char_prefix(char_prefixes, order, new_branches)
                    char_prefixes.clear()
                    order.clear()
                    new_branches.append(branch)
            self._flush_char_prefix(char_prefixes, order, new_branches)
            if len(new_branches) == 1:
                sequence.append(new_branches[0])
            else:
                sequence.append(_Branch(new_branches))
        sequence.extend(suffix)
        if len(sequence) == 1:
            return sequence[0]
        return _Sequence(sequence)
    def pack_characters(self):
        return _Branch([branch.pack_characters() for branch in self.branches])
    def is_empty(self):
        return all(branch.is_empty() for branch in self.branches)
    def is_atomic(self):
        return all(branch.is_atomic() for branch in self.branches)
    def contains_group(self):
        return any(branch.contains_group() for branch in self.branches)
    def compile(self, reverse=False):
        code = [(_OP.BRANCH, )]
        for branch in self.branches:
            code.extend(branch.compile(reverse))
            code.append((_OP.NEXT, ))
        code[-1] = (-_OP.BRANCH, )
        return code
    def remove_captures(self):
        self.branches = [branch.remove_captures() for branch in self.branches]
        return self
    def dump(self, indent=0, reverse=False):
        print "%sBRANCH" % (_INDENT * indent)
        self.branches[0].dump(indent + 1, reverse)
        for branch in self.branches[1 : ]:
            print "%sOR" % (_INDENT * indent)
            branch.dump(indent + 1, reverse)
    def _flush_char_prefix(self, prefixed, order, new_branches):
        for char_code, branches in sorted(prefixed.items(), key=lambda pair: order[pair[0]]):
            if len(branches) == 1:
                new_branches.extend(branches)
            else:
                subbranches = []
                optional = False
                for branch in branches:
                    b = branch.drop_first()
                    if b:
                        subbranches.append(b)
                    elif not optional:
                        subbranches.append(_Sequence())
                        optional = True
                sequence = _Sequence([_Character(char_code), _Branch(subbranches)])
                new_branches.append(sequence.optimise())
    def __eq__(self, other):
        return type(self) is type(other) and self.branches == other.branches

class _Category(_RegexBase):
    _opcode = {False: _OP.CATEGORY, True: _OP.CATEGORY_REV}
    _op_name = {False: "CATEGORY", True: "CATEGORY_REV"}
    _pos_text = {False: "NON-MATCH", True: "MATCH"}
    def __init__(self, positive, value):
        self.positive, self.value = bool(positive), value
        self._key = self.__class__, self.positive, self.value
    def compile(self, reverse=False):
        return [(self._opcode[reverse], int(self.positive), self.value)]
    def dump(self, indent=0, reverse=False):
        print "%s%s %s %s" % (_INDENT * indent, self._op_name[reverse], self._pos_text[self.positive], self.value)

class _Character(_RegexBase):
    _opcode = {False: _OP.CHARACTER, True: _OP.CHARACTER_REV}
    _op_name = {False: "CHARACTER", True: "CHARACTER_REV"}
    def __init__(self, ch):
        try:
            self.char_code = ord(ch)
        except TypeError:
            self.char_code = ch
        self._key = self.__class__, self.char_code
    def get_range(self):
        return (self.char_code, self.char_code)
    def compile(self, reverse=False):
        return [(self._opcode[reverse], self.char_code)]
    def dump(self, indent=0, reverse=False):
        print "%s%s %s" % (_INDENT * indent, self._op_name[reverse], self.char_code)

class _CharacterIgnore(_Character):
    _opcode = {False: _OP.CHARACTER_IGNORE, True: _OP.CHARACTER_IGNORE_REV}
    _op_name = {False: "CHARACTER_IGNORE", True: "CHARACTER_IGNORE_REV"}

class _Conditional(_StructureBase):
    def __init__(self, info, group, yes_item, no_item):
        self.info, self.group, self.yes_item, self.no_item = info, group, yes_item, no_item
    def fix_groups(self):
        try:
            self.group = int(self.group)
        except ValueError:
            try:
                self.group = self.info.group_index[self.group]
            except KeyError:
                raise error("unknown group")
        if not 1 <= self.group <= self.info.group_count:
            raise error("unknown group")
        self.yes_item.fix_groups()
        if self.no_item:
            self.no_item.fix_groups()
        else:
            self.no_item = _Sequence()
    def optimise(self):
        if self.yes_item.is_empty() and self.no_item.is_empty():
            return _Sequence()
        return _Conditional(self.info, self.group, self.yes_item.optimise(), self.no_item.optimise())
    def pack_characters(self):
        return _Conditional(self.info, self.group, self.yes_item.pack_characters(), self.no_item.pack_characters())
    def is_empty(self):
        return self.yes_item.is_empty() and self.no_item.is_empty()
    def is_atomic(self):
        return self.yes_item.is_atomic() and self.no_item.is_atomic()
    def contains_group(self):
        return self.yes_item.contains_group() or self.no_item.contains_group()
    def compile(self, reverse=False):
        code = [(_OP.GROUP_EXISTS, self.group)]
        code.extend(self.yes_item.compile(reverse))
        add_code = self.no_item.compile(reverse)
        if add_code:
            code.append((_OP.NEXT, ))
            code.extend(add_code)
        code.append((-_OP.GROUP_EXISTS, ))
        return code
    def remove_captures(self):
        self.yes_item = self.yes_item.remove_captures()
        if self.no_item:
            self.no_item = self.no_item.remove_captures()
    def dump(self, indent=0, reverse=False):
        print "%sGROUP_EXISTS %s" % (_INDENT * indent, self.group)
        self.yes_item.dump(indent + 1, reverse)
        if self.no_item:
            print "%sELSE" % (_INDENT * indent)
            self.no_item.dump(indent + 1, reverse)
    def __eq__(self, other):
        return type(self) is type(other) and (self.group, self.yes_item, self.no_item) == (other.group, other.yes_item, other.no_item)

class _EndOfLine(_RegexBase):
    def compile(self, reverse=False):
        return [(_OP.END_OF_LINE, )]
    def dump(self, indent=0, reverse=False):
        print "%sEND_OF_LINE" % (_INDENT * indent)

class _EndOfString(_RegexBase):
    def compile(self, reverse=False):
        return [(_OP.END_OF_STRING, )]
    def dump(self, indent=0, reverse=False):
        print "%sEND_OF_STRING" % (_INDENT * indent)

class _EndOfStringLine(_RegexBase):
    def compile(self, reverse=False):
        return [(_OP.END_OF_STRING_LINE, )]
    def dump(self, indent=0, reverse=False):
        print "%sEND_OF_STRING_LINE" % (_INDENT * indent)

class _GreedyRepeat(_StructureBase):
    _opcode = _OP.GREEDY_REPEAT
    _op_name = "GREEDY_REPEAT"
    def __init__(self, subpattern, min_count, max_count):
        self.subpattern, self.min_count, self.max_count = subpattern, min_count, max_count
    def fix_groups(self):
        self.subpattern.fix_groups()
    def optimise(self):
        subpattern = self.subpattern.optimise()
        if (self.min_count, self.max_count) == (1, 1) or subpattern.is_empty():
            return subpattern
        return type(self)(subpattern, self.min_count, self.max_count)
    def pack_characters(self):
        return type(self)(self.subpattern.pack_characters(), self.min_count, self.max_count)
    def is_empty(self):
        return self.subpattern.is_empty()
    def is_atomic(self):
        return self.min_count == self.max_count and self.subpattern.is_atomic()
    def contains_group(self):
        return self.subpattern.contains_group()
    def compile(self, reverse=False):
        repeat = [self._opcode, self.min_count]
        if self.max_count is None:
            repeat.append(_UNLIMITED)
        else:
            repeat.append(self.max_count)
        return [tuple(repeat)] + self.subpattern.compile(reverse) + [(-self._opcode, )]
    def remove_captures(self):
        self.subpattern = self.subpattern.remove_captures()
        return self
    def dump(self, indent=0, reverse=False):
        if self.max_count is None:
            print "%s%s %s INF" % (_INDENT * indent, self._op_name, self.min_count)
        else:
            print "%s%s %s %s" % (_INDENT * indent, self._op_name, self.min_count, self.max_count)
        self.subpattern.dump(indent + 1, reverse)
    def __eq__(self, other):
        return type(self) is type(other) and (self.subpattern, self.min_count, self.max_count) == (other.subpattern, other.min_count, other.max_count)

class _Group(_StructureBase):
    def __init__(self, info, group, subpattern):
        self.info, self.group, self.subpattern = info, group, subpattern
    def fix_groups(self):
        self.subpattern.fix_groups()
    def optimise(self):
        return _Group(self.info, self.group, self.subpattern.optimise())
    def pack_characters(self):
        return _Group(self.info, self.group, self.subpattern.pack_characters())
    def is_empty(self):
        return self.subpattern.is_empty()
    def is_atomic(self):
        return self.subpattern.is_atomic()
    def contains_group(self):
        return True
    def compile(self, reverse=False):
        return [(_OP.GROUP, self.group)] + self.subpattern.compile(reverse) + [(-_OP.GROUP, )]
    def remove_captures(self):
        return self.subpattern.remove_captures()
    def dump(self, indent=0, reverse=False):
        print "%sGROUP %s" % (_INDENT * indent, self.group)
        self.subpattern.dump(indent + 1, reverse)
    def __eq__(self, other):
        return type(self) is type(other) and (self.group, self.subpattern) == (other.group, other.subpattern)

class _LazyRepeat(_GreedyRepeat):
    _opcode = _OP.LAZY_REPEAT
    _op_name = "LAZY_REPEAT"

class _LookAround(_StructureBase):
    _dir_text = {False: "AHEAD", True: "BEHIND"}
    _pos_text = {False: "NON-MATCH", True: "MATCH"}
    def __init__(self, behind, positive, subpattern):
        self.behind, self.positive, self.subpattern = bool(behind), bool(positive), subpattern
    def fix_groups(self):
        self.subpattern.fix_groups()
    def optimise(self):
        subpattern = self.subpattern.optimise()
        if self.positive and subpattern.is_empty():
            return subpattern
        return _LookAround(self.behind, self.positive, subpattern)
    def pack_characters(self):
        return _LookAround(self.behind, self.positive, self.subpattern.pack_characters())
    def is_empty(self):
        return self.subpattern.is_empty()
    def is_atomic(self):
        return self.subpattern.is_atomic()
    def contains_group(self):
        return self.subpattern.contains_group()
    def compile(self, reverse=False):
        return [(_OP.LOOKAROUND, int(self.positive), int(not self.behind))] + self.subpattern.compile(self.behind) + [(-_OP.LOOKAROUND, )]
    def dump(self, indent=0, reverse=False):
        print "%sLOOKAROUND %s %s" % (_INDENT * indent, self._dir_text[self.behind], self._pos_text[self.positive])
        self.subpattern.dump(indent + 1, self.behind)
    def __eq__(self, other):
        return type(self) is type(other) and (self.behind, self.positive, self.subpattern) == (other.behind, other.positive, other.subpattern)

class _RefGroup(_RegexBase):
    _opcode = {False: _OP.REF_GROUP, True: _OP.REF_GROUP_REV}
    _op_name = {False: "REF_GROUP", True: "REF_GROUP_REV"}
    def __init__(self, info, group):
        self.info, self.group = info, group
    def fix_groups(self):
        try:
            self.group = int(self.group)
        except ValueError:
            try:
                self.group = self.info.group_index[self.group]
            except KeyError:
                raise error("unknown group")
        if not 1 <= self.group <= self.info.group_count:
            raise error("unknown group")
    def compile(self, reverse=False):
        return [(self._opcode[reverse], self.group)]
    def remove_captures(self):
        raise error("group reference not allowed")
    def dump(self, indent=0, reverse=False):
        print "%s%s %s" % (_INDENT * indent, self._op_name[reverse], self.group)
    def __eq__(self, other):
        return type(self) is type(other) and self.group == other.group

class _RefGroupIgnore(_RefGroup):
    _opcode = {False: _OP.REF_GROUP_IGNORE, True: _OP.REF_GROUP_IGNORE_REV}
    _op_name = {False: "REF_GROUP_IGNORE", True: "REF_GROUP_IGNORE_REV"}

class _SearchAnchor(_RegexBase):
    def compile(self, reverse=False):
        return [(_OP.SEARCH_ANCHOR, )]
    def dump(self, indent=0, reverse=False):
        print "%sSEARCH_ANCHOR" % (_INDENT * indent)

class _Sequence(_StructureBase):
    def __init__(self, sequence=None):
        if sequence is None:
            sequence = []
        self.sequence = sequence
    def fix_groups(self):
        for subpattern in self.sequence:
            subpattern.fix_groups()
    def optimise(self):
        sequence = []
        for subpattern in self.sequence:
            subpattern = subpattern.optimise()
            if isinstance(subpattern, _Sequence):
                sequence.extend(subpattern.sequence)
            else:
                sequence.append(subpattern)
        if len(sequence) == 1:
            return sequence[0]
        return _Sequence(sequence)
    def pack_characters(self):
        sequence = []
        char_type, characters = _Character, []
        for subpattern in self.sequence:
            t = type(subpattern)
            if t is char_type:
                characters.append(subpattern.char_code)
            else:
                self._flush_characters(char_type, characters, sequence)
                characters = []
                if t in _all_char_types:
                    char_type = t
                    characters.append(subpattern.char_code)
                else:
                    sequence.append(subpattern.pack_characters())
        self._flush_characters(char_type, characters, sequence)
        if len(sequence) == 1:
            return sequence[0]
        return _Sequence(sequence)
    def is_empty(self):
        return all(subpattern.is_empty() for subpattern in self.sequence)
    def is_atomic(self):
        return all(subpattern.is_atomic() for subpattern in self.sequence)
    def contains_group(self):
        return any(subpattern.contains_group() for subpattern in self.sequence)
    def get_first(self):
        if self.sequence:
            return self.sequence[0]
        return None
    def drop_first(self):
        if len(self.sequence) == 2:
            return self.sequence[1]
        return _Sequence(self.sequence[1 : ])
    def get_last(self):
        if self.sequence:
            return self.sequence[-1]
        return None
    def drop_last(self):
        if len(self.sequence) == 2:
            return self.sequence[-2]
        return _Sequence(self.sequence[ : -1])
    def compile(self, reverse=False):
        code = []
        if reverse:
            for subpattern in reversed(self.sequence):
                code.extend(subpattern.compile(reverse))
        else:
            for subpattern in self.sequence:
                code.extend(subpattern.compile(reverse))
        return code
    def remove_captures(self):
        self.sequence = [subpattern.remove_captures() for subpattern in self.sequence]
        return self
    def dump(self, indent=0, reverse=False):
        if reverse:
            for subpattern in reversed(self.sequence):
                subpattern.dump(indent, reverse)
        else:
            for subpattern in self.sequence:
                subpattern.dump(indent, reverse)
    def _flush_characters(self, char_type, characters, sequence):
        if not characters:
            return
        if len(characters) == 1:
            sequence.append(char_type(characters[0]))
        else:
            sequence.append(_string_classes[char_type](characters))
    def __eq__(self, other):
        return type(self) is type(other) and self.sequence == other.sequence

class _Set(_RegexBase):
    _opcode = {False: _OP.SET, True: _OP.SET_REV}
    _op_name = {False: "SET", True: "SET_REV"}
    _pos_text = {False: "NON-MATCH", True: "MATCH"}
    def __init__(self, positive, ranges):
        self.positive, self.ranges = bool(positive), ranges
        self._key = self.__class__, self.ranges
    def optimise(self):
        ranges = []
        others = set()
        for member in self.ranges:
            r = member.get_range()
            if r:
                ranges.append(r)
            else:
                others.add(member)
        ranges.sort()
        for i in range(len(ranges), 1, -1):
            r1, r2 = ranges[i - 2 : i]
            if r1[1] + 1 >= r2[0]:
                ranges[i - 2 : i] = [(r1[0], max(r1[1], r2[1]))]
        if self.positive and not others and len(ranges) == 1:
            r = ranges[0]
            if r[0] == r[1]:
                return self._as_character(r[0])
        new_ranges = []
        for r in ranges:
            if r[0] == r[1]:
                new_ranges.append(_Character(r[0]))
            else:
                new_ranges.append(_SetRange(*r))
        return _Set(self.positive, new_ranges + list(others))
    def compile(self, reverse=False):
        code = [(self._opcode[reverse], int(self.positive))]
        ranges = []
        others = []
        for subpattern in self.ranges:
            c = subpattern.get_range()
            if c:
                ranges.append(c)
            else:
                others.extend(subpattern.compile())
        if ranges:
            code.extend(self._make_bitset(ranges))
        code.extend(others)
        code.append((-self._opcode[reverse], ))
        return code
    def dump(self, indent=0, reverse=False):
        print "%s%s %s" % (_INDENT * indent, self._op_name[reverse], self._pos_text[self.positive])
        for subpattern in self.ranges:
            subpattern.dump(indent + 1)
    BITS_PER_CODE = 32
    CODE_MASK = (1 << BITS_PER_CODE) - 1
    CODES_PER_SUBSET = 256 // BITS_PER_CODE
    SUBSET_MASK = (1 << 256) - 1
    def _make_bitset(self, ranges):
        code = []
        # values are: top_bits bitset
        bitset_dict = defaultdict(int)
        for r in ranges:
            lo_top, lo_bottom = r[0] >> 8, r[0] & 0xFF
            hi_top, hi_bottom = r[1] >> 8, r[1] & 0xFF
            if lo_top == hi_top:
                bitset_dict[lo_top] |= (1 << (hi_bottom + 1)) - (1 << lo_bottom)
            else:
                code.append((_OP.RANGE, r[0], r[1]))
        for top_bits, bitset in bitset_dict.items():
            if bitset:
                code.append((_OP.BITSET, top_bits) + tuple(self._bitset_to_codes(bitset)))
        return code
    def _bitset_to_codes(self, bitset):
        codes = []
        for i in range(self.CODES_PER_SUBSET):
            codes.append(bitset & self.CODE_MASK)
            bitset >>= self.BITS_PER_CODE
        return codes
    def _as_character(self, char_code):
        return _Character(char_code)

class _SetIgnore(_Set):
    _opcode = {False: _OP.SET_IGNORE, True: _OP.SET_IGNORE_REV}
    _op_name = {False: "SET_IGNORE", True: "SET_IGNORE_REV"}
    def _as_character(self, char_code):
        return _CharacterIgnore(char_code)

class _SetRange(_RegexBase):
    def __init__(self, min_value, max_value):
        self.min_value, self.max_value = min_value, max_value
        self._key = self.__class__, self.min_value, self.max_value
    def optimise(self):
        if self.min_value == self.max_value:
            return _Character(self.min_value)
        return self
    def compile(self, reverse=False):
        return [(_OP.RANGE, self.min_value, self.max_value)]
    def dump(self, indent=0, reverse=False):
        print "%sRANGE %s %s" % (_INDENT * indent, self.min_value, self.max_value)
    def get_range(self):
        return (self.min_value, self.max_value)

class _StartOfLine(_RegexBase):
    def compile(self, reverse=False):
        return [(_OP.START_OF_LINE, )]
    def dump(self, indent=0, reverse=False):
        print "%sSTART_OF_LINE" % (_INDENT * indent)

class _StartOfString(_RegexBase):
    def compile(self, reverse=False):
        return [(_OP.START_OF_STRING, )]
    def dump(self, indent=0, reverse=False):
        print "%sSTART_OF_STRING" % (_INDENT * indent)

class _String(_RegexBase):
    _opcode = {False: _OP.STRING, True: _OP.STRING_REV}
    _op_name = {False: "STRING", True: "STRING_REV"}
    def __init__(self, characters):
        self.characters = characters
        self._key = self.__class__, self.characters
    def compile(self, reverse=False):
        return [(self._opcode[reverse], len(self.characters)) + tuple(self.characters)]
    def dump(self, indent=0, reverse=False):
        print "%s%s %s" % (_INDENT * indent, self._op_name[reverse], " ".join(str(ch) for ch in self.characters))
    def get_first_char(self):
        raise error("internal error")
    def drop_first_char(self):
        raise error("internal error")

class _StringIgnore(_String):
    _opcode = {False: _OP.STRING_IGNORE, True: _OP.STRING_IGNORE_REV}
    _op_name = {False: "STRING_IGNORE", True: "STRING_IGNORE_REV"}

_all_char_types = (_Character, _CharacterIgnore)
_string_classes = {_Character: _String, _CharacterIgnore: _StringIgnore}

# Character escape sequences.
_CHARACTER_ESCAPES = {
    "a": ord("\a"),
    "b": ord("\b"),
    "f": ord("\f"),
    "n": ord("\n"),
    "r": ord("\r"),
    "t": ord("\t"),
    "v": ord("\v"),
}

# Predefined character set escape sequences.
_CHARSET_ESCAPES = {
    "d": _Category(True, _categories["DIGIT"]),
    "D": _Category(False, _categories["DIGIT"]),
    "s": _Category(True, _categories["SPACE"]),
    "S": _Category(False, _categories["SPACE"]),
    "w": _Category(True, _categories["WORD"]),
    "W": _Category(False, _categories["WORD"]),
}

# Positional escape sequences.
_POSITION_ESCAPES = {
    "A": _StartOfString(),
    "b": _Boundary(True),
    "B": _Boundary(False),
    "Z": _EndOfString(),
}

class _Source(object):
    "Scanner for the regular expression source string."
    def __init__(self, string):
        self.string = string
        self.pos = 0
        self.ignore_space = False
        self.sep = string[ : 0]
    def get(self):
        try:
            if self.ignore_space:
                while self.string[self.pos].isspace():
                    self.pos += 1
            ch = self.string[self.pos]
            self.pos += 1
            return ch
        except IndexError:
            return self.sep
    def match(self, substring):
        try:
            if self.ignore_space:
                while self.string[self.pos].isspace():
                    self.pos += 1
            if not self.string.startswith(substring, self.pos):
                return False
            self.pos += len(substring)
            return True
        except IndexError:
            return False
    def expect(self, substring):
        if not self.match(substring):
            raise error("missing %s" % substring)
    def at_end(self):
        pos = self.pos
        try:
            if self.ignore_space:
                while self.string[pos].isspace():
                    pos += 1
            return pos >= len(self.string)
        except IndexError:
            return True
    def tell(self):
        return self.pos
    def seek(self, pos):
        self.pos = pos

class _Info(object):
    "Info about the regular expression."
    def __init__(self, flags=0):
        self.global_flags = flags & _GLOBAL_FLAGS
        self.local_flags = flags & _LOCAL_FLAGS
        self.group_count = 0
        self.group_index = {}
        self.used_groups = set()
    def new_group(self, name=None):
        group = self.group_index.get(name)
        if group is not None:
            if group in self.used_groups:
                raise error("duplicate group name")
        else:
            self.group_count += 1
            group = self.group_count
            if name:
                self.group_index[name] = group
        self.used_groups.add(group)
        return group

if __name__ != "__main__":
    # We define _pattern_type here after all the support objects have been
    # defined.
    _pattern_type = type(_compile("", 0))

    # Register myself for pickling.
    import copy_reg

    def _pickle(p):
        return _compile, (p.pattern, p.flags)

    copy_reg.pickle(_pattern_type, _pickle, _compile)

# --------------------------------------------------------------------
# Experimental stuff (see python-dev discussions for details).

class Scanner:
    def __init__(self, lexicon, flags=0):
        self.lexicon = lexicon

        # Combine phrases into a compound pattern.
        patterns = []
        for phrase, action in lexicon:
            # Parse the regular expression.
            source = _Source(phrase)
            info = _Info(flags)
            source.ignore_space = info.local_flags & VERBOSE
            parsed = _parse_pattern(source, info)
            if not source.at_end():
                raise error("trailing characters")

            # We want to forbid capture groups within each phrase.
            patterns.append(parsed.remove_captures())

        # Combine all the subpatterns into one pattern.
        info = _Info(flags)
        patterns = [_Group(info, g + 1, p) for g, p in enumerate(patterns)]
        parsed = _Branch(patterns)

        # Optimise the compound pattern.
        parsed = parsed.optimise()

        # Compile the compound pattern. The result is a list of tuples.
        code = parsed.compile() + [(_OP.SUCCESS, )]

        # Flatten the code into a list of ints.
        code = _flatten_code(code)

        # Create the PatternObject.
        #
        # Local flags like IGNORECASE affect the code generation, but aren't
        # needed by the PatternObject itself. Conversely, global flags like
        # LOCALE _don't_ affect the code generation but _are_ needed by the
        # PatternObject.
        self.scanner = _regex.compile(None, flags & _GLOBAL_FLAGS, code, {}, {})
    def scan(self, string):
        result = []
        append = result.append
        match = self.scanner.scanner(string).match
        i = 0
        while True:
            m = match()
            if not m:
                break
            j = m.end()
            if i == j:
                break
            action = self.lexicon[m.lastindex - 1][1]
            if hasattr(action, '__call__'):
                self.match = m
                action = action(self, m.group())
            if action is not None:
                append(action)
            i = j
        return result, string[i : ]

def _create_header_file():
    import codecs
    import os

    header_file = codecs.open("_regex.h", "w", "utf-8")
    print "Header file written at %s\n" % os.path.abspath(header_file.name)

    header_file.write("""/*
 * Secret Labs' Regular Expression Engine
 *
 * regular expression matching engine
 *
 * Copyright (c) 1997-2001 by Secret Labs AB.  All rights reserved.
 *
 * NOTE: This file is generated by regex.py.  If you need
 * to change anything in here, edit regex.py and run it.
 *
 * 2010-01-16 mrab Re-written
 */

#define RE_MAGIC 20100116

/* Size of a code word (must be unsigned short or larger, and
   large enough to hold a Py_UNICODE character). */

#if SIZEOF_INT >= 4
#define RE_CODE unsigned int
#else
#define RE_CODE SIZEOF_LONG
#define RE_CODE unsigned long
#endif

#define RE_UNLIMITED (~(RE_CODE)0)

""")

    # The operators.
    op_list = sorted((value, name) for name, value in _OP.__dict__.items()
        if not name.startswith("_"))

    for value, name in op_list:
        header_file.write("#define RE_OP_%s %s\n" % (name, value))

    header_file.write("""
char* re_op_text[] = {
""")

    for value, name in op_list:
        header_file.write("    \"RE_OP_%s\",\n" % name)

    header_file.write("};\n")

    # The character categories.
    header_file.write("\n/* Character categories. */\n")

    # Sort by name length so that we get the shortest first.
    cat = {}
    for name, value in sorted(_categories.items(), key=lambda e: len(e[0])):
        cat.setdefault(value, name)

    # Sort by numerical order.
    for value, name in sorted(cat.items(), key=lambda e: e[0]):
        header_file.write("#define RE_CAT_%s %s\n" % (name, value))

    # The Unicode character properties.
    header_file.write("\n/* Unicode character properties. */\n")
    for name, mask in sorted(_property_masks.items()):
        header_file.write("#define RE_PROP_MASK_%s 0x%08X\n" % (name, mask))

    header_file.write("""
#define RE_PROP_MASK_ALNUM (RE_PROP_MASK_L | RE_PROP_MASK_ND)
#define RE_PROP_MASK_NONGRAPH (RE_PROP_MASK_Z | RE_PROP_MASK_C)
#define RE_PROP_MASK_PUNCT (RE_PROP_MASK_P | RE_PROP_MASK_S)
#define RE_PROP_MASK_SPACE (RE_PROP_MASK_ZL | RE_PROP_MASK_ZP | \\
  RE_PROP_MASK_CC | RE_PROP_MASK_CF)
#define RE_PROP_MASK_WORD (RE_PROP_MASK_L | RE_PROP_MASK_M | RE_PROP_MASK_N | \\
  RE_PROP_MASK_PC)
""")

    scripts = []
    for name, value_range in _script_ranges.items():
        scripts.append((_categories[name], name, value_range))

    scripts.sort()

    header_file.write("""
#define RE_MIN_SCRIPT %s
#define RE_MAX_SCRIPT %s

typedef struct RE_ScriptRange {
    unsigned int min_char;
    unsigned int max_char;
} RE_ScriptRange;

RE_ScriptRange re_script_ranges[] = {
""" % (scripts[0][0], scripts[-1][0]))

    for index, name, value_range in scripts:
        header_file.write("    {0x%X, 0x%X},\n" % value_range)

    header_file.write("};\n")

    # The ASCII character categories.
    header_file.write("\n/* ASCII character categories. */\n")

    cat = "DIGIT LOWER PUNCT SPACE UPPER XDIGIT"
    cat = [(n, 1 << i) for i, n in enumerate(cat.upper().split())]
    for name, mask in cat:
        header_file.write("#define RE_MASK_%s 0x%X}\n" % (name, mask))

    header_file.write("""
/* alpha = upper | lower */
#define RE_MASK_ALPHA (RE_MASK_UPPER | RE_MASK_LOWER)
/* alnum = alpha | digit */
#define RE_MASK_ALNUM (RE_MASK_ALPHA | RE_MASK_DIGIT)

char re_ascii_category[128] = {
""")
    mask_list = []
    cat = dict(cat)
    for ch in range(0x80):
        mask = 0
        c = unicodedata.category(unichr(ch))
        if c == "Nd":
            mask |= cat["DIGIT"]
        if c == "Ll":
            mask |= cat["LOWER"]
        if c.startswith(("P", "S")):
            mask |= cat["PUNCT"]
        if chr(ch) in " \t\r\n\v\f":
            mask |= cat["SPACE"]
        if c == "Lu":
            mask |= cat["UPPER"]
        if chr(ch) in _HEX_DIGITS:
            mask |= cat["XDIGIT"]
        mask_list.append(mask)
        if len(mask_list) == 8:
            header_file.write("    %s\n" % (" ".join("0x%02X," % mask for mask in mask_list)))
            mask_list = []
    header_file.write("};\n")

    header_file.write("\n")
    for name in sorted(__all__):
        if len(name) > 1 and name.isupper():
            value = globals()[name]
            header_file.write("#define RE_FLAG_%s 0x%X\n" % (name, value))

    header_file.close()

if __name__ == "__main__":
    _create_header_file()
