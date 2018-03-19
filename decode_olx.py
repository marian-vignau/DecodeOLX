"""
Software para generar un reporte pericial de la información encontrada en la base de datos
de la app de OLX.
"""

import configparser
from processor import createreportdir, dateconvert, createreport, create_pdf


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    dateconvert.set_locale(config.get("main", "locale"), config.get("main", "format_date"))

    items = createreportdir.run(config)
    report = createreport.Report(config)
    report.run(items)
    try:
        create_pdf.run(config.get("report_path", "report_dir"),
                   config.get("report_path", "report_resource_dir"))
    except Exception as e:
        print(e)