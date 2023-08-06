from django.forms import FileInput
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe

class XSendFileWidget(FileInput):
    """
    A FileField widget that shows its current value if it has one, using XSendFile as a link.
    """
    def __init__(self, attrs={}):
        super(XSendFileWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            output.append('%s <a target="_blank" href="%s">%s</a> <br />%s ' % \
                (_('Currently:'), value.instance.get_absolute_url(), value, _('Change:')))
        output.append(super(XSendFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))
