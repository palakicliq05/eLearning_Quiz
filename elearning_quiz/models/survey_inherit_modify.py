from multiprocessing import context
from odoo import models, fields, api,_

class Schedule(models.Model):
    _inherit="survey.question"


    upload_attachment = fields.Boolean(string="Upload Attachment")
    upload_attachment_mandatory=fields.Boolean(string="Upload Attachment Mandatory")
    

    
    
    