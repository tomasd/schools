from django.forms import widgets, fields
from django.forms.widgets import MultiWidget

class DatepickerDateInput(widgets.DateInput):
    format = '%d.%m.%Y'
    def __init__(self, *args, **kwargs):
        kwargs['attrs'] = kwargs.get('attrs', {})
        kwargs['attrs']['class'] = kwargs['attrs'].get('class', '')
        kwargs['attrs']['class'] += ' ' + 'datepicker'
        kwargs['attrs']['class'] = kwargs['attrs']['class'].strip()
        super(DatepickerDateInput, self).__init__(*args, **kwargs)

class TimepickerTimeInput(widgets.TimeInput):
    format = '%H:%M'
    def __init__(self, *args, **kwargs):
        kwargs['attrs'] = kwargs.get('attrs', {})
        kwargs['attrs']['class'] = kwargs['attrs'].get('class', '')
        kwargs['attrs']['class'] += ' ' + 'timepicker'
        kwargs['attrs']['class'] = kwargs['attrs']['class'].strip()
        super(TimepickerTimeInput, self).__init__(*args, **kwargs)
                
class SplitDatePickerTimePickerWidget(MultiWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes.
    """
    date_format = DatepickerDateInput.format
    time_format = TimepickerTimeInput.format

    def __init__(self, attrs=None, date_format=None, time_format=None):
        attrs = attrs or {}
        if date_format:
            self.date_format = date_format
        if time_format:
            self.time_format = time_format
        widgets = (DatepickerDateInput(attrs=attrs.copy(), format=self.date_format),
                   TimepickerTimeInput(attrs=attrs.copy(), format=self.time_format)
                   )
        super(SplitDatePickerTimePickerWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.date(), value.time().replace(microsecond=0)]
        return [None, None]
    
#widgets.DateInput= DatepickerDateInput
fields.DateField.widget = DatepickerDateInput
fields.TimeField.widget = TimepickerTimeInput
fields.DateTimeField.widget = SplitDatePickerTimePickerWidget
fields.DEFAULT_DATE_INPUT_FORMATS = tuple(['%d.%m.%Y'] + list(fields.DEFAULT_DATE_INPUT_FORMATS))