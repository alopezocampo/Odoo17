# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import json
import xlwt
import base64
import pytz, tempfile
from io import BytesIO


class SalespersonReportWizard(models.TransientModel):
	_name = "salesperson.report.wizard"
	_description = "Salesperson Report Wizard"


	start_date = fields.Date(string="Start Date", required=True);
	end_date = fields.Date(string="End Date", required=True);
	status = fields.Selection([('draft','Draft'),('post','Post'),('all','All')], string="States", default="all");
	salesperson_ids = fields.Many2many("res.users", "salesperson_report_wizard_ref", string="Salesperson");
	company_ids = fields.Many2many("res.company", "salesperson_report_company_wizard_ref", string="Companies");
	data = fields.Binary(string="Files");
	file_name = fields.Char(string="Filename");

	@api.model
	def default_get(self, fields):
		res = super(SalespersonReportWizard, self).default_get(fields);
		res["salesperson_ids"] = [(6,0,self.env.user.ids)];
		res["company_ids"] = [(6,0,self.env.company.ids)];
		return res;


	def get_report_data(self):
		if self.status == 'all':
			states = ['draft', 'posted'];
		elif self.status == 'post':
			states = ['posted'];
		else:
			states = ['draft'];

		main_data = {}
		for com in self.company_ids:
			journals = self.env["account.journal"].search([('type','in',['bank', 'cash']),
															('company_id','=',com.id)]);
			journal_type = {jou.name : 0 for jou in journals};
			salespersons = {};
			for salp in self.salesperson_ids:
				temp_list = [];
				invoices = self.env["account.move"].search([('invoice_date','>=',self.start_date),
															('invoice_date','<=',self.end_date),
															('invoice_user_id','in',salp.ids),
															('company_id','in',com.ids),
															('state','in',states),
															('move_type','in',['out_invoice','out_refund']),]);
				journal_type1 = {jou.name : 0 for jou in journals};
				for inv in invoices:
					if inv.is_outbound():
						sign = -1
					else:
						sign = 1
					dic = {}
					# dic = json.dumps(inv.invoice_payments_widget);
					dic = inv.invoice_payments_widget
					# if dic:
					temp_list.append([inv.name, 
							inv.invoice_date, 
							inv.invoice_user_id.name, 
							inv.partner_id.name] + [float(dic['content'][0].get("amount", 0)) * sign if dic and jj.name == dic['content'][0].get('journal_name',False) else 0 for jj in journals]);
					if dic and dic['content'][0].get('journal_name', 0) in journal_type:
						journal_type[dic['content'][0].get('journal_name', 0)] += (dic['content'][0].get("amount", 0) * sign);
						journal_type1[dic['content'][0].get('journal_name', 0)] += (dic['content'][0].get("amount", 0) * sign);
				salespersons.update({salp.name : [temp_list, journal_type1]});
			main_data.update({com.name : [salespersons, journal_type],})
		return main_data;


	def print_in_pdf_report(self):
		return self.env.ref("bi_salesperson_payment_reports.salespersons_payment_report").report_action(self);



	def print_in_xls_report(self):
		workbook = xlwt.Workbook();


		main_data = self.get_report_data();
		for key in main_data.keys():

			refund = 0;

			worksheet = workbook.add_sheet(key)
			worksheet.col(0).width = 8000

			comp = main_data[key];
			max_width = 6
			for sn in comp[0].keys():
				sp = comp[0][sn]
				for sps in sp[0]:
					if len(sps) > max_width:
						max_width = len(sps)-1;

			style_header = xlwt.easyxf(
				"font:height 400; font: name Liberation Sans, bold on,color black; align: vert centre, horiz center;pattern: pattern solid, pattern_fore_colour gray25;")
			style_line_heading = xlwt.easyxf(
				"font: name Liberation Sans, bold on; pattern: pattern solid, pattern_fore_colour gray25;")
			worksheet.write_merge(0, 1, 0, max_width, 'Invoice Payment Report', style=style_header)
			worksheet.write_merge(2, 2, 0, max_width, str(self.start_date)+' to '+str(self.end_date), style=xlwt.easyxf(
				"font:height 250; font: name Liberation Sans, bold on,color black; align: vert centre, horiz center;pattern: pattern solid, pattern_fore_colour gray25;"))
			worksheet.col(2).width = 8000

			sp_heading = ["Invoice", "Invoice Date", "Salesperson", "Customer"] + [jn for jn in comp[1].keys()] + ["Total"];
			style_line_heading = xlwt.easyxf(
				"font: name Liberation Sans;")
			row = 5;
			for sn in comp[0].keys():
				sp = comp[0][sn]
				worksheet.write_merge(row, row, 0, max_width, 'Salesperson: ' + str(sn), style=xlwt.easyxf(
					"font:height 250; font: name Liberation Sans, bold on,color black; align: vert centre, horiz center;pattern: pattern solid, pattern_fore_colour gray25;"));
				row += 2;
				col_no = 0;
				for n in range(len(sp_heading)):
					worksheet.col(col_no).width = 4000;
					col_no += 1;
					worksheet.write(row, n, str(sp_heading[n]), style=xlwt.easyxf(
						"font:height 250; font: name Liberation Sans, bold on,color black; align: vert centre, horiz center;pattern: pattern solid, pattern_fore_colour gray25;"));
				col_no = 0;
				row += 2;
				bottom_total = 0;
				for sps in sp[0]:
					if sum(sps[4:]) < 0:
						refund += sum(sps[4:]);
					for l in range(len(sps)):
						if l >= 4:
							style_line_heading = xlwt.easyxf(
								"font: name Liberation Sans; align: vert centre, horiz right;");
							if sum(sps[4:]) < 0:
								style_line_heading = xlwt.easyxf(
								"font: name Liberation Sans, color red; align: vert centre, horiz right;");
						else:
							style_line_heading = xlwt.easyxf(
								"font: name Liberation Sans;");
							if sum(sps[4:]) < 0:
								style_line_heading = xlwt.easyxf(
								"font: name Liberation Sans, color red;");
						worksheet.col(col_no).width = 5000;
						col_no += 1;
						worksheet.write(row, l, str(sps[l]), style=style_line_heading);
					worksheet.write(row, l+1, str(sum(sps[4:])), style=style_line_heading);
					bottom_total = bottom_total + sum(sps[4:]);
					row += 1;
				style_line_heading = xlwt.easyxf(
					"font: name Liberation Sans, bold on; align: vert centre, horiz center;");
				worksheet.write(row, 3, 'Total', style=style_line_heading);
				style_line_heading = xlwt.easyxf(
					"font: name Liberation Sans, bold on; align: vert centre, horiz right;");
				t_col = 4
				for tt in sp[1].keys():
					worksheet.write(row, t_col, str(sp[1][tt]), style=style_line_heading);
					t_col += 1;
				worksheet.write(row, t_col, str(bottom_total), style=style_line_heading);
				row += 3;

			worksheet.write_merge(row, row, 0, 1, "Payment Methods", style=xlwt.easyxf(
						"font:height 250; font: name Liberation Sans, bold on,color black; align: vert centre, horiz center;pattern: pattern solid, pattern_fore_colour gray25;"));

			row += 1;
			worksheet.write(row, 0, "Name", style=xlwt.easyxf(
						"font:height 250; font: name Liberation Sans, bold on,color black; align: vert centre, horiz center;pattern: pattern solid, pattern_fore_colour gray25;"));
			worksheet.write(row, 1, "Total", style=xlwt.easyxf(
						"font:height 250; font: name Liberation Sans, bold on,color black; align: vert centre, horiz center;pattern: pattern solid, pattern_fore_colour gray25;"));
			row += 1;
			for gt in comp[1].keys():
				worksheet.write(row, 0, str(gt), style=xlwt.easyxf(
						"font: name Liberation Sans,color black; align: vert centre, horiz left;"));
				worksheet.write(row, 1, str(comp[1][gt]), style=style_line_heading);
				row += 1;

			worksheet.write(row, 0, 'Refund', style=xlwt.easyxf(
						"font: name Liberation Sans,color black; align: vert centre, horiz left;"));
			worksheet.write(row, 1, str(refund), style=style_line_heading);
			row += 1;


		tz = pytz.timezone('Asia/Kolkata')
		file_data = BytesIO()
		workbook.save(file_data)
		self.write({
			'data': base64.encodebytes(file_data.getvalue()),
			'file_name': 'Salesperson Wise Invoice Payment Report.xls'
		})
		action = {
			'type': 'ir.actions.act_url',
			'name': 'contract',
			'url': '/web/content/salesperson.report.wizard/%s/data/Salesperson Wise Invoice Payment Report.xls?download=true' % (self.id),
			'target': 'self',
		}
		return action

