from Products.validation import validation
from Products.validation.validators.RegexValidator import RegexValidator


# Allow both commas and dots as decimal points.  And do not allow
# exponentials (like 5.0e2).

isCurrency = RegexValidator(
    'isCurrency',
    r'^([+-]?)(?=\d|[,\.]\d)\d*([,\.]\d*)?$',
    title='', description='',
    errmsg='is not a decimal number.')

validation.register(isCurrency)
