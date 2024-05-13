from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

def get_nama_bulan(number_of_month):
    if number_of_month == 1:
        bulan_name = 'January'
    elif number_of_month == 2:
        bulan_name = 'February'
    elif number_of_month == 3:
        bulan_name = 'March'
    elif number_of_month == 4:
        bulan_name = 'April'
    elif number_of_month == 5:
        bulan_name = 'May'
    elif number_of_month == 6:
        bulan_name = 'June'
    elif number_of_month == 7:
        bulan_name = 'July'
    elif number_of_month == 8:
        bulan_name = 'August'
    elif number_of_month == 9:
        bulan_name = 'September'
    elif number_of_month == 10:
        bulan_name = 'October'
    elif number_of_month == 11:
        bulan_name = 'November'
    elif number_of_month == 12:
        bulan_name = 'December'
    else:
        bulan_name = ''
    return bulan_name

class bahan_baku(models.Model):
    _name = 'bahan.baku'

    name = fields.Char(string="Name", default="New")
    uom = fields.Selection([('m2','m2'),('pcs','Pcs'),('roll','Roll')],string="UoM")

class penggunaan_bahan(models.Model):
    _name = 'penggunaan.bahan'

    def func_delete_data(self):
        delete_data = "delete from penggunaan_bahan where (extract(year from CURRENT_DATE) - EXTRACT(YEAR FROM tanggal_input)) > 10"
        self._cr.execute(delete_data)
        self._cr.commit()

        delete_data_line = "delete from penggunaan_bahan_line where id in (select a.id from penggunaan_bahan_line a " \
                      "join penggunaan_bahan b on b.id = a.penggunaan_bahan_id " \
                      "where (extract(year from CURRENT_DATE) - EXTRACT(YEAR FROM b.tanggal_input)) > 10)"
        self._cr.execute(delete_data_line)
        self._cr.commit()
        return True

    # @api.onchange('tanggal_input','admin')
    # def funct_onchange_name(self):
    #     if self.name == 'False':
    #         seq = self.env['ir.sequence'].next_by_code('penggunaan.bahan') or 'New'
    #         self.name = seq
    #     elif self.name == 'New':
    #         seq = self.env['ir.sequence'].next_by_code('penggunaan.bahan') or 'New'
    #         self.name = seq
    #     return {}

    @api.model
    def create(self, vals):
        res = super(penggunaan_bahan, self).create(vals)
        for rec in res:
            seq = self.env['ir.sequence'].next_by_code('penggunaan.bahan') or 'New'
            rec.name = seq
            list_line = []
            for line in rec.penggunaan_bahan_ids:
                if line.bahan_baku.id not in list_line:
                    list_line.append(line.bahan_baku.id)
                else:
                    raise ValidationError(_("Anda tidak dapat menginput bahan baku yang sama lebih dari satu line !"))
        return res

    def write(self, vals):
        res = super(penggunaan_bahan, self).write(vals)
        if 'penggunaan_bahan_ids' in vals:
            list_line = []
            for line in self.penggunaan_bahan_ids:
                if line.bahan_baku.id not in list_line:
                    list_line.append(line.bahan_baku.id)
                else:
                    raise ValidationError(_("Anda tidak dapat menginput bahan baku yang sama lebih dari satu line !"))
        return res

    name = fields.Char(string="Name", default="New")
    tanggal_input = fields.Date(string="Tanggal Input")
    admin = fields.Many2one('res.users',string="Nama Admin")
    # nama_admin = fields.Many2one(res.users, string="Nama Admin")
    penggunaan_bahan_ids = fields.One2many('penggunaan.bahan.line', 'penggunaan_bahan_id',string="Penggunaan Bahan Ids",copy=True)

class penggunaan_bahan_line(models.Model):
    _name = 'penggunaan.bahan.line'

    @api.onchange('bahan_baku')
    def funct_onchange_uom(self):
        check_data = self.env['bahan.baku'].sudo().search([('id', '=', self.bahan_baku.id)])
        if check_data:
            self.uom = check_data.uom
        return {}

    def get_bulan_tahun(self):
        for this in self:
            if this.penggunaan_bahan_id.id != False and this.penggunaan_bahan_id.tanggal_input != False:
                number_bulan = datetime.strptime(str(this.penggunaan_bahan_id.tanggal_input), "%Y-%m-%d").month
                number_tahun = datetime.strptime(str(this.penggunaan_bahan_id.tanggal_input), "%Y-%m-%d").year
                bulan = get_nama_bulan(number_bulan)
                tahun = str(number_tahun)
            else:
                bulan = ''
                tahun = ''
            this.bulan = bulan
            this.tahun = tahun

    penggunaan_bahan_id = fields.Many2one('penggunaan.bahan', string="Penggunaan Bahan Id")
    bulan = fields.Char(string="Bulan", compute=get_bulan_tahun)
    tahun = fields.Char(string="Tahun", compute=get_bulan_tahun)
    bahan_baku = fields.Many2one('bahan.baku', string="Bahan Baku")
    qty = fields.Float(string="Qty")
    uom = fields.Char(string="UoM")

class prediksi_semuabahan_report_wizard(models.TransientModel):
    _name = 'prediksi.semuabahan.report.wizard'

    name = fields.Char(string="Name")
    wizard_semuabahan_ids = fields.One2many('prediksi.semuabahan.report.wizard.line', 'wizard_semuabahan_id',
                                          string='Wizard Prediksi Semua Bahan Ids')

    def func_print_semuabahan_pdf(self):
        data = {'name': self.name}

        return self.env.ref('modul_prediksi.action_report_prediksi_semuabahan').report_action(self, data=data)

    def func_print_semuabahan_excel(self):
        vals_header = {
            "name": 'Laporan Prediksi Penggunaan Bahan Bulan Depan'
        }
        new_header = self.env['prediksi.semuabahan.report.wizard'].sudo().create(vals_header)
        self._cr.execute("""(
                            select id as id from bahan_baku
                        )""".format())
        data_bahan = self._cr.dictfetchall()
        check_data_bahan = self.env['bahan.baku'].sudo().search([('id', 'in', [item['id'] for item in data_bahan])])
        data_all = []
        for bahan in check_data_bahan:
            self._cr.execute("""(
                        select a.id as id,
                        c.name as nama_bahan,
                        b.qty as qty,
                        b.uom as uom
                        from penggunaan_bahan a
                        join penggunaan_bahan_line b on b.penggunaan_bahan_id = a.id 
                        join bahan_baku c on c.id = b.bahan_baku
                        where b.bahan_baku  = {_id}
                        order by a.tanggal_input asc
                    )""".format(_id=bahan.id))
            data_preview = self._cr.dictfetchall()
            y = []
            for item in data_preview:
                y.append(item.get('qty'))
                uom = item.get('uom')
                nama_bahan = item.get('nama_bahan')

            n = len(y)  # Jumlah elemen dalam variabel y

            if n % 2 == 0:  # Jika jumlah elemen genap
                x = [-1 * (n - 1) + i * 2 for i in range(n)]
            else:  # Jika jumlah elemen ganjil
                middle_index = n // 2
                # x = [-1 * ((middle_index + 1) - 1) + i for i in range(n)]
                x = [-1 * middle_index + i for i in range(n)]

            # Membuat variabel xy yang berisi hasil perkalian x dan y sesuai urutannya
            xy = [xi * yi for xi, yi in zip(x, y)]
            x2 = [xi ** 2 for xi in x]
            a = round(sum(y) / len(y), 2)

            if n % 2 == 0:  # Jika jumlah elemen genap
                x_prediksi = x[-1] + 2
            else:  # Jika jumlah elemen ganjil
                x_prediksi = x[-1] + 1
            # Menghitung variabel b berdasarkan rumus (jumlah dari variabel xy) dibagi (jumlah dari variabel x2)
            b = round(sum(xy) / sum(x2), 2)
            # Membuat variabel y_prediksi yang nilainya adalah a + b dikali x_prediksi
            y_prediksi = round(a + (b * x_prediksi), 2)
            # Membuat variabel yt yang nilainya adalah a + b dikali x untuk setiap nilai x dalam variabel x
            yt = [a + b * xi for xi in x]
            ape = [abs(yi - yti) / yi if yi != 0 else 0 for yi, yti in zip(y, yt)]
            mape = round((sum(ape) / n), 2) * 100
            check_data = self.env['penggunaan.bahan'].sudo().search([('id', 'in', [item['id'] for item in data_preview])])
            for check in check_data:
                tanggal_awal = str(check.tanggal_input)
            tanggal_awal_obj = datetime.strptime(tanggal_awal, "%Y-%m-%d")
            tanggal_berikutnya_obj = tanggal_awal_obj + relativedelta(months=1)
            # Ekstrak bulan dan tahun dari tanggal berikutnya
            bulan = tanggal_berikutnya_obj.strftime("%B")  # Format nama bulan
            tahun = tanggal_berikutnya_obj.strftime("%Y")  # Format tahun
            if round(mape, 0) < 10:
                keterangan = 'Sangat Baik'
            elif round(mape, 0) >= 10 and round(mape, 0) < 20:
                keterangan = 'Baik'
            elif round(mape, 0) >= 20 and round(mape, 0) <= 50:
                keterangan = 'Cukup Baik'
            elif round(mape, 0) > 50:
                keterangan = 'Kurang'
            else:
                keterangan = ''
            data_prediksi = {
                'bulan': bulan,
                'tahun': tahun,
                'bahan_baku': nama_bahan,
                'qty': y_prediksi,
                'uom': uom,
                'mape': round(mape,0),
                'keterangan': keterangan,
            }

            if len(data_prediksi) > 0:
                data_all.append(data_prediksi)
                uid = self._uid
        for data in data_all:
            ins_values = ",".join(["('{}','{}','{}','{}','{}',{},'{}',{},{})".format(
                data['bulan'] or '',
                data['tahun'] or '',
                data['bahan_baku'] or '',
                data['qty'] or 0,
                data['uom'] or '',
                data['mape'] or 0,
                data['keterangan'] or '',
                uid,
                new_header.id
            )])
            ins_query = "insert into prediksi_semuabahan_report_wizard_line (bulan," \
                        "tahun,bahan_baku,qty,uom,mape,keterangan," \
                        "create_uid,wizard_semuabahan_id) values {_values}".format(_values=ins_values)
            self._cr.execute(ins_query)
            self._cr.commit()

        return {
            'type': 'ir.actions.act_url',
            'url': '/prediksi_semuabahan_report/%s' % (new_header.id),
            'target': 'new',
        }

class prediksi_perbahan_report_wizard(models.TransientModel):
    _name = 'prediksi.perbahan.report.wizard'

    name = fields.Char(string="Name")
    bahan_baku = fields.Many2one('bahan.baku', string="Pilih Bahan Baku")
    wizard_perbahan_ids = fields.One2many('prediksi.perbahan.report.wizard.line', 'wizard_perbahan_id',
                                                 string='Wizard Semua Bahan Ids')

    # def func_print_perbahan_pdf(self):
    #     data = {
    #         'ids': self.ids,
    #         'model': self._name,
    #         'form': {
    #             'bahan_baku': self.bahan_baku.name
    #         },
    #     }
    #     return self.env.ref('modul_prediksi.action_report_prediksi_perbahan').report_action(self, data=data)

    def func_print_perbahan_pdf(self):
        data = {'bahan_baku': self.bahan_baku.id}

        return self.env.ref('modul_prediksi.action_report_prediksi_perbahan').report_action(self, data=data)

    def func_print_perbahan_excel(self):
        vals_header = {
            "name": 'Laporan Prediksi Penggunaan Bahan Bulan Depan',
            "bahan_baku": self.bahan_baku.id
        }
        new_header = self.env['prediksi.perbahan.report.wizard'].sudo().create(vals_header)
        self._cr.execute("""(
            select a.id as id,
            c.name as bahan_baku,
            b.qty as qty,
            b.uom as uom
            from penggunaan_bahan a
            join penggunaan_bahan_line b on b.penggunaan_bahan_id = a.id 
            join bahan_baku c on c.id = b.bahan_baku
            where b.bahan_baku  = {_id}
            order by a.tanggal_input asc
        )""".format(_id=self.bahan_baku.id))
        data_preview = self._cr.dictfetchall()
        y = []
        for item in data_preview:
            y.append(item.get('qty'))
            uom=item.get('uom')

        n = len(y)  # Jumlah elemen dalam variabel y

        if n % 2 == 0:  # Jika jumlah elemen genap
            x = [-1 * (n - 1) + i * 2 for i in range(n)]
        else:  # Jika jumlah elemen ganjil
            middle_index = n // 2
            # x = [-1 * ((middle_index + 1) - 1) + i for i in range(n)]
            x = [-1 * middle_index + i for i in range(n)]

        # Membuat variabel xy yang berisi hasil perkalian x dan y sesuai urutannya
        xy = [xi * yi for xi, yi in zip(x, y)]
        x2 = [xi ** 2 for xi in x]
        a = round(sum(y) / len(y), 2)
        if n % 2 == 0:  # Jika jumlah elemen genap
            x_prediksi = x[-1] + 2
        else:  # Jika jumlah elemen ganjil
            x_prediksi = x[-1] + 1
        # Menghitung variabel b berdasarkan rumus (jumlah dari variabel xy) dibagi (jumlah dari variabel x2)
        b = round(sum(xy) / sum(x2), 2)
        # Membuat variabel y_prediksi yang nilainya adalah a + b dikali x_prediksi
        y_prediksi = round(a + b * x_prediksi, 2)
        # Membuat variabel yt yang nilainya adalah a + b dikali x untuk setiap nilai x dalam variabel x
        yt = [a + b * xi for xi in x]
        ape = [abs(yi - yti) / yi if yi != 0 else 0 for yi, yti in zip(y, yt)]
        mape = round((sum(ape) / n), 2) * 100

        check_data = self.env['penggunaan.bahan'].sudo().search([('id','in',[item['id'] for item in data_preview])])
        for check in check_data:
            tanggal_awal = str(check.tanggal_input)
        tanggal_awal_obj = datetime.strptime(tanggal_awal, "%Y-%m-%d")
        tanggal_berikutnya_obj = tanggal_awal_obj + relativedelta(months=1)
        # Ekstrak bulan dan tahun dari tanggal berikutnya
        bulan = tanggal_berikutnya_obj.strftime("%B")  # Format nama bulan
        tahun = tanggal_berikutnya_obj.strftime("%Y")  # Format tahun
        if round(mape, 0) < 10:
            keterangan = 'Sangat Baik'
        elif round(mape, 0) >= 10 and round(mape, 0) < 20:
            keterangan = 'Baik'
        elif round(mape, 0) >= 20 and round(mape, 0) <= 50:
            keterangan = 'Cukup Baik'
        elif round(mape, 0) > 50:
            keterangan = 'Kurang'
        else:
            keterangan = ''
        data_prediksi = {
            'bulan' : bulan,
            'tahun' : tahun,
            'bahan_baku' : self.bahan_baku.name,
            'qty' : y_prediksi,
            'uom' : uom,
            'mape' : mape,
            'keterangan': keterangan
        }
        if len(data_prediksi) > 0:
            uid = self._uid
            # for data in data_prediksi:
            ins_values = ",".join(["('{}','{}','{}','{}','{}',{},'{}',{},{})".format(
                data_prediksi['bulan'] or '',
                data_prediksi['tahun'] or '',
                data_prediksi['bahan_baku'] or '',
                data_prediksi['qty'] or 0,
                data_prediksi['uom'] or '',
                data_prediksi['mape'] or 0,
                data_prediksi['keterangan'] or '',
                uid,
                new_header.id
            )])
            ins_query = "insert into prediksi_perbahan_report_wizard_line (bulan," \
                        "tahun,bahan_baku,qty,uom,mape,keterangan," \
                        "create_uid,wizard_perbahan_id) values {_values}".format(_values=ins_values)
            self._cr.execute(ins_query)
            self._cr.commit()

        return {
            'type': 'ir.actions.act_url',
            'url': '/prediksi_perbahan_report/%s' % (new_header.id),
            'target': 'new',
        }

class prediksi_perbahan_report_wizard_line(models.TransientModel):
    _name = 'prediksi.perbahan.report.wizard.line'

    wizard_perbahan_id = fields.Many2one('prediksi.perbahan.report.wizard', string='Wizard Perbahan Id')
    bulan = fields.Char(string='Bulan')
    tahun = fields.Char(string='Tahun')
    bahan_baku = fields.Char(string='Bahan')
    qty = fields.Float(string='Qty Prediksi')
    uom = fields.Char(string='UoM')
    mape = fields.Float(string='MAPE')
    keterangan = fields.Char(string='Keterangan')

class prediksi_perbahan_template_pdf(models.AbstractModel):
    _name = 'report.modul_prediksi.perbahan_template'

    def _get_report_values(self, docids, data=None):
        bahan_baku = data.get('bahan_baku')
        self._cr.execute("""(
                   select a.id as id,
                        c.name as bahan_baku,
                        b.qty as qty,
                        b.uom as uom
                    from penggunaan_bahan a
                        join penggunaan_bahan_line b on b.penggunaan_bahan_id = a.id 
                        join bahan_baku c on c.id = b.bahan_baku
                    where b.bahan_baku  = {_id}
                    order by a.tanggal_input asc
                    )""".format(_id=bahan_baku))

        data_preview = self._cr.dictfetchall()
        y = []
        data_prediksi = []
        docs = data_prediksi
        for item in data_preview:
            y.append(item.get('qty'))
            uom = item.get('uom')
            nama_bahan = item.get('bahan_baku')

        n = len(y)  # Jumlah elemen dalam variabel y

        if n % 2 == 0:  # Jika jumlah elemen genap
            x = [-1 * (n - 1) + i * 2 for i in range(n)]
        else:  # Jika jumlah elemen ganjil
            middle_index = n // 2
            # x = [-1 * ((middle_index + 1) - 1) + i for i in range(n)]
            x = [-1 * middle_index + i for i in range(n)]

        # Membuat variabel xy yang berisi hasil perkalian x dan y sesuai urutannya
        xy = [xi * yi for xi, yi in zip(x, y)]
        x2 = [xi ** 2 for xi in x]
        a = round((sum(y) / len(y)), 2)

        if n % 2 == 0:  # Jika jumlah elemen genap
            x_prediksi = x[-1] + 2
        else:  # Jika jumlah elemen ganjil
            x_prediksi = x[-1] + 1
        # Menghitung variabel b berdasarkan rumus (jumlah dari variabel xy) dibagi (jumlah dari variabel x2)
        b = round(sum(xy) / sum(x2), 2)
        # Membuat variabel y_prediksi yang nilainya adalah a + b dikali x_prediksi
        y_prediksi = round(a + (b * x_prediksi), 2)
        # Membuat variabel yt yang nilainya adalah a + b dikali x untuk setiap nilai x dalam variabel x
        yt = [a + b * xi for xi in x]
        ape = [abs(yi - yti) / yi if yi != 0 else 0 for yi, yti in zip(y, yt)]
        mape = round((sum(ape) / n), 2) * 100
        check_data = self.env['penggunaan.bahan'].sudo().search([('id', 'in', [item['id'] for item in data_preview])])
        for check in check_data:
            tanggal_awal = str(check.tanggal_input)
        tanggal_awal_obj = datetime.strptime(tanggal_awal, "%Y-%m-%d")
        tanggal_berikutnya_obj = tanggal_awal_obj + relativedelta(months=1)
        # Ekstrak bulan dan tahun dari tanggal berikutnya
        bulan = tanggal_berikutnya_obj.strftime("%B")  # Format nama bulan
        tahun = tanggal_berikutnya_obj.strftime("%Y")  # Format tahun
        if round(mape, 0) < 10:
            keterangan = 'Sangat Baik'
        elif round(mape, 0) >= 10 and round(mape, 0) < 20:
            keterangan = 'Baik'
        elif round(mape, 0) >= 20 and round(mape, 0) <= 50:
            keterangan = 'Cukup Baik'
        elif round(mape, 0) > 50:
            keterangan = 'Kurang'
        else:
            keterangan = ''

        result = {
            'bahan_baku': nama_bahan,
            'bulan': bulan,
            'tahun': tahun,
            'bahan_baku': nama_bahan,
            'qty': y_prediksi,
            'uom': uom,
            'mape': mape,
            'keterangan': keterangan,
        }
        return result

class prediksi_semuabahan_report_wizard_line(models.TransientModel):
    _name = 'prediksi.semuabahan.report.wizard.line'

    wizard_semuabahan_id = fields.Many2one('prediksi.semuabahan.report.wizard', string='Wizard semuabahan Id')
    bulan = fields.Char(string='Bulan')
    tahun = fields.Char(string='Tahun')
    bahan_baku = fields.Char(string='Bahan')
    qty = fields.Float(string='Qty Prediksi')
    uom = fields.Char(string='UoM')
    mape = fields.Float(string='MAPE')
    keterangan = fields.Char(string='Keterangan')

class prediksi_semuabahan_template_pdf(models.AbstractModel):
    _name = 'report.modul_prediksi.semuabahan_template'

    def _get_report_values(self, docids, data=None):
        self._cr.execute("""(
                                    select id as id from bahan_baku
                                )""".format())
        data_bahan = self._cr.dictfetchall()
        check_data_bahan = self.env['bahan.baku'].sudo().search([('id', 'in', [item['id'] for item in data_bahan])])
        data_all = []
        total_mape = 0
        for bahan in check_data_bahan:
            self._cr.execute("""(
                                select a.id as id,
                                c.name as nama_bahan,
                                b.qty as qty,
                                b.uom as uom
                                from penggunaan_bahan a
                                join penggunaan_bahan_line b on b.penggunaan_bahan_id = a.id 
                                join bahan_baku c on c.id = b.bahan_baku
                                where b.bahan_baku  = {_id}
                                order by a.tanggal_input asc
                            )""".format(_id=bahan.id))
            data_preview = self._cr.dictfetchall()
            y = []
            for item in data_preview:
                y.append(item.get('qty'))
                uom = item.get('uom')
                nama_bahan = item.get('nama_bahan')

            n = len(y)  # Jumlah elemen dalam variabel y

            if n % 2 == 0:  # Jika jumlah elemen genap
                x = [-1 * (n - 1) + i * 2 for i in range(n)]
            else:  # Jika jumlah elemen ganjil
                middle_index = n // 2
                # x = [-1 * ((middle_index + 1) - 1) + i for i in range(n)]
                x = [-1 * middle_index + i for i in range(n)]

            # Membuat variabel xy yang berisi hasil perkalian x dan y sesuai urutannya
            xy = [xi * yi for xi, yi in zip(x, y)]
            x2 = [xi ** 2 for xi in x]

            a = round(sum(y) / len(y), 2)
            if n % 2 == 0:  # Jika jumlah elemen genap
                x_prediksi = x[-1] + 2
            else:  # Jika jumlah elemen ganjil
                x_prediksi = x[-1] + 1
            # Menghitung variabel b berdasarkan rumus (jumlah dari variabel xy) dibagi (jumlah dari variabel x2)
            b = round(sum(xy) / sum(x2), 2)
            # Membuat variabel y_prediksi yang nilainya adalah a + b dikali x_prediksi
            y_prediksi = round(a + b * x_prediksi, 2)
            # Membuat variabel yt yang nilainya adalah a + b dikali x untuk setiap nilai x dalam variabel x
            yt = [a + b * xi for xi in x]
            ape = [abs(yi - yti) / yi if yi != 0 else 0 for yi, yti in zip(y, yt)]
            mape = round((sum(ape) / n), 2) * 100
            check_data = self.env['penggunaan.bahan'].sudo().search(
                [('id', 'in', [item['id'] for item in data_preview])])
            for check in check_data:
                tanggal_awal = str(check.tanggal_input)
            tanggal_awal_obj = datetime.strptime(tanggal_awal, "%Y-%m-%d")
            tanggal_berikutnya_obj = tanggal_awal_obj + relativedelta(months=1)
            # Ekstrak bulan dan tahun dari tanggal berikutnya
            bulan = tanggal_berikutnya_obj.strftime("%B")  # Format nama bulan
            tahun = tanggal_berikutnya_obj.strftime("%Y")  # Format tahun
            if round(mape, 0) < 10:
                keterangan = 'Sangat Baik'
            elif round(mape, 0) >= 10 and round(mape, 0) < 20:
                keterangan = 'Baik'
            elif round(mape, 0) >= 20 and round(mape, 0) <= 50:
                keterangan = 'Cukup Baik'
            elif round(mape, 0) > 50 :
                keterangan = 'Kurang'
            else:
                keterangan = ''
            total_mape += mape
            data_prediksi = {
                'bulan': bulan,
                'tahun': tahun,
                'bahan_baku': nama_bahan,
                'qty': y_prediksi,
                'uom': uom,
                'mape': round(mape, 0),
                'keterangan': keterangan,
            }
            if len(data_prediksi) > 0:
                data_all.append(data_prediksi)
                uid = self._uid
        data_final=[]
        docs = data_final
        for data in data_all:
            data_final.append({
                'bulan': data['bulan'],
                'tahun': data['tahun'],
                'bahan_baku': data['bahan_baku'],
                'qty': data['qty'],
                'uom': data['uom'],
                'mape': data['mape'],
                'keterangan': data['keterangan'],
            })
        if data_final:
            docs = data_final
        average_mape = total_mape / len(data_all)
        if round(average_mape, 0) < 10:
            keterangan_average_mape = 'Sangat Baik'
        elif round(average_mape, 0) >= 10 and round(mape, 0) < 20:
            keterangan_average_mape = 'Baik'
        elif round(average_mape, 0) >= 20 and round(mape, 0) <= 50:
            keterangan_average_mape = 'Cukup Baik'
        elif round(average_mape, 0) > 50:
            keterangan_average_mape = 'Kurang'
        else:
            keterangan_average_mape = ''
        result = {
            'docs': docs,
            'average_mape': average_mape,
            'keterangan_average_mape': keterangan_average_mape
        }
        return result



