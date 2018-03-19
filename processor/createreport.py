"""Aquí se consulta cada una de las bases de datos de la app de olx copiadas de
lo celulares a peritar y se genera el reporte en formato html"""

__author__ = "María Andrea Vignau"

import os
import json
import sqlite3
import re

import jinja2   # fades Jinja2

from . import dateconvert

class Report(object):
    def __init__(self, config):
        self.caseinfo = {}
        for opt in config.options("case_info"):
            self.caseinfo[opt] = config.get("case_info", opt)
        self.config = {}
        for opt in config.options("report_path"):
            self.config[opt] = config.get("report_path", opt)
        self.sourcedbfilename = config.get("main", 'olxMsgDatabase_file')
        self.template_dir = config.get("data_path", "template_dir")

    def query_results(self, db, sql, field, keywords):
        """esta función agrega al query 'sql' los criterios de busqueda.
        #db - realiza la conexión a la base de datos.
        #sql - es el query que se utilizará.
        #field - es el campo en el que se realizará la busqueda
        #keywords - son las palabras claves que se buscarán coincidencias."""
        if keywords:
            #template es un string que contiene: p.ej. "objects.objectData like '%s'"
            template = field + " like '%s'"
            list_conditions = [template % word for word in keywords]
            sql += ' where ' + ' or \n'.join(list_conditions)

        cursor = db.cursor()
        return cursor.execute(sql)

    def filter_query_key(self, cursor, key_field, regexp):
        """Filtra usando una expresión regular las filas de una consulta
        #cursor: la consulta realizada,
        #key_field: el número de columna donde se encuentra el campo
        #regexp: la expresión regular por la que se filtran las filas de la consulta
        """
        for row in cursor.fetchall():
            if re.match(regexp, row[key_field]):
                yield row

    def render_html(self, template_file, data):
        """Ejecuta el template con los datos del entorno
        Necesita tener como variables el directorio de templates template_dir
        #template_file: archivo de template que se usará
        #data: estructura de datos que se usará para los templates
        """
        templateLoader = jinja2.FileSystemLoader(searchpath=self.template_dir)
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(template_file)
        return template.render(data).encode('utf-8')

    def extract_threads(self, olxMsgDatabase_file):
        """Obtengo la información que se encuentra en la tabla objetos de la base de datos sqlite
        Identifico los threads, que son el tipo de registro que quiero decodificar, a partir
        de la expresión regular.
        La fecha del registro requirió una investigación adicional, se dedujo que la fecha
        se encontraba representada por un entero desde unix epoch, con precisión de milisegundos
        Se verificó que usando la función
        "Compute the date and time given a unix timestamp 1092941466, and compensate for your local timezone.
        SELECT datetime(1092941466, 'unixepoch', 'localtime'); "
        para convertir este número en una representación de tipo de datos fecha en sqlite, para
        luego formatearla usando la función strftime con el formato de fecha de uso en la Argentina.
        """
        db = sqlite3.connect(olxMsgDatabase_file)
        keywords = []
        sql = """
        select objects.objectKey, objects.objectData,
        strftime('%d-%m-%Y - %H:%M:%S', datetime(objects.objectDate/1000, 'unixepoch', 'localtime')) objectDate
        from objects
        """
        cursor = self.query_results(db, sql, "objects.objectData", keywords)
        for row in self.filter_query_key(cursor, 0, '........-....-....-....-............'):
            yield row[0], json.loads(row[1])


    def run(self, elementos):
        """Leo cada uno de los directorios con información del caso
        """
        #itero sobre cada elemento a peritar
        self.caseinfo["elemento"] = elementos
        for dirname in elementos:
            index = []
            # extraigo las filas de la tabla objetos
            path_sqlite_db = os.path.join(self.config["report_data_dir"],
                                          dirname, self.sourcedbfilename)

            for key, js in self.extract_threads(path_sqlite_db):
                # toma las claves y la estructura de datos del campo formato json
                # itera los items comerciados desde esta app
                if 'item' in js:
                    js['item']['date']['timestamp'] = dateconvert.fromdatestr(js['item']['date']['timestamp'])

                    # itera en cada uno de los mensajes, formatea y localiza las fechas
                    for msg in js['messages']:
                        if 'date' in msg:
                            msg['date'] = dateconvert.fromtimestamp(msg['date'])

                    # genera el archivo html a partir de la estructura de información
                    html_rendered = self.render_html('message_template.html', js)

                    # genera un nombre único a cada thread y lo graba en un archivo
                    pos = len(index) + 1
                    key = "t%03d %s" % (pos, key)
                    with open(os.path.join(self.config["report_dir"], dirname, key + '.html'), 'wb') as f:
                        f.write(html_rendered)

                    # agrega los partícipes y genera la entrada en el índice de cada element
                    senders = ' <> '.join([s['name'] for s in js['senders']])
                    index.append(
                        {'id': js['item']['title'] + ' - ' + str(js['item']['id']) + ' - ' + senders,
                         'url': key + '.html'}
                    )

            # arma un html con el índice de threads de cada elemento
            object_index = {'index': index, 'elto': dirname}
            html_rendered = self.render_html('publicated-items.html', object_index)
            with open(os.path.join(self.config["report_dir"], dirname, 'publicated-items.html'), 'wb') as f:
                f.write(html_rendered)

        # genera la página web de portada del caso, para generar archivo pdf.
        data2 = {'caseinfo': self.caseinfo}
        html_rendered = self.render_html('case-info.html', data2)
        with open(os.path.join(self.config["report_dir"], 'case-info.html'), 'wb') as f:
            f.write(html_rendered)

        # genera la página web de índice general del caso con iframes.
        html_rendered = self.render_html('index.html', data2)
        with open(os.path.join(self.config["report_dir"], 'index.html'), 'wb') as f:
            f.write(html_rendered)
