# Here you can create samples of your widgets by providing default parameters,
# inserting them in a container widget, mixing them with other widgets, etc...
# These samples will appear in the (unimplemented yet) widget browser.
import tw.forms as twf, tw.dynforms as twd, formencode as fe

class DemoGrowingTableForm(twd.GrowingTableForm):
    children = [
        twf.TextField('name'),
        twf.TextField('phone_number'),
        twf.CheckBox('personal'),
    ]

class DemoGrowingTableFieldSet(twd.GrowingTableFieldSet):
    children = [
        twf.TextField('name'),
        twf.TextField('phone_number'),
        twf.CheckBox('personal'),
    ]

class DemoHidingCheckBox(twd.HidingTableFieldSet):
    children = [
        twd.HidingCheckBox('delivery', label_text='Delivery required?', mapping={1:['address']}),
        twf.TextField('address')
    ]
    
class DemoHidingCheckBoxList(twd.HidingTableFieldSet):
    children = [
        twd.HidingCheckBoxList('contact', label_text='Contact method', options=('E-mail', 'Phone', 'SMS'), 
            mapping={
                0: ['email_address'],
                1: ['phone_number'],
                2: ['phone_number'],
            }),
        twf.TextField('email_address'),
        twf.TextField('phone_number'),
    ]

class DemoHidingRadioButtonList(twd.HidingTableFieldSet):
    children = [
        twd.HidingRadioButtonList('contact', label_text='Contact method', options=('E-mail', 'Phone', 'SMS'), 
            mapping={
                0: ['email_address'],
                1: ['phone_number'],
                2: ['phone_number'],
            }),
        twf.TextField('email_address'),
        twf.TextField('phone_number'),
    ]

class DemoHidingSingleSelectField(twd.HidingTableFieldSet):
    children = [
        twd.HidingSingleSelectField('contact', label_text='Contact method', options=[(0,'E-mail'), (1,'Phone'), (2,'SMS')],
            mapping={
                0: ['email_address'],
                1: ['phone_number'],
                2: ['phone_number'],
            }),
        twf.TextField('email_address'),
        twf.TextField('phone_number'),
    ]

class DemoOtherSingleSelectField(twd.OtherSingleSelectField):
    options = [(0,'Male'), (1,'Female')]
    
class DemoLinkContainer(twd.LinkContainer):
    children = [twf.SingleSelectField('widget', options=('', 'www.google.com','www.yahoo.com'))]
    link = 'http://$'
