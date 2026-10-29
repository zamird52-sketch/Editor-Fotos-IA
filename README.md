---
title: Separan Voces
emoji: 🎙️
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# Separan Voces

Aplicación personal en español para separar una canción en **voz** e **instrumental**, escuchar cada pista por separado y descargar los WAV.

## Ponerla en línea desde el celular

Este repositorio ya incluye la configuración Docker para un **Hugging Face Docker Space**.

1. En Hugging Face, creá un **Space** nuevo y elegí **Docker** como SDK.
2. En la configuración del Space, importá/subí los archivos de este repositorio (`index.html`, `app.py`, `requirements.txt`, `Dockerfile` y este `README.md`).
3. Esperá a que termine la construcción y abrí la pestaña **App**.

No hace falta entrenar un modelo ni pagar créditos por canción: usa el modelo abierto Demucs. **Importante:** el alojamiento gratuito puede dormir, limitar recursos o cambiar sus condiciones; no existe garantía de procesamiento ilimitado y gratis para siempre. La primera separación puede tardar bastante en CPU y el modelo necesita memoria.

## Qué incluye

- Interfaz web adaptable a celular.
- Separación con Demucs (`htdemucs`).
- Reproductores independientes para voz e instrumental.
- Descarga de ambos resultados en WAV.
- API FastAPI y endpoint de estado en `/api/health`.

## Ejecutar con Docker en una computadora

```bash
docker build -t separan-voces .
docker run --rm -p 7860:7860 -v separan-voces-output:/app/outputs separan-voces
```

Abrí `http://localhost:7860`.

## Configuración

- `MAX_UPLOAD_MB`: tamaño máximo de archivo (por defecto 100).
- `DEMUCS_MODEL`: modelo Demucs (por defecto `htdemucs`).
- `PROCESS_TIMEOUT_SECONDS`: tiempo máximo por tarea (por defecto 1800).

## Privacidad

El audio se procesa en el servidor donde esté alojada la app. No subas archivos privados a una instancia pública. Los archivos de salida quedan en el almacenamiento del servidor; esta versión todavía no incorpora limpieza automática ni acceso protegido, así que mantené el Space privado para uso personal cuando esa opción esté disponible. Procesá solamente audio que tengas derecho a usar.