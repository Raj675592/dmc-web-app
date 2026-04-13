import streamlit as st
from PIL import Image
from predict import load_model, predict
import tempfile
import os

st.title("🗑️ Dustbin & Spill Detector")
st.markdown("Upload an image to check if both a **dustbin** and a **spill** are present.")

@st.cache_resource
def get_model():
    with st.spinner("Loading model..."):
        return load_model()

model = get_model()
st.success("Model loaded successfully!")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    img = Image.open(uploaded_file).convert("RGB")
    st.image(img, caption="Uploaded Image", use_container_width=True)

    # Save to temp file for predict()
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img.save(tmp.name)
    tmp.close()

    with st.spinner("Running prediction..."):
        result = predict(model, tmp.name)

    os.unlink(tmp.name)

    st.markdown("---")
    if result == 1:
        st.error("🚨 Prediction: **1** — Dustbin + Spill BOTH detected!")
    else:
        st.success("✅ Prediction: **0** — No dustbin+spill combination found.")