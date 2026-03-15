import os
import tempfile


def wyodrebnij_audio(plik_video):
    """Wyciąga audio z video i zwraca ścieżkę do pliku mp3."""
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_audio:
        tmp_audio_path = tmp_audio.name

    wynik = os.system(
        f'ffmpeg -i "{plik_video}" -vn -acodec libmp3lame -q:a 4 "{tmp_audio_path}" -y -loglevel quiet'
    )

    if wynik != 0:
        raise Exception("FFmpeg nie mógł przetworzyć pliku video.")

    return tmp_audio_path


def transkrybuj_plik(client, uploaded_file, max_mb=25):
    """
    Transkrybuje plik audio lub video.
    Zwraca tekst transkrypcji lub rzuca wyjątek.
    """
    jest_video = uploaded_file.name.lower().endswith((".mp4", ".webm", ".mov", ".avi"))

    # Zapisz plik tymczasowo
    with tempfile.NamedTemporaryFile(
        suffix=os.path.splitext(uploaded_file.name)[1],
        delete=False
    ) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # Ekstrakcja audio z video
    if jest_video:
        try:
            audio_path = wyodrebnij_audio(tmp_path)
            os.unlink(tmp_path)
            tmp_path = audio_path
        except Exception as e:
            os.unlink(tmp_path)
            raise Exception(f"Błąd ekstrakcji audio: {e}")

    # Sprawdź rozmiar po ekstrakcji
    rozmiar_po = os.path.getsize(tmp_path) / (1024 * 1024)
    if rozmiar_po > max_mb:
        os.unlink(tmp_path)
        raise Exception(f"Audio po ekstrakcji nadal za duże ({rozmiar_po:.1f}MB). Maksimum to {max_mb}MB.")

    # Transkrypcja
    try:
        with open(tmp_path, "rb") as f:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        os.unlink(tmp_path)
        return transcript.text
    except Exception as e:
        os.unlink(tmp_path)
        raise Exception(f"Błąd transkrypcji: {e}")


def transkrybuj_nagranie(client, audio_file):
    """
    Transkrybuje nagranie z mikrofonu.
    Zwraca tekst transkrypcji lub rzuca wyjątek.
    """
    audio_file.seek(0)
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=("nagranie.wav", audio_file, "audio/wav")
    )
    return transcript.text
