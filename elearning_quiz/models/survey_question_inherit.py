from odoo import models,tools, _


class SurveyQuestionInherit(models.Model):
    _inherit = "survey.question"
    
    def _validate_char_box(self, answer):
        # Email format validation
        # all the strings of the form "<something>@<anything>.<extension>" will be accepted
        print("$$$$$$$$$$$$$$$$$$ answer: ", answer)
        print("$$$$$$$$$$$$$$$$$$ self id: ", self.id)
        print("$$$$$$$$$$$$$$$$$$ answerid: ", answer[str(self.id)])
        if self.validation_email:
            if not tools.email_normalize(answer[str(self.id)]):
                return {self.id: _('This answer must be an email address')}

        # Answer validation (if properly defined)
        # Length of the answer must be in a range
        if self.validation_required:
            if not (self.validation_length_min <= len(answer[str(self.id)]) <= self.validation_length_max):
                return {self.id: self.validation_error_msg}
        return {}