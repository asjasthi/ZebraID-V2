import streamlit as st
from main import generate_biography

st.set_page_config(
    page_title="ZebraID V2",
    page_icon="🦓",
    layout="centered"
)

COPY_BUTTON_HTML = """
<button id="zebraid-copy-button" type="button" aria-label="Copy generated ZebraID biography">
    <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
    >
        <rect width="14" height="14" x="8" y="8" rx="2"></rect>
        <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path>
    </svg>
    <span id="zebraid-copy-label">Copy</span>
</button>
"""

COPY_BUTTON_CSS = """
#zebraid-copy-button {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 8px 12px;
    border: 1px solid var(--st-border-color, #d0d0d0);
    border-radius: 8px;
    background: transparent;
    color: var(--st-text-color, inherit);
    font: inherit;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition:
        background-color 0.15s ease,
        border-color 0.15s ease,
        transform 0.05s ease;
}

#zebraid-copy-button:hover {
    background: var(--st-secondary-background-color, rgba(128, 128, 128, 0.10));
}

#zebraid-copy-button:active {
    transform: scale(0.98);
}

#zebraid-copy-button.copied {
    border-color: #2e8b57;
}

#zebraid-copy-button svg {
    width: 17px;
    height: 17px;
    flex-shrink: 0;
}
"""

COPY_BUTTON_JS = """
export default function(component) {
    const { data, parentElement } = component;

    const button = parentElement.querySelector("#zebraid-copy-button");
    const label = parentElement.querySelector("#zebraid-copy-label");

    let resetTimer = null;

    label.textContent = "Copy";
    button.classList.remove("copied");

    async function copyText(text) {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text);
            return;
        }

        const textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.left = "-9999px";
        textarea.style.top = "0";

        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();

        const copied = document.execCommand("copy");
        textarea.remove();

        if (!copied) {
            throw new Error("Browser clipboard copy failed.");
        }
    }

    button.onclick = async () => {
        const biography = data?.text ?? "";

        if (!biography) {
            label.textContent = "Nothing to copy";
            return;
        }

        try {
            await copyText(biography);

            label.textContent = "Copied!";
            button.classList.add("copied");

            if (resetTimer) {
                clearTimeout(resetTimer);
            }

            resetTimer = setTimeout(() => {
                label.textContent = "Copy";
                button.classList.remove("copied");
            }, 1500);
        } catch (error) {
            console.error("ZebraID copy failed:", error);
            label.textContent = "Copy failed";

            if (resetTimer) {
                clearTimeout(resetTimer);
            }

            resetTimer = setTimeout(() => {
                label.textContent = "Copy";
            }, 2000);
        }
    };

    return () => {
        button.onclick = null;

        if (resetTimer) {
            clearTimeout(resetTimer);
        }
    };
}
"""

copy_button = st.components.v2.component(
    "zebraid_copy_button",
    html=COPY_BUTTON_HTML,
    css=COPY_BUTTON_CSS,
    js=COPY_BUTTON_JS
)

st.title("🦓 ZebraID V2")

st.write(
    "Generate a random fictional first-person biography."
)

if "biography" not in st.session_state:
    st.session_state.biography = generate_biography()

if st.button(
    "Generate New Biography",
    type="primary",
    use_container_width=True
):
    st.session_state.biography = generate_biography()

st.subheader("Generated Biography")

st.text_area(
    "Output",
    value=st.session_state.biography,
    height=250,
    disabled=True
)

copy_button(
    key="zebraid_copy_button_instance",
    data={"text": st.session_state.biography}
)
