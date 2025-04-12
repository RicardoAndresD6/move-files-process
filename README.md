# 🗂️ Sistema de Transferencia y Registro de Datos desde Excel a MySQL

Este proyecto automatiza la transferencia de registros desde un archivo Excel hacia una carpeta de destino, asegurando que los datos no se dupliquen y registrándolos también en una base de datos MySQL. Además, monitorea los recursos del sistema y la conexión a internet para evitar sobrecargas.

---

## 🚀 Funcionalidades

- 📤 Transferencia controlada de registros desde un archivo Excel.
- 🔄 Verificación de duplicados mediante el campo `CODBARRA`.
- 📈 Control de uso de CPU y memoria para evitar sobrecarga.
- 🌐 Verificación de conectividad a internet antes de procesar.
- 🗃️ Registro de datos en una tabla MySQL.
- 💾 Guardado continuo del progreso en el archivo destino.

---

## 📦 Requisitos

- Python 3.x
- MySQL Server
- Archivo Excel llamado `MaestroFamiliasMin.xlsx` en la carpeta `OriginFolder`.

---

### 🐍 Dependencias de Python

Antes de ejecutar el proyecto, asegúrate de tener instaladas las siguientes dependencias. Puedes instalarlas ejecutando:

pip install -r [requirements.txt]

---

### ⚙️ Configuracion

Crea una base de datos en MySQL llamada move_file_process:

CREATE DATABASE move_file_process;

Crea la tabla productos:

CREATE TABLE productos (
    CODBARRA VARCHAR(50) PRIMARY KEY,
    NOMBRE VARCHAR(255),
    PRECIO DECIMAL(10, 2)
);

---

#### Credenciales BD

Cambiar Credenciales de MySQL
Las credenciales de conexión a la base de datos MySQL se encuentran en el archivo app.py. Modifica las siguientes variables según tu configuración:

MYSQL_HOST = 'localhost'  # Cambia si tu base de datos no está en localhost
MYSQL_USER = 'your_user'       # Usuario de MySQL
MYSQL_PASSWORD = 'your_password'  # Contraseña de MySQL
MYSQL_DATABASE = 'move_file_process'  # Nombre de la base de datos
MYSQL_TABLE = 'productos'  # Nombre de la tabla

---

#### ▶️ Ejecución

- Coloca el archivo Excel que deseas procesar en la carpeta OriginFolder/ y asegúrate de que el nombre del archivo coincida con el valor de la variable ARCHIVO_EXCEL en app.py:

ARCHIVO_EXCEL = 'MaestroFamiliasMin.xlsx'

---

#### Notas

- Recursos del sistema: El script verifica que el uso de CPU y memoria esté por debajo de los umbrales configurados (UMBRAL_CPU y UMBRAL_MEMORIA) antes de procesar cada fila.
- Conexión a Internet: El script requiere conexión a internet para continuar con el procesamiento.
- Progreso: Los datos procesados se guardan en el archivo de destino para evitar pérdida de información en caso de interrupciones.

---

#### Personalización

Puedes ajustar los siguientes parámetros en app.py:

- Umbrales de recursos:

UMBRAL_CPU = 70  # Porcentaje máximo de uso de CPU
UMBRAL_MEMORIA = 90  # Porcentaje máximo de uso de memoria

- Tiempo de espera entre iteraciones:

TIEMPO_ESPERA = 0.003  # En segundos
