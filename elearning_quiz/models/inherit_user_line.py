from odoo import fields,models,api


class SurveyUserInputmodify(models.Model):
    _inherit = "survey.user_input"

     
    @api.model
    def save_lines_text_box(self, question, answer, filename,filecontent, comment=None):
        if question.question_type in ['text_box'] or ['char_box']:
            old_answers = self.env['survey.user_input.line'].search([
                ('user_input_id', '=', self.id),
                ('question_id', '=', question.id)
            ])
            vals = {
                'user_input_id': self.id,
                'question_id': question.id,
                'skipped': False,
                'answer_type': question.question_type,
            }
            if question.question_type in ['text_box'] :
                vals['value_text_box'] = answer
            if question.question_type in ['char_box']:
                vals['value_char_box'] = answer
            vals['file_content'] = filecontent
            vals['file_name'] = filename
            print("===========vals['value_text_box']============",vals)
            if old_answers:
                old_answers.write(vals)
            else:
                self.env['survey.user_input.line'].create(vals)
        else:
            super().save_lines(question, answer,comment)
            
