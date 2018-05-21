# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import MissingError


class Process(models.Model):
    _name = 'sce_workflow.process'

    name = fields.Char(compute='_compute_name')
    workflow_id = fields.Many2one('sce_workflow.workflow', string='Workflow')
    res_model = fields.Char(string='Resource Model', related='workflow_id.res_model', store=True, index=True, readonly=True)
    current_workitem_id = fields.Many2one('sce_workflow.workitem')
    # Workflow 定义中model的数据库id
    res_id = fields.Integer()
    start_person_id = fields.Many2one('res.users')
    start_datetime = fields.Datetime()
    end_datetime = fields.Datetime()
    state = fields.Selection(selection=[
        ('created', 'Created'),
        ('started', 'Started'),
        ('finished', 'Finished'),
        ('aborted', 'Aborted'),
        ], default='created')

    # worknode_ids = fields.One2many('sce_workflow.worknode', 'process_id', string="Worknodes", copy=True)
    approval_ids = fields.One2many('sce_workflow.approval', 'process_id', string="Approvals")
    process_log = fields.Text(default="")

    res_model_name = fields.Char('Resource Model Name',compute='_compute_res_model_name', store=True)


    @api.depends('res_model', 'res_id')
    def _compute_res_model_name(self):
        for record in self:
            try:
                model = self.sudo().env[record.res_model].browse(record.res_id)
            except:
                continue
            try:
                record.res_model_name = model.name
            except:
                record.res_model_name = 'Deleted resource'

    @api.depends('workflow_id')
    def _compute_name(self):
        for record in self:
            record.name = "%s_%s_%d" % (record.workflow_id.name, record.res_model_name, record.id)

    # No worknode design
    @api.multi
    def start(self):
        for record in self:
            if record.state == 'created':
                workitem = record.workflow_id.get_start_workitem()
                if workitem:
                    record.current_workitem_id = workitem
                    record.start_datetime = fields.Datetime.now()
                    record._log("Process started.")
                    record.state = 'started'
                    model = self.env[record.res_model].browse(record.res_id)
                    if model.exists():
                        model.write({'approval_lock': True})
                    record._proceed()

    @api.multi
    def proceed(self):
        for record in self:
            if record.state == 'started':
                record._proceed()

    @api.multi
    def proceed_active_process(self):
        self.sudo().search([('state','=','started')]).proceed()

    def _proceed(self):
        self.ensure_one()
        print(self.current_workitem_id)
        if self.current_workitem_id == False or len(self.current_workitem_id)==0:
            rt = 'finish'
        elif self.current_workitem_id.type == 'approval':
            rt = self._proceed_approval(self.current_workitem_id)
        elif self.current_workitem_id.type == 'action':
            rt = 'finish' #TODO Adding action codes
        else:
            rt = 'wait'
        # Deal with proceed results
        if rt == 'finish':
            self.state = 'finished'
            self._log("Process finished")
        elif rt == 'walk':
           workitem = self.workflow_id.get_next_workitem(self.current_workitem_id)
           self.current_workitem_id = workitem
           self.proceed()
        elif rt == 'abort':
            self.state = 'aborted'
            self._log("Process aborted")
            model = self.env[self.res_model].browse(self.res_id)
            if model.exists():
                model.write({'approval_lock': False})
        else: # wait , etc..
            pass

    def _proceed_approval(self, workitem):
        if len(workitem.person_ids)<1:
            self._log("Workitem %s: Approval person list empty, skiped")
            return 'walk'
        approvals = self.env['sce_workflow.approval'].search([('process_id','=',self.id),('workitem_id','=',workitem.id)])
        if len(approvals) >0:
            # Has approvals
            if workitem.parallel_type == 'OR':
                all_reject = True
                for approval in approvals:
                    if approval.state == 'approved':
                        approvals.write({'is_active':False})
                        self._log(
                                "Workitem %s: Approved by %s at %s(Need one approve)." % (
                                    workitem.name, 
                                    approval.approver_id.name, 
                                    approval.approve_datetime))
                        return 'walk'
                    elif approval.state == 'pending':
                        all_reject = False
                else:
                    if all_reject:
                        approvals.write({'is_active':False})
                        self._log(
                                "Workitem %s: Rejected by all approvers.(Need one approve)." % (
                                    workitem.name,))
                        return 'abort'
                    else:
                        return 'wait'
            elif workitem.parallel_type == 'AND':
                all_approve = True
                for approval in approvals:
                    if approval.state == 'rejected':
                        approvals.write({'is_active':False})
                        self._log(
                                "Workitem %s: Rejected by %s at %s(Need all approve)." % (
                                    workitem.name,
                                    approval.approver_id.name,
                                    approval.approve_datetime))
                        return 'abort'
                    elif approval.state == 'pending':
                        all_approve = False
                else:
                    if all_approve:
                        approvals.write({'is_active':False})
                        self._log(
                                "Workitem %s: Approved by all approvers.(Need all approve)." % (
                                    workitem.name,))
                        return 'walk'
                    else:
                        return 'wait'
        else:
            for person in workitem.person_ids:
                approvals.create({
                    'process_id': self.id,
                    'requester_id': self.start_person_id.id,
                    'approver_id': person.id,
                    'workitem_id': workitem.id,
                    'is_active': True,
                    })
            return 'wait'

    def _log(self, message):
        self.process_log = "%s\n[%s] %s" % (
                self.process_log, 
                str(fields.Datetime.now()), 
                message)

        # if self.current_workitem_id:
            # result = self.current_workitem_id.proceed(self)
            # print(result)



class Worknode(models.Model):
    _name = 'sce_workflow.worknode'

    name = fields.Char(compute='_compute_name')
    process_id = fields.Many2one('sce_workflow.process', string="Related process", ondelete='cascade')
    current_workitem_id = fields.Many2one('sce_workflow.workitem')

    def _compute_name(self):
        for record in self:
            record.name = "%s-->%s" % (record.process_id.name, record.current_workitem_id.name)




