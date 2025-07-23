# --- Etapa 1: Imagen Base ---
# Usamos una imagen oficial de Python. Las versiones 'slim' son más ligeras.
# Se recomienda usar una versión específica (ej. 3.10) para compilaciones consistentes.
FROM python:3.12-slim

# --- Configuración del Entorno ---
# Evita que Python genere archivos .pyc, que no son necesarios en un contenedor.
ENV PYTHONDONTWRITEBYTECODE 1
# Asegura que la salida de Python se envíe directamente a la terminal sin búfer.
ENV PYTHONUNBUFFERED 1

# Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# --- Instalación de Dependencias ---
# Copiamos primero el archivo de requerimientos para aprovechar el caché de capas de Docker.
# De esta forma, las dependencias solo se reinstalarán si `requirements.txt` cambia.
COPY requirements.txt .

# Instala las dependencias de Python.
# --no-cache-dir reduce el tamaño de la imagen.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Copia del Código de la Aplicación ---
# Copia el resto del código de tu aplicación al directorio de trabajo.
# (Se recomienda usar un archivo .dockerignore para excluir archivos innecesarios).
COPY . .

# --- Seguridad: Ejecutar como usuario no-root ---
# Crea un usuario y grupo específicos para ejecutar la aplicación.
RUN addgroup --system app && adduser --system --group app
# Cambia al usuario no-root.
USER app

# --- Ejecución de la Aplicación ---
# Expone el puerto que usará la aplicación.
EXPOSE 8000

# Comando para iniciar el servidor Uvicorn.
# Asegúrate de que tu archivo principal se llame 'main.py' y la instancia de FastAPI se llame 'app'.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
