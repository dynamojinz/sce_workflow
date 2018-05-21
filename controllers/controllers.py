# -*- coding: utf-8 -*-
from odoo import http,_


class SceWechat(http.Controller):
    pass

        
#     @http.route('/sce_sso/sce_sso/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sce_sso/sce_sso/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sce_sso.listing', {
#             'root': '/sce_sso/sce_sso',
#             'objects': http.request.env['sce_sso.sce_sso'].search([]),
#         })

#     @http.route('/sce_sso/sce_sso/objects/<model("sce_sso.sce_sso"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sce_sso.object', {
#             'object': obj
#         })
