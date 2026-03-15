import streamlit as st
from dotenv import load_dotenv
from datetime import datetime

# --- importy własnych modułów ---
from config import init_openai, init_qdrant
from audio import transkrybuj_plik, transkrybuj_nagranie
from summarizer import generuj_podsumowanie, tlumacz_na_angielski
from database import zapisz_do_qdrant, wyszukaj_w_qdrant, pobierz_wszystkie, napraw_brakujace_en
from documents import generuj_docx_pl, generuj_docx_en, pobierz_wszystkie_jako_docx

load_dotenv()

# ====================================================
# KONFIGURACJA STRONY
# ====================================================

st.set_page_config(
    page_title="MeeetingSum",
    page_icon="uplogo.png",
    layout="centered"
)

# ====================================================
# INICJALIZACJA POŁĄCZEŃ
# ====================================================

client = init_openai()
qdrant, COLLECTION_NAME, qdrant_ok = init_qdrant()

MAX_MB = 25
MAX_MB_VIDEO = 500

# ====================================================
# SESSION STATE
# ====================================================

def reset_sesji():
    st.session_state.transkrypcja = None
    st.session_state.podsumowanie = None
    st.session_state.podsumowanie_en = None
    st.session_state.zapisano_qdrant = False

if "transkrypcja" not in st.session_state:
    st.session_state.transkrypcja = None
if "podsumowanie" not in st.session_state:
    st.session_state.podsumowanie = None
if "podsumowanie_en" not in st.session_state:
    st.session_state.podsumowanie_en = None
if "nazwa_pliku" not in st.session_state:
    st.session_state.nazwa_pliku = None
if "zapisano_qdrant" not in st.session_state:
    st.session_state.zapisano_qdrant = False
if "poprzedni_plik" not in st.session_state:
    st.session_state.poprzedni_plik = None

# ====================================================
# NAGŁÓWEK
# ====================================================

col_tytul, col_logo = st.columns([3, 1])

with col_tytul:
    st.markdown("""
        <style>
            .tytul {
                font-size: 55px;
                font-weight: bold;
                font-family: 'Verdana', sans-serif;
                color: #2C3E50;
                line-height: 1.1;
                margin-bottom: 0px;
            }
            .podtytul {
                font-size: 22px;
                font-weight: normal;
                font-family: 'Verdana', sans-serif;
                color: #5D6D7E;
                margin-top: 0px;
                margin-bottom: 4px;
            }
            .powered {
                font-size: 14px;
                font-family: 'Verdana', sans-serif;
                color: #AAB7B8;
                margin-top: 0px;
            }
        </style>
        <p class="tytul">MeeetingSum</p>
        <p class="podtytul">Podsumowanie spotkań AI</p>
        <p class="powered">Powered by KarmelCodeLab</p>
    """, unsafe_allow_html=True)

with col_logo:
    st.image("logo.png", width=150)

# ====================================================
# ZAKŁADKI GŁÓWNE
# ====================================================

tab1, tab2 = st.tabs(["Audio / Video", "Baza spotkań"])

# ====================================================
# TAB 1 — AUDIO / VIDEO
# ====================================================

with tab1:

    upload, record = st.tabs(["Wgraj plik", "Nagraj"])

    # ---------- UPLOAD ----------
    with upload:

        uploaded_file = st.file_uploader(
            "Wgraj plik audio lub video",
            type=["mp3", "wav", "m4a", "mp4", "webm", "mov", "avi"]
        )

        if uploaded_file:

            if uploaded_file.name != st.session_state.poprzedni_plik:
                reset_sesji()
                st.session_state.poprzedni_plik = uploaded_file.name

            rozmiar_mb = uploaded_file.size / (1024 * 1024)
            jest_video = uploaded_file.name.lower().endswith((".mp4", ".webm", ".mov", ".avi"))
            limit = MAX_MB_VIDEO if jest_video else MAX_MB

            if rozmiar_mb > limit:
                st.error(f"Plik za duży ({rozmiar_mb:.1f}MB). Maksimum to {limit}MB.")
            else:
                st.caption(f"Rozmiar: {rozmiar_mb:.1f}MB")
                if not jest_video:
                    st.audio(uploaded_file)

                if jest_video:
                    st.info("📹 Wykryto plik video — audio zostanie automatycznie wyodrębnione przed transkrypcją.")

                if st.button("Transkrybuj plik", key="transkrybuj_plik"):
                    try:
                        if jest_video:
                            with st.spinner("Wyodrębniam audio z video (może chwilę potrwać)..."):
                                tekst = transkrybuj_plik(client, uploaded_file, MAX_MB)
                        else:
                            with st.spinner("Transkrybuję..."):
                                tekst = transkrybuj_plik(client, uploaded_file, MAX_MB)

                        st.session_state.transkrypcja = tekst
                        st.session_state.nazwa_pliku = uploaded_file.name
                        st.success("Transkrypcja gotowa!")

                    except Exception as e:
                        st.error(str(e))

    # ---------- NAGRAJ ----------
    with record:
        st.write("Nagrywanie w przeglądarce")

        audio_file = st.audio_input("Nagraj notatkę")

        if audio_file is None:
            st.info("Brak nagrania – kliknij mikrofon, powiedz kilka sekund i zatrzymaj.")
        else:
            st.audio(audio_file)

            if st.button("Transkrybuj nagranie", key="transkrybuj_nagranie_webrtc"):
                try:
                    with st.spinner("Transkrybuję..."):
                        tekst = transkrybuj_nagranie(client, audio_file)
                    st.session_state.transkrypcja = tekst
                    st.session_state.nazwa_pliku = "nagranie"
                    st.success("Transkrypcja gotowa.")
                except Exception as e:
                    st.error(f"Błąd transkrypcji: {e}")

    # ====================================================
    # TRANSKRYPCJA I PODSUMOWANIE
    # ====================================================

    if st.session_state.transkrypcja:

        with st.expander("Pokaż transkrypcję"):
            st.text_area("Transkrypcja", st.session_state.transkrypcja, height=300)

        st.caption(f"Długość: {len(st.session_state.transkrypcja)} znaków")

        if st.button("Generuj podsumowanie", key="generuj_podsumowanie"):
            try:
                with st.spinner("Generuję podsumowanie..."):
                    st.session_state.podsumowanie = generuj_podsumowanie(
                        client, st.session_state.transkrypcja
                    )

                with st.spinner("Tłumaczę na angielski..."):
                    st.session_state.podsumowanie_en = tlumacz_na_angielski(
                        client, st.session_state.podsumowanie
                    )

                st.session_state.zapisano_qdrant = False

            except Exception as e:
                st.error(f"Błąd generowania podsumowania: {e}")

    if st.session_state.podsumowanie:

        st.subheader("Podsumowanie (PL)")
        st.write(st.session_state.podsumowanie)

        st.subheader("Summary (EN)")
        st.write(st.session_state.podsumowanie_en)

        teraz = datetime.now().strftime("%Y-%m-%d_%H-%M")

        col1, col2, col3 = st.columns(3)

        with col1:
            if not qdrant_ok:
                st.warning("Brak połączenia z bazą")
            elif st.session_state.zapisano_qdrant:
                st.success("Zapisano w bazie!")
            else:
                if st.button("Zapisz w bazie", key="zapisz_baza_main"):
                    try:
                        with st.spinner("Zapisuję..."):
                            zapisz_do_qdrant(
                                client,
                                qdrant,
                                COLLECTION_NAME,
                                st.session_state.podsumowanie,
                                st.session_state.transkrypcja,
                                st.session_state.nazwa_pliku,
                                st.session_state.podsumowanie_en
                            )
                        st.session_state.zapisano_qdrant = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Błąd zapisu do bazy: {e}")

        with col2:
            buf_pl = generuj_docx_pl(
                st.session_state.podsumowanie,
                st.session_state.transkrypcja,
                st.session_state.nazwa_pliku
            )
            st.download_button(
                "Pobierz PL",
                buf_pl,
                file_name=f"spotkanie_{teraz}_PL.docx",
                key="pobierz_pl"
            )

        with col3:
            buf_en = generuj_docx_en(st.session_state.podsumowanie_en)
            st.download_button(
                "Pobierz EN",
                buf_en,
                file_name=f"meeting_{teraz}_EN.docx",
                key="pobierz_en"
            )

# ====================================================
# TAB 2 — BAZA SPOTKAŃ
# ====================================================

with tab2:

    st.subheader("Pobierz wszystkie spotkania")

    if qdrant_ok:
        teraz = datetime.now().strftime("%Y-%m-%d_%H-%M")
        col_dl1, col_dl2 = st.columns(2)

        with col_dl1:
            try:
                buf_all_pl = pobierz_wszystkie_jako_docx(qdrant, COLLECTION_NAME, jezyk="PL")
                st.download_button(
                    "📥 Pobierz wszystkie (PL)",
                    buf_all_pl,
                    file_name=f"wszystkie_spotkania_PL_{teraz}.docx",
                    key="pobierz_wszystkie_pl"
                )
            except Exception as e:
                st.error(f"Błąd generowania pliku: {e}")

        with col_dl2:
            try:
                buf_all_en = pobierz_wszystkie_jako_docx(qdrant, COLLECTION_NAME, jezyk="EN")
                st.download_button(
                    "📥 Pobierz wszystkie (EN)",
                    buf_all_en,
                    file_name=f"all_meetings_EN_{teraz}.docx",
                    key="pobierz_wszystkie_en"
                )
            except Exception as e:
                st.error(f"Błąd generowania pliku: {e}")

        st.divider()

        # Naprawa brakujących tłumaczeń EN
        if st.button("🔧 Napraw brakujące tłumaczenia EN", key="migracja_en"):
            try:
                with st.spinner("Tłumaczę brakujące podsumowania..."):
                    naprawiono = napraw_brakujace_en(client, qdrant, COLLECTION_NAME)
                st.success(f"Naprawiono {naprawiono} rekordów!")
            except Exception as e:
                st.error(f"Błąd migracji: {e}")

    st.divider()
    st.subheader("Wyszukaj spotkania")

    if not qdrant_ok:
        st.error("Brak połączenia z Qdrant.")
    else:
        query = st.text_input("Wpisz temat")

        if query:
            try:
                with st.spinner("Szukam..."):
                    hits = wyszukaj_w_qdrant(client, qdrant, COLLECTION_NAME, query)

                if hits:
                    for h in hits:
                        p = h.payload
                        trafnosc = round(h.score * 100, 1)
                        data = p.get("data", "brak daty")[:16]
                        plik = p.get("plik", "brak nazwy")
                        with st.expander(f"{data} — {plik} (trafność: {trafnosc}%)"):
                            st.write(p.get("podsumowanie", "brak podsumowania"))
                else:
                    st.info("Brak wyników.")
            except Exception as e:
                st.error(f"Błąd wyszukiwania: {e}")

        st.divider()
        st.subheader("Wszystkie spotkania")

        if st.button("Załaduj wszystkie", key="zaladuj_wszystkie"):
            try:
                notatki = pobierz_wszystkie(qdrant, COLLECTION_NAME)

                if notatki:
                    for n in notatki:
                        p = n.payload
                        data = p.get("data", "brak daty")[:16]
                        plik = p.get("plik", "brak nazwy")
                        with st.expander(f"{data} — {plik}"):
                            st.write(p.get("podsumowanie", "brak podsumowania"))
                else:
                    st.info("Brak zapisanych spotkań.")

            except Exception as e:
                st.error(f"Błąd ładowania: {e}")
