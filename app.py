import random
import uuid
import math

import matplotlib.pyplot as plt
import requests
import streamlit as st


GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyqa0OpJ9XYZ_3Tr22DdcsQNzSwYiUT_Swx0u_lGL47NXmT8xDs1Td4A4qctICr80smyQ/exec"


st.set_page_config(
    page_title="Pilotstudie – Stochastische BATNA",
    page_icon="🏠",
    layout="centered",
)


PRICE_POINTS = [850, 925, 975, 1000, 1025, 1075, 1150]


STIMULI = {
    "eng": {
        "title": "Stochastischer BATNA",
        "intro_text": """Stell dir folgende Situation vor:

Du beginnst in zwei Wochen ein sechsmonatiges Pflichtpraktikum in Frankfurt am Main und verdienst in dieser Zeit 1.750 € netto pro Monat.

Da du nicht in Frankfurt wohnst, brauchst du für diese sechs Monate eine eigene 1-Zimmer-Wohnung. Du hast bereits eine perfekte Wohnung gefunden – WOHNUNG A:

Der Vermieter macht dir gleich ein Angebot. Du kannst Wohnung A direkt annehmen oder ablehnen und auf eine andere ähnliche Wohnung warten. Diese alternativen Angebote nennen wir WOHNUNG B.""",
        "distribution_text": """Die Preise vergleichbarer Wohnungen liegen meist dicht beieinander. Die meisten Angebote bewegen sich um 1.000 € pro Monat. Größere Abweichungen nach oben oder unten sind selten.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen verteilt sind:""",
        "check_correct": "a",
        "mu": 1000,
        "sigma": 50,
    },
    "breit": {
        "title": "Stochastischer BATNA",
        "intro_text": """Stell dir folgende Situation vor:

Du beginnst in zwei Wochen ein sechsmonatiges Pflichtpraktikum in Frankfurt am Main und verdienst in dieser Zeit 1.750 € netto pro Monat.

Da du nicht in Frankfurt wohnst, brauchst du für diese sechs Monate eine eigene 1-Zimmer-Wohnung. Du hast bereits eine perfekte Wohnung gefunden – WOHNUNG A:

Der Vermieter macht dir gleich ein Angebot. Du kannst Wohnung A direkt annehmen oder ablehnen und auf eine andere ähnliche Wohnung warten. Diese alternativen Angebote nennen wir WOHNUNG B.""",
        "distribution_text": """Die Preise vergleichbarer Wohnungen schwanken stärker. Die Angebote liegen weiterhin im Durchschnitt bei etwa 1.000 € pro Monat, können aber deutlich günstiger oder deutlich teurer ausfallen.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen verteilt sind:""",
        "check_correct": "b",
        "mu": 1000,
        "sigma": 150,
    },
}


def init_state():
    defaults = {
        "phase": "welcome",
        "condition": None,
        "price_order": [],
        "price_index": 0,
        "responses": {},
        "demographics": {},
        "risk_attitude": None,
        "participant_id": None,
        "submission_id": None,
        "already_saved": False,
        "manipulation_answer": None,
        "manipulation_result": None,
        "save_status": None,
        "save_error": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_study():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_state()


def generate_price_order():
    prices = PRICE_POINTS[:]
    random.shuffle(prices)
    return prices


def get_assignment_from_google_sheet():
    response = requests.get(
        GOOGLE_SCRIPT_URL,
        params={"action": "start"},
        timeout=15,
    )
    response.raise_for_status()

    data = response.json()

    if data.get("status") != "ok":
        raise RuntimeError(f"Apps Script Antwort war nicht ok: {data}")

    if data.get("condition") not in ["eng", "breit"]:
        raise RuntimeError(f"Ungültige Bedingung erhalten: {data}")

    if not data.get("participant_id"):
        raise RuntimeError(f"Keine participant_id erhalten: {data}")

    return data["participant_id"], data["condition"]


def start_study():
    participant_id, condition = get_assignment_from_google_sheet()

    st.session_state.phase = "stimulus"
    st.session_state.condition = condition
    st.session_state.participant_id = participant_id
    st.session_state.submission_id = str(uuid.uuid4())
    st.session_state.price_order = generate_price_order()
    st.session_state.price_index = 0
    st.session_state.responses = {}
    st.session_state.demographics = {}
    st.session_state.risk_attitude = None
    st.session_state.already_saved = False
    st.session_state.manipulation_answer = None
    st.session_state.manipulation_result = None
    st.session_state.save_status = None
    st.session_state.save_error = None


def normal_pdf(x, mu, sigma):
    return (1 / (sigma * math.sqrt(2 * math.pi))) * math.exp(
        -0.5 * ((x - mu) / sigma) ** 2
    )


def make_distribution_plot(condition):
    stim = STIMULI[condition]
    mu = stim["mu"]
    sigma = stim["sigma"]

    x_min = 400
    x_max = 1600
    total_offers = 100

    if condition == "eng":
        bin_width = 35
        bar_edges = list(range(850, 1151, bin_width))
        y_max = 34
    else:
        bin_width = 70
        bar_edges = list(range(580, 1421, bin_width))
        y_max = 24

    bar_centers = []
    bar_counts = []

    for i in range(len(bar_edges) - 1):
        left = bar_edges[i]
        right = bar_edges[i + 1]
        center = (left + right) / 2

        expected_count = normal_pdf(center, mu, sigma) * bin_width * total_offers

        bar_centers.append(center)
        bar_counts.append(expected_count)

    x_values = list(range(x_min, x_max + 1, 5))
    curve_values = [
        normal_pdf(x, mu, sigma) * bin_width * total_offers
        for x in x_values
    ]

    fig, ax = plt.subplots(figsize=(12, 4.8))

    ax.bar(
        bar_centers,
        bar_counts,
        width=bin_width * 0.9,
        alpha=0.75,
        label="Mietangebote",
        edgecolor="white",
        linewidth=1,
    )

    ax.plot(
        x_values,
        curve_values,
        linewidth=2,
        label="Verteilungskurve",
    )

    ax.axvline(
        mu,
        linewidth=2,
        label="Mittelwert μ = 1,000 €",
    )

    ax.text(
        mu + 12,
        y_max * 0.88,
        "Ø 1,000 €",
        fontsize=10,
        fontweight="bold",
    )

    ax.text(
        1435,
        y_max * 0.82,
        f"Kennzahlen\nμ (Mittelwert)  1,000 €\nσ (Std.-Abw.)   {sigma} €",
        fontsize=9,
        va="top",
        ha="left",
        bbox=dict(boxstyle="square,pad=0.45", facecolor="white", edgecolor="lightgray"),
    )

    ax.set_title(
        "Monatliche Mietpreise in Frankfurt am Main",
        fontsize=12,
        pad=18,
    )

    ax.set_xlabel("Monatliche Miete (€)")
    ax.set_ylabel("Anzahl Angebote")

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0, y_max)

    x_ticks = list(range(400, 1601, 100))
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([f"{x:,} €" for x in x_ticks])

    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper right", frameon=False, ncol=3, fontsize=9)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    return fig


def show_current_histogram():
    fig = make_distribution_plot(st.session_state.condition)
    st.pyplot(fig, clear_figure=True)


def compute_rp_binaer(responses):
    yes_prices = [
        price
        for price, answer in responses.items()
        if answer.get("accept") == "Ja"
    ]

    if not yes_prices:
        return ""

    return max(yes_prices)


def compute_rp_skala(responses):
    ok_prices = [
        price
        for price, answer in responses.items()
        if int(answer.get("feeling", 0)) >= 3
    ]

    if not ok_prices:
        return ""

    return max(ok_prices)


def build_result_row():
    rp_binaer = compute_rp_binaer(st.session_state.responses)
    rp_skala = compute_rp_skala(st.session_state.responses)

    row = {
        "submission_id": st.session_state.submission_id,
        "participant_id": st.session_state.participant_id,
        "condition": st.session_state.condition,
        "risikobereitschaft_0_10": st.session_state.risk_attitude,
        "alter": st.session_state.demographics.get("alter"),
        "studiengang": st.session_state.demographics.get("studiengang"),
        "schon_selbst_wohnung_gemietet": st.session_state.demographics.get("gemietet"),
        "manipulation_answer": st.session_state.manipulation_answer,
        "manipulation_result": st.session_state.manipulation_result,
        "rp_binaer": rp_binaer,
        "rp_skala": rp_skala,
    }

    for price in PRICE_POINTS:
        answer = st.session_state.responses.get(price, {})
        row[f"preis_{price}_accept"] = answer.get("accept")
        row[f"preis_{price}_feeling"] = answer.get("feeling")

    for i, price in enumerate(st.session_state.price_order, start=1):
        row[f"reihenfolge_{i}"] = price

    return row


def save_results():
    row = build_result_row()

    response = requests.post(
        GOOGLE_SCRIPT_URL,
        json=row,
        timeout=15,
    )

    response.raise_for_status()

    result = response.json()

    if result.get("status") not in ["ok", "duplicate_ignored"]:
        raise RuntimeError(f"Apps Script Antwort war nicht ok: {result}")


init_state()


st.title("Pilotstudie — Stochastische BATNA & Reservationspreis")


if st.session_state.phase == "welcome":
    st.write("Bitte starte die Umfrage, wenn du bereit bist.")

    if st.button("Umfrage starten", type="primary"):
        try:
            start_study()
            st.rerun()
        except Exception as e:
            st.error("Die Umfrage konnte gerade nicht gestartet werden.")
            st.caption(str(e))


elif st.session_state.phase == "stimulus":
    condition = st.session_state.condition
    stim = STIMULI[condition]

    st.subheader(stim["title"])
    st.markdown(stim["intro_text"])
    st.markdown("---")
    st.markdown(stim["distribution_text"])

    show_current_histogram()

    with st.form("manipulation_check"):
        answer = st.radio(
            "Welche Aussage trifft auf die alternativen Wohnungen am ehesten zu?",
            options=[
                "a) Die Preise sind sehr ähnlich – fast alle liegen nah beieinander",
                "b) Die Preise schwanken stark – es gibt günstige und teure Angebote",
            ],
            index=None,
        )

        submitted = st.form_submit_button("Weiter")

    if submitted and answer:
        selected = "a" if answer.startswith("a)") else "b"

        st.session_state.manipulation_answer = selected
        st.session_state.manipulation_result = (
            "richtig" if selected == stim["check_correct"] else "falsch"
        )

        st.session_state.phase = "price_questions"
        st.rerun()


elif st.session_state.phase == "price_questions":
    idx = st.session_state.price_index
    price = st.session_state.price_order[idx]
    total = len(st.session_state.price_order)

    show_current_histogram()

    st.markdown("---")
    st.subheader(f"Preisabfrage {idx + 1} von {total}")
    st.metric("Aktueller Preis für Wohnung A", f"{price} €")

    st.markdown("---")

    with st.form(f"price_form_{price}_{idx}"):
        accept = st.radio(
            "Würdest du Wohnung A zu diesem Preis nehmen?",
            options=["Ja", "Nein"],
            index=None,
            horizontal=True,
        )

        feeling = st.radio(
            "Wie würdest du dich dabei fühlen, Wohnung A zu diesem Preis zu nehmen?",
            options=[1, 2, 3, 4, 5],
            index=None,
            horizontal=True,
            format_func=lambda x: {
                1: "1 = sehr schlecht",
                2: "2 = schlecht",
                3: "3 = neutral",
                4: "4 = gut",
                5: "5 = sehr gut",
            }[x],
        )

        submitted = st.form_submit_button(
            "Nächster Preis" if idx < total - 1 else "Weiter"
        )

    if submitted and accept and feeling is not None:
        st.session_state.responses[price] = {
            "accept": accept,
            "feeling": int(feeling),
        }

        st.session_state.price_index += 1

        if st.session_state.price_index >= total:
            st.session_state.phase = "demographics"

        st.rerun()


elif st.session_state.phase == "demographics":
    st.subheader("Abschlussfragen")

    with st.form("demography_form"):
        risk_attitude = st.radio(
            "Wie schätzen Sie sich persönlich ein: Sind Sie im Allgemeinen ein risikobereiter Mensch, oder versuchen Sie, Risiken zu vermeiden? Bitte kreuzen Sie ein Kästchen auf der Skala an, wobei der Wert 0 bedeutet gar nicht risikobereit und der Wert 10 sehr risikobereit.",
            options=list(range(0, 11)),
            index=None,
            horizontal=True,
            format_func=lambda x: str(x),
        )

        alter = st.number_input(
            "Alter",
            min_value=0,
            max_value=120,
            step=1,
        )

        studiengang = st.text_input("Studiengang")

        gemietet = st.radio(
            "Schon mal selbst eine Wohnung gemietet?",
            options=["Ja", "Nein"],
            index=None,
            horizontal=True,
        )

        submitted = st.form_submit_button("Umfrage abschließen")

    if submitted and risk_attitude is not None and gemietet:
        st.session_state.risk_attitude = int(risk_attitude)

        st.session_state.demographics = {
            "alter": int(alter),
            "studiengang": studiengang.strip(),
            "gemietet": gemietet,
        }

        if not st.session_state.already_saved:
            st.session_state.already_saved = True

            try:
                save_results()
                st.session_state.save_status = "online_saved"
                st.session_state.save_error = None
                st.session_state.phase = "end"

            except Exception as e:
                st.session_state.save_status = "not_saved"
                st.session_state.save_error = str(e)
                st.session_state.phase = "save_error"

        else:
            st.session_state.phase = "end"

        st.rerun()


elif st.session_state.phase == "save_error":
    st.error("Die Antwort konnte gerade nicht gespeichert werden.")
    st.write("Bitte informiere die Versuchsleitung.")

    if st.session_state.save_error:
        st.caption(st.session_state.save_error)

    if st.button("Speichern erneut versuchen"):
        try:
            save_results()
            st.session_state.save_status = "online_saved"
            st.session_state.save_error = None
            st.session_state.phase = "end"
            st.rerun()
        except Exception as e:
            st.session_state.save_error = str(e)
            st.caption(str(e))


elif st.session_state.phase == "end":
    st.success("Vielen Dank für deine Teilnahme.")
    st.write("Die Umfrage ist abgeschlossen.")