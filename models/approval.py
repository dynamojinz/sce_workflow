# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Approval(models.Model):
    _name = 'sce_workflow.approval'

    name = fields.Char(compute='_compute_name')
    requester_id = fields.Many2one('res.users')
    approver_id = fields.Many2one('res.users')
    process_id = fields.Many2one('sce_workflow.process')
    # workitem_id = fields.Many2one('sce_workflow.workitem')
    workitem_id = fields.Integer()
    state = fields.Selection(selection=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ], default='pending')
    approve_datetime = fields.Datetime()
    is_active = fields.Boolean(default=True)
    # Related model
    res_model = fields.Char(string='Resource Model', related='process_id.res_model', store=True, index=True, readonly=True)
    res_id = fields.Integer(string="Resource ID", related='process_id.res_id', store=True, readonly=True)
    res_model_name = fields.Char(String='Resource Model Name', related='process_id.res_model_name', store=True, readonly=True)
    # Payload
    content_url = fields.Char()

    def _compute_name(self):
        for record in self:
            record.name = "[%s]%s" % (record.requester_id.name, record.process_id.name)

    def action_approve(self):
        for record in self:
            if record.approver_id == self.env.user:
                record = record.sudo()
                record.state = 'approved'
                record.approve_datetime = fields.Datetime.now()
                record.process_id.proceed()
                # record.is_active = False
            # Check approver is self

    def action_reject(self):
        for record in self:
            if record.approver_id == self.env.user:
                record = record.sudo()
                record.state = 'rejected'
                record.approve_datetime = fields.Datetime.now()
                record.process_id.proceed()
                # record.is_active = False
            # Check approver is self

    def action_view(self):
        self.ensure_one()
        return {
                'name': "View Model",
                'type': "ir.actions.act_window",
                'view_mode': "form",
                'res_model': self.res_model,
                'res_id': self.res_id,
                }


class ApprovalMixin(models.AbstractModel):
    _name = 'sce_workflow.approval.mixin'
    _description = 'Approval Mixin'

    approval_state = fields.Selection(related='approval_process_id.state', readonly=True)
    approval_process_id = fields.Many2one('sce_workflow.process')
    approval_button_submit = fields.Char(compute='_compute_approval_button_submit')
    approval_lock = fields.Boolean(default=False)


    @api.multi
    def _compute_approval_button_submit(self):
        for record in self:
            if record.approval_state:
                record.approval_button_submit = _('Resubmit Approval')
            else:
                record.approval_button_submit = _('Submit Approval')

    @api.multi
    def approval_action_submit(self):
        self.ensure_one()
        # Get related workflow
        if self.approval_process_id:
            # Restart process
            self.sudo().approval_process_id.restart()
        else:
            workflow = self.env['sce_workflow.workflow'].search([('res_model','=',self._name)])
            #TODO: check only one workflow, else do something.
            workflow.ensure_one()
            # Start process
            process = workflow.start_process(self)
            process.sudo().start()
            self.sudo().approval_process_id = process


    def approval_action_view(self):
        self.ensure_one()
        if self.approval_process_id:
            return {
                'name': "View Process",
                'type': "ir.actions.act_window",
                'view_mode': "form",
                'res_model': 'sce_workflow.process',
                'res_id': self.approval_process_id.id,
                }

    # Need to be overide by Actual class
    def approval_get_content_url(self):
        return False








