{
    'name': 'Module Custom Purchase',
    'version': '15.0.1.0.0',
    'category': 'purchase',
    'summary': 'Prediction Custom Module',
    'description': """
        Prediction Custom Module UMKM Hafiz By Bagoes
    """,
    'website': '',
    'author': 'Bagoes Ardianjar',
    'depends': ['web','base','product'],
    'data': [
        'security/ir.model.access.csv',
        'views/prediksi_umkm_view.xml',
        'views/prediksi_umkm_action.xml',
        'views/prediksi_umkm_menuitem.xml',
        'views/prediksi_umkm_sequence.xml',
        'views/prediksi_umkm_cron.xml',
        # 'reports/paper_format_report.xml',
        'reports/prediksi_perbahan.xml',
        'reports/prediksi_semuabahan.xml',
        'reports/paper_format_report.xml',
        'reports/report_pdf.xml'
    ],
    'installable': True,
    'license': 'OEEL-1',
}