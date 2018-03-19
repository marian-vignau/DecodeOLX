"""A partir de los archivos html generados, crea un archivo .pdf"""

__author__ = "María Andrea Vignau"
import os
import platform
import pdfkit   # fades pdfkit


def run(report_dir, report_resource_dir):
    """Crea un archivo pdf para poder imprimir la información.

    """

    # configura el path del archivo ejecutable que convierte html a pdf
    config = pdfkit.configuration()
    if platform.system() == "Windows":
        config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

    # archivo css que tiene los estilos que se aplicarón
    css = os.path.join(report_resource_dir, 'myStyle.css')
    options = {
        # 'quiet': '',
        'user-style-sheet': css
    }

    # arma la lista de archivos que serán incluidos en el pdf.
    file_list = []
    for root, dir, files in os.walk(report_dir):
        for file in files:
            if file.endswith('html') and file != "index.html":
                #print(os.path.join(root, file))
                file_list.append(os.path.join(root, file))

    # ejecuta la conversión finalmente
    pdfkit.from_file(file_list,
                     os.path.join(report_dir, 'Report.pdf'),
                     options=options,
                     configuration=config)