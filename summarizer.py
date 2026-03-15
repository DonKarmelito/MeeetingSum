def generuj_podsumowanie(client, transkrypcja):
    """Generuje podsumowanie spotkania po polsku."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Stwórz krótkie podsumowanie spotkania. Wypisz tematy, decyzje i zadania."
            },
            {
                "role": "user",
                "content": transkrypcja
            }
        ]
    )
    return response.choices[0].message.content


def tlumacz_na_angielski(client, podsumowanie_pl):
    """Tłumaczy podsumowanie z polskiego na angielski."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Translate this meeting summary to professional English."
            },
            {
                "role": "user",
                "content": podsumowanie_pl
            }
        ]
    )
    return response.choices[0].message.content
