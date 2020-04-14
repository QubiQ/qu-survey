# -*- coding: utf-8 -*-
# Copyright 2018 Sergi Oliva <sergi.oliva@qubiq.es>
# Copyright 2018 Xavier Jiménez <xavier.jimenez@qubiq.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, exceptions, _
import base64
import csv
from io import StringIO

import logging
_logger = logging.getLogger(__name__)


class ImportSuerveyQuestions(models.TransientModel):
    _name = 'import.survey.questions'

    data = fields.Binary('File', required=True)
    name = fields.Char('Filename')
    delimeter = fields.Char('Delimiter',
                            default=';',
                            help='Default delimiter ";"')
    update = fields.Boolean(string='Update', default=True)
    survey_id = fields.Many2one(comodel_name='survey.survey', required=True)

    def _prepare_answer_vals(self, values, question_id):
        data_list = []
        data = {}
        for k, v in values.items():
            if 'answer' in k and 'correct' not in k and v != '':
                data = {
                    'value': v, 'question_id': question_id,
                    'type': 'checkbox'}
                if k[-1] == values['correctAnswer']:
                    data.update({'quizz_mark': 1})
                else:
                    data.update({'quizz_mark': -0.5})
                data_list.append(data)
        return data_list

    def _prepare_question_val(self, values):
        data = {}
        data['type'] = 'simple_choice'
        data['question'] = values['question']
        data['survey_id'] = self.survey_id.id
        return data

    def _create_questions(self, values):
        # Search Page
        page_id = self.env['survey.page'].search([
            ('title', '=', values['section'])
        ])
        if not page_id:
            page_id = page_id.create(
                {'title': values['section'], 'survey_id': self.survey_id.id})

        question = self.env['survey.question'].search([
            ('question', '=', values['question']),
            ('survey_id', '=', self.survey_id.id),
            ('page_id', '=', page_id.id)
        ])
        if question and not self.update:
            return

        question_val = self._prepare_question_val(values)
        question_val['page_id'] = page_id.id
        if question:
            question_val.update({'labels_ids': [(5, 0, 0)]})
            question.write(question_val)
        else:
            question = question.create(question_val)
        answ_obj = self.env['survey.label']
        for answer_val in self._prepare_answer_vals(values, question.id):
            answ_obj.create(answer_val)

    '''
        Function to read the csv file and convert it to a dict.

        :return Dict with the columns and its value.
    '''

    def action_import(self):
        """Load Inventory data from the CSV file."""
        if not self.data:
            raise exceptions.Warning(_("You need to select a file!"))
        # Decode the file data
        data = base64.b64decode(self.data).decode('utf-8')
        file_input = StringIO(data)
        file_input.seek(0)
        reader_info = []
        if self.delimeter:
            delimeter = str(self.delimeter)
        else:
            delimeter = ','
        reader = csv.reader(file_input,
                            delimiter=delimeter,
                            lineterminator='\r\n')
        try:
            reader_info.extend(reader)
        except Exception:
            raise exceptions.Warning(_("Not a valid file!"))
        keys = reader_info[0]

        # Get column names
        keys_init = reader_info[0]
        keys = []
        for k in keys_init:
            temp = k.replace(' ', '_')
            keys.append(temp)
        del reader_info[0]
        values = {}

        for i in range(len(reader_info)):
            # Don't read rows that start with ( or are empty
            if not (reader_info[i][0] == '' or reader_info[i][0][0] == '('
                    or reader_info[i][0][0] == ' '):
                field = reader_info[i]
                values = dict(zip(keys, field))
                self._create_questions(values)

        return {'type': 'ir.actions.act_window_close'}
