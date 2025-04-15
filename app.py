import os
import psutil
import time
import socket
import pandas as pd
import mysql.connector
from mysql.connector import Error
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

# Configuraciones
RAIZ_PROYECTO = os.getcwd()
CARPETA_ORIGEN = os.path.join(RAIZ_PROYECTO, 'OriginFolder')
CARPETA_DESTINO = os.path.join(RAIZ_PROYECTO, 'DestinationFolder')
ARCHIVO_EXCEL = 'MaestroFamiliasMin.xlsx'
BASE_DATOS = 'data.db'
TIEMPO_ESPERA = 0.003  # 3ms en segundos
UMBRAL_CPU = 70  # %
UMBRAL_MEMORIA = 90  # %
TAMANIO_PAQUETE_KB = 10

# Configuración de MySQL
MYSQL_HOST = 'localhost'  # Cambia si tu base de datos no está en localhost
MYSQL_USER = 'your_user'       # Usuario de MySQL
MYSQL_PASSWORD = 'your_password'  # Contraseña de MySQL
MYSQL_DATABASE = 'move_file_process'  # Nombre de la base de datos
MYSQL_TABLE = 'productos'  # Nombre de la tabla

# Crear carpeta destino si no existe
os.makedirs(CARPETA_DESTINO, exist_ok=True)

# Conectar a MySQL
def conectar_mysql():
    try:
        conexion = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        if conexion.is_connected():
            print(f"{Fore.GREEN}✅ Conexión exitosa a MySQL.")
        return conexion
    except Error as e:
        print(f"{Fore.RED}❌ Error al conectar a MySQL: {e}")
        return None
    
# Registrar fila en MySQL
def registrar_fila_mysql(fila):
    conexion = conectar_mysql()
    if not conexion:
        return False
    
    cursor = conexion.cursor()
    try:
        # Verificar si el registro ya existe
        query_verificar = f"SELECT COUNT(*) FROM {MYSQL_TABLE} WHERE cod_barra = %s"
        cursor.execute(query_verificar, (fila['CODBARRA'],))
        existe = cursor.fetchone()[0]

        if existe:
            print(f"{Fore.YELLOW}⚠️ Registro ya existe en MySQL: CODBARRA={fila['CODBARRA']}")
            return False

        # Insertar el registro si no existe
        query_insertar = f"""
        INSERT INTO {MYSQL_TABLE} (num_suc, sku, cod_barra, descripcion, fam, sal_fis_suc, valor)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        valores = (fila['NumSuc'], fila['Sku'], fila['CODBARRA'], fila['Descripcion'], fila['Fam'], fila['SalFisSuc'], fila['Valor'])
        cursor.execute(query_insertar, valores)
        conexion.commit()
        print(f"{Fore.GREEN}✅ Registro insertado en MySQL: {valores}")
        return True
    except Error as e:
        print(f"{Fore.RED}❌ Error al registrar en MySQL: {e}")
        conexion.rollback()
        return False
    finally:
        cursor.close()
        conexion.close()

# Verificar recursos del sistema
def recursos_son_aceptables():
    uso_cpu = psutil.cpu_percent(interval=1)
    uso_memoria = psutil.virtual_memory().percent
    print(f"{Fore.CYAN}🔍 Recursos actuales: CPU={uso_cpu}%, Memoria={uso_memoria}%")
    return uso_cpu < UMBRAL_CPU and uso_memoria < UMBRAL_MEMORIA

def hay_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        print(f"{Fore.GREEN}🌐 Internet disponible.")
        return True
    except OSError:
        print(f"{Fore.RED}❌ Sin conexión a Internet.")
        return False

# Transferir datos por "paquetes"
def transferir_archivo():
    origen = os.path.join(CARPETA_ORIGEN, ARCHIVO_EXCEL)
    destino = os.path.join(CARPETA_DESTINO, ARCHIVO_EXCEL)

    print(f"{Fore.YELLOW}🟡 Iniciando transferencia de datos...")
    print(f"{Fore.YELLOW}📂 Archivo origen: {origen}")
    print(f"{Fore.YELLOW}📂 Archivo destino: {destino}")

    if not os.path.exists(origen):
        print(f"{Fore.RED}❌ Archivo origen no encontrado.")
        return

    df_origen = pd.read_excel(origen)

    # Crear archivo destino si no existe
    if not os.path.exists(destino):
        pd.DataFrame(columns=df_origen.columns).to_excel(destino, index=False)
        print(f"{Fore.GREEN}✅ Archivo destino creado.")

    # Leer archivo destino existente
    df_destino = pd.read_excel(destino)

    total_filas = len(df_origen)
    for index, fila in df_origen.iterrows():
        print(f"{Fore.BLUE}➡️ Procesando fila {index + 1} de {total_filas}...")
        while True:
            if not hay_internet():
                print(f"{Fore.RED}❌ Esperando conexión a Internet...")
                time.sleep(2)
                continue

            if not recursos_son_aceptables():
                print(f"{Fore.YELLOW}⚠️ Recursos limitados. Esperando...")
                time.sleep(1)
                continue

            # Validar duplicados y transferir fila
            if 'CODBARRA' in df_origen.columns:
                if not ((df_destino['CODBARRA'] == fila['CODBARRA']).any()):
                    if not fila.dropna().empty:
                        df_destino = pd.concat([df_destino, pd.DataFrame([fila])], ignore_index=True)
                        print(f"{Fore.GREEN}✅ Registro transferido CODBARRA={fila['CODBARRA']}")
                        registrar_fila_mysql(fila)
                else:
                    print(f"{Fore.YELLOW}⚠️ Registro duplicado ignorado CODBARRA={fila['CODBARRA']}")
            else:
                if not fila.dropna().empty:
                    df_destino = pd.concat([df_destino, pd.DataFrame([fila])], ignore_index=True)
                    print(f"{Fore.GREEN}✅ Registro transferido (sin validación de duplicado)")
                    registrar_fila_mysql(fila)

            # Guardar progreso en el archivo destino
            df_destino.to_excel(destino, index=False)
            print(f"{Fore.CYAN}💾 Progreso guardado en: {destino}")
            time.sleep(TIEMPO_ESPERA)
            break

    print(f"{Fore.GREEN}✅ Transferencia completa.")

# Todo::INICIO DEL PROCESO
def ejecutar_proceso():
    print(f"{Style.BRIGHT}{Fore.WHITE}=======================================")
    print(f"{Style.BRIGHT}{Fore.RED}  INICIO DEL PROCESO DE TRANSFERENCIA")
    print(f"{Style.BRIGHT}{Fore.WHITE}=======================================")
    transferir_archivo()
    print(f"{Style.BRIGHT}{Fore.WHITE}=======================================")
    print(f"{Style.BRIGHT}{Fore.RED}  FIN DEL PROCESO DE TRANSFERENCIA")
    print(f"{Style.BRIGHT}{Fore.WHITE}=======================================")

    destino = os.path.join(CARPETA_DESTINO, ARCHIVO_EXCEL)
    if os.path.exists(destino):
        print(f"{Fore.GREEN}✅ Archivo salida: {destino}")
        print(f"{Fore.GREEN}📦 Tamaño: {os.path.getsize(destino)} bytes")
    else:
        print(f"{Fore.RED}❌ No se creó el archivo de destino.")

if __name__ == '__main__':
    ejecutar_proceso()