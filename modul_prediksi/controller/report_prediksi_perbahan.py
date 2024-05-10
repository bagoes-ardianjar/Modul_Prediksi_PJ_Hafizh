from odoo import http
from odoo.http import content_disposition, request
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import io
import xlsxwriter

class prediksi_perbahan_controller(http.Controller):
    @http.route(['/prediksi_perbahan_report/<model("prediksi.perbahan.report.wizard"):wizard>', ], type='http', auth="user",
                csrf=False)
    def get_prediksi_perbahan_report_excel(self, wizard=None, **args):
        response = request.make_response(
            None,
            headers=[
                ('Content-Type', 'application/vnd.ms-excel'),
                ('Content-Disposition', content_disposition('Laporan Prediksi Penggunaan Bahan Bulan Depan' + '.xlsx'))
            ]
        )

        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        header_style = workbook.add_format(
            {'font_size': 14, 'valign': 'vcenter', 'align': 'center', 'bold': True})
        header_style_left = workbook.add_format(
            {'font_size': 14, 'valign': 'vcenter', 'align': 'left', 'bold': True})
        header_style_bold_left = workbook.add_format(
            {'font_size': 11, 'valign': 'vcenter', 'align': 'left', 'bottom': 1})
        header_style_bold = workbook.add_format(
            {'font_size': 11, 'valign': 'vcenter', 'align': 'center', 'bold': True})
        sub_header_style = workbook.add_format({'font_size': 11, 'valign': 'vcenter', 'align': 'center'})
        table_style = workbook.add_format(
            {'font_size': 11, 'valign': 'vcenter', 'align': 'centre', 'bold': True, 'bg_color': '#4ead2f',
             'color': 'white', 'text_wrap': True, 'border': 1})
        detail_table_style = workbook.add_format(
            {'font_size': 11, 'valign': 'vcenter', 'align': 'centre', 'text_wrap': True, 'border': 1})
        table_left_style = workbook.add_format(
            {'font_size': 11, 'valign': 'vcenter', 'align': 'left', 'bold': True, 'text_wrap': True, 'border': 1})
        detail_table_left_style = workbook.add_format(
            {'font_size': 11, 'valign': 'vcenter', 'align': 'left', 'text_wrap': True, 'border': 1})
        currency_detail_table_style = workbook.add_format({'font_size': 11, 'valign': 'vcenter', 'align': 'centre',
                                                           'num_format': '_-"Rp"* #,##0.00_-;-"Rp"* #,##0.00_-;_-"Rp"* "-"_-;_-@_-',
                                                           'text_wrap': True, 'border': 1})
        currency_detail_table_bold_style = workbook.add_format({'font_size': 11, 'valign': 'vcenter', 'align': 'centre', 'bold': True,
                                                           'num_format': '_-"Rp"* #,##0.00_-;-"Rp"* #,##0.00_-;_-"Rp"* "-"_-;_-@_-',
                                                           'text_wrap': True, 'border': 1})

        for atas in wizard:
            sheet = workbook.add_worksheet(atas.name)

            sheet.set_landscape()

            sheet.set_paper(9)

            sheet.set_column(0, 0, 10)
            sheet.set_column(1, 1, 10)
            sheet.set_column(2, 2, 25)
            sheet.set_column(3, 3, 10)
            sheet.set_column(4, 4, 10)
            sheet.set_column(5, 5, 10)

            sheet.merge_range('A1:F1', 'UMKM Permak dan Jahit Hafizh', header_style_left)
            sheet.merge_range('A2:F2', 'Sendangguwo RT15/RW01 Kec. Tembalang, Kota Semarang', header_style_bold_left)
            sheet.merge_range('A3:F3', '', header_style)
            sheet.merge_range('A4:F4', atas.name, header_style)
            sheet.merge_range('A5:F5', 'Bahan Baku : ' + str(atas.bahan_baku.name), header_style_bold)
            sheet.merge_range('A6:F6', '', header_style)

            record_line = request.env['prediksi.perbahan.report.wizard.line'].search([('wizard_perbahan_id', '=', atas.id)])
            row = 6

            # isi judul tabel
            sheet.write(row, 0, 'Bulan', table_style)
            sheet.write(row, 1, 'Tahun', table_style)
            sheet.write(row, 2, 'Bahan Baku', table_style)
            sheet.write(row, 3, 'Qty Prediksi', table_style)
            sheet.write(row, 4, 'UoM', table_style)
            sheet.write(row, 5, 'MAPE(%)', table_style)
            row += 1
            # cari record data yang dipilih
            record_line = request.env['prediksi.perbahan.report.wizard.line'].search([('wizard_perbahan_id', '=', atas.id)])
            for line in record_line:
                # content/isi tabel
                sheet.write(row, 0, line.bulan, detail_table_style)
                sheet.write(row, 1, line.tahun or 0, detail_table_style)
                sheet.write(row, 2, line.bahan_baku or 0, detail_table_left_style)
                sheet.write(row, 3, line.qty or 0, detail_table_style)
                sheet.write(row, 4, line.uom or 0, detail_table_style)
                sheet.write(row, 5, line.mape or 0, detail_table_style)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response