# -*- coding: utf-8 -*-

import sys
from docutils.nodes import paragraph
from docutils.parsers.rst import Directive
from docutils.statemachine import ViewList

TABLE_COLS = ['Name', 'Required', 'Searchable', 'Type', 'Storage']

class AutoATSchemaDirective(Directive):
    """
    """
    required_arguments = 1
    has_content = False

    def __init__(self,
                 directive,
                 arguments,
                 options,           # ignored
                 content,           # ignored
                 lineno,
                 content_offset,    # ignored
                 block_text,        # ignored
                 state,
                 state_machine,     # ignored
                ):
        assert directive == 'autoatschema'
        self.name = arguments[0]
        self.state = state
        self.lineno = lineno

    def run(self):

        schema_data_tableinfo = []
        for col in TABLE_COLS:
            schema_data_tableinfo.append(len(col))
        
        schema_data = []
        schema = _resolve_dotted_name(self.name)
        for field in schema._fields:
            field = schema.get(field)
            schema_data.append([
                str(field.getName()),
                str(field.required),
                str(field.searchable),
                str(field.type),
                str(field.storage.__class__.__name__),
                ])

            if len(str(field.getName())) > schema_data_tableinfo[0]:
                schema_data_tableinfo[0] = len(str(field.getName()))
            if len(str(field.required)) > schema_data_tableinfo[1]:
                schema_data_tableinfo[1] = len(str(field.required))
            if len(str(field.searchable)) > schema_data_tableinfo[2]:
                schema_data_tableinfo[2] = len(str(field.searchable))
            if len(str(field.type)) > schema_data_tableinfo[3]:
                schema_data_tableinfo[3] = len(str(field.type))
            if len(str(field.storage.__class__.__name__)) > schema_data_tableinfo[4]:
                schema_data_tableinfo[4] = len(str(field.storage.__class__.__name__))

        result = ViewList()
        result.append(u'', '<autoatschema>')
        result.append(u'%s: ``%s``' % (self.name.split('.')[-1], self.name), '<autoatschema>')
        result.append(u'', '<autoatschema>')
        for line in self._buildTable('|l|c|c|l|l|', schema_data,
                                        schema_data_tableinfo):
            result.append(line, '<autoatschema>')
        result.append(u'', '<autoatschema>')
        node = paragraph()
        self.state.nested_parse(result, 0, node)
        return node.children

    def _buildTable(self, specs, data, datainfo):
        result = [u'.. tabularcolumns:: '+specs, u'']
        
        # separator line
        separator_line = ''
        for colnum in datainfo:
            separator_line += '='*colnum
            separator_line += ' '
        separator_line = separator_line[:-1]

        # header
        header = ''
        for pos, col in enumerate(TABLE_COLS):
            header += col+(datainfo[pos]-len(col))*' '
            header += ' '
        header = header[:-1]

        result.append(separator_line)
        result.append(header)
        result.append(separator_line)

        for data_row in data:
            row = ''
            for pos, data_col in enumerate(data_row):
                row += data_col+(datainfo[pos]-len(data_col))*' '
                row += ' '
            result.append(row[:-1])

        result.append(separator_line)
        return result

def _resolve_dotted_name(dotted):
    tokens = dotted.split('.')
    path, name = tokens[:-1], tokens[-1]
    thing = __import__('.'.join(path), {}, {}, [name])
    return getattr(thing, name)

def setup(app):
    app.add_directive('autoatschema', AutoATSchemaDirective,
                      0, (1, 0, 1) )
