"""Esta función crea una nueva estructura de directorios donde se guardará el reporte,
y los archivo del caso.
Si existian los directorios previamente, los borra y crea de nuevo."""

__author__ = "María Andrea Vignau"

import os
import shutil

def run(config):
    # Recursive directory creation function. Like mkdir, but makes all intermediate-level
    # directories needed to contain the leaf directory.
    # como el parámetro exist_ok está en TRUE, recrea los directorios si es necesario
    for option in ["report_dir", "report_data_dir", "report_resource_dir"]:
        new_dir_path = config.get("report_path", option)
        os.makedirs(new_dir_path, 0o777, True)

    # itera sobre los directorios de data y copia las bases de datos si están
    elementos = []
    data_dir = config.get("case_info", "data_dir")
    for dirname in os.listdir(data_dir):
        if os.path.isdir(os.path.join(data_dir, dirname)):

            # copia la base de datos sqlite en caso de existir
            database = os.path.join(data_dir, dirname, config.get("main", "olxMsgDatabase_file"))
            elementos.append(dirname)
            if os.path.exists(database):
                dest_dir = os.path.join(config.get("report_path", "report_data_dir"), dirname)
                os.makedirs(dest_dir, 0o777, True)
                os.makedirs(os.path.join(config.get("report_path", "report_dir"), dirname), 0o777, True)
                shutil.copy(database,
                            os.path.join(dest_dir, config.get("main", "olxMsgDatabase_file")))

    # copia los estilos y el logo
    shutil.copy(config.get("data_path", "template_dir") + '/myStyle.css',
                config.get("report_path", "report_resource_dir") + '/myStyle.css')
    shutil.copy(config.get("data_path", "img_dir") + '/logo.png',
                config.get("report_path", "report_resource_dir") + '/logo.png')
    return elementos
