from odoo import fields,models,api



class attachmentsurvey(models.Model):
    _inherit = "survey.user_input.line"

    file_content = fields.Text("file content")
    file_name = fields.Char("file name")  

    
    
    def get_download_file_url(self):
        return '/survey/answer/attachment/download/'+ str(self.id)
    
