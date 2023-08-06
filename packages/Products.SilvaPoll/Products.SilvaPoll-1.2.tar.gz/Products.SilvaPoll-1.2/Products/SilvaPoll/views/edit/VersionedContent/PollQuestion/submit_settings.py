from Products.Formulator.Errors import ValidationError, FormValidationError

from zope.i18n import translate
from Products.SilvaPoll.i18n import translate as _

model = context.REQUEST.model
version = model.get_editable()

try:
    result = context.form.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_edit(message_type="error",
                message=context.render_form_errors(e))

try:
    version.save(result['question'], result['answers'], True)
except model.get_OverwriteNotAllowed():
    # note that we don't add an i18n domain since the message is exactly the
    # same as in the core (this does mean it needs to be kept in sync, though!)
    return context.tab_edit(message_type='error',
                            message=translate(_((
                                        'overwriting values not allowed, '
                                        'either you\'re trying to change the '
                                        'number of answers (not allowed) or '
                                        'you\'re trying to change answers '
                                        'when people have already voted'))))
except model.get_TooManyAnswers():
    return context.tab_edit(message_type='error',
                            message=translate(_(('you have exceeded the '
                                                    'maximum of 20 allowed '
                                                    'answers'))))

return context.tab_edit(message_type='feedback', message=translate(_('updated')))
