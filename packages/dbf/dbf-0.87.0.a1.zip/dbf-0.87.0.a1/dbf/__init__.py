"""
Copyright
=========
    - Copyright: 2008-2009 Ad-Mail, Inc -- All rights reserved.
    - Author: Ethan Furman
    - Contact: ethanf@admailinc.com
    - Organization: Ad-Mail, Inc.
    - Version: 0.85.005 as of 29 Oct 2009

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    - Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    - Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    - Neither the name of Ad-Mail, Inc nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY Ad-Mail, Inc ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Ad-Mail, Inc BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

B{I{Summary}}

Python package for reading/writing dBase III and VFP 6 tables and memos

The entire table is read into memory, and all operations occur on the in-memory
table, with data changes being written to disk as they occur.

Goals:  programming style with databases
    - C{table = dbf.table('table name' [, fielddesc[, fielddesc[, ....]]])}
        - fielddesc examples:  C{name C(30); age N(3,0); wisdom M; marriage D}
    - C{record = [ table.current() | table[int] | table.append() | table.[next|prev|top|bottom|goto]() ]}
    - C{record.field | record['field']} accesses the field

NOTE:  Of the VFP data types, auto-increment and null settings are not implemented.
"""
import os

from dbf.dates import Date, DateTime, Time
from dbf.exceptions import DbfWarning, Bof, Eof, DbfError, DataOverflow, FieldMissing
from dbf.tables import DbfTable, Db3Table, VfpTable, DbfList, DbfCsv
from dbf.tables import ascii, codepage, encoding, version_map

version = (0, 86, 0)

__docformat__ = 'epytext'

def Table(filename, field_specs='', memo_size=128, ignore_memos=False, \
          read_only=False, keep_memos=False, meta_only=False, type='db3', codepage=None):
    "returns an open table of the correct type, or creates it if field_specs is given"
    type = type.lower()
    if field_specs:
        if type == 'db3':
            return Db3Table(filename, field_specs, memo_size, ignore_memos)
        elif type == 'vfp':
            return VfpTable(filename, field_specs, memo_size, ignore_memos)
        elif type == 'dbf':
            return DbfTable(filename, field_specs)
        else:
            raise TypeError("Unknown table type: %s" % type)
    else:
        base, ext = os.path.splitext(filename)
        if ext == '':
            filename = base + '.dbf'
        if not os.path.exists(filename):
            raise DbfError("File %s not found, field_specs not specified" % filename)
        fd = open(filename)
        version = fd.read(1)
        fd.close()
        fd = None
        if not version in version_map:
            raise TypeError("Unknown dbf type: %x" % ord(version))
        for tabletype in (Db3Table, VfpTable):
            if version in tabletype._supported_tables:
                return tabletype(filename, field_specs, memo_size, ignore_memos, \
                                 read_only, keep_memos, meta_only)
        else:
            raise TypeError("Tables of type <%s [%x]> are not supported." % (version_map.get(version, 'Unknown: %s' % version), ord(version)))
def table_type(filename):
    "returns text representation of a table's dbf version"
    base, ext = os.path.splitext(filename)
    if ext == '':
        filename = base + '.dbf'
    if os.path.exists(filename):
        fd = open(filename)
        version = fd.read(1)
        fd.close()
        fd = None
        if not version in version_map:
            raise TypeError("Unknown dbf type: %s (%x)" % (version, ord(version)))
        return version_map[version]
    return 'File %s not found' % filename
def add_fields(table, field_specs):
    "adds fields to an existing table"
    table = Table(table)
    try:
        table.add_fields(field_specs)
    finally:
        table.close()
def delete_fields(table, field_names):
    "deletes fields from an existing table"
    table = Table(table)
    try:
        table.delete_fields(field_names)
    finally:
        table.close()
def export(table, filename='', fields='', format='csv', header=True):
    "creates a csv or tab-delimited file from an existing table"
    table = Table(table)
    try:
        table.export(filename, fields, format, header)
    finally:
        table.close()
def first_record(table):
    "prints the first record of a table"
    table = Table(table)
    try:
        print str(table[0])
    finally:
        table.close()
def from_csv(csvfile, to_disk=False, filename=None, field_names=None):
    "creates a Character table from a csv file"
    reader = csv.reader(open(csvfile))
    if field_names is None:
        field_names = ['f0']
    else:
        field_names = field_names.replace(', ',',').split(',')
    mtable = Table(':memory:', '%s M' % field_names[0])
    field_count = 1
    for row in reader:
        while field_count < len(row):
            if field_count == len(field_names):
                field_names.append('f%d' % field_count)
            mtable.add_fields('%s M' % field_names[field_count])
            field_count += 1
        mtable.append(tuple(row))
    if to_disk:
        if filename is None:
            filename = os.path.splitext(csvfile)[0]
        length = [1] * field_count
        for record in mtable:
            for i in range(field_count):
                length[i] = max(length[i], len(record[i]))
        fields = mtable.field_names
        fielddef = []
        for i in range(field_count):
            if length[i] < 255:
                fielddef.append('%s C(%d)' % (fields[i], length[i]))
            else:
                fielddef.append('%s M' % (fields[i]))
        csvtable = Table(filename, ','.join(fielddef))
        for record in mtable:
            csvtable.append(record.scatter_fields())
    return mtable
def get_fields(table):
    "returns the list of field names of a table"
    table = Table(table)
    return table.field_names
def info(table):
    "prints table info"
    table = Table(table)
    print str(table)
def rename_field(table, oldfield, newfield):
    "renames a field in a table"
    table = Table(table)
    try:
        table.rename_field(oldfield, newfield)
    finally:
        table.close()
def structure(table, field=None):
    "returns the definition of a field (or all fields)"
    table = Table(table)
    return table.structure(field)
def hex_dump(records):
    "just what it says ;)"
    for index,dummy in enumerate(records):
        chars = dummy._data
        print "%2d: " % index,
        for char in chars[1:]:
            print " %2x " % ord(char),
        print

