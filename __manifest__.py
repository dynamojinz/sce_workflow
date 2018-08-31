# -*- coding: utf-8 -*-
{
    'name': "SCE Workflow",

    'summary': """
        SCE approval workflow""",

    'description': """
        Used for approval process.
    """,

    'author': "Jin Zan",
    'website': "http://www.sce-re.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sce_sso'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'security/security.xml',
        'views/workflow_views.xml',
        'views/process_views.xml',
        'views/approval_views.xml',
        'views/role_views.xml',
        'views/menus.xml',
        'views/templates.xml',
        'data/cron_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
    'installable' : True,
}
