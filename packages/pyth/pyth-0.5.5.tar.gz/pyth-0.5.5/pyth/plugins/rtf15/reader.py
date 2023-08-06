"""
Read documents from RTF 1.5

http://www.biblioscape.com/rtf15_spec.htm

This module is potentially compatible with RTF versions up to 1.9.1,
but may not ignore all necessary control groups.
"""
import string, re, itertools

from pyth import document
from pyth.format import PythReader

_CONTROLCHARS = set(string.ascii_letters + string.digits + "-*")
_DIGITS = set(string.digits)

# Maps Symbol typeface to Unicode, extracted from http://en.wikipedia.org/wiki/Symbol_(typeface)
symbolTable = {
    33: 33, 34: 8704, 35: 35, 36: 8707, 37: 37, 38: 38, 39: 8717, 40: 40, 41: 41, 42: 42, 43: 43, 44: 44, 45: 45, 46: 46, 
    47: 47, 48: 48, 49: 49, 50: 50, 51: 51, 52: 52, 53: 53, 54: 54, 55: 55, 56: 56, 57: 57, 58: 58, 59: 59, 60: 60, 61: 61,
    62: 62, 63: 63, 64: 8773, 65: 913, 66: 914, 67: 935, 68: 916, 69: 917, 70: 934, 71: 915, 72: 919, 73: 921, 74: 977, 
    75: 922, 76: 923, 77: 924, 78: 925, 79: 927, 80: 928, 81: 920, 82: 929, 83: 931, 84: 932, 85: 933, 86: 962, 87: 937, 
    88: 926, 89: 936, 90: 918, 91: 91, 92: 8756, 93: 93, 94: 8869, 95: 95, 96: 63717, 97: 945, 98: 946, 99: 967, 100: 948, 
    101: 949, 102: 966, 103: 947, 104: 951, 105: 953, 106: 981, 107: 954, 108: 955, 109: 956, 110: 957, 111: 959, 112: 960, 
    113: 952, 114: 961, 115: 963, 116: 964, 117: 965, 118: 982, 119: 969, 120: 958, 121: 968, 122: 950, 123: 123, 124: 124, 
    125: 125, 126: 126, 160: 8364, 161: 978, 162: 697, 163: 8804, 164: 8260, 165: 8734, 166: 402, 167: 9827, 168: 9830, 
    169: 9829, 170: 9824, 171: 8596, 172: 8592, 173: 8593, 174: 8594, 175: 8595, 176: 176, 177: 177, 178: 698, 179: 8805, 
    180: 215, 181: 8733, 182: 8706, 183: 8226, 184: 247, 185: 8800, 186: 8801, 187: 8776, 188: 8230, 189: 9168, 190: 9135, 
    191: 8629, 192: 8501, 193: 8465, 194: 8476, 195: 8472, 196: 8855, 197: 8853, 198: 8709, 199: 8745, 200: 8746, 201: 8835, 
    202: 8839, 203: 8836, 204: 8834, 205: 8838, 206: 8712, 207: 8713, 208: 8736, 209: 8711, 210: 174, 211: 169, 212: 8482, 
    213: 8719, 214: 8730, 215: 8901, 216: 172, 217: 8743, 218: 8744, 219: 8660, 220: 8656, 221: 8657, 222: 8658, 223: 8659,
    224: 9674, 225: 12296, 226: 174, 227: 169, 228: 8482, 229: 8721, 230: 9115, 231: 9116, 232: 9117, 233: 9121, 234: 9122, 
    235: 9123, 236: 9127, 237: 9128, 238: 9129, 239: 9130, 241: 12297, 242: 8747, 243: 8992, 244: 9134, 245: 8993, 246: 9118, 
    247: 9119, 248: 9120, 249: 9124, 250: 9125, 251: 9126, 252: 9131, 253: 9132, 254: 9133}

_CODEPAGES = {
    0: "cp1252",   # ANSI
    1: "cp1252",   # Default (this is wrong, but there is no right)

    2: symbolTable,   # Symbol
    77: "mac-roman", # Mac Roman

    # Does Python have built-in support for these? What is it?
    # 78: "10001", # Mac Shift Jis
    # 79: "10003", # Mac Hangul
    # 80: "10008", # Mac GB2312
    # 81: "10002", # Mac Big5
    # 83: "10005", # Mac Hebrew

    84: "mac-arabic", # Mac Arabic
    85: "mac-greek", # Mac Greek
    86: "mac-turkish", # Mac Turkish

    # 87: "10021", # Mac Thai
    # 88: "10029", # Mac East Europe
    # 89: "10007", # Mac Russian

    128: "cp932",  # Shift JIS
    129: "cp949",  # Hangul
    130: "cp1361", # Johab
    134: "cp936",  # GB2312
    136: "cp950",  # Big5
    161: "cp1253", # Greek
    162: "cp1254", # Turkish
    163: "cp1258", # Vietnamese
    177: "cp1255", # Hebrew
    178: "cp1256", # Arabic 
    186: "cp1257", # Baltic
    204: "cp1251", # Russian
    222: "cp874",  # Thai
    238: "cp1250", # Eastern European
    254: "cp437",  # PC 437
    255: "cp850",  # OEM
}





class BackslashEscape(Exception):
    pass


class Rtf15Reader(PythReader):

    @classmethod
    def read(self, source):
        """
        source: A list of P objects.
        """

        reader = Rtf15Reader(source)
        return reader.go()


    def __init__(self, source):
        self.source = source
        self.document = document.Document


    def go(self):
        self.source.seek(0)

        if self.source.read(5) != r"{\rtf":
            from pyth.errors import WrongFileType
            raise WrongFileType("Doesn't look like an RTF file")

        self.source.seek(0)

        self.group = Group()
        self.charsetTable = None
        self.stack = [self.group]
        self.parse()
        return self.build()


    def parse(self):
        while True:
            next = self.source.read(1)

            if not next:
                break

            if next in '\r\n':
                continue
            if next == '{':
                subGroup = Group(self.group, self.charsetTable)
                self.stack.append(subGroup)
                self.group = subGroup
            elif next == '}':
                subGroup = self.stack.pop()
                self.group = self.stack[-1]

                subGroup.finalize()
                if subGroup.specialMeaning == 'FONT_TABLE':
                    self.charsetTable = subGroup.charsetTable
                self.group.content.append(subGroup)

            elif next == '\\':
                control, digits = self.getControl()
                self.group.handle(control, digits)
            else:
                self.group.char(unicode(next))


    def getControl(self):
        chars = []
        digits = []
        current = chars
        first = True
        while True:
            next = self.source.read(1)

            if not next:
                break

            if first and next == '\\':
                chars.extend("control_symbol")
                digits.append(next)
                break

            if first and next in '\r\n':
                # Special-cased in RTF, equivalent to a \par
                chars.extend("par")
                break

            first = False

            if next == "'":
                # ANSI escape, takes two hex digits
                chars.extend("ansi_escape")
                digits.extend(self.source.read(2))
                break

            if next == ' ':
                # Don't rewind, the space is just a delimiter
                break

            if next not in _CONTROLCHARS:
                # Rewind, it's a meaningful character
                self.source.seek(-1, 1)
                break

            if next in _DIGITS:
                current = digits

            current.append(next)

        return "".join(chars), "".join(digits)


    def build(self):
        doc = document.Document()
       
        ctx = DocBuilder(doc)

        for bit in self.group.flatten():
            typeName = type(bit).__name__
            getattr(ctx, "handle_%s" % typeName)(bit)

        ctx.flushParagraph()

        return doc



class DocBuilder(object):

    def __init__(self, doc):
        self.run = []
        self.propStack = [{}]
        self.block = None

        self.listLevel = None
        self.listStack = [doc]


    def flushRun(self):
        if self.block is None:
            self.block = document.Paragraph()

        self.block.content.append(
            document.Text(self.propStack[-1].copy(), 
                          [u"".join(self.run)]))

        self.run[:] = []


    def cleanParagraph(self):
        """
        Compress text runs, remove whitespace at start and end, 
        skip empty blocks, etc
        """

        runs = self.block.content

        if not runs:
            self.block = None
            return

        joinedRuns = []
        hasContent = False

        for run in runs:

            if run.content[0]: 
                hasContent = True
            else: 
                continue

            # For whitespace-only groups, remove any property stuff,
            # to avoid extra markup in output
            if not run.content[0].strip():
                run.properties = {}

            # Join runs only if their properties match
            if joinedRuns and (run.properties == joinedRuns[-1].properties):
                joinedRuns[-1].content[0] += run.content[0]
            else:
                joinedRuns.append(run)

        if hasContent:
            # Strip beginning of paragraph
            joinedRuns[0].content[0] = joinedRuns[0].content[0].lstrip()
            # And then strip the end
            joinedRuns[-1].content[0] = joinedRuns[-1].content[0].rstrip()
            self.block.content = joinedRuns
        else:
            self.block = None


    def flushParagraph(self):
        self.flushRun()
        if self.block.content:
            self.cleanParagraph()
            if self.block is not None:
                self.listStack[-1].append(self.block)


    def handle_unicode(self, bit):
        self.run.append(bit)


    def handle_Push(self, _):
        self.propStack.append(self.propStack[-1].copy())


    def handle_Pop(self, _):
        self.flushRun()
        self.propStack.pop()


    def handle_Para(self, para):
        
        self.flushParagraph()

        prevListLevel = self.listLevel
        self.listLevel = para.listLevel

        if self.listLevel > prevListLevel:
            l = document.List()
            self.listStack.append(l)

        elif self.listLevel < prevListLevel:
            l = self.listStack.pop()
            self.listStack[-1].append(l)

        self.block = None


    def handle_Reset(self, _):
        self.flushRun()
        self.propStack[-1].clear()

    
    def handle_ReadableMarker(self, marker):
        self.flushRun()
        if marker.val:
            # RTF needs underline markers for hyperlinks,
            # but nothing else does. If we're in a hyperlink,
            # ignore underlines.
            if 'url' in self.propStack[-1] and marker.name == 'underline':
                return

            self.propStack[-1][marker.name] = marker.val
        else:
            if marker.name in self.propStack[-1]:
                del self.propStack[-1][marker.name]



class Group(object):

    def __init__(self, parent=None, charsetTable=None):
        self.parent = parent

        if parent:
            self.props = parent.props.copy()
            self.charset = self.parent.charset
        else:
            self.props = {}
            self.charset = 'cp1252' # ?

        self.specialMeaning = None
        self.skip = False
        self.url = None
        self.currentParaTag = None
        self.destination = False

        self.charsetTable = charsetTable

        self.content = []


    def handle(self, control, digits):

        if control == '*':
            self.destination = True
            return

        handler = getattr(self, 'handle_%s' % control, None)
        if handler is None:
            return

        if digits:
            handler(digits)
        else:
            handler()


    def char(self, char):
        self.content.append(char)


    def _finalize(self):
        
        if self.destination:
            self.skip = True

        if self.specialMeaning is not None:
            self.skip = True

        if self.skip:
            return       

        stuff = []
        i = 0
        while i < len(self.content):
            thing = self.content[i]
            if isinstance(thing, Skip):
                i += thing.count
            else:
                stuff.append(thing)
            i += 1

        self.content = stuff


    # This is only the default,
    # and is overridden by some controls
    finalize = _finalize


    def flatten(self):
        if self.skip:
            return []

        stuff = [Push]
        for thing in self.content:
            if isinstance(thing, Group):
                stuff.extend(thing.flatten())
            else:
                stuff.append(thing)
        stuff.append(Pop)

        return stuff


    def handle_fonttbl(self):
        self.specialMeaning = 'FONT_TABLE'
        self.charsetTable = {}


    def handle_f(self, fontNum):
        if 'FONT_TABLE' in (self.parent.specialMeaning, self.specialMeaning):
            self.fontNum = int(fontNum)
        elif self.charsetTable is not None:
            self.charset = self.charsetTable[int(fontNum)]

            
    def handle_fcharset(self, charsetNum):
        if 'FONT_TABLE' in (self.parent.specialMeaning, self.specialMeaning):
            # Theoretically, \fN should always be before \fcharsetN
            # I don't really expect that will always be true, but let's crash
            # if it's not, and see if it happens in the real world.
            charset = _CODEPAGES.get(int(charsetNum))

            # XXX Todo: Figure out a more graceful way to handle the fact that
            # RTF font declarations can be in their own groups or not
            if self.parent.charsetTable is not None:
                self.parent.charsetTable[self.fontNum] = charset
            else: 
                self.charsetTable[self.fontNum] = charset


    def handle_ansi_escape(self, code):
        code = int(code, 16)

        if isinstance(self.charset, dict):
            uni_code = self.charset.get(code)
            if uni_code is None:
                char = '?'
            else:
                char = unichr(uni_code)
            

        else:
            try:
                char = chr(code).decode(self.charset)
            except UnicodeDecodeError:
                char = '?'

        self.content.append(char)


    def handle_control_symbol(self, symbol):
        # Ignore ~, -, and _, since they are optional crap.
        if symbol in '\\{}':
            self.content.append(unicode(symbol))


    def handle_u(self, codepoint):
        self.content.append(unichr(int(codepoint)))
        self.content.append(Skip(self.props.get('unicode_skip', 1)))


    def handle_par(self):
        p = Para()
        self.content.append(p)
        self.currentParaTag = p


    def handle_pard(self):
        self.content.append(Reset)


    def handle_plain(self):
        self.content.append(Reset)


    def handle_line(self):
        self.content.append(u"\n")


    def handle_b(self, onOff=None):
        val = onOff in (None, "", "1")
        self.content.append(ReadableMarker("bold", val))


    def handle_i(self, onOff=None):
        val = onOff in (None, "", "1")
        self.content.append(ReadableMarker("italic", val))


    def handle_ul(self, onOff=None):
        val = onOff in (None, "", "1")
        self.content.append(ReadableMarker("underline", val))


    def handle_ilvl(self, level):
        if self.currentParaTag is not None:
            self.currentParaTag.listLevel = level
        else:
            # Well, now we're in trouble. But I'm pretty sure this
            # isn't supposed to happen anyway.
            pass


    def handle_up(self, amount):
        self.content.append(ReadableMarker("super", True))

    def handle_super(self):
        self.content.append(ReadableMarker("super", True))

    def handle_dn(self, amount):
        self.content.append(ReadableMarker("sub", True))

    def handle_sub(self):
        self.content.append(ReadableMarker("sub", True))

    def handle_emdash(self):
        self.content.append(u'\u2014')

    def handle_endash(self):
        self.content.append(u'\u2013')

    def handle_lquote(self):
        self.content.append(u'\u2018')

    def handle_rquote(self):
        self.content.append(u'\u2019')

    def handle_ldblquote(self):
        self.content.append(u'\u201C')

    def handle_rdblquote(self):
        self.content.append(u'\u201D')


    def handle_field(self):
        def finalize():
            if len(self.content) != 2:
                return u""

            destination, content = self.content

            # The destination isn't allowed to contain any controls,
            # so this should be safe.
            # Except when it isn't, like this:
            # {\field{\*\fldinst {\rtlch\fcs1 \af0 \ltrch\fcs0 \insrsid15420660  PAGE   \\* MERGEFORMAT }}
            try:
                destination = u"".join(destination.content)
            except:
                return u""

            match = re.match(ur'HYPERLINK "(.*)"', destination)
            if match:
                content.skip = False
                self.content = [ReadableMarker("url", match.group(1)),
                                content]
            else:
                return u""

        self.finalize = finalize


    def __repr__(self):
        return "G(%s)" % repr(self.content)

    def ignore(self, _=None):
        self.skip = True


    # Header
    handle_filetbl = ignore
    handle_colortbl = ignore
    handle_stylesheet = ignore
    handle_listtable = ignore
    handle_listoverridetable = ignore
    handle_revtbl = ignore

    handle_mmath = ignore

    handle_header = ignore
    handle_footer = ignore
    handle_headerl = ignore
    handle_headerr = ignore
    handle_headerf = ignore
    handle_footerl = ignore
    handle_footerr = ignore
    handle_footerf = ignore


    # Document
    handle_info = ignore
    handle_docfmt = ignore
    handle_pgdsctbl = ignore
    handle_listtext = ignore

    # Revision hacks
    handle_revauthdel = ignore




class Skip(object):
    def __init__(self, count):
        self.count = count


class ReadableMarker(object):
    def __init__(self, name=None, val=None):
        if name is not None:
            self.name = name
        self.val = val

    def __repr__(self):
        if self.val is None:
            return "!%s!" % self.name
        else:
            return "!%s::%s!" % (self.name, self.val)


class Para(ReadableMarker):
    listLevel = None

    def __init__(self):
        ReadableMarker.__init__(self, "Para")

    def __repr__(self):
        return "!Para:%s!" % self.listLevel


class Reset(ReadableMarker):
    name = "Reset"

class Push(ReadableMarker):
    name = "Push"

class Pop(ReadableMarker):
    name = "Pop"


# Yes, yes, I know, I'll clean it up later.
Reset = Reset()
Push = Push()
Pop = Pop()
