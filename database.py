import uuid
from datetime import datetime
from qdrant_client.models import PointStruct


def get_embedding(client, text):
    """Generuje embedding dla podanego tekstu."""
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return res.data[0].embedding


def zapisz_do_qdrant(client, qdrant, collection_name, podsumowanie, transkrypcja, nazwa, podsumowanie_en=""):
    """Zapisuje spotkanie do bazy Qdrant."""
    embedding = get_embedding(client, podsumowanie + "\n" + transkrypcja)
    qdrant.upsert(
        collection_name=collection_name,
        points=[
            PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "podsumowanie": podsumowanie,
                    "podsumowanie_en": podsumowanie_en,
                    "transkrypcja": transkrypcja,
                    "plik": nazwa,
                    "data": datetime.now().isoformat()
                }
            )
        ]
    )


def wyszukaj_w_qdrant(client, qdrant, collection_name, query, limit=5):
    """Wyszukuje spotkania w Qdrant na podstawie zapytania."""
    emb = get_embedding(client, query)
    try:
        # nowe API qdrant-client (>=1.7)
        hits = qdrant.query_points(
            collection_name=collection_name,
            query=emb,
            limit=limit,
            with_payload=True
        ).points
    except AttributeError:
        # fallback na starsze wersje
        hits = qdrant.search(
            collection_name=collection_name,
            query_vector=emb,
            limit=limit,
            with_payload=True
        )
    return hits


def pobierz_wszystkie(qdrant, collection_name, limit=100):
    """Pobiera wszystkie spotkania z Qdrant, posortowane od najnowszych."""
    wyniki = qdrant.scroll(
        collection_name=collection_name,
        limit=limit,
        with_payload=True,
        with_vectors=False
    )
    notatki = sorted(
        wyniki[0],
        key=lambda x: x.payload.get("data", ""),
        reverse=True
    )
    return notatki


def napraw_brakujace_en(client, qdrant, collection_name):
    """Tłumaczy i uzupełnia brakujące podsumowania EN w Qdrant."""
    wyniki = qdrant.scroll(
        collection_name=collection_name,
        limit=100,
        with_payload=True,
        with_vectors=False
    )

    naprawiono = 0
    for n in wyniki[0]:
        p = n.payload
        if p.get("podsumowanie_en"):
            continue

        response_en = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Translate this meeting summary to professional English."
                },
                {
                    "role": "user",
                    "content": p.get("podsumowanie", "")
                }
            ]
        )
        podsumowanie_en = response_en.choices[0].message.content

        qdrant.set_payload(
            collection_name=collection_name,
            payload={"podsumowanie_en": podsumowanie_en},
            points=[n.id]
        )
        naprawiono += 1

    return naprawiono
