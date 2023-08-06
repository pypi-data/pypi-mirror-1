from Products.Silva.i18n import translate as _
from Products.Formulator.Errors import FormValidationError

from zope.i18n import translate
from Products.SilvaPoll.i18n import translate as _

model = context.REQUEST.model

try:
    result = context.tab_status_form_author.validate_all(context.REQUEST)
except FormValidationError, e:
    return context.tab_status(
        message_type="error", message=context.render_form_errors(e))

# check for status
message=None

viewable = model.get_viewable()
if viewable is None:
    return context.tab_status(
        message_type="error", message=_(
        "Dates not set. No public version found."))
viewable.set_question_start_datetime(result['question_start_datetime'])
viewable.set_question_end_datetime(result['question_end_datetime'])
viewable.set_result_start_datetime(result['result_start_datetime'])
viewable.set_result_end_datetime(result['result_end_datetime'])

return context.tab_status(message_type="feedback", 
                          message=translate(_("Dates set.", 'silva_poll')))
