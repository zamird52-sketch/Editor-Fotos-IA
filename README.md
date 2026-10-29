---
title: Separan Voces
emoji: 🎙️
colorFrom: purple
colorTo: blue
sdk: gradio
app_file: app.py
pinned: false
---

# Separan Voces

Aplicación web en español para separar una canción en **voz aislada** y **beat/instrumental**, escuchar cada pista y descargarla en WAV.

## Cómo funciona

- Interfaz adaptable a celulares con Gradio.
- Usa Demucs (htdemucs) para separar voz e instrumental.
- Usa GPU compartida ZeroGPU de Hugging Face mediante el decorador spaces.GPU.

## Publicación

Este repositorio está preparado para usarse como **Gradio Space con ZeroGPU**. Para obtener un enlace público hay que crear un Space en una cuenta de Hugging Face elegible y subir/sincronizar estos archivos.

1. Entrá a https://huggingface.co/new-space
2. Elegí el nombre separan-voces, SDK **Gradio** y hardware **ZeroGPU**.
3. Subí app.py, requirements.txt y este README.md.
4. Esperá la construcción; después abrí la pestaña App.

**Nota:** las cuentas personales gratuitas deben cumplir los requisitos de Hugging Face para alojar ZeroGPU Spaces (cuenta con más de 30 días y correo verificado). La cuota gratuita de GPU es limitada; no es procesamiento ilimitado. Ver https://huggingface.co/docs/hub/spaces-zerogpu

## Privacidad

El audio se envía al Space para procesarlo. No subas archivos que no tengas derecho a procesar.
