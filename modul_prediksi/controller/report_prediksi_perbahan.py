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
            sheet.set_column(1, 1, 25)
            sheet.set_column(2, 2, 5)
            sheet.set_column(3, 3, 25)
            sheet.set_column(4, 4, 10)

            sheet.merge_range('A1:E1', 'UMKM Permak dan Jahit Hafizh', header_style_left)
            sheet.merge_range('A2:E2', 'Sendangguwo RT15/RW01 Kec. Tembalang, Kota Semarang', header_style_bold_left)
            sheet.merge_range('A3:E3', '', header_style)
            sheet.merge_range('A4:E4', atas.name, header_style)
            sheet.merge_range('A5:E5', 'Bahan Baku : ' + str(atas.bahan_baku.name), header_style_bold)
            sheet.merge_range('A6:E6', '', header_style)

            record_line = request.env['prediksi.perbahan.report.wizard.line'].search([('wizard_perbahan_id', '=', atas.id)])
            row = 6

            record_line = request.env['prediksi.perbahan.report.wizard.line'].search([('wizard_perbahan_id', '=', atas.id)])
            for line in record_line:
                sheet.write(6, 1, 'Bulan / Tahun', table_style)
                sheet.write(6, 2, ':', detail_table_style)
                sheet.write(6, 3, line.bulan + '/' + line.tahun, detail_table_left_style)
                sheet.write(7, 1, 'Nama Bahan Baku', table_style)
                sheet.write(7, 2, ':', detail_table_style)
                sheet.write(7, 3, line.bahan_baku, detail_table_left_style)
                sheet.write(8, 1, 'Qty Prediksi'+'('+line.uom+')', table_style)
                sheet.write(8, 2, ':', detail_table_style)
                sheet.write(8, 3, line.qty, detail_table_left_style)
                sheet.write(9, 1, 'MAPE (%)', table_style)
                sheet.write(9, 2, ':', detail_table_style)
                sheet.write(9, 3, line.mape, detail_table_left_style)
                sheet.write(10, 1, 'Keterangan', table_style)
                sheet.write(10, 2, ':', detail_table_style)
                sheet.write(10, 3, line.keterangan, detail_table_left_style)
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
        return response