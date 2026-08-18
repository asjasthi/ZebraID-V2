import streamlit as st
from main import generate_biography

st.set_page_config(
    page_title="ZebraID V2",
    page_icon="🦓",
    layout="centered"
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
    height=250
)