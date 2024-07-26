import pandas as pd
import Code.utils as utils

# Función que valida que el archivo de clientes contenga los campos requeridos
def validar_campos_clientes(df):

    errores = []
    
    # Convertir nombres de columnas a mayúsculas y eliminar espacios
    df.columns = [str(i).strip().upper() for i in df.columns]

    # Definir los campos requeridos y sus posibles nombres
    campos_requeridos = {
        'CEDULA': ['NIT', 'CEDULA'],
        'Nombre y apellido': ['NOMBREINTE', 'NOMBRE Y APELLIDO'],
        'AGENCIA': ['AGENCIA', 'COD. AGENCIA', 'COD.AGENCIA'],
        'CODCIUDAD': ['CODCIUDAD']
    }

    # Verificar los campos requeridos
    campos = {}
    for campo, alias in campos_requeridos.items():
        encontrado = False
        for a in alias:
            if a in df.columns:
                encontrado = True
                df.rename(columns={a: campo}, inplace=True)
                campos[campo] = a
                break
        if not encontrado:
            errores.append(f"Falta el campo requerido: {campo} en el informe de Clientes")
    
    # Validar tipos de datos
    try:
        df["CEDULA"] = df["CEDULA"].astype('int64', errors='ignore')
    except:
        errores.append(f"{campos['CEDULA']} debe ser un número entero.")

    # Removiendo datos duplicados
    df = df.drop_duplicates(subset='CEDULA', keep='first')
    
    # Validar campos opcionales
    campos_opcionales = ['INGRESOS', 'EGRESOS', 'ACTIVOS', 'PASIVOS']
    for campo in campos_opcionales:
        if campo in df.columns and not pd.api.types.is_numeric_dtype(df[campo]):
            errores.append(f"{campo} debe ser numérico si está presente.")
        else:
            df[campo.capitalize()] = 0.0

    # Agregando código = 0.0
    df["Codigo"] = 0.0

    return errores, df


# Función que valida que el archivo de transacciones OPA contenga los campos requeridos
def validar_campos_transacciones_opa(df):
    errores = []

    # Convirtiendo en mayúsculas
    df.columns = [str(i).strip().upper() for i in df.columns]

    # Definir los campos requeridos y sus posibles nombres
    campos_requeridos = {
        'FECHA': ['FECHA', 'FECHA_REGISTRO'],
        'CEDULA': ['CEDULA'],
        'OPERACION': ['NATURALEZA', 'TIPO DE MOVIMIENTO', 'TIPODEMOVIMIENTO', 'OPERACION', 'OPERACIÓN'],
        'VALOR': ['VALOR', 'TOTAL EFECTIVO', 'TOTALEFECTIVO'],
        'PRODUCTO': ['CODLINEA', 'PRODUCTO'],
    }

    # Verificar los campos requeridos
    campos = {}
    for campo, alias in campos_requeridos.items():
        encontrado = False
        for a in alias:
            if a in df.columns:
                encontrado = True
                df.rename(columns={a: campo}, inplace=True)
                campos[campo] = a
                break
        if not encontrado:
            errores.append(f"[OPA] Falta el campo requerido: {campo} en el archivo de Transacciones")
    
    # Validar tipos de datos CEDULA
    if 'CEDULA' in df.columns:
        try:
            df["CEDULA"] = df["CEDULA"].astype('int64', errors='ignore')
        except:
            errores.append(f"{campos['CEDULA']} debe ser un entero.")
    
    if 'VALOR' in df.columns:
        if not pd.api.types.is_numeric_dtype(df['VALOR']):
            errores.append(f"{campos['VALOR']} debe ser un entero.")
    
    if 'OPERACION' in df.columns:
        if not df['OPERACION'].astype(str).str.upper().isin(['DEBITO', 'CREDITO', 'CNGC', 'RETC', 'C', 'R']).all():
            errores.append(f"{campos['OPERACION']} debe ser uno de los valores permitidos: DEBITO, CREDITO, CNGC, RETC, C, R.")
        # Convirtiendo operacion a DEBITO O CREDITO
        df['OPERACION'] = df['OPERACION'].astype(str).apply(utils.mapear_operacion)

    # CONDICION 1:
    # Convertir a datetime la fecha.
    if 'FECHA' in df.columns:
        df, errores = utils.convertir_fecha(df, errores, campos)

    # CONDICION 2:
    # Renombrando campo CODAGENCIA si se encuentra:
    for col in ['COD. AGENCIA', 'COD.AGENCIA']:
        if col in df.columns:
            df.rename(columns={col:"CODAGENCIA"}, inplace=True)

    # CONDICIÓN 3:
    # Si el canal no se agrega, entonces es Taquilla
    if 'CANAL' not in df.columns:
        df["CANAL"] = "Taquilla"

    return errores, df


# Función que valida que el archivo de transacciones VISIONAMOS contenga los campos requeridos
def validar_campos_transacciones_visionamos(df):
    errores = []

    # Convirtiendo en mayúsculas
    df.columns = [str(i).strip().upper() for i in df.columns]

    # Definir los campos requeridos y sus posibles nombres
    campos_requeridos = {
        'FECHA': ['FECHA_REGISTRO', 'FECHA'],
        'CEDULA': ['CEDULA', 'DOCUMENTO'],
        'OPERACION': ['OPERACION', 'TIPO DE MOVIMIENTO', 'TIPODEMOVIMIENTO', 'OPERACIÓN'],
        'VALOR': ['VALOR', 'TOTAL EFECTIVO', 'TOTALEFECTIVO'],
        'ESTADO': ['ESTADO'],
        'CANAL': ['CANAL']
    }

    # Verificar los campos requeridos
    campos = {}
    for campo, alias in campos_requeridos.items():
        encontrado = False
        for a in alias:
            if a in df.columns:
                encontrado = True
                df.rename(columns={a: campo}, inplace=True)
                campos[campo] = a
                break
        if not encontrado:
            errores.append(f"[Visionamos] Falta el campo requerido: {campo} en el archivo de Transacciones")
    
    # Validar tipos de datos CEDULA
    if 'CEDULA' in df.columns:
        try:
            df["CEDULA"] = df["CEDULA"].astype('int64', errors='ignore')
        except:
            errores.append(f"{campos['CEDULA']} debe ser un entero.")

    if 'VALOR' in df.columns:
        if not pd.api.types.is_numeric_dtype(df['VALOR']):
            errores.append(f"{campos['VALOR']} debe ser numérico.")

    if 'OPERACION' in df.columns:
        if not df['OPERACION'].astype(str).str.upper().isin(['DEBITO', 'CREDITO', 'CNGC', 'RETC', 'C', 'R']).all():
            errores.append(f"{campos['OPERACION']} debe ser uno de los valores permitidos: DEBITO, CREDITO, CNGC, RETC, C, R.")
        # Convirtiendo operacion DEBITO O CREDITO
        df['OPERACION'] = df['OPERACION'].astype(str).apply(utils.mapear_operacion)

    if 'ESTADO' in df.columns:
        if not df['ESTADO'].astype(str).str.upper().isin(['DECLINADA', 'APROBADA']).all():
            errores.append("ESTADO debe ser uno de los valores permitidos: DECLINADA, APROBADA.")
        # CONDICIÓN 1:
        # El estado de la transacción se toma APROBADA
        df = df[df["ESTADO"]=="APROBADA"]
    
    # CONDICION 2:
    # Convertir a datetime la fecha.
    if 'FECHA' in df.columns:
        df, errores = utils.convertir_fecha(df, errores, campos)

    # CONDICIÓN 3:
    # Si el producto no se agrega, entonces es Ahorros
    if 'PRODUCTO' not in df.columns:
        df["PRODUCTO"] = "Ahorros"

    # CONDICIÓN 4:
    # Si dispositivo está en la columna: Se agrega al canal.
    if 'DISPOSITIVO' in df.columns:
        df['CANAL'] = df['CANAL'] + ' - ' + df['DISPOSITIVO']

    # CONDICIÓN 5:
    # Dividir el campo valor entre 100
    if 'VALOR' in df.columns:
        df.loc[:, 'VALOR'] = df.loc[:, 'VALOR']/100

    return errores, df
