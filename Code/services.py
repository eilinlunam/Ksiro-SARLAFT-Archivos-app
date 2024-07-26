import pandas as pd
from Code.validations import *

def modificar_archivos(nombre_archivo1, nombre_archivo2, opcion):
    try:

        #============================================================================================================
        # CLIENTES
        #============================================================================================================
        # Leer y procesar archivo de clientes
        df_clientes = pd.read_excel(nombre_archivo1)
        df_clientes.columns = [col.strip().upper() for col in df_clientes.columns]

        # Verificando campos
        errores, df_clientes = validar_campos_clientes(df_clientes)
        if errores:
            return "Validación fallida", " - ".join(errores)
        
        df_clientes["CEDULA"] = pd.to_numeric(df_clientes["CEDULA"], errors='coerce').fillna(0).astype('int64')

        #============================================================================================================
        # TRANSACCIONES
        #============================================================================================================
        # Leer y procesar archivo de transacciones
        df_transacciones = pd.read_excel(nombre_archivo2)
        df_transacciones.columns = [col.strip().upper() for col in df_transacciones.columns]

        # Verificando campos
        if opcion.upper()=="VISIONAMOS":
            errores, df_transacciones = validar_campos_transacciones_visionamos(df_transacciones)
        else:
            errores, df_transacciones = validar_campos_transacciones_opa(df_transacciones)
        if errores:
            return "Validación fallida", " \n- ".join(errores)

        #============================================================================================================
        # EMPEZAMOS A MODIFICAR EL ARCHIVO DE TRANSACCIONES:
        #============================================================================================================

        # Agrupando por: CEDULA, FECHA, OPERACION, PRODUCTO y CANAL (Hallando conteo y suma del valor)
        df = df_transacciones[['CEDULA', 'FECHA', 'OPERACION', 'PRODUCTO', 'CANAL', 'VALOR']].copy()
        df = df.groupby(['CEDULA', 'FECHA', 'OPERACION', 'PRODUCTO', 'CANAL']).agg({'count', 'sum'}).reset_index()
        df.columns = df.columns.droplevel(level=0)
        df.columns.values[:5] = ['CEDULA', 'FECHA', 'OPERACION', 'PRODUCTO', 'CANAL']
        df = df.rename(columns={"sum":"VALOR", "count":"N_VALOR"})

        # Agrupamos por DÉBITO y CRÉDITO
        df_debito = df[df["OPERACION"]=="DEBITO"].rename(columns={"N_VALOR":"N_DEBITO", "VALOR":"SUMA_DEBITO"})
        df_credito = df[df["OPERACION"]=="CREDITO"].rename(columns={"N_VALOR":"N_CREDITO", "VALOR":"SUMA_CREDITO"})
        df = pd.concat([df_debito, df_credito]).fillna(0).sort_values(by=["CEDULA", "FECHA"])
        
        # Agregamos la JURISDICCIÓN en Transacciones
        if 'AGENCIA' not in df_transacciones.columns:
            df = pd.merge(df, df_clientes[['CEDULA', 'AGENCIA']], on='CEDULA', how='left')
        else:
            df = pd.merge(df, df_transacciones[['CEDULA', 'AGENCIA']], on='CEDULA', how='left')
        df = df.rename(columns={"AGENCIA":"JURISDICCION"})

        # Agregamos la JURISDICCIÓN1 en Transacciones
        if 'CODCIUDAD' not in df_transacciones.columns:
            df = pd.merge(df, df_clientes[['CEDULA', 'CODCIUDAD']], on='CEDULA', how='left')
        else:
            df = pd.merge(df, df_transacciones[['CEDULA', 'CODCIUDAD']], on='CEDULA', how='left')
        df = df.rename(columns={"CODCIUDAD":"JURISDICCION2"})

        # Retomamos y reordenamos
        dfC = df_clientes[["CEDULA", "Nombre y apellido", "Ingresos", "Egresos", "Activos", "Pasivos", "Codigo"]].fillna(0)
        dfT = df[["CEDULA", "FECHA", "N_DEBITO", "SUMA_DEBITO", "N_CREDITO", "SUMA_CREDITO", "PRODUCTO", "CANAL", "JURISDICCION", "JURISDICCION2"]]

        return dfC, dfT
    except Exception as e:
        raise Exception(f'ERROR: {str(e)}')

def guardar_excel(df, ruta, nombre_hoja):
    try:
        df.to_excel(ruta, index=False, sheet_name=nombre_hoja)
        return send_file(ruta, as_attachment=True)
    except Exception as e:
        raise Exception(f'Error al guardar archivo Excel: {str(e)}')