"table definitions"
import os
import sys
import csv
import codecs
import locale
import unicodedata
import weakref
from array import array
from decimal import Decimal
from shutil import copyfileobj
from dbf import _io as io
from dbf.dates import Date, DateTime, Time
from dbf.exceptions import Bof, Eof, DbfError, DataOverflow, FieldMissing, NonUnicode

input_decoding = locale.getdefaultlocale()[1]    # treat non-unicode data as ...
default_codepage = 'cp1252'  # if no codepage specified on dbf creation, use this
return_ascii = True         # convert back to icky ascii, losing chars if no mapping

version_map = {
        '\x02' : 'FoxBASE',
        '\x03' : 'dBase III Plus',
        '\x04' : 'dBase IV',
        '\x05' : 'dBase V',
        '\x30' : 'Visual FoxPro',
        '\x31' : 'Visual FoxPro (auto increment field)',
        '\x43' : 'dBase IV SQL',
        '\x7b' : 'dBase IV w/memos',
        '\x83' : 'dBase III Plus w/memos',
        '\x8b' : 'dBase IV w/memos',
        '\x8e' : 'dBase IV w/SQL table',
        '\xf5' : 'FoxPro w/memos'}

code_pages = {
        '\x00' : ('ascii', "plain ol' ascii"),
        '\x01' : ('cp437', 'U.S. MS-DOS'),
        '\x02' : ('cp850', 'International MS-DOS'),
        '\x03' : ('cp1252', 'Windows ANSI'),
        '\x04' : ('mac_roman', 'Standard Macintosh'),
        '\x08' : ('cp865', 'Danish OEM'),
        '\x09' : ('cp437', 'Dutch OEM'),
        '\x0A' : ('cp850', 'Dutch OEM (secondary)'),
        '\x0B' : ('cp437', 'Finnish OEM'),
        '\x0D' : ('cp437', 'French OEM'),
        '\x0E' : ('cp850', 'French OEM (secondary)'),
        '\x0F' : ('cp437', 'German OEM'),
        '\x10' : ('cp850', 'German OEM (secondary)'),
        '\x11' : ('cp437', 'Italian OEM'),
        '\x12' : ('cp850', 'Italian OEM (secondary)'),
        '\x13' : ('cp932', 'Japanese Shift-JIS'),
        '\x14' : ('cp850', 'Spanish OEM (secondary)'),
        '\x15' : ('cp437', 'Swedish OEM'),
        '\x16' : ('cp850', 'Swedish OEM (secondary)'),
        '\x17' : ('cp865', 'Norwegian OEM'),
        '\x18' : ('cp437', 'Spanish OEM'),
        '\x19' : ('cp437', 'English OEM (Britain)'),
        '\x1A' : ('cp850', 'English OEM (Britain) (secondary)'),
        '\x1B' : ('cp437', 'English OEM (U.S.)'),
        '\x1C' : ('cp863', 'French OEM (Canada)'),
        '\x1D' : ('cp850', 'French OEM (secondary)'),
        '\x1F' : ('cp852', 'Czech OEM'),
        '\x22' : ('cp852', 'Hungarian OEM'),
        '\x23' : ('cp852', 'Polish OEM'),
        '\x24' : ('cp860', 'Portugese OEM'),
        '\x25' : ('cp850', 'Potugese OEM (secondary)'),
        '\x26' : ('cp866', 'Russian OEM'),
        '\x37' : ('cp850', 'English OEM (U.S.) (secondary)'),
        '\x40' : ('cp852', 'Romanian OEM'),
        '\x4D' : ('cp936', 'Chinese GBK (PRC)'),
        '\x4E' : ('cp949', 'Korean (ANSI/OEM)'),
        '\x4F' : ('cp950', 'Chinese Big 5 (Taiwan)'),
        '\x50' : ('cp874', 'Thai (ANSI/OEM)'),
        '\x57' : ('cp1252', 'ANSI'),
        '\x58' : ('cp1252', 'Western European ANSI'),
        '\x59' : ('cp1252', 'Spanish ANSI'),
        '\x64' : ('cp852', 'Eastern European MS-DOS'),
        '\x65' : ('cp866', 'Russian MS-DOS'),
        '\x66' : ('cp865', 'Nordic MS-DOS'),
        '\x67' : ('cp861', 'Icelandic MS-DOS'),
        '\x68' : (None, 'Kamenicky (Czech) MS-DOS'),
        '\x69' : (None, 'Mazovia (Polish) MS-DOS'),
        '\x6a' : ('cp737', 'Greek MS-DOS (437G)'),
        '\x6b' : ('cp857', 'Turkish MS-DOS'),
        '\x78' : ('cp950', 'Traditional Chinese (Hong Kong SAR, Taiwan) Windows'),
        '\x79' : ('cp949', 'Korean Windows'),
        '\x7a' : ('cp936', 'Chinese Simplified (PRC, Singapore) Windows'),
        '\x7b' : ('cp932', 'Japanese Windows'),
        '\x7c' : ('cp874', 'Thai Windows'),
        '\x7d' : ('cp1255', 'Hebrew Windows'),
        '\x7e' : ('cp1256', 'Arabic Windows'),
        '\xc8' : ('cp1250', 'Eastern European Windows'),
        '\xc9' : ('cp1251', 'Russian Windows'),
        '\xca' : ('cp1254', 'Turkish Windows'),
        '\xcb' : ('cp1253', 'Greek Windows'),
        '\x96' : ('mac_cyrillic', 'Russian Macintosh'),
        '\x97' : ('mac_latin2', 'Macintosh EE'),
        '\x98' : ('mac_greek', 'Greek Macintosh') }

if sys.version_info[:2] < (2, 6):
    # define our own property type
    class property(object):
        "Emulate PyProperty_Type() in Objects/descrobject.c"
    
        def __init__(self, fget=None, fset=None, fdel=None, doc=None):
            self.fget = fget
            self.fset = fset
            self.fdel = fdel
            self.__doc__ = doc or fget.__doc__
        def __call__(self, func):
            self.fget = func
            if not self.__doc__:
                self.__doc__ = fget.__doc__
        def __get__(self, obj, objtype=None):
            if obj is None:
                return self         
            if self.fget is None:
                raise AttributeError, "unreadable attribute"
            return self.fget(obj)
        def __set__(self, obj, value):
            if self.fset is None:
                raise AttributeError, "can't set attribute"
            self.fset(obj, value)
        def __delete__(self, obj):
            if self.fdel is None:
                raise AttributeError, "can't delete attribute"
            self.fdel(obj)
        def setter(self, func):
            self.fset = func
            return self
        def deleter(self, func):
            self.fdel = func
            return self
class _DbfRecord(object):
    """Provides routines to extract and save data within the fields of a dbf record."""
    __slots__ = ['_recnum', '_layout', '_data', '__weakref__']
    def _retrieveFieldValue(yo, record_data, fielddef):
        """calls appropriate routine to fetch value stored in field from array
        @param record_data: the data portion of the record
        @type record_data: array of characters
        @param fielddef: description of the field definition
        @type fielddef: dictionary with keys 'type', 'start', 'length', 'end', 'decimals', and 'flags'
        @returns: python data stored in field"""

        field_type = fielddef['type']
        retrieve = yo._layout.fieldtypes[field_type]['Retrieve']
        datum = retrieve(record_data, fielddef, yo._layout.memo)
        if field_type in yo._layout.character_fields:
            datum = yo._layout.decoder(datum)[0]
            if yo._layout.return_ascii:
                try:
                    datum = yo._layout.output_encoder(datum)[0]
                except UnicodeEncodeError:
                    datum = unicodedata.normalize('NFD', datum).encode('ascii','ignore')
        return datum
    def _updateFieldValue(yo, fielddef, value):
        "calls appropriate routine to convert value to ascii bytes, and save it in record"
        field_type = fielddef['type']
        update = yo._layout.fieldtypes[field_type]['Update']
        if field_type in yo._layout.character_fields:
            if not isinstance(value, unicode):
                if yo._layout.input_decoder is None:
                    raise NonUnicode("String not in unicode format, no default encoding specified")
                value = yo._layout.input_decoder(value)[0]     # input ascii => unicode
            value = yo._layout.encoder(value)[0]           # unicode => table ascii
        bytes = array('c', update(value, fielddef, yo._layout.memo))
        size = fielddef['length']
        if len(bytes) > size:
            raise DataOverflow("tried to store %d bytes in %d byte field" % (len(bytes), size))
        blank = array('c', ' ' * size)
        start = fielddef['start']
        end = start + size
        blank[:len(bytes)] = bytes[:]
        yo._data[start:end] = blank[:]
        yo._update_disk(yo._recnum * yo._layout.header.record_length + yo._layout.header.start, yo._data.tostring())
    def _update_disk(yo, location='', data=None):
        if not yo._layout.inmemory:
            if yo._recnum < 0:
                raise DbfError("Attempted to update record that has been packed")
            if location == '':
                location = yo._recnum * yo._layout.header.record_length + yo._layout.header.start
            if data is None:
                data = yo._data
            yo._layout.dfd.seek(location)
            yo._layout.dfd.write(data)
    def __call__(yo, *specs):
        results = []
        if not specs:
            specs = yo._layout.index
        specs = _normalize_tuples(tuples=specs, length=2, filler=[_nop])
        for field, func in specs:
            results.append(func(yo[field]))
        return tuple(results)

    def __contains__(yo, key):
        return key in yo._layout.fields
    def __iter__(yo):
        return (yo[field] for field in yo._layout.fields)
    def __getattr__(yo, name):
        if name[0:2] == '__' and name[-2:] == '__':
            raise AttributeError, 'Method %s is not implemented.' % name
        elif not name in yo._layout.fields:
            raise FieldMissing(name)
        try:
            fielddef = yo._layout[name]
            value = yo._retrieveFieldValue(yo._data[fielddef['start']:fielddef['end']], fielddef)
            return value
        except DbfError, error:
            error.message = "field --%s-- is %s -> %s" % (name, yo._layout.fieldtypes[fielddef['type']]['Type'], error.message)
            raise
    def __getitem__(yo, item):
        if type(item) == int:
            if not -yo._layout.header.field_count <= item < yo._layout.header.field_count:
                raise IndexError("Field offset %d is not in record" % item)
            return yo[yo._layout.fields[item]]
        elif type(item) == slice:
            sequence = []
            for index in yo._layout.fields[item]:
                sequence.append(yo[index])
            return sequence
        elif type(item) == str:
            return yo.__getattr__(item)
        else:
            raise TypeError("%s is not a field name" % item)
    def __len__(yo):
        return yo._layout.header.field_count
    def __new__(cls, recnum, layout, kamikaze='', _fromdisk=False):
        """record = ascii array of entire record; layout=record specification; memo = memo object for table"""
        record = object.__new__(cls)
        record._recnum = recnum
        record._layout = layout
        if layout.blankrecord is None and not _fromdisk:
            record._createBlankRecord()
        record._data = layout.blankrecord
        if recnum == -1:                    # not a disk-backed record
            return record
        elif type(kamikaze) == array:
            record._data = kamikaze[:]
        elif type(kamikaze) == str:
            record._data = array('c', kamikaze)
        else:
            record._data = kamikaze._data[:]
        datalen = len(record._data)
        if datalen < layout.header.record_length:
            record._data.extend(layout.blankrecord[datalen:])
        elif datalen > layout.header.record_length:
            record._data = record._data[:layout.header.record_length]
        if not _fromdisk and not layout.inmemory:
            record._update_disk()
        return record
    def __setattr__(yo, name, value):
        if name in yo.__slots__:
            object.__setattr__(yo, name, value)
            return
        elif not name in yo._layout.fields:
            raise FieldMissing(name)
        fielddef = yo._layout[name]
        try:
            yo._updateFieldValue(fielddef, value)
        except DbfError, error:
            error.message = "field --%s-- is %s -> %s" % (name, yo._layout.fieldtypes[fielddef['type']]['Type'], error.message)
            error.data = name
            raise
            raise DbfError(message)
    def __setitem__(yo, name, value):
        if type(name) == str:
            yo.__setattr__(name, value)
        elif type(name) in (int, long):
            yo.__setattr__(yo._layout.fields[name], value)
        else:
            raise TypeError("%s is not a field name" % name)
    def __str__(yo):
        result = []
        for field in yo.field_names:
            result.append("%-10s: %s" % (field, yo[field]))
        return '\n'.join(result)
    def __repr__(yo):
        return yo._data.tostring()
    def _createBlankRecord(yo):
        "creates a blank record data chunk"
        layout = yo._layout
        ondisk = layout.ondisk
        layout.ondisk = False
        yo._data = array('c', ' ' * layout.header.record_length)
        layout.memofields = []
        for field in layout.fields:
            yo._updateFieldValue(layout[field], layout.fieldtypes[layout[field]['type']]['Blank']())
            if layout[field]['type'] in layout.memotypes:
                layout.memofields.append(field)
        layout.blankrecord = yo._data[:]
        layout.ondisk = ondisk
    def delete_record(yo):
        "marks record as deleted"
        yo._data[0] = '*'
        yo._update_disk(data='*')
    @property
    def field_names(yo):
        "fields in table/record"
        return yo._layout.fields[:]
    def gather_fields(yo, dict, drop=False):
        "saves a dictionary into a records fields\nkeys with no matching field will raise a FieldMissing exception unless drop = True"
        for key in dict:
            if not key in yo.field_names:
                if drop:
                    continue
                raise FieldMissing(key)
            yo.__setattr__(key, dict[key])
    @property
    def has_been_deleted(yo):
        "marked for deletion?"
        return yo._data[0] == '*'
    @property
    def record_number(yo):
        "physical record number"
        return yo._recnum
    @property
    def record_table(yo):
        table = yo._layout.table()
        if table is None:
            raise DbfError("table is no longer available")
        return table
    def reset_record(yo, keep_fields=None):
        "blanks record"
        if keep_fields is None:
            keep_fields = []
        keep = {}
        for field in keep_fields:
            keep[field] = yo[field]
        if yo._layout.blankrecord == None:
            yo._createBlankRecord()
        yo._data[:] = yo._layout.blankrecord[:]
        for field in keep_fields:
            yo[field] = keep[field]
        yo._update_disk()
    def scatter_fields(yo, blank=False):
        "returns a dictionary of fieldnames and values which can be used with gather_fields().  if blank is True, values are empty."
        keys = yo._layout.fields
        if blank:
            values = [yo._layout.fieldtypes[yo._layout[key]['type']]['Blank']() for key in keys]
        else:
            values = [yo[field] for field in keys]
        return dict(zip(keys, values))
    def undelete_record(yo):
        "marks record as active"
        yo._data[0] = ' '
        yo._update_disk(data=' ')
class _DbfMemo(object):
    """Provides access to memo fields as dictionaries
       must override _init, _get_memo, and _put_memo to
       store memo contents to disk"""
    def _init(yo):
        "initialize disk file usage"
    def _get_memo(yo, block):
        "retrieve memo contents from disk"
    def _put_memo(yo, data):
        "store memo contents to disk"
    def __init__(yo, meta):
        ""
        yo.meta = meta
        yo.memory = {}
        yo.nextmemo = 1
        yo._init()
        yo.meta.newmemofile = False
    def get_memo(yo, block, field):
        "gets the memo in block"
        if yo.meta.ignorememos or not block:
            return ''
        if yo.meta.ondisk:
            return yo._get_memo(block)
        else:
            return yo.memory[block]
    def put_memo(yo, data):
        "stores data in memo file, returns block number"
        if yo.meta.ignorememos or data == '':
            return 0
        if yo.meta.inmemory:
            thismemo = yo.nextmemo
            yo.nextmemo += 1
            yo.memory[thismemo] = data
        else:
            thismemo = yo._put_memo(data)
        return thismemo
class _Db3Memo(_DbfMemo):
    def _init(yo):
        "dBase III specific"
        yo.meta.memo_size= 512
        yo.record_header_length = 2
        if yo.meta.ondisk and not yo.meta.ignorememos:
            if yo.meta.newmemofile:
                yo.meta.mfd = open(yo.meta.memoname, 'w+b')
                yo.meta.mfd.write(io.packLongInt(1) + '\x00' * 508)
            else:
                try:
                    yo.meta.mfd = open(yo.meta.memoname, 'r+b')
                    yo.meta.mfd.seek(0)
                    yo.nextmemo = io.unpackLongInt(yo.meta.mfd.read(4))
                except:
                    raise DbfError("memo file appears to be corrupt")
    def _get_memo(yo, block):
        block = int(block)
        yo.meta.mfd.seek(block * yo.meta.memo_size)
        eom = -1
        data = ''
        while eom == -1:
            newdata = yo.meta.mfd.read(yo.meta.memo_size)
            if not newdata:
                return data
            data += newdata
            eom = data.find('\x1a\x1a')
        return data[:eom].rstrip()
    def _put_memo(yo, data):
        data = data.rstrip()
        length = len(data) + yo.record_header_length  # room for two ^Z at end of memo
        blocks = length // yo.meta.memo_size
        if length % yo.meta.memo_size:
            blocks += 1
        thismemo = yo.nextmemo
        yo.nextmemo = thismemo + blocks
        yo.meta.mfd.seek(0)
        yo.meta.mfd.write(io.packLongInt(yo.nextmemo))
        yo.meta.mfd.seek(thismemo * yo.meta.memo_size)
        yo.meta.mfd.write(data)
        yo.meta.mfd.write('\x1a\x1a')
        double_check = yo._get_memo(thismemo)
        if len(double_check) != len(data):
            uhoh = open('dbf_memo_dump.err','wb')
            uhoh.write('thismemo: %d' % thismemo)
            uhoh.write('nextmemo: %d' % yo.nextmemo)
            uhoh.write('saved: %d bytes' % len(data))
            uhoh.write(data)
            uhoh.write('retrieved: %d bytes' % len(double_check))
            uhoh.write(double_check)
            uhoh.close()
            raise DbfError("unknown error: memo not saved")
        return thismemo
class _VfpMemo(_DbfMemo):
    def _init(yo):
        "Visual Foxpro 6 specific"
        if yo.meta.ondisk and not yo.meta.ignorememos:
            yo.record_header_length = 8
            if yo.meta.newmemofile:
                if yo.meta.memo_size == 0:
                    yo.meta.memo_size = 1
                elif 1 < yo.meta.memo_size < 33:
                    yo.meta.memo_size *= 512
                yo.meta.mfd = open(yo.meta.memoname, 'w+b')
                nextmemo = 512 // yo.meta.memo_size
                if nextmemo * yo.meta.memo_size < 512:
                    nextmemo += 1
                yo.nextmemo = nextmemo
                yo.meta.mfd.write(io.packLongInt(nextmemo, bigendian=True) + '\x00\x00' + \
                        io.packShortInt(yo.meta.memo_size, bigendian=True) + '\x00' * 504)
            else:
                try:
                    yo.meta.mfd = open(yo.meta.memoname, 'r+b')
                    yo.meta.mfd.seek(0)
                    header = yo.meta.mfd.read(512)
                    yo.nextmemo = io.unpackLongInt(header[:4], bigendian=True)
                    yo.meta.memo_size = io.unpackShortInt(header[6:8], bigendian=True)
                except:
                    raise DbfError("memo file appears to be corrupt")
    def _get_memo(yo, block):
        yo.meta.mfd.seek(block * yo.meta.memo_size)
        header = yo.meta.mfd.read(8)
        length = io.unpackLongInt(header[4:], bigendian=True)
        return yo.meta.mfd.read(length)
    def _put_memo(yo, data):
        data = data.rstrip()     # no trailing whitespace
        yo.meta.mfd.seek(0)
        thismemo = io.unpackLongInt(yo.meta.mfd.read(4), bigendian=True)
        yo.meta.mfd.seek(0)
        length = len(data) + yo.record_header_length  # room for two ^Z at end of memo
        blocks = length // yo.meta.memo_size
        if length % yo.meta.memo_size:
            blocks += 1
        yo.meta.mfd.write(io.packLongInt(thismemo+blocks, bigendian=True))
        yo.meta.mfd.seek(thismemo*yo.meta.memo_size)
        yo.meta.mfd.write('\x00\x00\x00\x01' + io.packLongInt(len(data), bigendian=True) + data)
        return thismemo
class DbfTable(object):
    """Provides a framework for dbf style tables."""
    _version = 'basic memory table'
    _versionabbv = 'dbf'
    _fieldtypes = {
            'D' : { 'Type':'Date',    'Init':io.addDate,    'Blank':Date.today, 'Retrieve':io.retrieveDate,    'Update':io.updateDate, },
            'L' : { 'Type':'Logical', 'Init':io.addLogical, 'Blank':bool,       'Retrieve':io.retrieveLogical, 'Update':io.updateLogical, },
            'M' : { 'Type':'Memo',    'Init':io.addMemo,    'Blank':str,        'Retrieve':io.retrieveMemo,    'Update':io.updateMemo, } }
    _memoext = ''
    _memotypes = tuple('M', )
    _memoClass = _DbfMemo
    _yesMemoMask = ''
    _noMemoMask = ''
    _fixed_fields = ('M','D','L')           # always same length in table
    _variable_fields = tuple()              # variable length in table
    _character_fields = tuple('M', )        # field representing character data
    _decimal_fields = tuple()               # text-based numeric fields
    _numeric_fields = tuple()               # fields representing a number
    _dbfTableHeader = array('c', '\x00' * 32)
    _dbfTableHeader[0] = '\x00'             # table type - none
    _dbfTableHeader[8:10] = array('c', io.packShortInt(33))
    _dbfTableHeader[10] = '\x01'            # record length -- one for delete flag
    _dbfTableHeader[29] = '\x00'            # code page -- none, using plain ascii
    _dbfTableHeader = _dbfTableHeader.tostring()
    _dbfTableHeaderExtra = ''
    _supported_tables = []
    _read_only = False
    _meta_only = False
    _use_deleted = True
    _backed_up = False
    class _MetaData(dict):
        blankrecord = None
        fields = None
        filename = None
        dfd = None
        memoname = None
        newmemofile = False
        memo = None
        mfd = None
        ignorememos = False
        memofields = None
        index = []  # never mutated
        index_reversed = False
        orderresults = None
        current = -1
    class _TableHeader(object):
        def __init__(yo, data):
            if len(data) != 32:
                raise DbfError('table header should be 32 bytes, but is %d bytes' % len(data))
            yo._data = array('c', data + '\x0d')
        def codepage(yo, cp=None):
            "get/set code page of table"
            if cp is None:
                return yo._data[29]
            else:
                cp, sd, ld = _codepage_lookup(cp)
                yo._data[29] = cp                    
                return cp
        @property
        def data(yo):
            "main data structure"
            date = io.packDate(Date.today())
            yo._data[1:4] = array('c', date)
            return yo._data.tostring()
        @data.setter
        def data(yo, bytes):
            if len(bytes) < 32:
                raise DbfError("length for data of %d is less than 32" % len(bytes))
            yo._data[:] = array('c', bytes)
        @property
        def extra(yo):
            "extra dbf info (located after headers, before data records)"
            fieldblock = yo._data[32:]
            for i in range(len(fieldblock)//32+1):
                cr = i * 32
                if fieldblock[cr] == '\x0d':
                    break
            else:
                raise DbfError("corrupt field structure")
            cr += 33    # skip past CR
            return yo._data[cr:].tostring()
        @extra.setter
        def extra(yo, data):
            fieldblock = yo._data[32:]
            for i in range(len(fieldblock)//32+1):
                cr = i * 32
                if fieldblock[cr] == '\x0d':
                    break
            else:
                raise DbfError("corrupt field structure")
            cr += 33    # skip past CR
            yo._data[cr:] = array('c', data)                             # extra
            yo._data[8:10] = array('c', io.packShortInt(len(yo._data)))  # start
        @property
        def field_count(yo):
            "number of fields (read-only)"
            fieldblock = yo._data[32:]
            for i in range(len(fieldblock)//32+1):
                cr = i * 32
                if fieldblock[cr] == '\x0d':
                    break
            else:
                raise DbfError("corrupt field structure")
            return len(fieldblock[:cr]) // 32
        @property
        def fields(yo):
            "field block structure"
            fieldblock = yo._data[32:]
            for i in range(len(fieldblock)//32+1):
                cr = i * 32
                if fieldblock[cr] == '\x0d':
                    break
            else:
                raise DbfError("corrupt field structure")
            return fieldblock[:cr].tostring()
        @fields.setter
        def fields(yo, block):
            fieldblock = yo._data[32:]
            for i in range(len(fieldblock)//32+1):
                cr = i * 32
                if fieldblock[cr] == '\x0d':
                    break
            else:
                raise DbfError("corrupt field structure")
            cr += 32    # convert to indexing main structure
            fieldlen = len(block)
            if fieldlen % 32 != 0:
                raise DbfError("fields structure corrupt: %d is not a multiple of 32" % fieldlen)
            yo._data[32:cr] = array('c', block)                           # fields
            yo._data[8:10] = array('c', io.packShortInt(len(yo._data)))   # start
            fieldlen = fieldlen // 32
            recordlen = 1                                     # deleted flag
            for i in range(fieldlen):
                recordlen += ord(block[i*32+16])
            yo._data[10:12] = array('c', io.packShortInt(recordlen))
        @property
        def record_count(yo):
            "number of records (maximum 16,777,215)"
            return io.unpackLongInt(yo._data[4:8].tostring())
        @record_count.setter
        def record_count(yo, count):
            yo._data[4:8] = array('c', io.packLongInt(count))
        @property
        def record_length(yo):
            "length of a record (read_only) (max of 65,535)"
            return io.unpackShortInt(yo._data[10:12].tostring())
        @property
        def start(yo):
            "starting position of first record in file (must be within first 64K)"
            return io.unpackShortInt(yo._data[8:10].tostring())
        @start.setter
        def start(yo, pos):
            yo._data[8:10] = array('c', io.packShortInt(pos))
        @property
        def update(yo):
            "date of last table modification (read-only)"
            return io.unpackDate(yo._data[1:4].tostring())
        @property
        def version(yo):
            "dbf version"
            return yo._data[0]
        @version.setter
        def version(yo, ver):
            yo._data[0] = ver
    class _Table(object):
        "implements the weakref table for records"
        def __init__(yo, count, meta):
            yo._meta = meta
            yo._weakref_list = [weakref.ref(lambda x: None)] * count
        def __getitem__(yo, index):
            maybe = yo._weakref_list[index]()
            if maybe is None:
                if index < 0:
                    index += yo._meta.header.record_count
                size = yo._meta.header.record_length
                location = index * size + yo._meta.header.start
                yo._meta.dfd.seek(location)
                bytes = yo._meta.dfd.read(size)
                maybe = _DbfRecord(recnum=index, layout=yo._meta, kamikaze=bytes, _fromdisk=True)
                yo._weakref_list[index] = weakref.ref(maybe)
            return maybe
        def append(yo, record):
            yo._weakref_list.append(weakref.ref(record))
    class DbfIterator(object):
        "returns records using current index"
        def __init__(yo, table):
            yo._table = table
            yo._index = -1
            yo._more_records = True
        def __iter__(yo):
            return yo
        def next(yo):
            while yo._more_records:
                yo._index += 1
                if yo._index >= len(yo._table):
                    yo._more_records = False
                    continue
                record = yo._table[yo._index]
                if not yo._table.use_deleted and record.has_been_deleted:
                    continue
                return record
            else:
                raise StopIteration
    def _buildHeaderFields(yo):
        "constructs fieldblock for disk table"
        fieldblock = array('c', '')
        memo = False
        yo._meta.header.version = chr(ord(yo._meta.header.version) & ord(yo._noMemoMask))
        for field in yo._meta.fields:
            if yo._meta.fields.count(field) > 1:
                raise DbfError("corrupted field structure (noticed in _buildHeaderFields)")
            fielddef = array('c', '\x00' * 32)
            fielddef[:11] = array('c', io.packStr(field))
            fielddef[11] = yo._meta[field]['type']
            fielddef[12:16] = array('c', io.packLongInt(yo._meta[field]['start']))
            fielddef[16] = chr(yo._meta[field]['length'])
            fielddef[17] = chr(yo._meta[field]['decimals'])
            fielddef[18] = chr(yo._meta[field]['flags'])
            fieldblock.extend(fielddef)
            if yo._meta[field]['type'] in yo._meta.memotypes:
                memo = True
        yo._meta.header.fields = fieldblock.tostring()
        if memo:
            yo._meta.header.version = chr(ord(yo._meta.header.version) | ord(yo._yesMemoMask))
            if yo._meta.memo is None:
                yo._meta.memo = yo._memoClass(yo._meta)
    def _checkMemoIntegrity(yo):
        "dBase III specific"
        if yo._meta.header.version == '\x83':
            try:
                yo._meta.memo = yo._memoClass(yo._meta)
            except:
                yo._meta.dfd.close()
                yo._meta.dfd = None
                raise
        if not yo._meta.ignorememos:
            for field in yo._meta.fields:
                if yo._meta[field]['type'] in yo._memotypes:
                    if yo._meta.header.version != '\x83':
                        yo._meta.dfd.close()
                        yo._meta.dfd = None
                        raise DbfError("Table structure corrupt:  memo fields exist, header declares no memos")
                    elif not os.path.exists(yo._meta.memoname):
                        yo._meta.dfd.close()
                        yo._meta.dfd = None
                        raise DbfError("Table structure corrupt:  memo fields exist without memo file")
                    break
    def _initializeFields(yo):
        "builds the FieldList of names, types, and descriptions from the disk file"
        offset = 1
        fieldsdef = yo._meta.header.fields
        if len(fieldsdef) % 32 != 0:
            raise DbfError("field definition block corrupt: %d bytes in size" % len(fieldsdef))
        if len(fieldsdef) // 32 != yo.field_count:
            raise DbfError("Header shows %d fields, but field definition block has %d fields" % (yo.field_count, len(fieldsdef)//32))
        for i in range(yo.field_count):
            fieldblock = fieldsdef[i*32:(i+1)*32]
            name = io.unpackStr(fieldblock[:11])
            type = fieldblock[11]
            if not type in yo._meta.fieldtypes:
                raise DbfError("Unknown field type: %s" % type)
            start = offset
            length = ord(fieldblock[16])
            offset += length
            end = start + length
            decimals = ord(fieldblock[17])
            flags = ord(fieldblock[18])
            yo._meta.fields.append(name)
            yo._meta[name] = {'type':type,'start':start,'length':length,'end':end,'decimals':decimals,'flags':flags}
    def _fieldLayout(yo, i):
        "Returns field information Name Type(Length[,Decimals])"
        name = yo._meta.fields[i]
        type = yo._meta[name]['type']
        length = yo._meta[name]['length']
        decimals = yo._meta[name]['decimals']
        if type in yo._decimal_fields:
            description = "%s %s(%d,%d)" % (name, type, length, decimals)
        elif type in yo._fixed_fields:
            description = "%s %s" % (name, type)
        else:
            description = "%s %s(%d)" % (name, type, length)
        return description
    def _loadtable(yo):
        "loads the records from disk to memory"
        if yo._meta_only:
            raise DbfError("%s has been closed, records are unavailable" % yo.filename)
        dfd = yo._meta.dfd
        header = yo._meta.header
        dfd.seek(header.start)
        allrecords = dfd.read()                     # kludge to get around mysterious errno 0 problems
        dfd.seek(0)
        length = header.record_length
        for i in range(header.record_count):
            record_data = allrecords[length*i:length*i+length]
            yo._table.append(_DbfRecord(i, yo._meta, allrecords[length*i:length*i+length], _fromdisk=True))
            yo._index.append(i)
        dfd.seek(0)
    def _list_fields(yo, specs, sep=','):
        if specs is None:
            specs = yo.field_names
        elif isinstance(specs, str):
            specs = specs.split(sep)
        else:
            specs = list(specs)
        specs = [s.strip() for s in specs]
        return specs
    def _update_disk(yo, headeronly=False):
        "synchronizes the disk file with current data"
        if yo._meta.inmemory:
            return
        fd = yo._meta.dfd
        fd.seek(0)
        fd.write(yo._meta.header.data)
        if not headeronly:
            for record in yo._table:
                record._update_disk()
            fd.flush()
            fd.truncate(yo._meta.header.start + yo._meta.header.record_count * yo._meta.header.record_length)
    def __contains__(yo, key):
        return key in yo.field_names
    def __enter__(yo):
        return yo
    def __exit__(yo, *exc_info):
        yo.close()
    def __getattr__(yo, name):
        if name in ('_index','_table'):
                if yo._meta.ondisk:
                    yo._table = yo._Table(len(yo), yo._meta)
                    yo._index = range(len(yo))
                else:
                    yo._table = []
                    yo._index = []
                    yo._loadtable()
        return object.__getattribute__(yo, name)
    def __getitem__(yo, value):
        if type(value) == int:
            if not -yo._meta.header.record_count <= value < yo._meta.header.record_count: 
                raise IndexError("Record %d is not in table." % value)
            return yo._table[yo._index[value]]
        elif type(value) == slice:
            sequence = DbfList(desc='%s -->  %s' % (yo.filename, value))
            for index in yo._index[value]:
                record = yo._table[index]
                if yo.use_deleted is True or not record.has_been_deleted:
                    sequence.append(record)
            return sequence
        else:
            raise TypeError('type <%s> not valid for indexing' % type(value))
    def __init__(yo, filename=':memory:', field_specs=None, memo_size=128, ignore_memos=False, 
                 read_only=False, keep_memos=False, meta_only=False, codepage=None):
        """open/create dbf file
        filename should include path if needed
        field_specs can be either a ;-delimited string or a list of strings
        memo_size is always 512 for db3 memos
        ignore_memos is useful if the memo file is missing or corrupt
        read_only will load records into memory, then close the disk file
        keep_memos will also load any memo fields into memory
        meta_only will ignore all records, keeping only basic table information
        codepage will override whatever is set in the table itself"""
        if filename == ':memory:':
            if field_specs is None:
                raise DbfError("field list must be specified for in-memory tables")
        elif type(yo) is DbfTable:
            raise DbfError("only memory tables supported")
        yo._meta = meta = yo._MetaData()
        meta.table = weakref.ref(yo)
        meta.filename = filename
        meta.fields = []
        meta.fieldtypes = yo._fieldtypes
        meta.fixed_fields = yo._fixed_fields
        meta.variable_fields = yo._variable_fields
        meta.character_fields = yo._character_fields
        meta.decimal_fields = yo._decimal_fields
        meta.numeric_fields = yo._numeric_fields
        meta.memotypes = yo._memotypes
        meta.ignorememos = ignore_memos
        meta.memo_size = memo_size
        meta.input_decoder = codecs.getdecoder(input_decoding)      # from ascii to unicode
        meta.output_encoder = codecs.getencoder(input_decoding)     # and back to ascii
        meta.return_ascii = return_ascii
        meta.header = header = yo._TableHeader(yo._dbfTableHeader)
        header.extra = yo._dbfTableHeaderExtra
        header.data        #force update of date
        if filename == ':memory:':
            yo._index = []
            yo._table = []
            meta.ondisk = False
            meta.inmemory = True
            meta.memoname = ':memory:'
        else:
            base, ext = os.path.splitext(filename)
            if ext == '':
                meta.filename =  base + '.dbf'
            meta.memoname = base + yo._memoext
            meta.ondisk = True
            meta.inmemory = False
        if field_specs:
            if meta.ondisk:
                meta.dfd = open(meta.filename, 'w+b')
                meta.newmemofile = True
            yo.add_fields(field_specs)
            header.codepage = codepage or default_codepage
            meta.decoder = codecs.getdecoder(header.codepage) 
            meta.encoder = codecs.getencoder(header.codepage)
            return
        dfd = meta.dfd = open(meta.filename, 'r+b')
        dfd.seek(0)
        meta.header = header = yo._TableHeader(dfd.read(32))
        if not header.version in yo._supported_tables:
            dfd.close()
            dfd = None
            raise TypeError("Unsupported dbf type: %s [%x]" % (version_map.get(meta.header.version, 'Unknown: %s' % meta.header.version), ord(meta.header.version)))
        cp, sd, ld = _codepage_lookup(meta.header.codepage())
        yo._meta.decoder = codecs.getdecoder(sd) 
        yo._meta.encoder = codecs.getencoder(sd)
        fieldblock = dfd.read(header.start - 32)
        for i in range(len(fieldblock)//32+1):
            fieldend = i * 32
            if fieldblock[fieldend] == '\x0d':
                break
        else:
            raise DbfError("corrupt field structure in header")
        if len(fieldblock[:fieldend]) % 32 != 0:
            raise DbfError("corrupt field structure in header")
        header.fields = fieldblock[:fieldend]
        header.extra = fieldblock[fieldend+1:]  # skip trailing \r
        yo._initializeFields()
        yo._checkMemoIntegrity()
        meta.current = -1
        if len(yo) > 0:
            meta.current = 0
        dfd.seek(0)
        if meta_only:
            yo.close(keep_table=False, keep_memos=False)
        elif read_only:
            yo.close(keep_table=True, keep_memos=keep_memos)
        if codepage is not None:
            cp, sd, ld = _codepage_lookup(codepage)
            yo._meta.decoder = codecs.getdecoder(sd) 
            yo._meta.encoder = codecs.getencoder(sd)

    def __iter__(yo):
        return yo.DbfIterator(yo)           
    def __len__(yo):
        return yo._meta.header.record_count
    def __nonzero__(yo):
        return yo._meta.header.record_count != 0
    def __repr__(yo):
        if yo._read_only:
            return __name__ + ".Table('%s', read_only=True)" % yo._meta.filename
        elif yo._meta_only:
            return __name__ + ".Table('%s', meta_only=True)" % yo._meta.filename
        else:
            return __name__ + ".Table('%s')" % yo._meta.filename
    def __str__(yo):
        if yo._read_only:
            status = "read-only"
        elif yo._meta_only:
            status = "meta-only"
        else:
            status = "read/write"
        str =  """
        Table:         %s
        Type:          %s
        Codepage:      %s
        Status:        %s
        Last updated:  %s
        Record count:  %d
        Field count:   %d
        Record length: %d
        """ % (yo.filename, version_map.get(yo._meta.header.version, 'unknown - ' + hex(ord(yo._meta.header.version))),
                yo.codepage, status, yo.last_update, len(yo), yo.field_count, yo.record_length)
        str += "\n        --Fields--\n"
        for i in range(len(yo._meta.fields)):
            str += "        " + yo._fieldLayout(i) + "\n"
        return str
    @property
    def codepage(yo):
        return "%s (%s)" % code_pages[yo._meta.header.codepage()]
    @codepage.setter
    def codepage(yo, cp):
        cp = code_pages[yo._meta.header.codepage(cp)][0]
        yo._meta.decoder = codecs.getdecoder(cp) 
        yo._meta.encoder = codecs.getencoder(cp)
        yo._update_disk(headeronly=True)
    @property
    def field_count(yo):
        "the number of fields in the table"
        return yo._meta.header.field_count
    @property
    def field_names(yo):
        "a list of the fields in the table"
        return yo._meta.fields[:]
    @property
    def filename(yo):
        "table's file name, including path (if specified on open)"
        return yo._meta.filename
    @property
    def last_update(yo):
        "date of last update"
        return yo._meta.header.update
    @property
    def memoname(yo):
        "table's memo name (if path included in filename on open)"
        return yo._meta.memoname
    @property
    def record_length(yo):
        "number of bytes in a record"
        return yo._meta.header.record_length
    @property
    def record_number(yo):
        "index number of the current record"
        return yo._meta.current
    @property
    def supported_tables(yo):
        "allowable table types"
        return yo._supported_tables
    @property
    def use_deleted(yo):
        "process or ignore deleted records"
        return yo._use_deleted
    @use_deleted.setter
    def use_deleted(yo, new_setting):
        yo._use_deleted = new_setting
    @property
    def version(yo):
        "returns the dbf type of the table"
        return yo._version
    def add_fields(yo, field_specs):
        """adds field(s) to the table layout; format is Name Type(Length,Decimals)[; Name Type(Length,Decimals)[...]]
        backup table is created with _backup appended to name
        then modifies current structure"""
        all_records = [record for record in yo]
        if yo:
            yo.create_backup()
        yo._meta.blankrecord = None
        meta = yo._meta
        offset = meta.header.record_length
        fields = yo._list_fields(field_specs, sep=';')
        for field in fields:
            try:
                name, format = field.split()
                if name[0] == '_' or name[0].isdigit() or not name.replace('_','').isalnum():
                    raise DbfError("Field names cannot start with _ or digits, and can only contain the _, letters, and digits")
                name = name.lower()
                if name in meta.fields:
                    raise DbfError("Field '%s' already exists" % name)
                field_type = format[0].upper()
                if len(name) > 10:
                    raise DbfError("Maximum field name length is 10.  '%s' is %d characters long." % (name, len(name)))
                if not field_type in meta.fieldtypes.keys():
                    raise DbfError("Unknown field type:  %s" % field_type)
                length, decimals = yo._meta.fieldtypes[field_type]['Init'](format)
            except ValueError:
                raise DbfError("invalid field specifier: %s" % field)
            start = offset
            end = offset + length
            offset = end
            meta.fields.append(name)
            meta[name] = {'type':field_type, 'start':start, 'length':length, 'end':end, 'decimals':decimals, 'flags':0}
            if meta[name]['type'] in yo._memotypes and meta.memo is None:
                meta.memo = yo._memoClass(meta)
            for record in yo:
                record[name] = meta.fieldtypes[field_type]['Blank']()
        yo._buildHeaderFields()
        yo._update_disk()
    def append(yo, kamikaze='', drop=False, multiple=1):
        "adds <multiple> blank records, and fills fields with dict/tuple values if present"
        if not yo.field_count:
            raise DbfError("No fields defined, cannot append")
        empty_table = len(yo) == 0
        dictdata = False
        tupledata = False
        if not isinstance(kamikaze, _DbfRecord):
            if isinstance(kamikaze, dict):
                dictdata = kamikaze
                kamikaze = ''
            elif isinstance(kamikaze, tuple):
                tupledata = kamikaze
                kamikaze = ''
        newrecord = _DbfRecord(recnum=yo._meta.header.record_count, layout=yo._meta, kamikaze=kamikaze)
        yo._table.append(newrecord)
        yo._index.append(yo._meta.header.record_count)
        yo._meta.header.record_count += 1
        if dictdata:
            newrecord.gather_fields(dictdata, drop)
        elif tupledata:
            for index, item in enumerate(tupledata):
                newrecord[index] = item
        elif kamikaze == str:
            for field in yo._meta.memofields:
                newrecord[field] = ''
        elif kamikaze:
            for field in yo._meta.memofields:
                newrecord[field] = kamikaze[field]
        multiple -= 1
        if multiple:
            data = newrecord._data
            single = yo._meta.header.record_count
            total = single + multiple
            while single < total:
                multi_record = _DbfRecord(single, yo._meta, kamikaze=data)
                yo._table.append(multi_record)
                yo._index.append(single)
                for field in yo._meta.memofields:
                    multi_record[field] = newrecord[field]
                single += 1
            yo._meta.header.record_count = total   # += multiple
            yo._meta.current = yo._meta.header.record_count - 1
            newrecord = multi_record
        yo._update_disk(headeronly=True)
        if empty_table:
            yo._meta.current = 0
        return newrecord
    def bof(yo):
        "moves record pointer to previous usable record; returns True if no more usable records"
        while yo._meta.current > 0:
            yo._meta.current -= 1
            if yo.use_deleted or not yo.current().has_been_deleted:
                break
        else:
            yo._meta.current = -1
            return True
        return False    
    def bottom(yo, get_record=False):
        """sets record pointer to bottom of table
        if get_record, seeks to and returns last (non-deleted) record
        DbfError if table is empty
        Bof if all records deleted and use_deleted is False"""
        yo._meta.current = yo._meta.header.record_count
        if get_record:
            try:
                return yo.prev()
            except Bof:
                yo._meta.current = yo._meta.header.record_count
                raise Eof()
    def close(yo, keep_table=False, keep_memos=False):
        """closes disk files
        ensures table data is available if keep_table
        ensures memo data is available if keep_memos"""
        if keep_table:
            yo._table   # force read of table if not already in memory
        else:
            if '_index' in dir(yo):
                del yo._table
                del yo._index
        yo._meta.inmemory = True
        if yo._meta.ondisk:
            yo._meta.dfd.close()
            yo._meta.dfd = None
            if '_index' in dir(yo):
                yo._read_only = True
            else:
                yo._meta_only = True
        if yo._meta.mfd is not None:
            if not keep_memos:
                yo._meta.ignorememos = True
            else:
                memo_fields = []
                for field in yo.field_names:
                    if yo.is_memotype(field):
                        memo_fields.append(field)
                for record in yo:
                    for field in memo_fields:
                        record[field] = record[field]
            yo._meta.mfd.close()
            yo._meta.mfd = None
        yo._meta.ondisk = False
    def create_backup(yo, new_name=None, overwrite=False):
        "creates a backup table -- ignored if memory table"
        if yo.filename.startswith(':memory:'):
            return
        if new_name is None:
            new_name = os.path.splitext(yo.filename)[0] + '_backup.dbf'
        else:
            overwrite = True
        if overwrite or not yo._backed_up:
            bkup = open(new_name, 'wb')
            try:
                yo._meta.dfd.seek(0)
                copyfileobj(yo._meta.dfd, bkup)
                yo._backed_up = True
            finally:
                bkup.close()
    def current(yo, index=False):
        "returns current logical record, or its index"
        if yo._meta.current < 0:
            raise Bof()
        elif yo._meta.current >= yo._meta.header.record_count:
            raise Eof()
        if index:
            return yo._meta.current
        return yo._table[yo._index[yo._meta.current]]
    def delete_fields(yo, doomed):
        """removes field(s) from the table
        creates backup files with _backup appended to the file name,
        then modifies current structure"""
        doomed = yo._list_fields(doomed)
        for victim in doomed:
            if victim not in yo._meta.fields:
                raise DbfError("field %s not in table -- delete aborted" % victim)
        all_records = [record for record in yo]
        yo.create_backup()
        for victim in doomed:
            yo._meta.fields.pop(yo._meta.fields.index(victim))
            start = yo._meta[victim]['start']
            end = yo._meta[victim]['end']
            for record in yo:
                record._data = record._data[:start] + record._data[end:]
            for field in yo._meta.fields:
                if yo._meta[field]['start'] == end:
                    end = yo._meta[field]['end']
                    yo._meta[field]['start'] = start
                    yo._meta[field]['end'] = start + yo._meta[field]['length']
                    start = yo._meta[field]['end']
            yo._buildHeaderFields()
        yo._update_disk()
    def eof(yo):
        "moves record pointer to next usable record; returns True if no more usable records"
        while yo._meta.current < yo._meta.header.record_count - 1:
            yo._meta.current += 1
            if yo.use_deleted or not yo.current().has_been_deleted:
                break
        else:
            yo._meta.current = yo._meta.header.record_count
            return True
        return False
    def export(yo, records=None, filename=None, field_specs=None, format='csv', header=True):
        """writes the table using CSV or tab-delimited format, using the filename
        given if specified, otherwise the table name"""
        if filename is None:
            filename = yo.filename
        field_specs = yo._list_fields(field_specs)
        if records is None:
            records = yo
        format = format.lower()
        if format not in ('csv', 'tab'):
            raise DbfError("export format: csv or tab, not %s" % format)
        base, ext = os.path.splitext(filename)
        if ext.lower() in ('', '.dbf'):
            filename = base + "." + format
        fd = open(filename, 'wb')
        try:
            if format == 'csv':
                csvfile = csv.writer(fd, dialect='dbf')
                if header:
                    csvfile.writerow(field_specs)
                for record in records:
                    fields = []
                    for fieldname in field_specs:
                        fields.append(record[fieldname])
                    csvfile.writerow(fields)
            else:
                if header:
                    fd.write('\t'.join(field_specs) + '\n')
                for record in records:
                    fields = []
                    for fieldname in field_specs:
                        fields.append(str(record[fieldname]))
                    fd.write('\t'.join(fields) + '\n')
        finally:
            fd.close()
            fd = None
        return len(records)
    def get_record(yo, recno):
        "returns record at physical_index[recno]"
        return yo._table[recno]
    def goto(yo, criteria):
        """changes the record pointer to the first matching (non-deleted) record
        criteria should be either a tuple of tuple(value, field, func) triples, 
        or an integer to go to"""
        if isinstance(criteria, int):
            if not -yo._meta.header.record_count <= criteria < yo._meta.header.record_count:
                raise IndexError("Record %d does not exist" % criteria)
            if criteria < 0:
                criteria += yo._meta.header.record_count
            yo._meta.current = criteria
            return yo.current()
        criteria = _normalize_tuples(tuples=criteria, length=3, filler=[_nop])
        specs = tuple([(field, func) for value, field, func in criteria])
        match = tuple([value for value, field, func in criteria])
        current = yo.current(index=True)
        matchlen = len(match)
        while not yo.Eof():
            record = yo.current()
            results = record(*specs)
            if results == match:
                return record
        return yo.goto(current)
    def index(yo, sort=None, reverse=False):
        "orders the table using the tuple provided; removes index if no sort provided"
        if sort is None:
            results = []
            for field, func in yo._meta.index:
                results.append("%s(%s)" % (func.__name__, field))
            return ', '.join(results + ['reverse=%s' % yo._meta.index_reversed])
        yo._meta.index_reversed = reverse
        if sort == 'ORIGINAL':
            yo._index = range(yo._meta.header.record_count)
            yo._meta.index = []
            if reverse:
                yo._index.reverse()
            return
        new_sort = _normalize_tuples(tuples=sort, length=2, filler=[_nop])
        yo._meta.index = tuple(new_sort)
        yo._meta.orderresults = [''] * len(yo)
        for record in yo:
            yo._meta.orderresults[record.record_number] = record()
        yo._index.sort(key=lambda i: yo._meta.orderresults[i], reverse=reverse)
    def is_memotype(yo, name):
        "returns True if name is a memo type field"
        return yo._meta[name]['type'] in yo._memotypes
    def new(yo, filename, _field_specs=None):
        "returns a new table of the same type"
        if _field_specs is None:
            _field_specs = yo.structure()
        if filename != ':memory:':
            path, name = os.path.split(filename)
            if path == "":
                filename = os.path.join(os.path.split(yo.filename)[0], filename)
            elif name == "":
                filename = os.path.join(path, os.path.split(yo.filename)[1])
        return yo.__class__(filename, _field_specs)
    def next(yo):
        "set record pointer to next (non-deleted) record, and return it"
        if yo.eof():
            raise Eof()
        return yo.current()
    def pack(yo, _pack=True):
        "physically removes all deleted records"
        newtable = []
        newindex = []
        i = 0
        for record in yo._table:
            if record.has_been_deleted and _pack:
                record._recnum = -1
            else:
                record._recnum = i
                newtable.append(record)
                newindex.append(i)
                i += 1
        yo._table = newtable
        yo._index = newindex
        yo._meta.header.record_count = i
        yo._current = -1
        yo._meta.index = ''
        yo._update_disk()
    def prev(yo):
        "set record pointer to previous (non-deleted) record, and return it"
        if yo.bof():
            raise Bof
        return yo.current()
    def query(yo, sql=None, python=None):
        "uses exec to perform python queries on the table"
        if python is None:
            raise DbfError("query: python parameter must be specified")
        possible = DbfList(desc="%s -->  %s" % (yo.filename, python))
        query_result = {}
        select = 'query_result["keep"] = %s' % python
        g = {}
        for record in yo:
            query_result['keep'] = False
            g['query_result'] = query_result
            exec select in g, record
            if query_result['keep']:
                possible.append(record)
        return possible
    def rename_field(yo, oldname, newname):
        "renames an existing field"
        if yo:
            yo.create_backup()
        if not oldname in yo._meta.fields:
            raise DbfError("field --%s-- does not exist -- cannot rename it." % oldname)
        if newname[0] == '_' or newname[0].isdigit() or not newname.replace('_','').isalnum():
            raise DbfError("field names cannot start with _ or digits, and can only contain the _, letters, and digits")
        newname = newname.lower()
        if newname in yo._meta.fields:
            raise DbfError("field --%s-- already exists" % newname)
        if len(newname) > 10:
            raise DbfError("maximum field name length is 10.  '%s' is %d characters long." % (newname, len(newname)))
        yo._meta[newname] = yo._meta[oldname]
        yo._meta.fields[yo._meta.fields.index(oldname)] = newname
        yo._buildHeaderFields()
        yo._update_disk(headeronly=True)
    def search(yo, match, fuzzy=None, indices=False):
        """searches using a binary algorythm 
        looking for records that match the criteria in match, which is a tuple 
        with a data item per ordered field.  table must be sorted.  if index, 
        returns a list of records' indices from the current sort order.
        """
        if yo._meta.index is None:
            raise DbfError('table must be indexed to use Search')
        matchlen = len(match)
        if fuzzy:
            matchlen -= 1
            fuzzy_match = match[-1]
            fuzzy_field = yo._meta.index[matchlen][0]
            match = match[:-1]
            records = DbfList(desc="%s -->  search: index=%s, match=%s, fuzzy=%s(%s))" % (yo.filename, yo.index(), match, fuzzy.__name__, fuzzy_match))
        else:
            records = DbfList(desc="%s -->  search: index=%s, match=%s)" % (yo.filename, yo.index(), match))
        if indices:
            records = []
        if not isinstance(match, tuple):
            match = tuple(match)
        segment = len(yo)
        current = 0
        toosoon = True
        notFound = True
        while notFound:
            segment = segment // 2
            if toosoon:
                current += segment
            else:
                current -= segment
            if current % 2:
                segment += 1
            if current == len(yo) or segment == 0:
                break
            value = yo._meta.orderresults[yo[current].record_number][:matchlen]
            if value < match:
                toosoon = True
            elif value > match:
                toosoon = False
            else:
                notFound = False
                break
            if current == 0:
                break
        if notFound:
            return records
        while current > 0:
            current -= 1
            value = yo._meta.orderresults[yo[current].record_number][:matchlen]
            if value != match:
                current += 1
                break
        while True:
            value = yo._meta.orderresults[yo[current].record_number][:matchlen]
            if value != match:
                break
            if yo.use_deleted or not yo[current].has_been_deleted:
                if indices:
                    records.append(current)
                else:
                    records.append(yo[current])
            current += 1
            if current == len(yo):
                break
            if fuzzy:
                if indices:
                    records = [rec for rec in records if fuzzy(yo[rec][fuzzy_field]) == fuzzy_match]
                else:
                    final_records = [rec for rec in records if fuzzy(rec[fuzzy_field]) == fuzzy_match]
                    records.clear()
                    records.extend(final_records)
        return records
    def size(yo, field):
        "returns size of field as a tuple of (length, decimals)"
        if field in yo:
            return (yo._meta[field]['length'], yo._meta[field]['decimals'])
        raise DbfError("%s is not a field in %s" % (field, yo.filename))
    def structure(yo, fields=None):
        """return list of fields suitable for creating same table layout
        @param fields: list of fields or None for all fields"""
        field_specs = []
        fields = yo._list_fields(fields)
        try:
            for name in fields:
                field_specs.append(yo._fieldLayout(yo.field_names.index(name)))
        except ValueError:
            raise DbfError("field --%s-- does not exist" % name)
        return field_specs
    def top(yo, get_record=False):
        """sets record pointer to top of table; if get_record, seeks to and returns first (non-deleted) record
        DbfError if table is empty
        Eof if all records are deleted and use_deleted is False"""
        yo._meta.current = -1
        if get_record:
            try:
                return yo.next()
            except Eof:
                yo._meta.current = -1
                raise Bof()
    def type(yo, field):
        "returns type of field"
        if field in yo:
            return yo._meta[field]['type']
        raise DbfError("%s is not a field in %s" % (field, yo.filename))
    def zap(yo, areyousure=False):
        """removes all records from table -- this cannot be undone!
        areyousure must be True, else error is raised"""
        if areyousure:
            yo._table = []
            yo._index = []
            yo._meta.header.record_count = 0
            yo._current = -1
            yo._meta.index = ''
            yo._update_disk()
        else:
            raise DbfError("You must say you are sure to wipe the table")
    # these asignments are for backward compatibility, and will go away
class Db3Table(DbfTable):
    """Provides an interface for working with dBase III tables."""
    _version = 'dBase III Plus'
    _versionabbv = 'db3'
    _fieldtypes = {
            'C' : {'Type':'Character', 'Retrieve':io.retrieveCharacter, 'Update':io.updateCharacter, 'Blank':str, 'Init':io.addCharacter},
            'D' : {'Type':'Date', 'Retrieve':io.retrieveDate, 'Update':io.updateDate, 'Blank':Date.today, 'Init':io.addDate},
            'L' : {'Type':'Logical', 'Retrieve':io.retrieveLogical, 'Update':io.updateLogical, 'Blank':bool, 'Init':io.addLogical},
            'M' : {'Type':'Memo', 'Retrieve':io.retrieveMemo, 'Update':io.updateMemo, 'Blank':str, 'Init':io.addMemo},
            'N' : {'Type':'Numeric', 'Retrieve':io.retrieveNumeric, 'Update':io.updateNumeric, 'Blank':int, 'Init':io.addNumeric} }
    _memoext = '.dbt'
    _memotypes = ('M',)
    _memoClass = _Db3Memo
    _yesMemoMask = '\x80'
    _noMemoMask = '\x7f'
    _fixed_fields = ('D','L','M')
    _variable_fields = ('C','N')
    _character_fields = ('C','M') 
    _decimal_fields = ('N',)
    _numeric_fields = ('N',)
    _dbfTableHeader = array('c', '\x00' * 32)
    _dbfTableHeader[0] = '\x03'         # version - dBase III w/o memo's
    _dbfTableHeader[8:10] = array('c', io.packShortInt(33))
    _dbfTableHeader[10] = '\x01'        # record length -- one for delete flag
    _dbfTableHeader[29] = '\x03'        # code page -- 437 US-MS DOS
    _dbfTableHeader = _dbfTableHeader.tostring()
    _dbfTableHeaderExtra = ''
    _supported_tables = ['\x03', '\x83']
    _read_only = False
    _meta_only = False
    _use_deleted = True
    def _checkMemoIntegrity(yo):
        "dBase III specific"
        if yo._meta.header.version == '\x83':
            try:
                yo._meta.memo = yo._memoClass(yo._meta)
            except:
                yo._meta.dfd.close()
                yo._meta.dfd = None
                raise
        if not yo._meta.ignorememos:
            for field in yo._meta.fields:
                if yo._meta[field]['type'] in yo._memotypes:
                    if yo._meta.header.version != '\x83':
                        yo._meta.dfd.close()
                        yo._meta.dfd = None
                        raise DbfError("Table structure corrupt:  memo fields exist, header declares no memos")
                    elif not os.path.exists(yo._meta.memoname):
                        yo._meta.dfd.close()
                        yo._meta.dfd = None
                        raise DbfError("Table structure corrupt:  memo fields exist without memo file")
                    break
    def _initializeFields(yo):
        "builds the FieldList of names, types, and descriptions"
        offset = 1
        fieldsdef = yo._meta.header.fields
        if len(fieldsdef) % 32 != 0:
            raise DbfError("field definition block corrupt: %d bytes in size" % len(fieldsdef))
        if len(fieldsdef) // 32 != yo.field_count:
            raise DbfError("Header shows %d fields, but field definition block has %d fields" % (yo.field_count, len(fieldsdef)//32))
        for i in range(yo.field_count):
            fieldblock = fieldsdef[i*32:(i+1)*32]
            name = io.unpackStr(fieldblock[:11])
            type = fieldblock[11]
            if not type in yo._meta.fieldtypes:
                raise DbfError("Unknown field type: %s" % type)
            start = offset
            length = ord(fieldblock[16])
            offset += length
            end = start + length
            decimals = ord(fieldblock[17])
            flags = ord(fieldblock[18])
            yo._meta.fields.append(name)
            yo._meta[name] = {'type':type,'start':start,'length':length,'end':end,'decimals':decimals,'flags':flags}
class FpTable(DbfTable):
    'Provides an interface for working with FoxPro 2 tables'
    _version = 'Foxpro'
    _versionabbv = 'fp'
    _fieldtypes = {
            'C' : {'Type':'Character', 'Retrieve':io.retrieveCharacter, 'Update':io.updateCharacter, 'Blank':str, 'Init':io.addCharacter},
            'F' : {'Type':'Float', 'Retrieve':io.retrieveNumeric, 'Update':io.updateNumeric, 'Blank':float, 'Init':io.addVfpNumeric},
            'N' : {'Type':'Numeric', 'Retrieve':io.retrieveNumeric, 'Update':io.updateNumeric, 'Blank':int, 'Init':io.addVfpNumeric},
            'L' : {'Type':'Logical', 'Retrieve':io.retrieveLogical, 'Update':io.updateLogical, 'Blank':bool, 'Init':io.addLogical},
            'D' : {'Type':'Date', 'Retrieve':io.retrieveDate, 'Update':io.updateDate, 'Blank':Date.today, 'Init':io.addDate},
            'M' : {'Type':'Memo', 'Retrieve':io.retrieveMemo, 'Update':io.updateMemo, 'Blank':str, 'Init':io.addVfpMemo},
            'G' : {'Type':'General', 'Retrieve':io.retrieveMemo, 'Update':io.updateMemo, 'Blank':str, 'Init':io.addMemo},
            'P' : {'Type':'Picture', 'Retrieve':io.retrieveMemo, 'Update':io.updateMemo, 'Blank':str, 'Init':io.addMemo},
            '0' : {'Type':'_NullFlags', 'Retrieve':io.unsupportedType, 'Update':io.unsupportedType, 'Blank':int, 'Init':None} }
    _memoext = '.fpt'
    _memotypes = ('G','M','P')
    _memoClass = _VfpMemo
    _yesMemoMask = '\xf5'               # 1111 0101
    _noMemoMask = '\x03'                # 0000 0011
    _fixed_fields = ('B','D','G','I','L','M','P','T','Y')
    _variable_fields = ('C','F','N')
    _character_fields = ('C','M')       # field representing character data
    _decimal_fields = ('F','N')
    _numeric_fields = ('B','F','I','N','Y')
    _supported_tables = ('\x03', '\xf5')
    _dbfTableHeader = array('c', '\x00' * 32)
    _dbfTableHeader[0] = '\x30'         # version - Foxpro 6  0011 0000
    _dbfTableHeader[8:10] = array('c', io.packShortInt(33+263))
    _dbfTableHeader[10] = '\x01'        # record length -- one for delete flag
    _dbfTableHeader[29] = '\x03'        # code page -- 437 US-MS DOS
    _dbfTableHeader = _dbfTableHeader.tostring()
    _dbfTableHeaderExtra = '\x00' * 263
    _use_deleted = True
    def _checkMemoIntegrity(yo):
        if os.path.exists(yo._meta.memoname):
            try:
                yo._meta.memo = yo._memoClass(yo._meta)
            except:
                yo._meta.dfd.close()
                yo._meta.dfd = None
                raise
        if not yo._meta.ignorememos:
            for field in yo._meta.fields:
                if yo._meta[field]['type'] in yo._memotypes:
                    if not os.path.exists(yo._meta.memoname):
                        yo._meta.dfd.close()
                        yo._meta.dfd = None
                        raise DbfError("Table structure corrupt:  memo fields exist without memo file")
                    break
    def _initializeFields(yo):
        "builds the FieldList of names, types, and descriptions"
        offset = 1
        fieldsdef = yo._meta.header.fields
        if len(fieldsdef) % 32 != 0:
            raise DbfError("field definition block corrupt: %d bytes in size" % len(fieldsdef))
        if len(fieldsdef) // 32 != yo.field_count:
            raise DbfError("Header shows %d fields, but field definition block has %d fields" % (yo.field_count, len(fieldsdef)//32))
        for i in range(yo.field_count):
            fieldblock = fieldsdef[i*32:(i+1)*32]
            name = io.unpackStr(fieldblock[:11])
            type = fieldblock[11]
            if not type in yo._meta.fieldtypes:
                raise DbfError("Unknown field type: %s" % type)
            elif type == '0':
                return          # ignore nullflags
            start = offset
            length = ord(fieldblock[16])
            offset += length
            end = start + length
            decimals = ord(fieldblock[17])
            flags = ord(fieldblock[18])
            yo._meta.fields.append(name)
            yo._meta[name] = {'type':type,'start':start,'length':length,'end':end,'decimals':decimals,'flags':flags}
            
class VfpTable(DbfTable):
    'Provides an interface for working with Visual FoxPro 6 tables'
    _version = 'Visual Foxpro v6'
    _versionabbv = 'vfp'
    _fieldtypes = {
            'C' : {'Type':'Character', 'Retrieve':io.retrieveCharacter, 'Update':io.updateCharacter, 'Blank':str, 'Init':io.addCharacter},
            'Y' : {'Type':'Currency', 'Retrieve':io.retrieveCurrency, 'Update':io.updateCurrency, 'Blank':Decimal(), 'Init':io.addVfpCurrency},
            'B' : {'Type':'Double', 'Retrieve':io.retrieveDouble, 'Update':io.updateDouble, 'Blank':float, 'Init':io.addVfpDouble},
            'F' : {'Type':'Float', 'Retrieve':io.retrieveNumeric, 'Update':io.updateNumeric, 'Blank':float, 'Init':io.addVfpNumeric},
            'N' : {'Type':'Numeric', 'Retrieve':io.retrieveNumeric, 'Update':io.updateNumeric, 'Blank':int, 'Init':io.addVfpNumeric},
            'I' : {'Type':'Integer', 'Retrieve':io.retrieveInteger, 'Update':io.updateInteger, 'Blank':int, 'Init':io.addVfpInteger},
            'L' : {'Type':'Logical', 'Retrieve':io.retrieveLogical, 'Update':io.updateLogical, 'Blank':bool, 'Init':io.addLogical},
            'D' : {'Type':'Date', 'Retrieve':io.retrieveDate, 'Update':io.updateDate, 'Blank':Date.today, 'Init':io.addDate},
            'T' : {'Type':'DateTime', 'Retrieve':io.retrieveVfpDateTime, 'Update':io.updateVfpDateTime, 'Blank':DateTime.now, 'Init':io.addVfpDateTime},
            'M' : {'Type':'Memo', 'Retrieve':io.retrieveVfpMemo, 'Update':io.updateVfpMemo, 'Blank':str, 'Init':io.addVfpMemo},
            'G' : {'Type':'General', 'Retrieve':io.retrieveVfpMemo, 'Update':io.updateVfpMemo, 'Blank':str, 'Init':io.addVfpMemo},
            'P' : {'Type':'Picture', 'Retrieve':io.retrieveVfpMemo, 'Update':io.updateVfpMemo, 'Blank':str, 'Init':io.addVfpMemo},
            '0' : {'Type':'_NullFlags', 'Retrieve':io.unsupportedType, 'Update':io.unsupportedType, 'Blank':int, 'Init':None} }
    _memoext = '.fpt'
    _memotypes = ('G','M','P')
    _memoClass = _VfpMemo
    _yesMemoMask = '\x30'               # 0011 0000
    _noMemoMask = '\x30'                # 0011 0000
    _fixed_fields = ('B','D','G','I','L','M','P','T','Y')
    _variable_fields = ('C','F','N')
    _character_fields = ('C','M')       # field representing character data
    _decimal_fields = ('F','N')
    _numeric_fields = ('B','F','I','N','Y')
    _supported_tables = ('\x30',)
    _dbfTableHeader = array('c', '\x00' * 32)
    _dbfTableHeader[0] = '\x30'         # version - Foxpro 6  0011 0000
    _dbfTableHeader[8:10] = array('c', io.packShortInt(33+263))
    _dbfTableHeader[10] = '\x01'        # record length -- one for delete flag
    _dbfTableHeader[29] = '\x03'        # code page -- 437 US-MS DOS
    _dbfTableHeader = _dbfTableHeader.tostring()
    _dbfTableHeaderExtra = '\x00' * 263
    _use_deleted = True
    def _checkMemoIntegrity(yo):
        if os.path.exists(yo._meta.memoname):
            try:
                yo._meta.memo = yo._memoClass(yo._meta)
            except:
                yo._meta.dfd.close()
                yo._meta.dfd = None
                raise
        if not yo._meta.ignorememos:
            for field in yo._meta.fields:
                if yo._meta[field]['type'] in yo._memotypes:
                    if not os.path.exists(yo._meta.memoname):
                        yo._meta.dfd.close()
                        yo._meta.dfd = None
                        raise DbfError("Table structure corrupt:  memo fields exist without memo file")
                    break
    def _initializeFields(yo):
        "builds the FieldList of names, types, and descriptions"
        offset = 1
        fieldsdef = yo._meta.header.fields
        for i in range(yo.field_count):
            fieldblock = fieldsdef[i*32:(i+1)*32]
            name = io.unpackStr(fieldblock[:11])
            type = fieldblock[11]
            if not type in yo._meta.fieldtypes:
                raise DbfError("Unknown field type: %s" % type)
            elif type == '0':
                return          # ignore nullflags
            start = io.unpackLongInt(fieldblock[12:16])
            length = ord(fieldblock[16])
            offset += length
            end = start + length
            decimals = ord(fieldblock[17])
            flags = ord(fieldblock[18])
            yo._meta.fields.append(name)
            yo._meta[name] = {'type':type,'start':start,'length':length,'end':end,'decimals':decimals,'flags':flags}
class DbfList(object):
    "list of Dbf records, with set-like behavior"
    _desc = ''
    def __init__(yo, new_records=None, desc=None):
        yo._list = []
        yo._set = set()
        yo._current = -1
        if isinstance(new_records, DbfList):
            yo._list = new_records._list[:]
            yo._set = new_records._set.copy()
            yo._current = 0
        elif new_records is not None:
            for record in new_records:
                item = (record.record_table, record.record_number)
                if item not in yo._set:
                    yo._set.add(item)
                    yo._list.append(item)
            yo._current = 0
        if desc is not None:
            yo._desc = desc
    def __add__(yo, other):
        if isinstance(other, DbfList):
            result = DbfList()
            result._set = yo._set.copy()
            result._list[:] = yo._list[:]
            for item in other._list:
                if item not in result._set:
                    result._set.add(item)
                    result._list.append(item)
            result._current = 0 if result else -1
            return result
        return NotImplemented
    def __delitem__(yo, key):
        if isinstance(key, int):
            item = yo._list.pop[key]
            yo._set.remove(item)
        elif isinstance(key, slice):
            yo._set.difference_update(yo._list[key])
            yo._list.__delitem__(key)
        else:
            raise TypeError
    def __getitem__(yo, key):
        if isinstance(key, int):
            count = len(yo._list)
            if not -count <= key < count:
                raise IndexError("Record %d is not in list." % key)
            return yo._get_record(*yo._list[key])
        elif isinstance(key, slice):
            result = DbfList()
            result._list[:] = yo._list[key]
            result._set = set(result._list)
            result._current = 0 if result else -1
            return result
        else:
            raise TypeError
    def __iter__(yo):
        return (table.get_record(recno) for table, recno in yo._list)
    def __len__(yo):
        return len(yo._list)
    def __nonzero__(yo):
        return len(yo) > 0
    def __radd__(yo, other):
        return yo.__add__(other)
    def __repr__(yo):
        if yo._desc:
            return "DbfList(%s - %d records)" % (yo._desc, len(yo._list))
        else:
            return "DbfList(%d records)" % len(yo._list)
    def __rsub__(yo, other):
        if isinstance(other, DbfList):
            result = DbfList()
            result._list[:] = other._list[:]
            result._set = other._set.copy()
            lost = set()
            for item in yo._list:
                if item in result._list:
                    result._set.remove(item)
                    lost.add(item)
            result._list = [item for item in result._list if item not in lost]
            result._current = 0 if result else -1
            return result
        return NotImplemented
    def __sub__(yo, other):
        if isinstance(other, DbfList):
            result = DbfList()
            result._list[:] = yo._list[:]
            result._set = yo._set.copy()
            lost = set()
            for item in other._list:
                if item in result._set:
                    result._set.remove(item)
                    lost.add(item)
            result._list = [item for item in result._list if item not in lost]
            result._current = 0 if result else -1
            return result
        return NotImplemented
    def _maybe_add(yo, item):
        if item not in yo._set:
            yo._set.add(item)
            yo._list.append(item)
    def _get_record(yo, table=None, rec_no=None):
        if table is rec_no is None:
            table, rec_no = yo._list[yo._current]
        return table.get_record(rec_no)
    def append(yo, new_record):
        yo._maybe_add((new_record.record_table, new_record.record_number))
        if yo._current == -1 and yo._list:
            yo._current = 0
    def bottom(yo):
        if yo._list:
            yo._current = len(yo._list) - 1
            return yo._get_record()
        raise DbfError("DbfList is empty")
    def clear(yo):
        yo._list = []
        yo._set = set()
        yo._current = -1
    def current(yo):
        if yo._current < 0:
            raise Bof()
        elif yo._current == len(yo._list):
            raise Eof()
        return yo._get_record()
    def extend(yo, new_records):
        if isinstance(new_records, DbfList):
            for item in new_records._list:
                yo._maybe_add(item)
        else:
            for record in new_records:
                yo.append(record)
        if yo._current == -1 and yo._list:
            yo._current = 0
    def goto(yo, index_number):
        if yo._list:
            if 0 <= index_number <= len(yo._list):
                yo._current = index_number
                return yo._get_record()
            raise DbfError("index %d not in DbfList of %d records" % (index_number, len(yo._list)))
        raise DbfError("DbfList is empty")
    def index(yo, record, start=None, stop=None):
        item = record.record_table, record.record_number
        if start is None:
            start = 0
        if stop is None:
            stop = len(yo._list)
        return yo._list.index(item, start, stop)
    def insert(yo, i, table, record):
        item = table, record.record_number
        if item not in yo._set:
            yo._set.add(item)
            yo._list.insert(i, item)
    def next(yo):
        if yo._current < len(yo._list):
            yo._current += 1
            if yo._current < len(yo._list):
                return yo._get_record()
        raise Eof()
    def pop(yo, index=None):
        if index is None:
            table, recno = yo._list.pop()
            yo._set.remove((table, recno))
        else:
            table, recno = yo._list.pop(index)
            yo._set.remove((table, recno))
        return _get_record(table, recno)
    def prev(yo):
        if yo._current >= 0:
            yo._current -= 1
            if yo._current > -1:
                return yo._get_record()
        raise Bof()
    def remove(yo, record):
        item = record.record_table, record.record_number
        yo._list.remove(item)
        yo._set.remove(item)
    def reverse(yo):
        return yo._list.reverse()
    def top(yo):
        if yo._list:
            yo._current = 0
            return yo._get_record()
        raise DbfError("DbfList is empty")
    def sort(yo, key=None, reverse=False):
        if key is None:
            return yo._list.sort(reverse=reverse)
        #temp = []
        #for item in yo._list:
        #    temp.append((key(item[0].get_record(item[1])), item))
        #temp.sort(reverse=reverse)
        #yo._list[:] = temp[:]
        return yo._list.sort(key=lambda item: key(item[0].get_record(item[1])), reverse=reverse)

class DbfCsv(csv.Dialect):
    "csv format for exporting tables"
    delimiter = ','
    doublequote = True
    escapechar = None
    lineterminator = '\r\n'
    quotechar = '"'
    skipinitialspace = True
    quoting = csv.QUOTE_NONNUMERIC
csv.register_dialect('dbf', DbfCsv)

def _nop(value):
    "returns parameter unchanged"
    return value
def _normalize_tuples(tuples, length, filler):
    "ensures each tuple is the same length, using filler[-missing] for the gaps"
    final = []
    for t in tuples:
        if len(t) < length:
            final.append( tuple([item for item in t] + filler[len(t)-length:]) )
        else:
            final.append(t)
    return tuple(final)
def _codepage_lookup(cp):
    if cp not in code_pages:
        for code_page in sorted(code_pages.keys()):
            sd, ld = code_pages[code_page]
            if cp == sd or cp == ld:
                if sd is None:
                    raise DbfError("Unsupported codepage: %s" % ld)
                cp = code_page
                break
        else:
            raise DbfError("Unsupported codepage: %s" % cp)
    sd, ld = code_pages[cp]
    return cp, sd, ld
def ascii(new_setting=None):
    "get/set return_ascii setting"
    global return_ascii
    if new_setting is None:
        return return_ascii
    else:
        return_ascii = new_setting
def codepage(cp=None):
    "get/set default codepage for any new tables"
    global default_codepage
    cp, sd, ld = _codepage_lookup(cp or default_codepage)
    default_codepage = sd
    return "%s (LDID: 0x%02x - %s)" % (sd, ord(cp), ld)
def encoding(cp=None):
    "get/set default encoding for non-unicode strings passed into a table"
    global input_decoding
    cp, sd, ld = _codepage_lookup(cp or input_decoding)
    default_codepage = sd
    return "%s (LDID: 0x%02x - %s)" % (sd, ord(cp), ld)
class _Db4Table(DbfTable):
    version = 'dBase IV w/memos (non-functional)'
    _versionabbv = 'db4'
    _fieldtypes = {
            'C' : {'Type':'Character', 'Retrieve':io.retrieveCharacter, 'Update':io.updateCharacter, 'Blank':str, 'Init':io.addCharacter},
            'Y' : {'Type':'Currency', 'Retrieve':io.retrieveCurrency, 'Update':io.updateCurrency, 'Blank':Decimal(), 'Init':io.addVfpCurrency},
            'B' : {'Type':'Double', 'Retrieve':io.retrieveDouble, 'Update':io.updateDouble, 'Blank':float, 'Init':io.addVfpDouble},
            'F' : {'Type':'Float', 'Retrieve':io.retrieveNumeric, 'Update':io.updateNumeric, 'Blank':float, 'Init':io.addVfpNumeric},
            'N' : {'Type':'Numeric', 'Retrieve':io.retrieveNumeric, 'Update':io.updateNumeric, 'Blank':int, 'Init':io.addVfpNumeric},
            'I' : {'Type':'Integer', 'Retrieve':io.retrieveInteger, 'Update':io.updateInteger, 'Blank':int, 'Init':io.addVfpInteger},
            'L' : {'Type':'Logical', 'Retrieve':io.retrieveLogical, 'Update':io.updateLogical, 'Blank':bool, 'Init':io.addLogical},
            'D' : {'Type':'Date', 'Retrieve':io.retrieveDate, 'Update':io.updateDate, 'Blank':Date.today, 'Init':io.addDate},
            'T' : {'Type':'DateTime', 'Retrieve':io.retrieveVfpDateTime, 'Update':io.updateVfpDateTime, 'Blank':DateTime.now, 'Init':io.addVfpDateTime},
            'M' : {'Type':'Memo', 'Retrieve':io.retrieveMemo, 'Update':io.updateMemo, 'Blank':str, 'Init':io.addMemo},
            'G' : {'Type':'General', 'Retrieve':io.retrieveMemo, 'Update':io.updateMemo, 'Blank':str, 'Init':io.addMemo},
            'P' : {'Type':'Picture', 'Retrieve':io.retrieveMemo, 'Update':io.updateMemo, 'Blank':str, 'Init':io.addMemo},
            '0' : {'Type':'_NullFlags', 'Retrieve':io.unsupportedType, 'Update':io.unsupportedType, 'Blank':int, 'Init':None} }
    _memoext = '.dbt'
    _memotypes = ('G','M','P')
    _memoClass = _VfpMemo
    _yesMemoMask = '\x8b'               # 0011 0000
    _noMemoMask = '\x04'                # 0011 0000
    _fixed_fields = ('B','D','G','I','L','M','P','T','Y')
    _variable_fields = ('C','F','N')
    _character_fields = ('C','M')       # field representing character data
    _decimal_fields = ('F','N')
    _numeric_fields = ('B','F','I','N','Y')
    _supported_tables = ('\x04', '\x8b')
    _dbfTableHeader = ['\x00'] * 32
    _dbfTableHeader[0] = '\x8b'         # version - Foxpro 6  0011 0000
    _dbfTableHeader[10] = '\x01'        # record length -- one for delete flag
    _dbfTableHeader[29] = '\x03'        # code page -- 437 US-MS DOS
    _dbfTableHeader = ''.join(_dbfTableHeader)
    _dbfTableHeaderExtra = ''
    _use_deleted = True
    def _checkMemoIntegrity(yo):
        "dBase III specific"
        if yo._meta.header.version == '\x8b':
            try:
                yo._meta.memo = yo._memoClass(yo._meta)
            except:
                yo._meta.dfd.close()
                yo._meta.dfd = None
                raise
        if not yo._meta.ignorememos:
            for field in yo._meta.fields:
                if yo._meta[field]['type'] in yo._memotypes:
                    if yo._meta.header.version != '\x8b':
                        yo._meta.dfd.close()
                        yo._meta.dfd = None
                        raise DbfError("Table structure corrupt:  memo fields exist, header declares no memos")
                    elif not os.path.exists(yo._meta.memoname):
                        yo._meta.dfd.close()
                        yo._meta.dfd = None
                        raise DbfError("Table structure corrupt:  memo fields exist without memo file")
                    break

