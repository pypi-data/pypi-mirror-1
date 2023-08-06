import tw, tw.forms as twf
import sqlalchemy as sa, sqlalchemy.orm as sao, formencode as fe, turbojson

__all__ = ['FilteringGrid', 'WriteOnlyTextField', 'strip_wo_markers',
           'HidingSingleSelectField', 'IntNull', 'load_options',
           'GrowingTableFieldSet', 'GrowingTableForm',
           'OtherSingleSelectField', 'LinkContainer',
           'AjaxLookupField', 'GrowingRepeater', 'HidingCheckBox',
           'DeleteButton', 'HidingContainerMixin', 'HidingTableFieldSet',
           'HidingTableForm', 'HidingCheckBoxList', 'HidingRadioButtonList',
           'HidingLoopError', 'HidingMissingError', 'CustomisedForm',
           'SearchError']


#--
# Miscellaneous functions. TBD:  should these really exist in tw.dynforms?
#--
def unique(l):
    return dict.fromkeys(l, 1).keys()

class IntNull(fe.validators.Int):
    """Validator that parses a string to an integer, or returns None for the empty string."""
    def _to_python(self, value, state):
        if value == '':
            return None
        else:
            return super(IntNull, self)._to_python(value, state)

class StripDictValidator(fe.Schema):
    def __init__(self, strip):
        self.strip = strip
    def _to_python(self, value, state):
        return super(StripDictValidator, self)._to_python(value, state).get(self.strip, [])

def load_options(datasrc, code=None, extra=[('', '')]):
    """Load data from an SQLAlchemy object into list of (code, value) pairs, suitable for use with SingleSelectField and other widgets."""
    if hasattr(datasrc, 'query'): # TBD: figure a different test, this is a hack
        datasrc = datasrc.query
    data = datasrc.all()
    if data and not code:
        code = [c for c in data[0].c if c.primary_key][0].key
    options = [(getattr(x, code), str(x)) for x in datasrc.all()]
    options.sort(key = lambda x: x[1]) # TBD: remove this
    return extra + options

#--
# Dynamically filtering data grid
#--
class FilteringGrid(twf.TableForm):
    """This widget displays a grid of data that can be filtered by the user. The datasrc and columns parameters must be specified to create a static grid; other parameters allow the developer to add filtering controls."""
    params = {
        'datasrc':      'The source of data for a grid. This must be a callable that returns an SQLAlchemy Query object.',
        'columns':      'The columns to include in the grid. The must be a list of (name, label) pairs, where the name matches an attribute name on the objects returned by the query.',
        'search_cols':  'List of columns to include in free text search; at least one column must be specified for the search box to appear. Columns do not need to be displayed to be included in search.',
        'data_filter':  'List of columns to have data-based filtering dropdowns, similar to "Autofilter" in Excel.',
        'code_filter':  'Columns to have coded dropdown filters. The programmer specified the options available in the dropdown, and an SQLAlchemy query condition to apply to each. The parameter format is: {column_name: [(value1, condition1),...]}',
        'options':      'Checkboxes to display, that have coded filters. The parameter format is a list of (label, value, condition) tuples.',
        'blank_msg':    'Text to display if there is no data matching the filters.',
    }
    template = "tw.dynforms.templates.filtering_grid"

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

        query = params.get('datasrc', self.datasrc)()
        src = params['value'].get('src_text')

        if src:
            # Perform a text search
            query = query.filter(sa.or_(*[getattr(query.mapper.class_, c).like('%'+src+'%') for c in self.search_cols]))
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
                    query = query.filter(hasattr(c, '__call__') and c() or c)

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
# Miscellaneous widgets
#--
class LinkContainer(twf.FormField):
    """This widget provides a "View" link adjacent to any other widget required. This link is visible only when a value is selected, and allows the user to view detailed information on the current selection. You must give it a child called "widget"."""
    template = "tw.dynforms.templates.link_container"
    javascript = [tw.api.JSLink(modname=__name__, filename='static/dynforms.js')]
    params = {
        'link': 'The link target. If a $ character is present in the URL, it is replaced with the current value of the widget.',
        'view_text': 'Allows you to override the text string "view"',
        'popup_options': 'Options for popup window - passed to third argument of JS window.open',
    }
    popup_options = ''
    view_text = 'View'
    validator = StripDictValidator('widget')
    def update_params(self, params):
        super(LinkContainer, self).update_params(params)
        child_args = params.setdefault('child_args', getattr(self, 'child_args', {}))
        child_args.setdefault('widget', {}).setdefault('attrs', {})['onchange'] = 'twd_link_onchange(this)'

    # This is needed to avoid the value being coerced to a dict
    def adapt_value(self, value):
        return value


class SearchError(Exception):
    """This can be raised by a search callback function to indicate an error occured. It is caught by ajax_helper and translated to an error indicator in the JSON response, causing the error to be displayed on the client."""
    
class AjaxLookupField(twf.FormField):
    """A text field that searches using Ajax. The user is presented with a readable string, while internally the widget uses ID values. This is useful for foreign key relations to large tables, e.g. contact lists.
    
When the widget loses focus, it submits the value to a server-side controller method, that you define. The method will perform a search, returning the results to the client. If there is an exact match, the widget changes visually to confirm this; with multiple matches, the user must pick from a list. The controller method may call the ajax_helper method, to assist with its task."""
    template = "tw.dynforms.templates.ajax_lookup"
    javascript = [tw.api.JSLink(modname=__name__, filename="static/ajax_lookup.js")]
    params = {
        'datasrc': 'SQLAlchemy data src',
        'ajaxurl': 'URL of ajax responder; you must define this explicitly in your controller.',
        'max_results': 'Maximum number of results to return',
    }
    max_results = 20

    def ajax_helper(self, method, search):
        if method != 'POST':
            raise Exception('Ajax lookups only accept POST requests')
        try:
            data = list(self.datasrc.text_search(search))
            if len(data) > self.max_results:
                raise SearchError('More than %d results; please refine your search' % self.max_results)
        except SearchError, e:
            return dict(status=str(e))
        else:
            return dict(status='Successful', data=data)

        
class CustomisedForm(twf.Form):
    """A form that allows specification of several useful client-side behaviours."""
    params = {
        'blank_invisible': 'Blank out any invisible form fields on the page. This is required for hiding and growing to function correctly.',
        # TBD: 'save_prompt': 'If the user navigates away without submitted the form, and there are changes, this will prompt the user.',
        'disable_enter': 'Disable the enter button (except with textarea fields). This reduces the chance of users accidentally submitting the form.',
        'prevent_multi_submit': 'When the user clicks the submit button, disable it, to prevent the user causing multiple submissions.',
    }
    blank_invisible = True
    #save_prompt = True
    disable_enter = True
    prevent_multi_submit = True
    
    def update_params(self, params):
        super(CustomisedForm, self).update_params(params)
        if params.get('blank_invisible', self.blank_invisible):
            params.setdefault('attrs', {})['onsubmit'] = 'twd_blank_invisible()'
        if params.get('disable_enter', self.disable_enter):
            self.add_call('document.onkeypress = twd_suppress_enter;')
        if params.get('prevent_multi_submit', self.prevent_multi_submit):
            submit_args = params.setdefault('child_args', {}).setdefault('submit', {}) 
            submit_args['attrs'] = {'onclick': 'return twd_no_multi_submit(this)'}


class WriteOnlyMarker(object):
    pass

class WriteOnlyValidator(fe.validators.FancyValidator):
    def __init__(self, token, *args, **kw):
        super(WriteOnlyValidator, self).__init__(*args, **kw)
        self.token = token
    def to_python(self, value, state=None):
        return value == self.token and WriteOnlyMarker() or value

class WriteOnlyTextField(twf.TextField):
    """A text field that is write-only and never reveals database content. If a value exists in the database, a placeholder like "(supplied)" will be substituted. If the user does not modify the value, the validator will return a WriteOnlyMarker instance. Call strip_wo_markers to remove these from the dictionary."""
    params = {
        'token': 'Text that is displayed instead of the data. This can only be specified at widget creation, not at display time.'
    }
    token = '(supplied)'
    def __init__(self, *args, **kw):
        super(WriteOnlyTextField, self).__init__(*args, **kw)
        self.validator = WriteOnlyValidator(self.token)
    def adjust_value(self, value, validator=None):
        return value and self.token or value

def strip_wo_markers(val):
    """Remove WriteOnlyMarker instances from a dict/list structure. Where the marker is a value in a dictionary, the corresponding key is removed. Note: this is done separately from the validator, as an implementation details in TurboGears means a validator cannot reliably remove a key from a dictionary. This may be removed in future, if a workaround is found."""
    if isinstance(val, list):
        for v in val:
            strip_wo_markers(v)
    elif isinstance(val, dict):
        for k,v in val.items():
            if isinstance(v, WriteOnlyMarker):
                del val[k]
    return val


#--
# Growing forms
#--
class DeleteButton(twf.ImageButton):
    """A button to delete a row in a growing form. This is created automatically and would not usually be used directly."""
    attrs = {
        'alt': 'Delete row',
        'onclick': 'twd_grow_del(this); return false;',
    }
    src = tw.api.Link(modname=__name__, filename="static/del.png")

class TrFieldSet(twf.FieldSet):
    template = "tw.dynforms.templates.tr_fieldset"

    def update_params(self, d):
        super(TrFieldSet, self).update_params(d)
        if d.get('isextra', True):
            if not d.get('child_args'):
                d['child_args'] = {}
            for c in self.children:
                l = d['args_for'](c)
                if not l.has_key('attrs'):
                    l['attrs'] = c.attrs.copy()
                if c.id.endswith('del'):
                    l['attrs']['style'] = 'display:none;' + l['attrs'].get('style', '')
                else:
                    l['attrs']['onchange'] = 'twd_grow_add(this);' + l['attrs'].get('onchange', '')
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

class StrippingFieldRepeater(twf.FormFieldRepeater):
    extra = 1
    repetitions = 0

    def update_params(self, kw):
        if kw.get('error'):
            kw['extra'] = 0
        super(StrippingFieldRepeater, self).update_params(kw)

    def post_init(self, *args, **kwargs):
        self.validator = StripBlanks(self.children._widget.validator)

class GrowingTableMixin(object):
    """A grid of input widgets that can dynamically grow on the client. This is useful for allowing users to enter a list of items that can vary in length. The widgets are presented as a grid, with each field being a column. Delete and undo functionality is provided."""
    javascript = [tw.api.JSLink(modname=__name__, filename="static/dynforms.js")]
    params = {
        'dotitle': 'Whether to include a title row in the table',
    }
    dotitle = True
    validator = StripDictValidator('grow')
    show_error = True

    def clone(self, *args, **kw):
        super(GrowingTableMixin, self).clone(duringclone=True, *args, **kw)

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
        return super(GrowingTableMixin, cls).__new__(cls, id, parent, children, **kw)

    def update_params(self, params):
        params['undo_url'] = tw.api.Link(modname=__name__, filename="static/undo.png").link
        super(GrowingTableMixin, self).update_params(params)

class GrowingTableFieldSet(GrowingTableMixin, twf.FieldSet):
    __doc__ = GrowingTableMixin.__doc__ + """ To function correctly, the widget must appear inside a CustomisedForm."""
    template = 'tw.dynforms.templates.growing_table_fieldset'

class GrowingTableForm(GrowingTableMixin, twf.TableForm):
    __doc__ = GrowingTableMixin.__doc__
    template = 'tw.dynforms.templates.growing_table_form'
    def update_params(self, params):
        params['undo_url'] = tw.api.Link(modname=__name__, filename="static/undo.png").link
        # Avoid calling Form.update_params
        return twf.FormField.update_params(self, params)

class GrowingRepeater(twf.FieldSet):
    """A set of input widgets that can dynamically grow on the client."""
    validator = StripDictValidator('grow')
    javascript = [tw.api.JSLink(modname=__name__, filename="static/dynforms.js")]
    template = 'tw.dynforms.templates.growing_repeater'
    params = {
        'button_text': 'Text to use on "add" button',
        'widget': 'Widget to repeat',
    }
    button_text = 'Add'

    def __new__(cls, id=None, parent=None, children=[], widget=None, **kw):
        children = [
            StrippingFieldRepeater('grow', widget=widget, extra=0),
            widget('spare'),
            twf.Button('add', default=cls.button_text, named_button=False, attrs={'onclick':'twd_grow_add(this)'}),
        ]
        return twf.FieldSet.__new__(cls, id, parent, children, widget=widget, **kw)


#--
# Hiding forms
#--
class HidingLoopError(tw.core.WidgetException):
    """This is raised by HidingContainerMixin if a loop is detected in mappings."""

class HidingMissingError(tw.core.WidgetException):
    """This is raised by HidingContainerMixin if a control's mapping contains a widget that does not exist."""

class HidingContainerMixin(object):
    """Mixin to add hiding functionality to a container widget. The developer can use multiple inheritence to combine this class with a container widget, e.g. ListFieldSet. For this to work correctly, the container must make use of the container_attrs parameter on child widgets."""
    def update_params(self, params):
        super(HidingContainerMixin, self).update_params(params)
        visible = self.process_hiding(self.hiding_root, params['value_for'])
        for v in self.hiding_ctrls:
            if v not in visible:
                params.setdefault('child_args', {}).setdefault(v, {}).setdefault('container_attrs', {})['style'] = 'display:none'
        
    def process_hiding(self, ctrls, value_for, visible=None):
        if visible is None:
            visible = set(self.hiding_root)
        for c in ctrls:
            if isinstance(self.children[c], HidingComponentMixin):                
                for v,cs in self.children[c].mapping.iteritems():
                    val = value_for(c)
                    if c in visible and ((v == val) or (isinstance(val, list) and v in val)):
                        visible.update(cs)
                    self.process_hiding(cs, value_for, visible)
        return visible

    def post_init(self, *args, **kw):
        super(HidingContainerMixin, self).post_init(*args, **kw)
        self.hiding_ctrls = set()
        parents = {}
        for c in self.children:
            if isinstance(c, HidingComponentMixin):
                dep_ctrls = set()
                for m in c.mapping.values():
                    dep_ctrls.update(m)
                self.hiding_ctrls.update(dep_ctrls)
                for d in dep_ctrls:
                    if not self.children._widget_dct.has_key(d):
                        raise HidingMissingError('Widget referenced in mapping does not exist: ' + d)
                    parents.setdefault(d, set())
                    for dd in [d] + list(parents[d]):
                        if dd in parents.get(c._id, []):
                            raise HidingLoopError('Mapping loop caused by: ' + c.id)
                    parents[d].add(c._id)
                    parents[d].update(parents.get(c._id, []))
        self.hiding_root = [c._id for c in self.children
            if isinstance(c, HidingComponentMixin) and not parents.has_key(c._id)]
        

class HidingTableFieldSet(HidingContainerMixin, twf.TableFieldSet):
    """A TableFieldSet that can contain hiding widgets."""

class HidingTableForm(HidingContainerMixin, twf.TableForm):
    """A TableForm that can contain hiding widgets."""

class HidingComponentMixin(object):
    """This widget is a $$ with additional functionality to hide or show other widgets in the form, depending on the value selected. To function correctly, the widget must be used inside a suitable container, e.g. HidingTableForm.""" 
    javascript = [tw.api.JSLink(modname=__name__, filename='static/dynforms.js')]
    params = {
        'mapping': 'Dict that maps selection values to visible controls. This can only be specified at __init__ time, not display time.'
    }
    mapping = {}
    def update_params(self, params):
        super(HidingComponentMixin, self).update_params(params)
        mapping = turbojson.jsonify.encode(params.get('mapping', self.mapping))
        self.add_call('twd_mapping_store["%s"] = %s;' % (self.id, mapping))

class HidingSingleSelectField(HidingComponentMixin, twf.SingleSelectField):
    __doc__ = HidingComponentMixin.__doc__.replace('$$', 'SingleSelectField')
    attrs = {'onchange': 'twd_hiding_onchange(this)'}

class HidingCheckBox(HidingComponentMixin, twf.CheckBox):
    __doc__ = HidingComponentMixin.__doc__.replace('$$', 'CheckBox')
    attrs = {'onclick': 'twd_hiding_onchange(this)'}

class HidingSelectionList(HidingComponentMixin, twf.SelectionList):
    def update_params(self, params):
        super(HidingSelectionList, self).update_params(params)
        for opt in params['options']:
            opt[2]['onclick'] = 'twd_hiding_listitem_onchange(this)'

class HidingCheckBoxList(HidingSelectionList, twf.CheckBoxList):
    __doc__ = HidingComponentMixin.__doc__.replace('$$', 'CheckBoxList')

class HidingRadioButtonList(HidingSelectionList, twf.RadioButtonList):
    __doc__ = HidingComponentMixin.__doc__.replace('$$', 'RadioButtonList')


#--
# Other select field
#--
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


class OtherSingleSelectField(HidingContainerMixin, twf.FormField):
    """A SingleSelectField that has "Other" as an option. If a user selects "Other", they are prompted to enter a text string. The validator stores the new text strings in the database."""
    template = "tw.dynforms.templates.other_select_field"

    params = {
        'datasrc':      'The SQLAlchemy data source to use; this can be a mapped class or query. If not specified, defaults to dataobj.',
        'dataobj':      'The SQLAlchemy object to use',
        'field':        'The field on the object to use for the "other" text',
        'code':         'The field on the object that is the code',
        'other_code':   'The code used for "other"; occasionally you may need to override the default to avoid a clash with a valid value.',
        'other_text':   'The text string display for the "other" choice.',
        'specify_text': 'The text string display to prompt for a text value.',
        'fixed_fields': 'Specify field values on newly created objects',
    }
    code = 'id'
    other_code = 10000
    other_text = 'Other'
    specify_text = 'Please specify:'
    fixed_fields = {}

    def __new__(cls, id=None, parent=None, children=[], **kw):
        children = [
            HidingSingleSelectField('select', mapping={kw.get('other_code', cls.other_code): ['other']}),            
            twf.TextField('other'),
        ]
        return super(OtherSingleSelectField, cls).__new__(cls, id, parent, children, **kw)

    def __init__(self, id, dataobj, field, datasrc=None, *args, **kw):
        self.datasrc = datasrc and datasrc or dataobj
        super(OtherSingleSelectField, self).__init__(id, *args, **kw)
        self.validator = OtherChoiceValidator(dataobj, field,
                kw.get('code', self.code),
                kw.get('other_code', self.other_code),
                kw.get('fixed_fields', self.fixed_fields))

    # This is needed to avoid the value being coerced to a dict
    def adapt_value(self, value):
        return value

    def update_params(self, kw):
        options = load_options(self.datasrc, self.code)
        options.append((self.other_code, self.other_text))
        kw.setdefault('child_args', {})['select'] = {'options': options}
        return super(OtherSingleSelectField, self).update_params(kw)
