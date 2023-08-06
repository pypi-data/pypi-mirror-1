from pysmvt import appimportauto, user
from pysmvt.view import HtmlTemplatePage
from forms import MyForm

class Index(HtmlTemplatePage):
    def default(self):
        pass

class FormTest(HtmlTemplatePage):
    def prep(self):
        self.form = MyForm()
        
    def post(self):
        if self.form.is_cancel():
            self.assign('cancel', True)
        elif self.form.is_valid():
            self.assign('values', self.form.get_values())
        elif self.form.is_submitted():
            # form was submitted, but invalid
            self.form.assign_user_errors()
        self.default()
    
    def default(self):
        self.assign('form', self.form)