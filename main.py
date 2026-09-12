import base64
import json
import re
import secrets
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


DEFAULT_DATA_FILE = Path(__file__).with_name(
    "ZebraID_V2_Natural_Data.txt"
)


# ---------------------------------------------------------
# PAGE SETTINGS
# ---------------------------------------------------------

st.set_page_config(
    page_title="ZebraID | Random Persona Generator",
    page_icon="🦓",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ---------------------------------------------------------
# WEBSITE DESIGN
# ---------------------------------------------------------

st.markdown(
    """
    <style>
    :root {
        --blue: #3B5BDB;
        --dark-blue: #2F4BB8;
        --text: #101828;
        --muted: #667085;
        --border: #E4E7EC;
        --white: #FFFFFF;
    }

    .stApp {
        background: #F7F9FC;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.75rem;
        padding-bottom: 3.5rem;
    }

    .zebra-brand {
        color: var(--text);
        font-size: 1.25rem;
        font-weight: 750;
        margin-bottom: 3rem;
    }

    .zebra-eyebrow {
        color: var(--blue);
        font-size: 0.82rem;
        font-weight: 750;
        letter-spacing: 0.12em;
        margin-bottom: 0.8rem;
    }

    .zebra-hero h1 {
        color: var(--text);
        font-size: clamp(2.35rem, 5vw, 4rem);
        font-weight: 780;
        letter-spacing: -0.045em;
        line-height: 1.04;
        margin: 0 0 1rem 0;
        max-width: 760px;
    }

    .zebra-hero p {
        color: var(--muted);
        font-size: 1.08rem;
        line-height: 1.65;
        margin: 0;
        max-width: 720px;
    }

    .zebra-spacer {
        height: 2.25rem;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--white);
        border: 1px solid var(--border);
        border-radius: 18px;
        box-shadow: 0 8px 24px rgba(16, 24, 40, 0.05);
    }

    h1, h2, h3, label {
        color: var(--text);
    }

    div[data-testid="stCaptionContainer"] {
        color: var(--muted);
    }

    .stButton > button {
        min-height: 48px;
        border-radius: 10px;
        font-size: 1rem;
        font-weight: 650;
    }

    .stButton > button[kind="primary"] {
        background: var(--blue);
        border-color: var(--blue);
        color: #FFFFFF;
    }

    .stButton > button[kind="primary"]:hover {
        background: var(--dark-blue);
        border-color: var(--dark-blue);
        box-shadow: 0 5px 14px rgba(59, 91, 219, 0.22);
    }

    .stTextInput input,
    .stNumberInput input,
    .stSelectbox div[data-baseweb="select"] > div,
    .stTextArea textarea {
        border-radius: 10px;
    }

    .stTextArea textarea {
        color: #344054;
        font-size: 1rem;
        line-height: 1.65;
        padding: 1rem;
    }

    .zebra-benefits {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-top: 2.5rem;
    }

    .zebra-benefit {
        background: #FFFFFF;
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.1rem;
    }

    .zebra-benefit strong {
        color: var(--text);
        display: block;
        font-size: 0.98rem;
        margin-bottom: 0.25rem;
    }

    .zebra-benefit span {
        color: var(--muted);
        font-size: 0.87rem;
        line-height: 1.4;
    }

    footer,
    #MainMenu {
        visibility: hidden;
    }

    @media (max-width: 800px) {
        .block-container {
            padding-top: 1rem;
        }

        .zebra-brand {
            margin-bottom: 2rem;
        }

        .zebra-benefits {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    @media (max-width: 520px) {
        .zebra-benefits {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# READ THE DATA FILE
# ---------------------------------------------------------

def numbered_value(line):
    match = re.match(r"^\d+\.\s+(.+)$", line.strip())

    if match:
        return match.group(1).strip()

    return None


@st.cache_data(show_spinner=False)
def read_data(data_file=str(DEFAULT_DATA_FILE)):
    path = Path(data_file)

    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path.name}. "
            "Keep it in the same folder as main.py."
        )

    headings = {
        "100 TEMPLATES": "templates",
        "100 FIRST NAMES": "names",
        "100 LOCATIONS": "locations",
        "100 CAREER PROFILES": "careers",
        "100 RELATIONSHIP DESCRIPTIONS": "relationships",
        "100 WEEKEND ACTIVITIES": "weekends",
        "100 PET DESCRIPTIONS": "pets",
        "100 HOBBIES": "hobbies",
        "100 FOOD PREFERENCES": "foods",
    }

    data = {
        name: []
        for name in headings.values()
    }

    active = None

    for raw in path.read_text(
        encoding="utf-8"
    ).splitlines():

        line = raw.strip()

        if line in headings:
            active = headings[line]
            continue

        if not line:
            continue

        if set(line) <= {"=", "-"}:
            continue

        if active:
            value = numbered_value(line)

            if value:
                data[active].append(value)

    for section, values in data.items():
        if len(values) != 100:
            raise ValueError(
                f"Expected exactly 100 entries in "
                f"{section}, found {len(values)}."
            )

    return data


# ---------------------------------------------------------
# BIOGRAPHY GENERATOR
# ---------------------------------------------------------

def article_job(job):
    cleaned_job = job.strip()

    if cleaned_job[:1].lower() in "aeiou":
        article = "an"
    else:
        article = "a"

    return f"{article} {cleaned_job}"


def insert_age(biography, age):
    if age is None:
        return biography

    age_sentence = f" I'm {int(age)} years old."

    abbreviations = {
        "st",
        "mr",
        "mrs",
        "ms",
        "dr",
    }

    for match in re.finditer(r"\.\s", biography):
        preceding_text = biography[:match.start()]

        preceding_word = re.search(
            r"([A-Za-z]+)$",
            preceding_text,
        )

        if (
            preceding_word
            and preceding_word.group(1).lower()
            in abbreviations
        ):
            continue

        sentence_end = match.start()

        return (
            biography[:sentence_end + 1]
            + age_sentence
            + biography[sentence_end + 1:]
        )

    return f"{biography}{age_sentence}"


def generate_biography(
    data_file=DEFAULT_DATA_FILE,
    name_override="",
    location_override="",
    age_override=None,
    job_override="",
    education_override="",
    relationship_override="Random",
):
    data = read_data(str(data_file))

    template = secrets.choice(
        data["templates"]
    )

    name = (
        name_override.strip()
        or secrets.choice(data["names"])
    )

    location = (
        location_override.strip()
        or secrets.choice(data["locations"])
    )

    career = secrets.choice(
        data["careers"]
    )

    try:
        random_job, random_education, reason = [
            part.strip()
            for part in career.split("|", 2)
        ]

    except ValueError as error:
        raise ValueError(
            "Each career profile must contain: "
            "job | education | reason"
        ) from error

    job = (
        job_override.strip()
        or random_job
    )

    education = (
        education_override.strip()
        or random_education
    )

    relationship_options = {
        "Random": secrets.choice(
            data["relationships"]
        ),
        "Single": "I'm currently single",
        "Dating": "I'm currently dating someone",
        "In a relationship":
            "I'm in a committed relationship",
        "Married": "I'm married",
    }

    relationship = relationship_options[
        relationship_override
    ]

    replacements = {
        "[FNAME]": name,
        "[LOCATION]": location,
        "[ARTICLE_JOB]": article_job(job),
        "[EDUCATION]": education,
        "[CAREER_REASON]": reason,
        "[CAREER_REASON_CAP]":
            reason[:1].upper() + reason[1:],
        "[RELATIONSHIP]": relationship,
        "[WEEKEND]": secrets.choice(
            data["weekends"]
        ),
        "[PET]": secrets.choice(
            data["pets"]
        ),
        "[HOBBY]": secrets.choice(
            data["hobbies"]
        ),
        "[FOOD]": secrets.choice(
            data["foods"]
        ),
    }

    result = template

    for placeholder, value in replacements.items():
        result = result.replace(
            placeholder,
            value,
        )

    if "[AGE]" in result:
        if age_override is not None:
            age_value = str(int(age_override))
        else:
            age_value = str(
                secrets.choice(range(21, 87))
            )

        result = result.replace(
            "[AGE]",
            age_value,
        )

    elif age_override is not None:
        result = insert_age(
            result,
            age_override,
        )

    unresolved = re.findall(
        r"\[[A-Z_]+\]",
        result,
    )

    if unresolved:
        unknown = ", ".join(
            sorted(set(unresolved))
        )

        raise ValueError(
            "Unrecognized template "
            f"placeholder(s): {unknown}"
        )

    return result


# ---------------------------------------------------------
# COPY BUTTON
# ---------------------------------------------------------

def render_copy_button(text):
    encoded_text = base64.b64encode(
        text.encode("utf-8")
    ).decode("ascii")

    component_id = (
        "copy-" + secrets.token_hex(5)
    )

    components.html(
        f"""
        <button
            id="{component_id}"
            type="button"
            onclick="copyBiography()"
        >
            <span aria-hidden="true">⧉</span>
            <span id="{component_id}-label">
                Copy
            </span>
        </button>

        <script>
        const encoded = {json.dumps(encoded_text)};

        const biography =
            new TextDecoder().decode(
                Uint8Array.from(
                    atob(encoded),
                    character =>
                        character.charCodeAt(0)
                )
            );

        async function copyBiography() {{
            const label =
                document.getElementById(
                    "{component_id}-label"
                );

            try {{
                await navigator.clipboard.writeText(
                    biography
                );
            }}

            catch (error) {{
                const temporary =
                    document.createElement(
                        "textarea"
                    );

                temporary.value = biography;
                temporary.style.position =
                    "fixed";
                temporary.style.opacity = "0";

                document.body.appendChild(
                    temporary
                );

                temporary.select();

                document.execCommand("copy");

                temporary.remove();
            }}

            label.textContent = "Copied!";

            window.setTimeout(
                () =>
                    label.textContent = "Copy",
                1500
            );
        }}
        </script>

        <style>
        body {{
            margin: 0;
            background: transparent;
            font-family: Arial, sans-serif;
        }}

        button {{
            align-items: center;
            background: #FFFFFF;
            border: 1px solid #D0D5DD;
            border-radius: 9px;
            color: #344054;
            cursor: pointer;
            display: flex;
            font-size: 14px;
            font-weight: 650;
            gap: 7px;
            justify-content: center;
            min-height: 40px;
            padding: 0 14px;
            width: 100%;
        }}

        button:hover {{
            background: #F9FAFB;
            border-color: #98A2B3;
        }}

        button:focus-visible {{
            outline: 3px solid
                rgba(59, 91, 219, 0.25);
            outline-offset: 2px;
        }}
        </style>
        """,
        height=42,
    )


# ---------------------------------------------------------
# INITIAL BIOGRAPHY
# ---------------------------------------------------------

def initialize_biography():
    if "biography" not in st.session_state:
        biography = generate_biography()

        st.session_state.biography = biography
        st.session_state.biography_editor = biography


# ---------------------------------------------------------
# TOP OF WEBSITE
# ---------------------------------------------------------

st.markdown(
    """
    <div class="zebra-brand">
        🦓 ZebraID
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="zebra-hero">
        <div class="zebra-eyebrow">
            RANDOM. REALISTIC. UNIQUE.
        </div>

        <h1>
            Generate a Random<br>
            Persona Biography
        </h1>

        <p>
            Create a realistic fictional person
            with a unique background, career,
            interests, and more. Customize a few
            details or leave everything blank for
            a completely random result.
        </p>
    </section>

    <div class="zebra-spacer"></div>
    """,
    unsafe_allow_html=True,
)


try:
    initialize_biography()

except (FileNotFoundError, ValueError) as error:
    st.error(str(error))
    st.stop()


# ---------------------------------------------------------
# TWO-COLUMN WEBSITE LAYOUT
# ---------------------------------------------------------

left, right = st.columns(
    [0.92, 1.08],
    gap="large",
)


# ---------------------------------------------------------
# LEFT SIDE: CUSTOMIZATION
# ---------------------------------------------------------

with left:
    with st.container(border=True):
        st.subheader("⚙️ Customize")

        st.caption(
            "All fields are optional. "
            "Blank fields stay random."
        )

        audience = st.radio(
            "Who is this biography for?",
            [
                "Random person",
                "Me",
                "My friend",
            ],
            horizontal=True,
        )

        if audience == "Me":
            name_label = (
                "Your name (optional)"
            )

            name_placeholder = (
                "Example: Aadarsh"
            )

        elif audience == "My friend":
            name_label = (
                "Friend's name (optional)"
            )

            name_placeholder = (
                "Example: Bob"
            )

        else:
            name_label = (
                "Name (optional)"
            )

            name_placeholder = (
                "Leave blank for random"
            )

        chosen_name = st.text_input(
            name_label,
            placeholder=name_placeholder,
        )

        city_column, age_column = (
            st.columns(2)
        )

        with city_column:
            chosen_location = st.text_input(
                "City, State (optional)",
                placeholder="Phoenix, AZ",
            )

        with age_column:
            chosen_age = st.number_input(
                "Age (optional)",
                min_value=18,
                max_value=100,
                value=None,
                step=1,
                placeholder="28",
            )

        with st.expander("More options"):
            chosen_job = st.text_input(
                "Job (optional)",
                placeholder=(
                    "Software engineer"
                ),
            )

            chosen_education = st.text_input(
                "Education / major (optional)",
                placeholder=(
                    "Computer science"
                ),
            )

            chosen_relationship = (
                st.selectbox(
                    "Relationship status",
                    [
                        "Random",
                        "Single",
                        "Dating",
                        "In a relationship",
                        "Married",
                    ],
                )
            )

        generate_clicked = st.button(
            "✨ Generate New Biography",
            type="primary",
            use_container_width=True,
        )

        if generate_clicked:
            try:
                new_biography = (
                    generate_biography(
                        name_override=chosen_name,
                        location_override=(
                            chosen_location
                        ),
                        age_override=chosen_age,
                        job_override=chosen_job,
                        education_override=(
                            chosen_education
                        ),
                        relationship_override=(
                            chosen_relationship
                        ),
                    )
                )

                st.session_state.biography = (
                    new_biography
                )

                st.session_state.biography_editor = (
                    new_biography
                )

            except (
                FileNotFoundError,
                ValueError,
            ) as error:
                st.error(str(error))


# ---------------------------------------------------------
# RIGHT SIDE: BIOGRAPHY
# ---------------------------------------------------------

with right:
    with st.container(border=True):
        heading_column, copy_column = (
            st.columns([3.2, 1])
        )

        with heading_column:
            st.subheader(
                "📄 Generated Biography"
            )

        with copy_column:
            render_copy_button(
                st.session_state.biography_editor
            )

        st.caption(
            "You can edit the text "
            "before copying it."
        )

        st.text_area(
            "Biography",
            height=330,
            key="biography_editor",
            label_visibility="collapsed",
        )

        character_count = len(
            st.session_state.biography_editor
        )

        word_count = len(
            st.session_state.biography_editor.split()
        )

        st.caption(
            f"{word_count} words · "
            f"{character_count} characters"
        )


# ---------------------------------------------------------
# BOTTOM BENEFITS
# ---------------------------------------------------------

st.markdown(
    """
    <section
        class="zebra-benefits"
        aria-label="ZebraID benefits"
    >
        <div class="zebra-benefit">
            <strong>👤 Realistic</strong>
            <span>
                Natural details from curated data
            </span>
        </div>

        <div class="zebra-benefit">
            <strong>🔀 Highly varied</strong>
            <span>
                Millions of possible combinations
            </span>
        </div>

        <div class="zebra-benefit">
            <strong>⧉ Instant copy</strong>
            <span>
                Copy the complete biography
                in one click
            </span>
        </div>

        <div class="zebra-benefit">
            <strong>🛡️ Fictional</strong>
            <span>
                Designed for creative and
                testing projects
            </span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown(
    """
    <p style="
        text-align: center;
        color: #98A2B3;
        font-size: 0.82rem;
        margin-top: 2.5rem;
    ">
        ZebraID creates fictional personas.
        Do not use generated identities to
        impersonate real people.
    </p>
    """,
    unsafe_allow_html=True,
)
