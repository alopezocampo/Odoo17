{
    'name': 'Sewing',
    'version': '0.1.42',
    'summary': 'Módulo de control de requerimientos de costureria',
    'author': 'Quality Systems',
    'website': 'https://www.qualitysystems.com',
    'category':'Services',
    'depends': [
        'hr',
        'mail',
        'crm',
        'sale',
    ],
    'data': [
        'reports/ir_actions_report.xml',
        'reports/ticket_invoice_report.xml',
        'views/views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}