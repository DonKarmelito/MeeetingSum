# MeeetingSum 🎙️

**Aplikacja do automatycznego podsumowywania spotkań przy użyciu AI.**

Wgraj lub nagraj plik audio/video ze spotkania, a aplikacja automatycznie wygeneruje transkrypcję i podsumowanie w języku polskim oraz angielskim. Podsumowania są zapisywane w bazie wektorowej Qdrant i można je wyszukiwać semantycznie.

> Powered by KarmelCodeLab

---

## Spis treści

- [Funkcje](#funkcje)
- [Technologie](#technologie)
- [Struktura projektu](#struktura-projektu)
- [Instalacja lokalna](#instalacja-lokalna)
- [Wdrożenie na Streamlit Cloud](#wdrożenie-na-streamlit-cloud)
- [Jak używać aplikacji](#jak-używać-aplikacji)
- [Opis modułów](#opis-modułów)
- [Zmienne środowiskowe](#zmienne-środowiskowe)
- [Limity i ograniczenia](#limity-i-ograniczenia)
- [Rozwiązywanie problemów](#rozwiązywanie-problemów)

---

## Funkcje

- **Transkrypcja audio** — obsługa plików MP3, WAV, M4A
- **Transkrypcja video** — automatyczna ekstrakcja audio z MP4, WebM, MOV, AVI przed transkrypcją
- **Nagrywanie w przeglądarce** — wbudowany rejestrator mikrofonu
- **Podsumowanie AI** — automatyczne generowanie podsumowania spotkania (tematy, decyzje, zadania)
- **Tłumaczenie EN** — automatyczne tłumaczenie podsumowania na angielski
- **Eksport do Word** — pobieranie notatki jako plik .docx (PL i EN)
- **Baza spotkań** — zapisywanie i wyszukiwanie semantyczne wszystkich spotkań w Qdrant
- **Pobieranie historii** — generowanie zbiorczego pliku Word ze wszystkich spotkań

---

## Technologie

| Technologia | Zastosowanie |
|---|---|
| [Streamlit](https://streamlit.io) | Interfejs użytkownika |
| [OpenAI Whisper](https://openai.com/research/whisper) | Transkrypcja audio |
| [OpenAI GPT-4o-mini](https://openai.com/gpt-4) | Generowanie podsumowań i tłumaczenia |
| [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings) | Wektoryzacja tekstu |
| [Qdrant](https://qdrant.tech) | Baza wektorowa (przechowywanie i wyszukiwanie spotkań) |
| [FFmpeg](https://ffmpeg.org) | Ekstrakcja audio z plików video |
| [python-docx](https://python-docx.readthedocs.io) | Generowanie plików Word |

---

## Struktura projektu

```
meetingsum/
│
├── app.py            # Główny plik — interfejs użytkownika (Streamlit)
├── config.py         # Inicjalizacja połączeń (OpenAI, Qdrant), obsługa sekretów
├── audio.py          # Transkrypcja plików audio i video, ekstrakcja audio z video
├── summarizer.py     # Generowanie podsumowań PL i tłumaczenie na EN
├── database.py       # Operacje na bazie Qdrant (zapis, wyszukiwanie, pobieranie)
├── documents.py      # Generowanie plików Word (.docx)
│
├── logo.png          # Logo wyświetlane w aplikacji
├── uplogo.png        # Ikona zakładki przeglądarki (favicon)
│
├── requirements.txt  # Zależności Pythona
├── packages.txt      # Pakiety systemowe (FFmpeg dla Streamlit Cloud)
├── .env              # Klucze API (tylko lokalnie, NIE wgrywać na GitHub!)
└── .gitignore        # Pliki ignorowane przez Git
```

---

## Instalacja lokalna

### Wymagania wstępne

- Python 3.9+
- Conda lub venv
- FFmpeg zainstalowany w systemie
- Konto OpenAI z kluczem API
- Konto Qdrant Cloud (lub lokalna instancja Qdrant)

### Krok 1 — Sklonuj repozytorium

```bash
git clone https://github.com/TwojaNazwa/MeeetingSum.git
cd MeeetingSum
```

### Krok 2 — Utwórz środowisko i zainstaluj zależności

```bash
conda create -n app_meetingsum python=3.11
conda activate app_meetingsum
pip install -r requirements.txt
```

### Krok 3 — Zainstaluj FFmpeg

**Windows:**
```bash
winget install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg
```

### Krok 4 — Utwórz plik `.env`

Utwórz plik `.env` w folderze projektu:

```env
OPENAI_API_KEY=sk-...
QDRANT_URL=https://twoj-klaster.qdrant.io
QDRANT_API_KEY=twoj-klucz-qdrant
```

### Krok 5 — Uruchom aplikację

```bash
streamlit run app.py
```

Aplikacja otworzy się automatycznie w przeglądarce pod adresem `http://localhost:8501`.

---

## Wdrożenie na Streamlit Cloud

### Krok 1 — Przygotuj repozytorium GitHub

Upewnij się że w repozytorium znajdują się pliki:
- `requirements.txt`
- `packages.txt` (z zawartością `ffmpeg`)
- Wszystkie pliki `.py`
- `logo.png` i `uplogo.png`
- **NIE wgrywaj** pliku `.env` — dodaj go do `.gitignore`

### Krok 2 — Dodaj sekrety w Streamlit Cloud

1. Wejdź na [share.streamlit.io](https://share.streamlit.io)
2. Znajdź aplikację → kliknij **⋮** → **Settings**
3. Zakładka **Secrets**
4. Wklej:

```toml
OPENAI_API_KEY = "sk-..."
QDRANT_URL = "https://twoj-klaster.qdrant.io"
QDRANT_API_KEY = "twoj-klucz-qdrant"
```

5. Kliknij **Save**

### Krok 3 — Wdróż

```bash
git add .
git commit -m "Deploy"
git push
```

Streamlit Cloud automatycznie wykryje zmiany i zrestartuje aplikację.

---

## Jak używać aplikacji

### Zakładka „Audio / Video"

#### Wgrywanie pliku

1. Wybierz zakładkę **Wgraj plik**
2. Kliknij **Browse files** i wybierz plik audio lub video
3. Kliknij **Transkrybuj plik**
   - Dla plików video aplikacja automatycznie wyodrębni audio (może potrwać chwilę)
4. Po zakończeniu transkrypcji kliknij **Generuj podsumowanie**
5. Poczekaj na wygenerowanie podsumowania PL i tłumaczenia EN
6. Wybierz co zrobić z wynikiem:
   - **Zapisz w bazie** — zapisuje do Qdrant (umożliwia późniejsze wyszukiwanie)
   - **Pobierz PL** — pobiera plik Word z podsumowaniem i transkrypcją po polsku
   - **Pobierz EN** — pobiera plik Word z podsumowaniem po angielsku

#### Nagrywanie

1. Wybierz zakładkę **Nagraj**
2. Kliknij ikonę mikrofonu i nagraj notatkę
3. Kliknij **Transkrybuj nagranie**
4. Dalej tak samo jak przy wgrywaniu pliku

### Zakładka „Baza spotkań"

- **Pobierz wszystkie (PL/EN)** — generuje zbiorczy plik Word ze wszystkimi zapisanymi spotkaniami
- **Wyszukaj spotkania** — wpisz temat aby znaleźć semantycznie podobne spotkania z historii
- **Załaduj wszystkie** — wyświetla listę wszystkich spotkań z bazy

---

## Opis modułów

### `app.py`
Główny plik aplikacji. Zawiera wyłącznie kod interfejsu użytkownika (Streamlit). Importuje funkcje ze wszystkich pozostałych modułów. Zarządza stanem sesji (`st.session_state`).

### `config.py`
Odpowiada za inicjalizację połączeń z zewnętrznymi serwisami. Zawiera funkcję `get_secret()` która czyta klucze API z pliku `.env` lokalnie lub z `st.secrets` na Streamlit Cloud. Inicjalizuje klientów OpenAI i Qdrant.

### `audio.py`
Obsługuje wszystko związane z dźwiękiem:
- `wyodrebnij_audio()` — używa FFmpeg do wyciągnięcia ścieżki audio z pliku video
- `transkrybuj_plik()` — transkrybuje przesłany plik (audio lub video) przez Whisper API
- `transkrybuj_nagranie()` — transkrybuje nagranie z mikrofonu przez Whisper API

### `summarizer.py`
Obsługuje generowanie treści przez GPT-4o-mini:
- `generuj_podsumowanie()` — tworzy podsumowanie spotkania po polsku (tematy, decyzje, zadania)
- `tlumacz_na_angielski()` — tłumaczy podsumowanie na profesjonalny angielski

### `database.py`
Wszystkie operacje na bazie Qdrant:
- `get_embedding()` — generuje wektor tekstu przez OpenAI Embeddings
- `zapisz_do_qdrant()` — zapisuje spotkanie (podsumowanie PL, EN, transkrypcja, nazwa pliku, data)
- `wyszukaj_w_qdrant()` — wyszukuje semantycznie podobne spotkania
- `pobierz_wszystkie()` — zwraca wszystkie spotkania posortowane od najnowszych

### `documents.py`
Generuje pliki Word (.docx) w pamięci (bez zapisywania na dysk):
- `generuj_docx_pl()` — notatka z jednego spotkania po polsku (podsumowanie + transkrypcja)
- `generuj_docx_en()` — notatka z jednego spotkania po angielsku
- `pobierz_wszystkie_jako_docx()` — zbiorczy plik ze wszystkich spotkań z Qdrant (PL lub EN)

---

## Zmienne środowiskowe

| Zmienna | Opis | Gdzie uzyskać |
|---|---|---|
| `OPENAI_API_KEY` | Klucz API OpenAI | [platform.openai.com](https://platform.openai.com/api-keys) |
| `QDRANT_URL` | URL klastra Qdrant | [cloud.qdrant.io](https://cloud.qdrant.io) |
| `QDRANT_API_KEY` | Klucz API Qdrant | Panel Qdrant Cloud |

---

## Limity i ograniczenia

| Limit | Wartość | Powód |
|---|---|---|
| Maksymalny rozmiar pliku audio | 25 MB | Limit Whisper API |
| Maksymalny rozmiar pliku video | 500 MB | Limit wgrywania Streamlit |
| Maksymalna liczba spotkań w bazie | 100 (na jedno zapytanie) | Domyślny limit scroll Qdrant |
| Model transkrypcji | Whisper-1 | OpenAI |
| Model podsumowań | GPT-4o-mini | OpenAI |
| Model embeddingów | text-embedding-3-small (1536 dim) | OpenAI |

> **Uwaga:** Pliki na Streamlit Cloud są efemeryczne — znikają po restarcie aplikacji. Dlatego wszystkie dane są przechowywane w Qdrant, a pliki Word generowane są dynamicznie na żądanie.

---

## Rozwiązywanie problemów

### „Brak połączenia z Qdrant"
- Sprawdź czy `QDRANT_URL` i `QDRANT_API_KEY` są poprawnie ustawione
- Lokalnie: sprawdź plik `.env`
- Na Streamlit Cloud: sprawdź **Settings → Secrets**

### „FFmpeg nie mógł przetworzyć pliku video"
- Lokalnie: upewnij się że FFmpeg jest zainstalowany (`ffmpeg -version`)
- Na Streamlit Cloud: upewnij się że plik `packages.txt` zawiera linię `ffmpeg`

### „Audio po ekstrakcji nadal za duże"
- Plik video zawiera bardzo długie nagranie lub audio wysokiej jakości
- Rozwiązanie: skróć nagranie lub zmniejsz jego jakość przed wgraniem

### Puste podsumowanie EN w pobranym pliku zbiorczym
- Starsze spotkania zapisane przed naprawą kodu nie mają pola `podsumowanie_en`
- Rozwiązanie: użyj przycisku **🔧 Napraw brakujące tłumaczenia EN** w zakładce Baza spotkań

### Zakładka „Baza spotkań" jest pusta
- Upewnij się że połączenie z Qdrant działa poprawnie
- Sprawdź czy masz zapisane jakieś spotkania (przycisk **Załaduj wszystkie**)
