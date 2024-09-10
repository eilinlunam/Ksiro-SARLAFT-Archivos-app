import os
import shutil
import pandas as pd

# Verificar la extensión del archivo
def archivo_permitido(nombre_archivo):
    EXTENSIONES_PERMITIDAS = {'xlsx'}
    return '.' in nombre_archivo and nombre_archivo.rsplit('.', 1)[1].lower() in EXTENSIONES_PERMITIDAS


# Verificar si la carpeta existe y vaciarla si es necesario
def vaciar_carpeta(ruta_carpeta):
    try:
        if os.path.exists(ruta_carpeta):
            for archivo in os.listdir(ruta_carpeta):
                ruta_archivo = os.path.join(ruta_carpeta, archivo)
                if os.path.isfile(ruta_archivo):
                    os.remove(ruta_archivo)
                elif os.path.isdir(ruta_archivo):
                    shutil.rmtree(ruta_archivo)
        else:
            print(f'La carpeta {ruta_carpeta} no existe.')
    except Exception as e:
        print(f'Ocurrió un error al vaciar la carpeta {ruta_carpeta}: {str(e)}')

def mapear_operacion(operacion):
    operacion = operacion.upper()  # Convertir a mayúsculas
    if operacion=='CREDITO' or operacion=='CNGC' or operacion=='C':
        return 'CREDITO'
    elif operacion=='DEBITO' or operacion=='RETC' or operacion=='R':
        return 'DEBITO'
    else:
        return operacion  # Mantener el valor original si no coincide con ninguna categoría
    
def convertir_fecha(df, errores, campos):
    formatos = ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d", "%Y%m%d"]
    fecha_convertida = None
    texto=""
    for formato in formatos:
        try:
            df_temp = df.copy()
            df_temp['FECHA'] = pd.to_datetime(df_temp['FECHA'], format=formato, errors='coerce')
            # Verificar si la conversión fue exitosa
            if df_temp['FECHA'].notna().all():
                fecha_convertida = df_temp['FECHA']
                break
        except Exception as e:
            errores.append(f"Error al convertir con formato {formato}: {str(e)}")
    if fecha_convertida is None:
        texto = f"No se pudo convertir la columna {campos.get('FECHA', 'FECHA')} en formato fecha"
    else:
        df['FECHA'] = fecha_convertida.dt.to_period('M')
    if texto!="": errores.append(texto)
    return df, errores