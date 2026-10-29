# Separan Voces

Aplicación web en español para subir una canción, separar voz e instrumental con IA, escuchar ambas pistas en reproductores independientes y descargar los archivos WAV.

## Cómo funciona

- Interfaz web responsiva en `index.html`.
- API en FastAPI.
- Separación de dos pistas mediante Demucs (`htdemucs`).
- Reproductores independientes para voz e instrumental.
- Descargas en WAV.

## Ejecutar con Docker

Requiere Docker instalado. En la carpeta del proyecto:

```bash
docker build -t separan-voces .
docker run --rm -p 8000:8000 -v separan-voces-output:/app/outputs separan-voces
```

Abrí http://localhost:8000. La primera separación puede tardar porque Demucs descarga el modelo si no está en caché. La inferencia puede ser lenta y consumir memoria; una GPU compatible mejora el rendimiento.

## Ejecutar localmente

Necesitás Python 3.11 y FFmpeg:

```bash
pip install -r requirements.txt
python app.py
```

Luego abrí http://localhost:8000.

## Configuración

- `MAX_UPLOAD_MB`: tamaño máximo del archivo (por defecto 100).
- `DEMUCS_MODEL`: modelo Demucs (por defecto `htdemucs`).
- `PROCESS_TIMEOUT_SECONDS`: tiempo máximo por tarea (por defecto 1800).

## Importante para desplegar

Esta app necesita un servidor Python con FFmpeg y Demucs; no alcanza con publicar únicamente el HTML como sitio estático. Los archivos generados se guardan en `outputs/`. Para un servicio público, configurá limpieza periódica de archivos, límites de uso y almacenamiento adecuado.

## Privacidad

Los audios subidos se procesan en el servidor que aloja la aplicación. No subas material sensible a una instancia pública. Usá únicamente audio que tengas derecho a procesar.
