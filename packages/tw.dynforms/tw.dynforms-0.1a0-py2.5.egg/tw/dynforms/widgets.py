import tw, tw.forms as twf
import sqlalchemy as sa, sqlalchemy.orm as sao, formencode as fe, turbojson

__all__ = ['FilteringGrid', 'WriteOnlyTextField', 'strip_wo_markers',
           'HidingSingleSelectField', 'IntNull', 'load_options',
           'GrowableTableFieldSet', 'GrowableTableForm',
           'OtherSingleSelectField', 'LinkSingleSelectField',
           'AjaxLookupField', 'GrowableRepeater', 'HidingCheckBox']

def unique(l):
    return dict.fromkeys(l, 1).keys()

#--
# Dynamically filtering data grid
#--
class FilteringGrid(twf.TableForm):
    params = \
    {
        'datasrc':      'SQLAlchemy Query object to use as the data source',
        'columns':      'List of (name, label) pairs to display',
        'search_cols':  'List of column names to include in keyword search',
        'data_filter':  'List of column names to have autofilter dropdowns',
        'code_filter':  'Columns to have codified dropdown filters - this takes the following format: {name: [(value1, condition1),...]}',
        'options':      'Checkbox options; a list of (label, value, condition) tuples',
        'blank_msg':    'Text to display if there are no results',
    }
    template = "tw.dynforms.templates.smartlist"

    blank_msg = "(nothing to show)"
    search_cols = []
    options = []
    data_filter = []
    code_filter = {}

    def __new__(cls, *args, **kwargs):
        children = [
            twf.TextField('src_text'),
            twf.SubmitButton('src_search', default='Search'),
            twf.SubmitButton('src_clear', default='Clear'),
        ] + [twf.SingleSelectField(c) for c in cls.data_filter] \
          + [twf.SingleSelectField(c, options=[x[0] for x in m]) for c,m in cls.code_filter.items()] \
          + [twf.CheckBox('cb_%d'%i, label=l) for i,(l,v,c) in enumerate(cls.options)]
        return super(FilteringGrid, cls).__new__(cls, children=children, *args, **kwargs)

    def update_params(self, params):
        if not params['value']:
            params['value'] = {}

        query = params.get('datasrc', self.datasrc)
        src = params['value'].get('src_text')

        if src:
            # Perform a text search
            query = query.filter(sa.or_(*[self.datasrc.c[c].like('%'+src+'%') for c in self.search_cols]))
            params['data'] = query.all()

        else:
            # Generate query conditions from any active filters
            for q in self.code_filter:
                v = params['value'].get(q)
                z = [y for x,y in self.code_filter[q] if x == v]
                if z and z[0]:
                    query = query.filter(hasattr(z[0], '__call__') and z[0]() or z[0])
            for i,(l,t,c) in enumerate(self.options):
                v = bool(params['value'].get('cb_%d' % i))
                if v == t:
                    query = query.filter(hasattr(c, '__call__') and z[0]() or z[0])

            # Apply data filters
            out = []
            for x in query.all():
                for q in self.data_filter:
                    if params['value'].get(q) not in (None, 'All', str(getattr(x, q))):
                        break
                else:
                    out.append(x)
            params['data'] = out

        # Generate events. Can't be done in __new__ as self.id not available
        params.setdefault('child_args', {})
        attrs = {'onchange':'document.getElementById("%s").submit()' % self.id}
        if src: attrs['disabled'] = True
        for d in self.data_filter + self.code_filter.keys():
            params['child_args'][d] = dict(attrs=attrs)
        attrs = {'onclick':'document.getElementById("%s").submit()' % self.id}
        if src: attrs['disabled'] = True
        for i,x in enumerate(self.options):
            params['child_args']['cb_%d'%i] = dict(attrs=attrs)
        attrs = {'onclick': 'document.getElementById("%s_src_text").value=""' % self.id}
        params['child_args']['src_clear'] = dict(attrs=attrs)

        # Generate contents for data dropdowns
        for d in self.data_filter:
            vals = unique(str(getattr(r,d)) for r in params['data'])
            v = params['value'].get(d)
            if v and v != 'All' and v not in vals:
                vals.append(v)
            params['child_args'][d]['options'] = ['All'] + sorted(vals)

        super(FilteringGrid, self).update_params(params)


#--
# Write-only text fields; the server never discloses the content
#--
class WriteOnlyMarker(object):
    pass

class WriteOnlyValidator(fe.validators.FancyValidator):
    def __init__(self, token, *args, **kw):
        super(WriteOnlyValidator, self).__init__(*args, **kw)
        self.token = token
    def to_python(self, value, state=None):
        return value == self.token and WriteOnlyMarker() or value

class WriteOnlyTextField(twf.TextField):
    """A text field that is write-only and never reveals database content"""
    params = {'token': 'Text that is displayed instead of the data. This can only be specified at widget creation, not at display time.'}
    token = '(supplied)'
    def __init__(self, *args, **kw):
        super(WriteOnlyTextField, self).__init__(*args, **kw)
        self.validator = WriteOnlyValidator(self.token)
    def adjust_value(self, value, validator=None):
        return value and self.token or value

def strip_wo_markers(val):
    if isinstance(val, list):
        for v in val:
            strip_wo_markers(v)
    elif isinstance(val, dict):
        for k,v in val.items():
            if isinstance(v, WriteOnlyMarker):
                del val[k]
    return val


#--
#
#--
class IntNull(fe.validators.Int):
    def _to_python(self, value, state):
        if value == '':
            return None
        else:
            return super(IntNull, self)._to_python(value, state)

def load_options(datasrc, code=None, extra=[('', '')]):
    if hasattr(datasrc, 'query'): # TBD: figure a different test, this is a hack
        datasrc = datasrc.query
    data = datasrc.all()
    if data and not code:
        code = [c for c in data[0].c if c.primary_key][0].key
    options = [(getattr(x, code), str(x)) for x in datasrc.all()]
    options.sort(key = lambda x: x[1]) # TBD: remove this
    return extra + options


#--
# Growable forms
#--
class DeleteButton(twf.ImageButton):
    attrs = {'onclick': 'growing_del(this); return false;'}
    src = tw.api.Link(modname=__name__, filename="static/del.png")

class TrFieldSet(twf.FieldSet):
    template = "tw.dynforms.templates.trfieldset"

    def update_params(self, d):
        super(TrFieldSet, self).update_params(d)       
        if d.get('isextra', True):
            d.setdefault('child_args', {})
            for c in self.children:
                l = d['args_for'](c)        
                if not l.has_key('attrs'):
                    l['attrs'] = c.attrs.copy()
                if c.id.endswith('del'):
                    l['attrs']['style'] = 'display:none;' + l['attrs'].get('style', '')
                else:
                    l['attrs']['onchange'] = 'add_section(this);' + l['attrs'].get('onchange', '')
                d['child_args'][c._id] = l

    def post_init(self, *args, **kwargs):
        super(TrFieldSet, self).post_init(*args, **kwargs)
        self.validator.if_missing = None

class StripBlanks(fe.ForEach):
    def any_content(self, val):
        if type(val) == list:
            for v in val:
                if self.any_content(v):
                    return True
            return False
        elif type(val) == dict:
            for k in val:
                if k == 'id':
                    continue
                if self.any_content(val[k]):
                    return True
            return False
        else:
            return bool(val)

    def _to_python(self, value, state):
        val = super(StripBlanks, self)._to_python(value, state)
        return [v for v in val if self.any_content(v)]

class StripGrow(fe.Schema):
    def _to_python(self, value, state):
        return super(StripGrow, self)._to_python(value, state).get('grow', [])

class StrippingFieldRepeater(twf.FormFieldRepeater):
    extra = 1
    repetitions = 0
    max_repetitions = 10 # TBD: recode toscawidgets to not need this
    def post_init(self, *args, **kwargs):
        self.validator = StripBlanks(self.children[0].validator)

class GrowableMixin(object):
    javascript = [tw.api.JSLink(modname=__name__, filename="static/growing.js")]
    params = {
        'colspan': '',
        'dotitle': 'Whether to include a title row in the table',
    }
    colspan = 1
    dotitle = True
    validator = StripGrow

    def clone(self, *args, **kw):
        super(GrowableMixin, self).clone(duringclone=True, *args, **kw)

    def __new__(cls, id=None, parent=None, children=[], duringclone=False, **kw):
        if not children:
            children = list(cls._cls_children)
        if not duringclone:
            children.append(DeleteButton('del'))
            children.append(twf.HiddenField('id', validator=fe.validators.Int))
            children = [
                StrippingFieldRepeater('grow', widget=TrFieldSet('row', children=children)),
                TrFieldSet('spare', children=children),
            ]
        return super(GrowableMixin, cls).__new__(cls, id, parent, children, **kw)

    def update_params(self, params):
        params['undo_url'] = tw.api.Link(modname=__name__, filename="static/undo.png").link
        super(GrowableMixin, self).update_params(params)

class GrowableTableFieldSet(GrowableMixin, twf.FieldSet):
    template = 'tw.dynforms.templates.table_field_set'

class GrowableTableForm(GrowableMixin, twf.TableForm):
    template = 'tw.dynforms.templates.table_form'
    # Avoid calling Form.update_params
    def update_params(self, params):
        params['undo_url'] = tw.api.Link(modname=__name__, filename="static/undo.png").link
        return twf.FormField.update_params(self, params)

class GrowableRepeater(twf.FieldSet):
    validator = StripGrow
    javascript = [tw.api.JSLink(modname=__name__, filename="static/growing.js")]
    template = 'tw.dynforms.templates.growablerepeater'
    params = ['button_text', 'widget']
    button_text = 'Add'
    button_text__doc = 'Text to use on "add" button'
    widget__doc = 'Widget to repeat'

    def __new__(cls, id=None, parent=None, children=[], widget=None, **kw):
        children = [
            StrippingFieldRepeater('grow', widget=widget, extra=0, repetitions=1, max_repetitions=10),
            widget('spare'),
            twf.Button('add', default=cls.button_text, attrs={'onclick':"add_section(this, '')"}),
        ]
        return twf.FieldSet.__new__(cls, id, parent, children, widget=widget, **kw)


#--
# Fancy SingleSelectField derivatices
#--
class HidingSingleSelectField(twf.SingleSelectField):
    javascript = [tw.api.JSLink(modname=__name__, filename='static/hiding.js')]
    params = {
        'mapping': 'Dict that maps selection values to visible controls'
    }
    include_dynamic_js_calls = True

    def update_params(self, params):
        super(HidingSingleSelectField, self).update_params(params)
        mapping = turbojson.jsonify.encode(params.get('mapping', self.mapping))
        params['attrs']['onchange'] = \
            "hssf_change(this, %s);" % mapping + params['attrs'].get('onchange', '')
        self.add_call("hssf_change(document.getElementById('%s'), %s);"  % (self.id, mapping))


class HidingCheckBox(twf.CheckBox):
    javascript = [tw.api.JSLink(modname=__name__, filename='static/hiding.js')]
    params = {
        'mapping': 'Dict that maps selection values to visible controls'
    }
    include_dynamic_js_calls = True

    def update_params(self, params):
        super(HidingCheckBox, self).update_params(params)
        mapping = turbojson.jsonify.encode(params.get('mapping', self.mapping))
        params['attrs']['onclick'] = \
            "hcb_change(this, %s);" % mapping + params['attrs'].get('onchange', '')
        self.add_call("hcb_change(document.getElementById('%s'), %s);"  % (self.id, mapping))


class LinkSingleSelectField(twf.SingleSelectField):
    template = "tw.dynforms.templates.link_select_field"
    javascript = [tw.api.JSLink(modname=__name__, filename='static/hiding.js')]
    params = {
        'link':         'Link target',
        'view_text':    'Allows you to override the text string "view"',
    }
    view_text = 'View'
    include_dynamic_js_calls = True

    def update_params(self, params):
        super(LinkSingleSelectField, self).update_params(params)
        self.add_call("sel_link_change(document.getElementById('%s'))" % self.id)


class OtherChoiceValidator(fe.Schema):
    select = IntNull()
    other = fe.validators.String()

    def __init__(self, dataobj, field, code, other_code, fixed_fields, *args, **kwargs):
        super(OtherChoiceValidator, self).__init__(*args, **kwargs)
        self.dataobj = dataobj
        self.field = field
        self.code = code
        self.other_code = other_code
        self.fixed_fields = fixed_fields

    def _to_python(self, value, state):
        val = super(OtherChoiceValidator, self)._to_python(value, state)
        if val['select'] == self.other_code:
            data = {self.field: value['other']}
            data.update(self.fixed_fields)
            obj = self.dataobj(**data)
            sao.object_session(obj).flush([obj])
            return getattr(obj, self.code)
        else:
            return val['select']


class OtherSingleSelectField(twf.FormField):
    template = "tw.dynforms.templates.ossf"

    params = {
        'datasrc':      'The SQLAlchemy data source to use',
        'dataobj':      'The SQLAlchemy object to use',
        'field':        'The field on the object to use for the "other" text',
        'code':         'The field on the object that is the code',
        'other_code':   'Allows you to override the code used for "other"',
        'other_text':   'Allows you to override the text string "other"',
        'specify_text': 'Allows you to override the text string "Please specify:"',
        'fixed_fields': 'Specify field values on newly created objects',
    }
    code = 'id'
    other_code = 10000
    other_text = 'Other'
    specify_text = 'Please specify:'
    fixed_fields = {}

    children = [
        HidingSingleSelectField('select'),
        twf.TextField('other'),
    ]

    # This is needed to avoid the value being coerced to a dict
    def adapt_value(self, value):
        return value

    def update_params(self, kw):
        options = load_options(self.datasrc, self.code)
        options.append((self.other_code, self.other_text))
        kw['child_args'] = {'select': {
            'options': options,
            'mapping': {self.other_code: ['other']}
        }}
        return super(OtherSingleSelectField, self).update_params(kw)

    def __init__(self, id, dataobj, field, datasrc=None, *args, **kw):
        self.datasrc = datasrc and datasrc or dataobj
        super(OtherSingleSelectField, self).__init__(id, *args, **kw)
        self.validator = OtherChoiceValidator(dataobj, field,
                kw.get('code', self.code),
                kw.get('other_code', self.other_code),
                kw.get('fixed_fields', self.fixed_fields))


#--
# Contact lookup
#--
class AjaxLookupField(twf.FormField):
    "A text field that searches using AJAX"
    javascript = [tw.api.JSLink(modname=__name__, filename="static/ajax_lookup.js"),
                  tw.api.JSLink(modname=__name__, filename="static/hiding.js")] # just for hiding the view link
    params = {
        'attrs':    '',
        'datasrc':  'SQLAlchemy data src',
        'ajaxurl':  'URL of ajax responder',
        'link':     'Link target',
        'view_text':'Allows you to override the text string "view"',
    }
    attrs = {}
    view_text = 'View'

    template = "tw.dynforms.templates.contact_field"

    def display(self, value, **params):
        if value:
            params['visvalue'] = str(self.datasrc.query.get(value))
            params['showview'] = 'inline'
        else:
            params['visvalue'] = ''
            params['showview'] = 'none'
        return super(AjaxLookupField, self).display(value, **params)

