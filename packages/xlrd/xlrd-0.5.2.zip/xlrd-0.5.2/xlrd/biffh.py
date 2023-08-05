##
# Support module for the xlrd package.
##

DEBUG = 0

from struct import unpack
import sys

class XLRDError(Exception):
    pass

FUN, FDT, FNU, FGE, FTX = range(5) # unknown, date, number, general, text
DATEFORMAT = FDT
NUMBERFORMAT = FNU

XL_CELL_EMPTY, XL_CELL_TEXT, XL_CELL_NUMBER, XL_CELL_DATE, XL_CELL_BOOLEAN, XL_CELL_ERROR = range(6)

biff_text_from_num = {
    20: "2",
    30: "3",
    40: "4S",
    45: "4W",
    50: "5",
    70: "7",
    80: "8",
    85: "8X",
    }

##
# <p>This dictionary can be used to produce a text version of the internal codes
# that Excel uses for error cells. Here are its contents:
# <pre>
# 0x00: '#NULL!',  # Intersection of two cell ranges is empty
# 0x07: '#DIV/0!', # Division by zero
# 0x0F: '#VALUE!', # Wrong type of operand
# 0x17: '#REF!',   # Illegal or deleted cell reference
# 0x1D: '#NAME?',  # Wrong function or range name
# 0x24: '#NUM!',   # Value range overflow
# 0x2A: '#N/A!',   # Argument or function not available
# </pre></p>

error_text_from_code = {
    0x00: '#NULL!',  # Intersection of two cell ranges is empty
    0x07: '#DIV/0!', # Division by zero
    0x0F: '#VALUE!', # Wrong type of operand
    0x17: '#REF!',   # Illegal or deleted cell reference
    0x1D: '#NAME?',  # Wrong function or range name
    0x24: '#NUM!',   # Value range overflow
    0x2A: '#N/A!',   # Argument or function not available
}

BIFF_FIRST_UNICODE = 80

XL_WORKBOOK_GLOBALS = WBKBLOBAL = 0x5
XL_WORKBOOK_GLOBALS_4W = 0x100
XL_WORKSHEET = WRKSHEET = 0x10

XL_BOUNDSHEET_WORKSHEET = 0x00
XL_BOUNDSHEET_CHART     = 0x02
XL_BOUNDSHEET_VB_MODULE = 0x06

# XL_RK2 = 0x7e
XL_ARRAY = 0x221
XL_BOF = 0x809
XL_BOOLERR = 0x205
XL_BOUNDSHEET = 0x85
XL_BUILTINFMTCOUNT = 0x56
XL_CODEPAGE = 0x42
XL_CONTINUE = 0x3c
XL_COUNTRY = 0x8C
XL_DATEMODE = 0x22
XL_DIMENSION = 0x200
XL_DIMENSION2 = 0x0
XL_EOF = 0x0a
XL_EXTSST = 0xff
XL_FILEPASS = 0x2f
XL_FORMAT = 0x41e
XL_FORMAT2 = 0x1E # BIFF2, BIFF3
XL_FORMULA = 0x6
XL_FORMULA3 = 0x206
XL_FORMULA4 = 0x406
XL_INDEX = 0x20b
XL_LABEL = 0x204
XL_LABEL2 = 0x04
XL_LABELSST = 0xfd
XL_MSO_DRAWING = 0x00EC
XL_MSO_DRAWING_GROUP = 0x00EB
XL_MSO_DRAWING_SELECTION = 0x00ED
XL_MULRK = 0xbd
XL_NAME = 0x18
XL_NOTE = 0x1c
XL_NUMBER = 0x203
XL_OBJ = 0x5D
XL_RK = 0x27e
XL_ROW = 0x208
XL_RSTRING = 0xd6
XL_SHEETHDR = 0x8F # BIFF4W only
XL_SHEETSOFFSET = 0x8E # BIFF4W only
XL_SHRFMLA = 0x04bc
XL_SST = 0xfc
XL_STRING = 0x207
XL_TABLEOP = 0x236
XL_TABLEOP2 = 0x37
XL_TABLEOP_B2 = 0x36
XL_TXO = 0x1b6
XL_UNCALCED = 0x5e
XL_UNKNOWN = 0xffff
XL_WRITEACCESS = 0x5C
XL_XF = 0xe0
XL_XF2 = 0x0043 # BIFF2 version of XF record
XL_XF3 = 0x0243 # BIFF3 version of XF record
XL_XF4 = 0x0443 # BIFF4 version of XF record

boflen = {0x0809: 8, 0x0409: 6, 0x0209: 6, 0x0009: 4}
bofcodes = (0x0809, 0x0409, 0x0209, 0x0009)

_cell_opcode_list = [
    XL_BOOLERR,
    XL_FORMULA,
    XL_FORMULA3,
    XL_FORMULA4,
    XL_LABEL,
    XL_LABELSST,
    XL_MULRK,
    XL_NUMBER,
    XL_RK,
    XL_RSTRING,
    ]
_cell_opcode_dict = {}
for _cell_opcode in _cell_opcode_list:
    _cell_opcode_dict[_cell_opcode] = 1
is_cell_opcode = _cell_opcode_dict.has_key

def unpack_string(data, pos, encoding, lenlen=1):
    nchars = unpack('<' + 'BH'[lenlen-1], data[pos:pos+lenlen])[0]
    pos += lenlen
    return unicode(data[pos:pos+nchars], encoding)

def unpack_unicode(data, pos, lenlen=2):
    "Return unicode_strg"
    nchars = unpack('<' + 'BH'[lenlen-1], data[pos:pos+lenlen])[0]
    pos += lenlen
    options = ord(data[pos])
    pos += 1
    # phonetic = options & 0x04
    # richtext = options & 0x08
    if options & 0x08:
        # rt = unpack('<H', data[pos:pos+2])[0] # unused
        pos += 2
    if options & 0x04:
        # sz = unpack('<i', data[pos:pos+4])[0] # unused
        pos += 4
    if options & 0x01:
        # Uncompressed UTF-16-LE
        rawstrg = data[pos:pos+2*nchars]
        # if DEBUG: print "nchars=%d pos=%d rawstrg=%r" % (nchars, pos, rawstrg)
        # strg = rawstrg.decode('utf-16le')
        strg = unicode(rawstrg, 'utf-16le')
        # pos += 2*nchars
    else:
        # Note: this is COMPRESSED (not ASCII!) encoding!!!
        # Merely returning the raw bytes would work OK 99.99% of the time
        # if the local codepage was cp1252 -- however this would rapidly go pear-shaped
        # for other codepages so we grit our Anglocentric teeth and return Unicode :-)
        strg = u''.join([unichr(ord(x)) for x in data[pos:pos+nchars]])
        # pos += nchars
    # if richtext:
    #     pos += 4 * rt
    # if phonetic:
    #     pos += sz
    # return (strg, pos)
    return strg

brecstrg = """\
0000 DIMENSIONS
0001 BLANK
0002 INTEGER
0003 NUMBER
0004 LABEL
0005 BOOLERR
0006 FORMULA
0007 STRING
0008 ROW
0009 BOF
000A EOF
000B INDEX
000C CALCCOUNT
000D CALCMODE
000E PRECISION
000F REFMODE
0010 DELTA
0011 ITERATION
0012 PROTECT
0013 PASSWORD
0014 HEADER
0015 FOOTER
0016 EXTERNCOUNT
0017 EXTERNSHEET
0018 NAME
0019 WINDOWPROTECT
001A VERTICALPAGEBREAKS
001B HORIZONTALPAGEBREAKS
001C NOTE
001D SELECTION
001E FORMAT
001F BUILTINFMTCOUNT
0020 COLUMNDEFAULT
0021 ARRAY
0022 DATEMODE
0023 EXTERNNAME
0024 COLWIDTH
0025 DEFAULTROWHEIGHT
0026 LEFTMARGIN
0027 RIGHTMARGIN
0028 TOPMARGIN
0029 BOTTOMMARGIN
002A PRINTHEADERS
002B PRINTGRIDLINES
002F FILEPASS
0031 FONT
0036 TABLEOP_B2
0037 TABLEOP2
003C CONTINUE
003D WINDOW1
003E WINDOW2
0040 BACKUP
0041 PANE
0042 CODEPAGE
0043 XF_B2
0044 IXFE
0045 EFONT
004D PLS
0051 DCONREF
0055 DEFCOLWIDTH
0056 BUILTINFMTCOUNT
0059 XCT
005A CRN
005B FILESHARING
005C WRITEACCESS
005D OBJECT
005E UNCALCED
005F SAVERECALC
0063 OBJECTPROTECT
007D COLINFO
007E RK2_mythical_?
0080 GUTS
0081 WSBOOL
0082 GRIDSET
0083 HCENTER
0084 VCENTER
0085 BOUNDSHEET
0086 WRITEPROT
008C COUNTRY
008D HIDEOBJ
008E SHEETSOFFSET
008F SHEETHDR
0090 SORT
0092 PALETTE
009C FNGROUPCOUNT
0099 STANDARDWIDTH
00A0 SCL
00A1 SETUP
00AB GCW
00BD MULRK
00BE MULBLANK
00C1 MMS
00D6 RSTRING
00D7 DBCELL
00DA BOOKBOOL
00DD SCENPROTECT
00E0 XF
00E1 INTERFACEHDR
00E2 INTERFACEEND
00E5 MERGEDCELLS
00E9 BITMAP
00EB MSO_DRAWING_GROUP
00EC MSO_DRAWING
00ED MSO_DRAWING_SELECTION
00EF PHONETIC
00FC SST
00FD LABELSST
00FF EXTSST
013D TABID
015F LABELRANGES
0160 USESELFS
0161 DSF
01AE SUPBOOK
01AF PROTECTIONREV4
01B0 CONDFMT
01B2 DVAL
01B6 TXO
01B7 REFRESHALL
01B8 HLINK
01BC PASSWORDREV4
01BE DV
01C0 XL9FILE
01C1 RECALCID
0200 DIMENSIONS
0201 BLANK
0203 NUMBER
0204 LABEL
0205 BOOLERR
0206 FORMULA_B3
0207 STRING
0208 ROW
0209 BOF
020B INDEX
0218 NAME
0221 ARRAY
0223 EXTERNNAME
0225 DEFAULTROWHEIGHT
0231 FONT
0236 TABLEOP
023E WINDOW2
0243 XF_B3
027E RK
0293 STYLE
0406 FORMULA_B4
0409 BOF
041E FORMAT
0443 XF_B4
04BC SHRFMLA
0800 QUICKTIP
0809 BOF
0862 SHEETLAYOUT
0867 SHEETPROTECTION
0868 RANGEPROTECTION
"""

biff_rec_name_dict = {}
lines = brecstrg.splitlines()
for buff in lines:
    numh, name = buff.split()
    biff_rec_name_dict[int(numh, 16)] = name

def hex_char_dump(strg, ofs, dlen, base=0, fout=sys.stdout):
    endpos = min(ofs + dlen, len(strg))
    pos = ofs
    while pos < endpos:
        endsub = min(pos + 16, endpos)
        substrg = strg[pos:endsub]
        lensub = endsub - pos
        if lensub <= 0 or lensub != len(substrg):
            print '??? hex_char_dump: ofs=%d dlen=%d base=%d -> endpos=%d pos=%d endsub=%d substrg=%r' \
                % (ofs, dlen, base, endpos, pos, endsub, substrg)
            break
        hexd = ''.join(["%02x " % ord(c) for c in substrg])
        chard = ''
        for c in substrg:
            if c == '\0':
                c = '~'
            elif not (' ' <= c <= '~'):
                c = '?'
            chard += c
        print >> fout, "%5d:      %-48s %s" % (base+pos-ofs, hexd, chard)
        pos = endsub


def biff_dump(mem, stream_offset, stream_len, base=0, fout=sys.stdout):
    pos = stream_offset
    stream_end = stream_offset + stream_len
    adj = base - stream_offset
    dummies = 0
    while stream_end - pos >= 4:
        rc, length = unpack('<HH', mem[pos:pos+4])
        if rc == 0 and length == 0:
            if mem[pos:] == '\0' * (stream_end - pos):
                dummies = stream_end - pos
                savpos = pos
                pos = stream_end
                break
            if dummies:
                dummies += 4
            else:
                savpos = pos
                dummies = 4
            pos += 4
        else:
            if dummies:
                print >> fout, "%5d: ---- %d zero bytes skipped ----" % (adj+savpos, dummies)
                dummies = 0
            recname = biff_rec_name_dict.get(rc, '<UNKNOWN>')
            print >> fout, "%5d: %04x %s len = %04x (%d)" % (adj+pos, rc, recname, length, length)
            pos += 4
            hex_char_dump(mem, pos, length, adj+pos, fout)
            pos += length
    if dummies:
        print >> fout, "%5d: ---- %d zero bytes skipped ----" % (adj+savpos, dummies, )
    if pos < stream_end:
        print >> fout, "%5d: ---- Misc bytes at end ----"  % (adj + pos,)
        hex_char_dump(mem, pos, stream_end-pos, adj + pos, fout)
    elif pos > stream_end:
        print >> fout, "Last dumped record has length (%d) that is too large" % length

encoding_from_codepage = {
    1200 : 'utf_16_le',
    10000: 'mac_roman',
    10006: 'mac_greek', # guess
    10007: 'mac_cyrillic', # guess
    10029: 'mac_latin2', # guess
    10079: 'mac_iceland', # guess
    10081: 'mac_turkish', # guess
    32768: 'mac_roman',
    32769: 'cp1252',
    }
# some more guessing, for Indic scripts
# codepage 57000 range:
# 2 Devanagari [0]
# 3 Bengali [1]
# 4 Tamil [5]
# 5 Telegu [6]
# 6 Assamese [1] c.f. Bengali
# 7 Oriya [4]
# 8 Kannada [7]
# 9 Malayalam [8]
# 10 Gujarati [3]
# 11 Gurmukhi [2]