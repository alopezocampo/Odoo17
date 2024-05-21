# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.


{
    "name" : "Salesperson Wise Invoice Payment Report",
    "version" : "17.0.0.0",
    "category" : "Accounting",
    "summary": "Salesperson wise Invoice Payment Report Salesperson wise Invoice Report Salesperson wise Payment Report Invoice details report sales person wise invoice report salesperson wise bill payment report invoices payment reports payment details report for invoice",
    "description": """
    
        Payment Reports By Salespersons in odoo,
        Salesperson wise Invoice Payment Report in odoo,
        Print Payment Reports By Salesperson in odoo,
        Salesperson In Payment Reports in odoo,
        Filter Record by Start and End Date in odoo,
        Filter Record by Single or Multi Companies in odoo,
        Filter Record by States in odoo,
        Filter Record by Salesperson in odoo,
        Print Salesperson wise Invoice Payment Report in PDF in odoo,
        Print Salesperson wise Invoice Payment Report in XLS in odoo,
 
    """,
    "author": "BrowseInfo",
    "price": 19,
    "currency": "EUR",
    "website": "https://www.browseinfo.com",
    "depends" : ["base","account"],
    "data": [
                "security/bi_salesperson_payment_report_security.xml",
                "security/ir.model.access.csv",
                "report/bi_all_report.xml",
                "report/bi_report_template.xml",
                "wizard/report_payment_wizard.xml",
        ],
    "demo": [],
    "qweb": [],
    'license': 'OPL-1',
    "auto_install": False,
    "installable": True,
    'live_test_url':'https://youtu.be/GsSJFmt2yJA',
    "images":['static/description/Banner.gif'],
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
