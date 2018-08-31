# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Workflow(models.Model):
    _name = 'sce_workflow.workflow'

    name = fields.Char()
    res_model_id = fields.Many2one('ir.model', 'Releated Resource Model', index=True)
    res_model = fields.Char(string='Resource Model', related='res_model_id.model', store=True, index=True, readonly=True)
    start_action_id = fields.Many2one('ir.actions.server')
    finish_action_id = fields.Many2one('ir.actions.server')
    abort_action_id = fields.Many2one('ir.actions.server')

    workitem_ids = fields.One2many('sce_workflow.workitem', 'workflow_id', string="Workitems", copy=True)

    def get_start_workitem(self):
        self.ensure_one()
        if len(self.workitem_ids)>0:
            return self.workitem_ids.sorted('sequence')[0]
        else:
            return False

    def get_next_workitem(self, workitem):
        self.ensure_one()
        workitem_size = len(self.workitem_ids)
        workitem_ids = self.workitem_ids.sorted('sequence')
        index = workitem_ids.ids.index(workitem.id)
        if index>=0 and index<workitem_size-1:
            return workitem_ids[index+1]
        else:
            return False

    def start_process(self, model):
        process =  self.sudo().env['sce_workflow.process'].create({
            'workflow_id': self.id,
            'res_id': model.id,
            'start_person_id': self.env.user.id,
            # 'current_workitem_id': self.get_start_workitem().id,
            'state': 'created',
            })
        return process

class Workitem(models.Model):
    _name = 'sce_workflow.workitem'
    _order = 'sequence'

    name = fields.Char()
    sequence = fields.Integer()
    workflow_id = fields.Many2one('sce_workflow.workflow', string="Related workflow", ondelete='cascade')
    condition = fields.Char()
    # If more than one person, set to parallel approving
    person_ids = fields.Many2many('res.users')
    role_ids = fields.Many2many('sce_workflow.role')
    # parallel type
    parallel_type = fields.Selection(selection=[
        ('AND', 'Need all approved'),
        ('OR', 'Need one approved'),
        ],default='AND')
    action_id = fields.Many2one('ir.actions.server')
    type = fields.Selection(selection=[
        ('approval', 'Approval(Person)'),
        ('approval_role', 'Approval(Role)'),
        ('action', 'Action Server'),
        ], default='approval')




