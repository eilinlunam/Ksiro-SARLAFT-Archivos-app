# Importando paquetes
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import pandas as pd
import os

# Importando código:
from Code.utils import *
import Code.services as services

# API FLASK
app = Flask(__name__)

# Configuración de la carpeta de subida
CARPETA_ARCHIVOS = 'Uploads/'
CARPETA_RESULTADOS = 'Results/'
app.config['CARPETA_ARCHIVOS'] = CARPETA_ARCHIVOS
app.config['CARPETA_RESULTADOS'] = CARPETA_RESULTADOS

# Endpoint para manejar archivos OPA y Visionamos y procesarlos a Ksiro-SARLAFT
@app.route('/obtenerArchivosSARLAFT', methods=['POST'])
def obtener_archivos_sarlaft():

    if request.method == 'POST':
        # Verificar si se reciben los archivos archivo1 y archivo2
        if 'archivo1' not in request.files or 'archivo2' not in request.files:
            return jsonify({'mensaje': 'Debe subir ambos archivos.'}), 400
        
        # Recibiendo parámetros
        archivo1 = request.files['archivo1']  # Clientes
        archivo2 = request.files['archivo2']  # Transacciones
        tipobd = request.form.get('tipobd')  # Visionamos o OPA
        opcion_archivo = request.form.get('opcion_archivo')

        # Parámetros para definir el nombre del archivo:
        mes_seleccionado = request.form.get('mes')
        año_seleccionado = request.form.get('anio')
        historico = request.form.get('historico', 'false') 
        if mes_seleccionado==None: mes_seleccionado="SARLAFT"
        if año_seleccionado==None: año_seleccionado=""

        if not tipobd:
            return jsonify({'mensaje': 'Debe seleccionar el tipo de bases de datos: OPA o VISIONAMOS'}), 400

        # Verificar si los archivos son válidos
        if archivo1.filename == '' or archivo2.filename == '':
            return jsonify({'mensaje': 'Debe subir ambos archivos: CLIENTES y TRANSACCIONES'}), 400
        
        # Si los archivos cumplen con las extensión permitida: .xlsx
        if archivo1 and archivo_permitido(archivo1.filename) and archivo2 and archivo_permitido(archivo2.filename):
            
            # Limpiar la carpeta de subida antes de guardar los nuevos archivos
            vaciar_carpeta(app.config['CARPETA_ARCHIVOS'])
            vaciar_carpeta(app.config['CARPETA_RESULTADOS'])

            # Guardar los archivos en la carpeta de subida
            nombre_archivo1 = secure_filename(archivo1.filename)
            nombre_archivo2 = secure_filename(archivo2.filename)

            ruta_archivo1 = os.path.join(app.config['CARPETA_ARCHIVOS'], nombre_archivo1)
            ruta_archivo2 = os.path.join(app.config['CARPETA_ARCHIVOS'], nombre_archivo2)
            
            archivo1.save(ruta_archivo1)
            archivo2.save(ruta_archivo2)
            
            # Modificar archivos según la opción seleccionada
            try:
                df_clientes, df_transacciones = services.modificar_archivos(ruta_archivo1, ruta_archivo2, tipobd)
            except Exception as e:
                return jsonify({'mensaje': f'Error en la modificación de archivos: {str(e)}'}), 500
            
            # Verificar si hay errores en la modificación de archivos
            if isinstance(df_clientes, str):
                return jsonify({'mensaje': df_transacciones}), 400
            
            # Nombres de archivos resultantes
            if historico == "true":
                ruta_clientes = "Clientes Histórico.xlsx"
                ruta_transacciones = "T-Histórico OPA.xlsx" if tipobd == "OPA" else "T-Histórico Visionamos.xlsx"
            else:
                ruta_clientes = f"Clientes-{mes_seleccionado}{año_seleccionado}.xlsx"
                ruta_transacciones = f"T-{mes_seleccionado}{año_seleccionado} OPA.xlsx" if tipobd == "OPA" else f"T-{mes_seleccionado}{año_seleccionado} Visionamos.xlsx"
            
            # Guardar archivos y devolver las rutas de descarga
            try:
                if opcion_archivo.upper() == "CLIENTES":
                    return guardar_excel(df_clientes, ruta_clientes, "Cliente")
                else:
                    return guardar_excel(df_transacciones, ruta_transacciones, "Transacciones")
            except Exception as e:
                return jsonify({'mensaje': f'Error al guardar archivos: {str(e)}'}), 500
            

# Ruta para unir archivos
@app.route('/unir_archivos_resultantes', methods=['POST'])
def unir_archivos_resultantes():
    if request.method == 'POST':
        
        # Verificar si se reciben los archivos archivo1 y archivo2
        if 'archivo_visionamos' not in request.files or 'archivo_opa' not in request.files:
            return jsonify({'mensaje': 'Debe subir ambos archivos.'}), 400
        
        archivo1 = request.files['archivo_visionamos']  # Visionamos
        archivo2 = request.files['archivo_opa']  # Visionamos

        # Parámetros para definir el nombre del archivo:
        mes_seleccionado = request.form.get('mes')
        año_seleccionado = request.form.get('anio')
        historico = request.form.get('historico', 'false') 
        if mes_seleccionado==None: mes_seleccionado="SARLAFT"
        if año_seleccionado==None: año_seleccionado=""

        if archivo1.filename == '' or archivo2.filename == '':
            return jsonify({'mensaje': 'Debe subir ambos archivos.'}), 400
        
        if archivo1 and archivo_permitido(archivo1.filename) and archivo2 and archivo_permitido(archivo2.filename):
            vaciar_carpeta(app.config['CARPETA_ARCHIVOS'])
            vaciar_carpeta(app.config['CARPETA_RESULTADOS'])

            nombre_archivo1 = secure_filename(archivo1.filename)
            nombre_archivo2 = secure_filename(archivo2.filename)

            ruta_archivo1 = os.path.join(app.config['CARPETA_ARCHIVOS'], nombre_archivo1)
            ruta_archivo2 = os.path.join(app.config['CARPETA_ARCHIVOS'], nombre_archivo2)
            
            archivo1.save(ruta_archivo1)
            archivo2.save(ruta_archivo2)

            try:
                df1 = pd.read_excel(ruta_archivo1)
                df2 = pd.read_excel(ruta_archivo2)
                df = pd.concat([df1, df2])
                df1["BD"] = "VISIONAMOS"
                df2["BD"] = "OPA"
                df = pd.concat([df1, df2])
                df = df.sort_values(by=["CEDULA", "Fecha"])
            except Exception as e:
                return jsonify({'mensaje': f'Error al unir archivos: {str(e)}'}), 500
            
            # Nombre del archivo resultante
            ruta = "T-Histórico (All).xlsx" if historico == "true" else f"T-{mes_seleccionado}{año_seleccionado} (All).xlsx"
            
            # Guardar archivos y devolver las rutas de descarga
            try:
                return guardar_excel(df, ruta, "Transacciones")
            except Exception as e:
                return jsonify({'mensaje': f'Error al guardar archivo: {str(e)}'}), 500

def guardar_excel(df, filename, sheetname):
    columnas_pesos = ["Ingresos", "Egresos", "Activos", "Pasivos", "SUMA_DEBITO", "SUMA_CREDITO"]
    
    # Crear un escritor de Excel y guardar el DataFrame en la hoja especificada
    with pd.ExcelWriter(app.config['CARPETA_RESULTADOS']+filename, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name=sheetname)
        workbook = writer.book
        worksheet = writer.sheets[sheetname]
        
        # Formato de moneda
        formato_moneda = workbook.add_format({'num_format': '$#,##0.00'})
        
        # Ajustar el ancho de las columnas
        for idx, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(idx, idx, max_len, formato_moneda if col in columnas_pesos else None)

    print("Archivo %s guardado con éxito"%(filename))
    return send_file(app.config['CARPETA_RESULTADOS']+filename, 
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True)
    
if __name__ == '__main__':
    app.run(debug=True)