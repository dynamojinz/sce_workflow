# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class Role(models.Model):
    _name = 'sce_workflow.role'

    name = fields.Char(required=True)
    res_module_name = fields.Char(related="res_module_id.name", store=True, index=True, readonly=True)
    res_module_id = fields.Many2one("ir.module.module")
    role_type = fields.Selection(selection=[
        ('person', 'Person Range'),
        ('department', 'Department Range'),
        ], default='person')
    roleline_ids = fields.One2many("sce_workflow.role.line", "role_id", copy=True)

    @api.multi
    def get_person_ids_by_person(self, person):
        ## TODO: Need Changing to one query to improve performance.
        person_ids = []
        for record in self:
            rolelines = self.env['sce_workflow.role.line'].search([('role_id', '=', record.id), ('person_range_ids','=', person.id)])
            if rolelines:
                person_ids.append(rolelines[0].role_person_id)
                # print("Role reslove: %s to %s by %s" % (record.name, rolelines[0].role_person_id.name, person.name))
        return person_ids


class RoleLine(models.Model):
    _name = 'sce_workflow.role.line'

    role_person_id = fields.Many2one("res.users")
    person_range_ids = fields.Many2many("res.users")
    role_id = fields.Many2one("sce_workflow.role", ondelete="cascade")

