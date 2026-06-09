import random
import uuid
from pathlib import Path

import requests
import streamlit as st
import streamlit.components.v1 as components


GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbyqa0OpJ9XYZ_3Tr22DdcsQNzSwYiUT_Swx0u_lGL47NXmT8xDs1Td4A4qctICr80smyQ/exec"

BASE_DIR = Path(__file__).resolve().parent

IMAGE_FILES = {
    "phase1": {
        "eng": BASE_DIR / "Unimodal_eng.png",
        "breit": BASE_DIR / "Unimodal_breit.png",
    },
    "phase2": {
        "eng_kontrolle": BASE_DIR / "Unimodal_eng_kontrolle.png",
        "breit_kontrolle": BASE_DIR / "Unimodal_breit_kontrolle.png",
        "eng_bimodal": BASE_DIR / "Bimodal_eng.png",
        "breit_bimodal": BASE_DIR / "Bimodal_breit.png",
    },
}


st.set_page_config(
    page_title="Pilotstudie – Stochastische BATNA",
    page_icon="🏠",
    layout="centered",
)


PRICE_POINTS = [850, 925, 975, 1000, 1025, 1075, 1150]


STIMULI = {
    "phase1": {
        "eng": {
            "title": "Stochastischer BATNA",
            "intro_text": """Stell dir folgende Situation vor:

Du beginnst in zwei Wochen ein sechsmonatiges Pflichtpraktikum in Frankfurt am Main und verdienst in dieser Zeit 1.750 € netto pro Monat.

Da du nicht in Frankfurt wohnst, brauchst du für diese sechs Monate eine eigene 1-Zimmer-Wohnung. Du hast bereits eine perfekte Wohnung gefunden – WOHNUNG A.

Der Vermieter macht dir gleich ein Angebot. Du kannst Wohnung A direkt annehmen oder ablehnen und auf eine andere ähnliche Wohnung warten. Diese alternativen Angebote nennen wir WOHNUNG B.""",
            "distribution_text": """Aus deinen Recherchen weißt du außerdem: Die Preise vergleichbarer Wohnungen liegen meistens dicht beieinander. Die meisten Angebote bewegen sich um einen ähnlichen Mietpreis, starke Abweichungen nach oben oder unten sind eher selten.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen verteilt sind:""",
            "check_correct": "a",
        },
        "breit": {
            "title": "Stochastischer BATNA",
            "intro_text": """Stell dir folgende Situation vor:

Du beginnst in zwei Wochen ein sechsmonatiges Pflichtpraktikum in Frankfurt am Main und verdienst in dieser Zeit 1.750 € netto pro Monat.

Da du nicht in Frankfurt wohnst, brauchst du für diese sechs Monate eine eigene 1-Zimmer-Wohnung. Du hast bereits eine perfekte Wohnung gefunden – WOHNUNG A.

Der Vermieter macht dir gleich ein Angebot. Du kannst Wohnung A direkt annehmen oder ablehnen und auf eine andere ähnliche Wohnung warten. Diese alternativen Angebote nennen wir WOHNUNG B.""",
            "distribution_text": """Aus deinen Recherchen weißt du außerdem: Die Preise vergleichbarer Wohnungen schwanken deutlich stärker. Es gibt sowohl günstigere als auch deutlich teurere Angebote, die Mietpreise liegen also weiter auseinander.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen verteilt sind:""",
            "check_correct": "b",
        },
    },
    "phase2": {
        "intro_text": """Einige Monate später wird dein Praktikumsvertrag überraschend verlängert. Du möchtest weiterhin in Frankfurt bleiben, aber dein aktueller Mietvertrag läuft bald aus und kann nicht verlängert werden.

Deshalb musst du erneut eine passende 1-Zimmer-Wohnung finden. Wieder findest du eine perfekte Wohnung – WOHNUNG A.

Der Vermieter macht dir erneut ein Angebot. Du kannst Wohnung A direkt annehmen oder ablehnen und auf alternative Wohnungen warten. Diese alternativen Angebote nennen wir wieder WOHNUNG B.

Wenn du nicht rechtzeitig eine Wohnung findest, müsstest du kurzfristig eine deutlich unpraktischere Übergangslösung suchen, zum Beispiel längeres Pendeln oder eine teurere Zwischenmiete.""",
        "distribution_texts": {
            "eng_kontrolle": """Auch in dieser neuen Situation liegen die Preise vergleichbarer Wohnungen meistens dicht beieinander. Die meisten Angebote bewegen sich um einen ähnlichen Mietpreis, starke Abweichungen nach oben oder unten sind eher selten.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen in dieser neuen Situation verteilt sind:""",
            "breit_kontrolle": """Auch in dieser neuen Situation schwanken die Preise vergleichbarer Wohnungen deutlich stärker. Es gibt sowohl günstigere als auch deutlich teurere Angebote, die Mietpreise liegen also weiter auseinander.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen in dieser neuen Situation verteilt sind:""",
            "eng_bimodal": """In dieser neuen Situation konzentrieren sich die Preise vergleichbarer Wohnungen nicht nur um einen einzelnen Bereich, sondern eher um zwei nahe beieinanderliegende Preisbereiche. Es gibt also zwei Häufungen von Angeboten.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen in dieser neuen Situation verteilt sind:""",
            "breit_bimodal": """In dieser neuen Situation konzentrieren sich die Preise vergleichbarer Wohnungen nicht nur um einen einzelnen Bereich, sondern eher um zwei deutlich getrennte Preisbereiche. Es gibt also zwei Häufungen von Angeboten: einen günstigeren und einen teureren Bereich.

Hier siehst du, wie die monatlichen Mietpreise vergleichbarer Wohnungen in dieser neuen Situation verteilt sind:""",
        },
    },
}


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

                    const selectors = [
                        '[data-testid="stAppViewContainer"]',
                        '[data-testid="stMain"]',
                        '[data-testid="stVerticalBlock"]',
                        '.stApp',
                        'section.main',
                        'main',
                        '.main'
                    ];

                    selectors.forEach(selector => {{
                        const elements = doc.querySelectorAll(selector);
                        elements.forEach(el => {{
                            if (el) {{
                                el.scrollTop = 0;
                            }}
                        }});
                    }});

                    const scrollableElements = Array.from(doc.querySelectorAll('*')).filter(el => {{
                        const style = window.parent.getComputedStyle(el);
                        return (
                            (style.overflowY === 'auto' || style.overflowY === 'scroll') &&
                            el.scrollHeight > el.clientHeight
                        );
                    }});

                    scrollableElements.forEach(el => {{
                        el.scrollTop = 0;
                    }});

                }} catch (e) {{
                    console.log("Scroll-to-top failed:", e);
                }}
            }}

            forceScrollTop();
            setTimeout(forceScrollTop, 50);
            setTimeout(forceScrollTop, 150);
            setTimeout(forceScrollTop, 300);
            setTimeout(forceScrollTop, 600);
            setTimeout(forceScrollTop, 1000);
            setTimeout(forceScrollTop, 1500);
        </script>
        """,
        height=0,
    )


def init_state():
    defaults = {
        "phase": "welcome",
        "scroll_token": 0,
        "phase1_condition": None,
        "phase2_arm": None,
        "phase2_distribution": None,
        "phase1_price_order": [],
        "phase2_price_order": [],
        "phase1_price_index": 0,
        "phase2_price_index": 0,
        "phase1_responses": {},
        "phase2_responses": {},
        "demographics": {},
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

    phase1_condition = data.get("phase1_condition") or data.get("condition")
    phase2_arm = data.get("phase2_arm")

    if phase1_condition not in ["eng", "breit"]:
        raise RuntimeError(f"Ungültige Bedingung erhalten: {data}")

    if phase2_arm not in ["kontrolle", "bimodal"]:
        raise RuntimeError(f"Ungültige zweite Bedingung erhalten: {data}")

    if not data.get("participant_id"):
        raise RuntimeError(f"Keine participant_id erhalten: {data}")

    return data["participant_id"], phase1_condition, phase2_arm


def start_study():
    participant_id, phase1_condition, phase2_arm = get_assignment_from_google_sheet()
    phase2_distribution = f"{phase1_condition}_{phase2_arm}"

    st.session_state.phase = "first_stimulus"
    st.session_state.participant_id = participant_id
    st.session_state.phase1_condition = phase1_condition
    st.session_state.phase2_arm = phase2_arm
    st.session_state.phase2_distribution = phase2_distribution
    st.session_state.submission_id = str(uuid.uuid4())

    st.session_state.phase1_price_order = generate_price_order()
    st.session_state.phase2_price_order = generate_price_order()

    st.session_state.phase1_price_index = 0
    st.session_state.phase2_price_index = 0

    st.session_state.phase1_responses = {}
    st.session_state.phase2_responses = {}
    st.session_state.demographics = {}

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


def show_histogram(stage):
    if stage == "first":
        image_path = IMAGE_FILES["phase1"][st.session_state.phase1_condition]
    else:
        image_path = IMAGE_FILES["phase2"][st.session_state.phase2_distribution]

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

    row = {
        "submission_id": st.session_state.submission_id,
        "participant_id": st.session_state.participant_id,

        "phase1_condition": st.session_state.phase1_condition,
        "phase2_arm": st.session_state.phase2_arm,
        "phase2_distribution": st.session_state.phase2_distribution,

        "phase1_manipulation_answer": st.session_state.phase1_manipulation_answer,
        "phase1_manipulation_result": st.session_state.phase1_manipulation_result,
        "phase2_manipulation_answer": st.session_state.phase2_manipulation_answer,
        "phase2_manipulation_result": st.session_state.phase2_manipulation_result,

        "phase1_rp_binaer": phase1_rp_binaer,
        "phase1_rp_skala": phase1_rp_skala,
        "phase2_rp_binaer": phase2_rp_binaer,
        "phase2_rp_skala": phase2_rp_skala,

        "risiko_investition_A_sicher": st.session_state.risk_investment_safe,
        "risiko_investition_B_riskant": st.session_state.risk_investment_risky,

        "alter": st.session_state.demographics.get("alter"),
        "studiengang": st.session_state.demographics.get("studiengang"),
        "schon_selbst_wohnung_gemietet": st.session_state.demographics.get("gemietet"),
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


def render_price_question(stage):
    scroll_to_top(
        token=f"{stage}_{st.session_state.phase1_price_index}_{st.session_state.phase2_price_index}_{st.session_state.scroll_token}"
    )

    if stage == "first":
        idx = st.session_state.phase1_price_index
        price_order = st.session_state.phase1_price_order
        responses_key = "phase1_responses"
        next_page = "second_intro"
    else:
        idx = st.session_state.phase2_price_index
        price_order = st.session_state.phase2_price_order
        responses_key = "phase2_responses"
        next_page = "demographics"

    price = price_order[idx]
    total = len(price_order)

    show_histogram(stage)

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

scroll_to_top(token=f"global_{st.session_state.phase}_{st.session_state.scroll_token}")

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


elif st.session_state.phase == "first_stimulus":
    condition = st.session_state.phase1_condition
    stim = STIMULI["phase1"][condition]

    st.subheader(stim["title"])
    st.markdown(stim["intro_text"])
    st.markdown("---")
    st.markdown(stim["distribution_text"])

    show_histogram("first")

    with st.form("first_manipulation_check"):
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

        st.session_state.phase1_manipulation_answer = selected
        st.session_state.phase1_manipulation_result = (
            "richtig" if selected == stim["check_correct"] else "falsch"
        )

        st.session_state.scroll_token += 1
        st.session_state.phase = "first_prices"
        st.rerun()


elif st.session_state.phase == "first_prices":
    render_price_question("first")


elif st.session_state.phase == "second_intro":
    st.subheader("Neue Wohnsituation")
    st.markdown(STIMULI["phase2"]["intro_text"])

    if st.button("Weiter", type="primary"):
        st.session_state.scroll_token += 1
        st.session_state.phase = "second_stimulus"
        st.rerun()


elif st.session_state.phase == "second_stimulus":
    st.subheader("Stochastischer BATNA")

    distribution_text = STIMULI["phase2"]["distribution_texts"][
        st.session_state.phase2_distribution
    ]

    st.markdown(distribution_text)

    show_histogram("second")

    if st.session_state.phase2_arm == "bimodal":
        with st.form("second_manipulation_check"):
            answer = st.radio(
                "Welche Aussage beschreibt die Verteilung der alternativen Wohnungen am ehesten?",
                options=[
                    "a) Die Preise konzentrieren sich vor allem um einen Bereich.",
                    "b) Die Preise konzentrieren sich um zwei verschiedene Preisbereiche.",
                ],
                index=None,
            )

            submitted = st.form_submit_button("Weiter")

        if submitted and answer:
            selected = "a" if answer.startswith("a)") else "b"

            st.session_state.phase2_manipulation_answer = selected
            st.session_state.phase2_manipulation_result = (
                "richtig" if selected == "b" else "falsch"
            )

            st.session_state.scroll_token += 1
            st.session_state.phase = "second_prices"
            st.rerun()

    else:
        st.session_state.phase2_manipulation_answer = ""
        st.session_state.phase2_manipulation_result = ""

        if st.button("Weiter"):
            st.session_state.scroll_token += 1
            st.session_state.phase = "second_prices"
            st.rerun()


elif st.session_state.phase == "second_prices":
    render_price_question("second")


elif st.session_state.phase == "demographics":
    st.subheader("Abschlussfragen")

    with st.form("demography_form"):
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

    if submitted and gemietet:
        st.session_state.risk_investment_risky = int(risky_amount)
        st.session_state.risk_investment_safe = int(100000 - risky_amount)

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
    st.success("Vielen Dank für deine Teilnahme.")
    st.write("Die Umfrage ist abgeschlossen.")