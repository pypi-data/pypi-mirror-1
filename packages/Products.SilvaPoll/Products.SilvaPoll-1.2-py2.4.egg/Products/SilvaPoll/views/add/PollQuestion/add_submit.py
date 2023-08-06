from Products.Silva import mangle

from zope.i18n import translate
from Products.SilvaPoll.i18n import translate as _

model = context.REQUEST.model
REQUEST = context.REQUEST

lookup_mode = REQUEST.get('lookup_mode', 0)

# if we cancelled, then go back to edit tab
if REQUEST.has_key('add_cancel'):
    if lookup_mode:
        return context.object_lookup()
    return context.tab_edit()

# validate form
from Products.Formulator.Errors import ValidationError, FormValidationError
try:
    result = context.form.validate_all(REQUEST)
except FormValidationError, e:
    # in case of errors go back to add page and re-render form
    return context.add_form(message_type="error",
              message = context.render_form_errors(e))

id = result['object_id'].encode('ascii')
title = result['object_title']
question = result['question']
answers = [x.strip() for x in result['answers'].strip().split('\n\n')]
if len(answers) > 20:
    return context.add_form(message_type='error',
            message=_(('you have exceeded the maximum of 20 allowed answers')))

# if we don't have the right id, reject adding
mid = mangle.Id(model, id)
id_check = mid.validate()
if id_check == mid.OK:
    mid = str(mid)
else:
    return context.add_form(message_type="error",
        message=context.get_id_status_text(mid))

# process data in result and add using validation result
try:
    model.manage_addProduct['SilvaPoll'].manage_addPollQuestion(
                                          id, title, question, answers)
except ValueError, e:
    message = _('Problem: ${problem}',
        mapping={'problem': context.render_form_errors(e)})
    message = translate(message)
    return context.add_form(message_type="error", message=message)

object = getattr(model, id)

# update last author info in new object
object.sec_update_last_author_info()

if lookup_mode:
    return context.object_lookup()

# now go to tab_edit in case of add and edit, back to container if not.
if REQUEST.has_key('add_edit_submit'):
    REQUEST.RESPONSE.redirect(object.absolute_url() + '/edit/tab_edit')
else:
    message = _('Added ${meta_type} ${id}.',
        mapping={'meta_type': object.meta_type, 'id': context.quotify(id)})
    message = translate(message)
    return context.tab_edit(
        message_type="feedback",
        message=message)
