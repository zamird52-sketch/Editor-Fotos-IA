import os
import tempfile
from pathlib import Path

import gradio as gr
import spaces

MODEL_NAME = os.getenv("DEMUCS_MODEL", "htdemucs")


@spaces.GPU(duration=300)
def separate_song(audio_path):
    if not audio_path:
        raise gr.Error("Primero elegí una canción.")
    allowed = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac", ".mp4"}
    if Path(audio_path).suffix.lower() not in allowed:
        raise gr.Error("Formato no compatible. Probá MP3, WAV, FLAC, M4A u OGG.")

    import torch
    import torchaudio
    from demucs.apply import apply_model
    from demucs.pretrained import get_model
    from demucs.audio import convert_audio

    try:
        model = get_model(MODEL_NAME)
        device = "cuda"
        model.to(device)
        wav, sample_rate = torchaudio.load(audio_path)
        reference = wav.mean(0)
        wav = (wav - reference.mean()) / (reference.std() + 1e-8)
        wav = convert_audio(wav, sample_rate, model.samplerate, model.audio_channels)
        with torch.inference_mode():
            sources = apply_model(
                model, wav[None], device=device, shifts=1,
                split=True, overlap=0.25, progress=True
            )[0]
        sources = sources * reference.std() + reference.mean()
        vocal_index = model.sources.index("vocals")
        vocals = sources[vocal_index].cpu()
        instrumental = (sources.sum(dim=0) - sources[vocal_index]).cpu()

        output_dir = tempfile.mkdtemp(prefix="separan-voces-")
        vocal_path = os.path.join(output_dir, "voz-aislada.wav")
        instrumental_path = os.path.join(output_dir, "beat-instrumental.wav")
        torchaudio.save(vocal_path, vocals, model.samplerate)
        torchaudio.save(instrumental_path, instrumental, model.samplerate)
        del model, sources
        torch.cuda.empty_cache()
        return vocal_path, instrumental_path, vocal_path, instrumental_path, "¡Listo! Escuchá o descargá cada pista."
    except gr.Error:
        raise
    except Exception as exc:
        raise gr.Error(f"No se pudo separar el audio: {str(exc)[:400]}") from exc


with gr.Blocks(title="Separan Voces", theme=gr.themes.Soft()) as demo:
    gr.Markdown(
        "# 🎙️ Separan Voces\n"
        "Subí una canción y obtené **la voz aislada** y **el beat/instrumental** por separado."
    )
    song = gr.Audio(label="Tu canción", type="filepath", sources=["upload"])
    separate_button = gr.Button("Separar voz y beat", variant="primary")
    status = gr.Markdown()
    with gr.Row():
        with gr.Column():
            voice_audio = gr.Audio(label="🎤 Voz aislada", type="filepath")
            voice_file = gr.File(label="Descargar voz (WAV)")
        with gr.Column():
            instrumental_audio = gr.Audio(label="🥁 Beat / instrumental", type="filepath")
            instrumental_file = gr.File(label="Descargar instrumental (WAV)")
    separate_button.click(
        fn=separate_song,
        inputs=[song],
        outputs=[voice_audio, instrumental_audio, voice_file, instrumental_file, status],
    )
    gr.Markdown(
        "El procesamiento usa Demucs en una GPU compartida. La disponibilidad y el tiempo "
        "pueden variar según la cuota gratuita del servicio."
    )

if __name__ == "__main__":
    demo.launch()
