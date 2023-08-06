from z3c.form.interfaces import ITextWidget

"""
class NOCHANGE(object):
    def __repr__(self):
        return '<NOCHANGE>'
NOCHANGE = NOCHANGE()
"""

NOCHANGE = "collective.z3cform.filewidget: NOCHANGE"

class IFileWidget(ITextWidget):
    """ widget"""
