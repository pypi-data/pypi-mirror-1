from turbogears import validators
from turbogears.widgets import ListForm, TextField, HiddenField, SubmitButton
from turbogears.widgets import SingleSelectField

from tg_expanding_form_widget.tg_expanding_form_widget import ExpandingForm


class MXNumber(validators.FancyValidator):
    
    messages = {
        'number': 'Please enter a number',
    }
    
    def _to_python(self, value, state):
        
        # This is the hack to support MXPreferenceValidator error
        #   propagation.
        if isinstance(value, list):
            raise validators.Invalid(self.message('number', state),
                          value, state)
        
        try:
            value = float(value)
            if value == int(value):
                return int(value)
            return value
        except ValueError:
            raise validators.Invalid(self.message('number', state),
                          value, state)

class MXPreferenceValidator(validators.FancyValidator):
    def _to_python(self, value, state):
        # print "MXPreferenceValidator value:",value
        rtype = value.get('type', None)
        if rtype and rtype == 'MX':
            try:
                value['preference'] = int(value['preference'])
            except ValueError:
                # This is kind of a hack, but the only way I could
                #   propagate this error back to the field's own validator.
                # Without this the error was being displayed for all
                #   fields in the list...
                value['preference'] = [value['preference']]
                # raise validators.Invalid(
                #     'Please enter a number.',
                #     value, state)
        
        return value
    



class FormSchema(validators.Schema):
    hostname = validators.UnicodeString(not_empty=True, max=256, strip=True)
    type = validators.OneOf(['A', 'CNAME', 'MX', 'NS', 'TXT'])
    preference = MXNumber()
    value = validators.UnicodeString(not_empty=True, max=256, strip=True)


class ExpandingFormSchema(validators.Schema):
    zones = validators.ForEach(
        validators.All(
            FormSchema(),
            MXPreferenceValidator()
        )
    )
    
# class ExpandingFormSchema(validators.Schema):
#     zones = validators.All(validators.ForEach(FormSchema()), MXPreferenceValidator())


class FixedListForm(ListForm):
    template = 'zoner.templates.fixed_list_form'


def createForm():
    hostname = TextField(name='hostname', label=_(u'Hostname'), attrs=dict(size=30))
    rtype = SingleSelectField(
            name='type',
            label=_(u'Type'),
            options=[('A','A'), ('MX','MX'), ('CNAME','CNAME'), ('NS','NS'), ('TXT', 'TXT')],
            attrs=dict(onchange='typeChanged(this);')
            )
    preference = TextField(name='preference', label=_(u'Preference'), attrs=dict(size=4, style='visibility:visible;'))
    value = TextField(name='value', label=_(u'Value'), attrs=dict(size=25))
    afs = ExpandingForm(
            name='zones',
            label=_(u''),
            fields=[hostname, rtype, preference, value],
            # validator=FormSchema()
    )
    zonef = HiddenField(name='zone')
    cancel = SubmitButton(name='cancel', attrs=dict(value=_(u'Cancel'), style="margin-top:1em;"), label=_(u'Cancel all changes'))
    fields = [afs, zonef, cancel]
    
    form = FixedListForm(
        'zoneform',
        fields=fields,
        action='save_data',
        submit_text=_(u'Submit Data'),
        validator=ExpandingFormSchema()
    )
    
    return form


expanding_form = createForm()