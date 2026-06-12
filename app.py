import random
import uuid
from pathlib import Path

import requests
import streamlit as st
import streamlit.components.v1 as components


GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyqa0OpJ9XYZ_3Tr22DdcsQNzSwYiUT_Swx0u_lGL47NXmT8xDs1Td4A4qctICr80smyQ/exec"

BASE_DIR = Path(__file__).resolve().parent

IMAGE_FILES = {
    "unimodal_eng": BASE_DIR / "Unimodal_eng.png",
    "unimodal_breit": BASE_DIR / "Unimodal_breit.png",
    "bimodal_eng": BASE_DIR / "Bimodal_eng.png",
    "bimodal_breit": BASE_DIR / "Bimodal_breit.png",
}


st.set_page_config(
    page_title="Pilotstudie – Stochastische BATNA",
    page_icon="🏠",
    layout="centered",
)


PRICE_POINTS = [850, 925, 975, 1000, 1025, 1075, 1150]


DISTRIBUTION_INFO = {
    "unimodal_eng": {
        "form": "unimodal",
        "spread": "eng",
        "description_first": """Aus deinen Recherchen weißt du außerdem: Die Preise vergleichbarer Wohnungen liegen meistens dicht beieinander. Die meisten Angebote bewegen sich um einen ähnlichen Mietpreis, starke Abweichungen nach oben oder unten sind eher selten.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen verteilt sind:""",
        "description_second": """In dieser neuen Situation liegen die Preise vergleichbarer Wohnungen meistens dicht beieinander. Die meisten Angebote bewegen sich um einen ähnlichen Mietpreis, starke Abweichungen nach oben oder unten sind eher selten.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen in dieser neuen Situation verteilt sind:""",
        "check_correct": "a",
    },
    "unimodal_breit": {
        "form": "unimodal",
        "spread": "breit",
        "description_first": """Aus deinen Recherchen weißt du außerdem: Die Preise vergleichbarer Wohnungen schwanken deutlich stärker. Es gibt sowohl günstigere als auch deutlich teurere Angebote, die Mietpreise liegen also weiter auseinander.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen verteilt sind:""",
        "description_second": """In dieser neuen Situation schwanken die Preise vergleichbarer Wohnungen deutlich stärker. Es gibt sowohl günstigere als auch deutlich teurere Angebote, die Mietpreise liegen also weiter auseinander.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen in dieser neuen Situation verteilt sind:""",
        "check_correct": "b",
    },
    "bimodal_eng": {
        "form": "bimodal",
        "spread": "eng",
        "description_first": """Aus deinen Recherchen weißt du außerdem: Die Preise vergleichbarer Wohnungen konzentrieren sich nicht nur um einen einzelnen Bereich, sondern eher um zwei nahe beieinanderliegende Preisbereiche. Es gibt also zwei Häufungen von Angeboten.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen verteilt sind:""",
        "description_second": """In dieser neuen Situation konzentrieren sich die Preise vergleichbarer Wohnungen nicht nur um einen einzelnen Bereich, sondern eher um zwei nahe beieinanderliegende Preisbereiche. Es gibt also zwei Häufungen von Angeboten.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen in dieser neuen Situation verteilt sind:""",
        "check_correct": "c",
    },
    "bimodal_breit": {
        "form": "bimodal",
        "spread": "breit",
        "description_first": """Aus deinen Recherchen weißt du außerdem: Die Preise vergleichbarer Wohnungen konzentrieren sich nicht nur um einen einzelnen Bereich, sondern eher um zwei deutlich getrennte Preisbereiche. Es gibt also zwei Häufungen von Angeboten: einen günstigeren und einen teureren Bereich.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen verteilt sind:""",
        "description_second": """In dieser neuen Situation konzentrieren sich die Preise vergleichbarer Wohnungen nicht nur um einen einzelnen Bereich, sondern eher um zwei deutlich getrennte Preisbereiche. Es gibt also zwei Häufungen von Angeboten: einen günstigeren und einen teureren Bereich.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen in dieser neuen Situation verteilt sind:""",
        "check_correct": "d",
    },
}


FIRST_SITUATION_TEXT = """Stell dir folgende Situation vor:

Du beginnst in zwei Wochen ein sechsmonatiges Pflichtpraktikum in Frankfurt am Main und verdienst in dieser Zeit 1.750 € netto pro Monat.

Da du nicht in Frankfurt wohnst, brauchst du für diese sechs Monate eine eigene 1-Zimmer-Wohnung. Du hast bereits eine perfekte Wohnung gefunden – WOHNUNG A.

Der Vermieter macht dir gleich ein Angebot. Du kannst Wohnung A direkt annehmen oder ablehnen und auf eine andere ähnliche Wohnung warten. Diese alternativen Angebote nennen wir WOHNUNG B."""


SECOND_SITUATION_TEXT = """Stell dir nun eine neue Situation vor:

Dein Praktikum in Frankfurt wird verlängert, aber dein aktueller Mietvertrag läuft bald aus und kann nicht verlängert werden.

Du musst deshalb erneut eine Wohnung suchen und findest wieder eine perfekte Wohnung – WOHNUNG A.

Der Vermieter macht dir ein Angebot. Du kannst Wohnung A direkt annehmen oder ablehnen und auf alternative Wohnungen warten. Diese alternativen Angebote nennen wir wieder WOHNUNG B."""


MANIPULATION_OPTIONS = [
    "a) Die Preise liegen meistens dicht beieinander und konzentrieren sich um einen ähnlichen Mietpreis.",
    "b) Die Preise schwanken stark und es gibt sowohl günstigere als auch deutlich teurere Angebote.",
    "c) Die Preise konzentrieren sich um zwei nahe beieinanderliegende Preisbereiche.",
    "d) Die Preise konzentrieren sich um zwei deutlich getrennte Preisbereiche.",
]


def scroll_to_top(token=""):
    components.html(
        f"""
        <script>
            const scrollToken = "{token}";

            function forceScrollTop() {{
                try {{
                    const doc = window.parent.document;

                    window.parent.scrollTo(0, 0);
                    doc.documentElement.scrollTop = 0;
                    doc.body.scrollTop = 0;

                    const mainContainers = doc.querySelectorAll(
                        '[data-testid="stAppViewContainer"], [data-testid="stMain"], main, section.main'
                    );

                    mainContainers.forEach(el => {{
                        if (el) {{
                            el.scrollTop = 0;
                        }}
                    }});

                }} catch (e) {{
                    console.log("Scroll-to-top failed:", e);
                }}
            }}

            requestAnimationFrame(forceScrollTop);
            setTimeout(forceScrollTop, 80);
        </script>
        """,
        height=0,
    )


def init_state():
    defaults = {
        "phase": "welcome",
        "scroll_token": 0,

        "phase1_distribution": None,
        "phase2_distribution": None,

        "phase1_price_order": [],
        "phase2_price_order": [],
        "phase1_price_index": 0,
        "phase2_price_index": 0,

        "phase1_responses": {},
        "phase2_responses": {},

        "demographics": {},
        "distribution_weighting_text": None,
        "feedback_text": None,
        "ambiguity_choice": None,

        "risk_investment_safe": None,
        "risk_investment_risky": None,

        "participant_id": None,
        "submission_id": None,
        "already_saved": False,

        "phase1_manipulation_answer": None,
        "phase1_manipulation_result": None,
        "phase2_manipulation_answer": None,
        "phase2_manipulation_result": None,

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
        timeout=20,
    )
    response.raise_for_status()

    data = response.json()

    if data.get("status") != "ok":
        raise RuntimeError(f"Apps Script Antwort war nicht ok: {data}")

    phase1_distribution = data.get("phase1_distribution") or data.get("phase1_condition")
    phase2_distribution = data.get("phase2_distribution")

    if phase1_distribution not in DISTRIBUTION_INFO:
        raise RuntimeError(f"Ungültige erste Verteilung erhalten: {data}")

    if phase2_distribution not in DISTRIBUTION_INFO:
        raise RuntimeError(f"Ungültige zweite Verteilung erhalten: {data}")

    if phase1_distribution == phase2_distribution:
        raise RuntimeError(f"Erste und zweite Verteilung dürfen nicht gleich sein: {data}")

    if not data.get("participant_id"):
        raise RuntimeError(f"Keine participant_id erhalten: {data}")

    return data["participant_id"], phase1_distribution, phase2_distribution


def start_study():
    participant_id, phase1_distribution, phase2_distribution = get_assignment_from_google_sheet()

    st.session_state.phase = "first_stimulus"
    st.session_state.participant_id = participant_id
    st.session_state.phase1_distribution = phase1_distribution
    st.session_state.phase2_distribution = phase2_distribution
    st.session_state.submission_id = str(uuid.uuid4())

    st.session_state.phase1_price_order = generate_price_order()
    st.session_state.phase2_price_order = generate_price_order()

    st.session_state.phase1_price_index = 0
    st.session_state.phase2_price_index = 0

    st.session_state.phase1_responses = {}
    st.session_state.phase2_responses = {}
    st.session_state.demographics = {}

    st.session_state.distribution_weighting_text = None
    st.session_state.feedback_text = None
    st.session_state.ambiguity_choice = None

    st.session_state.risk_investment_safe = None
    st.session_state.risk_investment_risky = None

    st.session_state.already_saved = False
    st.session_state.phase1_manipulation_answer = None
    st.session_state.phase1_manipulation_result = None
    st.session_state.phase2_manipulation_answer = None
    st.session_state.phase2_manipulation_result = None
    st.session_state.save_status = None
    st.session_state.save_error = None
    st.session_state.scroll_token += 1


def show_histogram(distribution_key):
    image_path = IMAGE_FILES[distribution_key]

    if image_path.exists():
        st.image(str(image_path), use_container_width=True)
    else:
        st.error(f"Histogramm-Datei nicht gefunden: {image_path.name}")


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


def add_response_columns(row, prefix, responses, price_order):
    for price in PRICE_POINTS:
        answer = responses.get(price, {})
        row[f"{prefix}_preis_{price}_accept"] = answer.get("accept")
        row[f"{prefix}_preis_{price}_feeling"] = answer.get("feeling")

    for i, price in enumerate(price_order, start=1):
        row[f"{prefix}_reihenfolge_{i}"] = price


def build_result_row():
    phase1_rp_binaer = compute_rp_binaer(st.session_state.phase1_responses)
    phase1_rp_skala = compute_rp_skala(st.session_state.phase1_responses)

    phase2_rp_binaer = compute_rp_binaer(st.session_state.phase2_responses)
    phase2_rp_skala = compute_rp_skala(st.session_state.phase2_responses)

    phase1_info = DISTRIBUTION_INFO[st.session_state.phase1_distribution]
    phase2_info = DISTRIBUTION_INFO[st.session_state.phase2_distribution]

    row = {
        "submission_id": st.session_state.submission_id,
        "participant_id": st.session_state.participant_id,

        "phase1_condition": st.session_state.phase1_distribution,
        "phase1_distribution": st.session_state.phase1_distribution,
        "phase1_form": phase1_info["form"],
        "phase1_spread": phase1_info["spread"],

        "phase2_arm": phase2_info["form"],
        "phase2_distribution": st.session_state.phase2_distribution,
        "phase2_form": phase2_info["form"],
        "phase2_spread": phase2_info["spread"],

        "phase1_manipulation_answer": st.session_state.phase1_manipulation_answer,
        "phase1_manipulation_result": st.session_state.phase1_manipulation_result,
        "phase2_manipulation_answer": st.session_state.phase2_manipulation_answer,
        "phase2_manipulation_result": st.session_state.phase2_manipulation_result,

        "phase1_rp_binaer": phase1_rp_binaer,
        "phase1_rp_skala": phase1_rp_skala,
        "phase2_rp_binaer": phase2_rp_binaer,
        "phase2_rp_skala": phase2_rp_skala,

        "gewichteter_verteilungsbereich": st.session_state.distribution_weighting_text,

        "risiko_investition_A_sicher": st.session_state.risk_investment_safe,
        "risiko_investition_B_riskant": st.session_state.risk_investment_risky,

        "ambiguitaet_urne_wahl": st.session_state.ambiguity_choice,

        "alter": st.session_state.demographics.get("alter"),
        "geschlecht": st.session_state.demographics.get("geschlecht"),
        "studiengang": st.session_state.demographics.get("studiengang"),
        "schon_selbst_wohnung_gemietet": st.session_state.demographics.get("gemietet"),

        "feedback_optional": st.session_state.feedback_text,
    }

    add_response_columns(
        row,
        "phase1",
        st.session_state.phase1_responses,
        st.session_state.phase1_price_order,
    )

    add_response_columns(
        row,
        "phase2",
        st.session_state.phase2_responses,
        st.session_state.phase2_price_order,
    )

    return row


def save_results():
    row = build_result_row()

    response = requests.post(
        GOOGLE_SCRIPT_URL,
        json=row,
        timeout=30,
    )

    response.raise_for_status()

    result = response.json()

    if result.get("status") not in ["ok", "duplicate_ignored"]:
        raise RuntimeError(f"Apps Script Antwort war nicht ok: {result}")


def render_manipulation_check(stage, distribution_key):
    info = DISTRIBUTION_INFO[distribution_key]

    if stage == "first":
        form_key = "first_manipulation_check"
        answer_key = "phase1_manipulation_answer"
        result_key = "phase1_manipulation_result"
        next_phase = "first_prices"
    else:
        form_key = "second_manipulation_check"
        answer_key = "phase2_manipulation_answer"
        result_key = "phase2_manipulation_result"
        next_phase = "second_prices"

    with st.form(form_key):
        answer = st.radio(
            "Welche Aussage trifft auf die alternativen Wohnungen am ehesten zu?",
            options=MANIPULATION_OPTIONS,
            index=None,
        )

        submitted = st.form_submit_button("Weiter")

    if submitted and answer:
        selected = answer[0]

        st.session_state[answer_key] = selected
        st.session_state[result_key] = (
            "richtig" if selected == info["check_correct"] else "falsch"
        )

        st.session_state.scroll_token += 1
        st.session_state.phase = next_phase
        st.rerun()


def render_price_question(stage):
    scroll_to_top(
        token=f"{stage}_{st.session_state.phase1_price_index}_{st.session_state.phase2_price_index}_{st.session_state.scroll_token}"
    )

    if stage == "first":
        idx = st.session_state.phase1_price_index
        price_order = st.session_state.phase1_price_order
        responses_key = "phase1_responses"
        next_page = "second_intro"
        distribution_key = st.session_state.phase1_distribution
    else:
        idx = st.session_state.phase2_price_index
        price_order = st.session_state.phase2_price_order
        responses_key = "phase2_responses"
        next_page = "demographics"
        distribution_key = st.session_state.phase2_distribution

    price = price_order[idx]
    total = len(price_order)

    show_histogram(distribution_key)

    st.markdown("---")
    st.subheader(f"Preisabfrage {idx + 1} von {total}")
    st.metric("Aktueller Preis für Wohnung A", f"{price} €")

    st.markdown("---")

    with st.form(f"{stage}_price_form_{price}_{idx}"):
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
        st.session_state[responses_key][price] = {
            "accept": accept,
            "feeling": int(feeling),
        }

        st.session_state.scroll_token += 1

        if stage == "first":
            st.session_state.phase1_price_index += 1

            if st.session_state.phase1_price_index >= total:
                st.session_state.phase = next_page
        else:
            st.session_state.phase2_price_index += 1

            if st.session_state.phase2_price_index >= total:
                st.session_state.phase = next_page

        st.rerun()


init_state()


if st.session_state.phase == "welcome":
    st.title("Pilotstudie — Stochastische BATNA & Reservationspreis")
    st.write("Bitte starte die Umfrage, wenn du bereit bist.")

    if st.button("Umfrage starten", type="primary"):
        try:
            start_study()
            st.rerun()
        except Exception as e:
            st.error("Die Umfrage konnte gerade nicht gestartet werden.")
            st.caption(str(e))


elif st.session_state.phase == "first_stimulus":
    st.title("Pilotstudie — Stochastische BATNA & Reservationspreis")

    distribution_key = st.session_state.phase1_distribution
    info = DISTRIBUTION_INFO[distribution_key]

    st.subheader("Stochastischer BATNA")
    st.markdown(FIRST_SITUATION_TEXT)
    st.markdown("---")
    st.markdown(info["description_first"])

    show_histogram(distribution_key)

    render_manipulation_check("first", distribution_key)


elif st.session_state.phase == "first_prices":
    render_price_question("first")


elif st.session_state.phase == "second_intro":
    st.subheader("Neue Wohnsituation")
    st.markdown(SECOND_SITUATION_TEXT)

    if st.button("Weiter", type="primary"):
        st.session_state.scroll_token += 1
        st.session_state.phase = "second_stimulus"
        st.rerun()


elif st.session_state.phase == "second_stimulus":
    distribution_key = st.session_state.phase2_distribution
    info = DISTRIBUTION_INFO[distribution_key]

    st.subheader("Stochastischer BATNA")
    st.markdown(info["description_second"])

    show_histogram(distribution_key)

    render_manipulation_check("second", distribution_key)


elif st.session_state.phase == "second_prices":
    render_price_question("second")


elif st.session_state.phase == "demographics":
    scroll_to_top(token=f"demographics_{st.session_state.scroll_token}")

    st.subheader("Abschlussfragen")

    with st.form("demography_form"):
        distribution_weighting_text = st.text_area(
            "Wenn Sie an die gezeigten Mietpreis-Verteilungen zurückdenken: Haben Sie sich bei Ihrer Entscheidung eher an einem günstigeren Bereich, einem teureren Bereich oder an der gesamten Verteilung orientiert? Erläutern Sie dies bitte kurz in 1–2 Sätzen.",
            height=100,
        )

        st.markdown("---")

        st.markdown(
            """Stellen Sie sich vor, Sie haben 100.000 € zum Investieren und können diesen Betrag frei auf zwei Investitionsmöglichkeiten aufteilen.

Investition A verdoppelt den investierten Betrag garantiert.

Investition B hat eine 50%-Chance, den investierten Betrag zu verfünffachen, und eine 50%-Chance, den investierten Betrag vollständig zu verlieren.

Wie viel der 100.000 € würden Sie in Investition B investieren?

**Der restliche Betrag wird automatisch in Investition A investiert.**"""
        )

        risky_amount = st.slider(
            "Betrag für Investition B",
            min_value=0,
            max_value=100000,
            value=50000,
            step=5000,
            format="%d €",
        )

        st.markdown("---")

        st.markdown(
            """Stellen Sie sich vor, Sie können zwischen zwei Urnen wählen. Aus der gewählten Urne wird zufällig eine Kugel gezogen. Wenn die Kugel rot ist, gewinnen Sie 100 €.

**Urne A:** enthält 50 rote und 50 schwarze Kugeln.

**Urne B:** enthält 100 Kugeln, aber das Verhältnis von roten und schwarzen Kugeln ist unbekannt.

Für welche Urne entscheiden Sie sich?"""
        )

        ambiguity_choice = st.radio(
            "Bitte wählen Sie eine Urne aus:",
            options=[
                "Urne A – bekannte Wahrscheinlichkeit",
                "Urne B – unbekannte Wahrscheinlichkeit",
            ],
            index=None,
        )

        st.markdown("---")

        alter = st.number_input(
            "Alter",
            min_value=0,
            max_value=120,
            step=1,
        )

        geschlecht = st.radio(
            "Geschlecht",
            options=[
                "weiblich",
                "männlich",
                "divers",
                "keine Angabe",
            ],
            index=None,
            horizontal=True,
        )

        studiengang = st.text_input("Studiengang")

        gemietet = st.radio(
            "Schon mal selbst eine Wohnung gemietet?",
            options=["Ja", "Nein"],
            index=None,
            horizontal=True,
        )

        feedback_text = st.text_area(
            "Gab es etwas, das unklar war, oder haben Sie Verbesserungsvorschläge? Diese Antwort ist optional.",
            height=100,
        )

        submitted = st.form_submit_button("Umfrage abschließen")

    if submitted:
        required_missing = False

        if not distribution_weighting_text.strip():
            st.error("Bitte erläutern Sie kurz, welcher Bereich der Verteilung für Ihre Entscheidung wichtig war.")
            required_missing = True

        if ambiguity_choice is None:
            st.error("Bitte wählen Sie bei der Urnenfrage eine Antwort aus.")
            required_missing = True

        if geschlecht is None:
            st.error("Bitte wählen Sie beim Geschlecht eine Antwort aus.")
            required_missing = True

        if gemietet is None:
            st.error("Bitte beantworten Sie, ob Sie schon mal selbst eine Wohnung gemietet haben.")
            required_missing = True

        if not required_missing:
            if ambiguity_choice.startswith("Urne A"):
                ambiguity_value = "bekannte_wahrscheinlichkeit"
            else:
                ambiguity_value = "unbekannte_wahrscheinlichkeit"

            st.session_state.distribution_weighting_text = distribution_weighting_text.strip()
            st.session_state.feedback_text = feedback_text.strip()
            st.session_state.ambiguity_choice = ambiguity_value

            st.session_state.risk_investment_risky = int(risky_amount)
            st.session_state.risk_investment_safe = int(100000 - risky_amount)

            st.session_state.demographics = {
                "alter": int(alter),
                "geschlecht": geschlecht,
                "studiengang": studiengang.strip(),
                "gemietet": gemietet,
            }

            if not st.session_state.already_saved:
                st.session_state.already_saved = True

                try:
                    save_results()
                    st.session_state.save_status = "online_saved"
                    st.session_state.save_error = None
                    st.session_state.scroll_token += 1
                    st.session_state.phase = "end"

                except Exception as e:
                    st.session_state.save_status = "not_saved"
                    st.session_state.save_error = str(e)
                    st.session_state.scroll_token += 1
                    st.session_state.phase = "save_error"

            else:
                st.session_state.scroll_token += 1
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
            st.session_state.scroll_token += 1
            st.session_state.phase = "end"
            st.rerun()
        except Exception as e:
            st.session_state.save_error = str(e)
            st.caption(str(e))


elif st.session_state.phase == "end":
    st.title("Pilotstudie — Stochastische BATNA & Reservationspreis")
    st.success("Vielen Dank für deine Teilnahme.")
    st.write("Die Umfrage ist abgeschlossen.")