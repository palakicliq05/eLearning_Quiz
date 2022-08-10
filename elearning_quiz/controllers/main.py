from odoo import fields, http
from odoo.http import request
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
from odoo.addons.survey.controllers.main import Survey
from odoo.http import request, content_disposition, Response
import base64

class SurveyInherit(Survey):
    @http.route('/survey/submit/<string:survey_token>/<string:answer_token>', type='json', auth='public', website=True)
    def survey_submit(self, survey_token, answer_token, **post):
        """ Submit a page from the survey.
        This will take into account the validation errors and store the answers to the questions.
        If the time limit is reached, errors will be skipped, answers will be ignored and
        survey state will be forced to 'done'"""
        # Survey Validation
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=True)
        if access_data['validity_code'] is not True:
            return {'error': access_data['validity_code']}
        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']

        if answer_sudo.state == 'done':
            return {'error': 'unauthorized'}
    
        questions, page_or_question_id = survey_sudo._get_survey_questions(answer=answer_sudo,
                                                                            page_id=post.get('page_id'),
                                                                            question_id=post.get('question_id'))

        if not answer_sudo.test_entry and not survey_sudo._has_attempts_left(answer_sudo.partner_id, answer_sudo.email, answer_sudo.invite_token):
            # prevent cheating with users creating multiple 'user_input' before their last attempt
            return {'error': 'unauthorized'}

        if answer_sudo.survey_time_limit_reached or answer_sudo.question_time_limit_reached:
            if answer_sudo.question_time_limit_reached:
                time_limit = survey_sudo.session_question_start_time + relativedelta(
                    seconds=survey_sudo.session_question_id.time_limit
                )
                time_limit += timedelta(seconds=3)
            else:
                time_limit = answer_sudo.start_datetime + timedelta(minutes=survey_sudo.time_limit)
                time_limit += timedelta(seconds=10)
            if fields.Datetime.now() > time_limit:
                # prevent cheating with users blocking the JS timer and taking all their time to answer
                return {'error': 'unauthorized'}

        errors = {}
        # Prepare answers / comment by question, validate and save answers
        for question in questions:
            inactive_questions = request.env['survey.question'] if answer_sudo.is_session_answer else answer_sudo._get_inactive_conditional_questions()
            if question in inactive_questions:  # if question is inactive, skip validation and save
                continue
            
            answer, comment = self._extract_comment_from_answers(question, post.get(str(question.id)))
            errors.update(question.validate_question(answer, comment))
            if not errors.get(question.id):
                if question.question_type in ['text_box'] or ['char_box']:
                    if question.upload_attachment :
                        text_question_json = json.loads(json.dumps(answer))
                        textanswer = text_question_json[str(question.id)]
                        filename = text_question_json["filename"+str(question.id)]
                        filecontent = text_question_json["myfile"+str(question.id)]
                        answer_sudo.save_lines_text_box(question, textanswer, filename, filecontent, comment)
                    else:
                        text_question_json = json.loads(json.dumps(answer))
                        textanswer = text_question_json[str(question.id)]
                        answer_sudo.save_lines(question, textanswer,comment)

                else:    
                    answer_sudo.save_lines(question, answer,comment)
            

        if errors and not (answer_sudo.survey_time_limit_reached or answer_sudo.question_time_limit_reached):
            return {'error': 'validation', 'fields': errors}

        if not answer_sudo.is_session_answer:
            answer_sudo._clear_inactive_conditional_answers()

        if answer_sudo.survey_time_limit_reached or survey_sudo.questions_layout == 'one_page':
            answer_sudo._mark_done()
        elif 'previous_page_id' in post:
            # Go back to specific page using the breadcrumb. Lines are saved and survey continues
            return self._prepare_question_html(survey_sudo, answer_sudo, **post)
        else:
            vals = {'last_displayed_page_id': page_or_question_id}
            if not answer_sudo.is_session_answer:
                next_page = survey_sudo._get_next_page_or_question(answer_sudo, page_or_question_id)
                if not next_page:
                    answer_sudo._mark_done()

            answer_sudo.write(vals)

        return self._prepare_question_html(survey_sudo, answer_sudo)
    
    @http.route('/survey/answer/attachment/download/<int:answerId>', type='http', auth="public", methods=['GET'])
    def attachment_download(self,answerId, **kw):
        rec = http.request.env['survey.user_input.line'].sudo().browse(answerId)       
        file_name = rec.file_name
        file_content = base64.b64decode(rec.file_content)

        return request.make_response(
            file_content,
            [
                ('Content-Type', 'application/*'),
                ('Content-Disposition', content_disposition(file_name)),
            ]
        )