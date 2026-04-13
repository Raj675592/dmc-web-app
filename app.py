import streamlit as st
from PIL import Image
from predict import load_model, predict
import tempfile
import os

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Spill & Dustbin Detector",
    page_icon="🗑️",
    layout="centered",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #0f0f1a 100%);
    min-height: 100vh;
}

/* Hide default streamlit header */
#MainMenu, footer, header {visibility: hidden;}

/* Hero section */
.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    background: linear-gradient(90deg, #e0e0ff, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.4rem;
    letter-spacing: -1px;
}
.hero p {
    color: #9ca3af;
    font-size: 1rem;
    font-weight: 300;
    margin: 0;
}

/* Card */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 2rem;
    margin: 1.2rem 0;
    backdrop-filter: blur(12px);
}

/* Upload area */
.upload-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 0.5rem;
}

/* File uploader override */
[data-testid="stFileUploader"] {
    background: rgba(167,139,250,0.05) !important;
    border: 2px dashed rgba(167,139,250,0.3) !important;
    border-radius: 14px !important;
    padding: 1rem !important;
    transition: border-color 0.3s;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(167,139,250,0.7) !important;
}

/* Image display */
[data-testid="stImage"] img {
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}

/* Result boxes */
.result-positive {
    background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.05));
    border: 1px solid rgba(239,68,68,0.4);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    text-align: center;
    margin-top: 1rem;
}
.result-negative {
    background: linear-gradient(135deg, rgba(52,211,153,0.15), rgba(52,211,153,0.05));
    border: 1px solid rgba(52,211,153,0.4);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    text-align: center;
    margin-top: 1rem;
}
.result-icon {
    font-size: 2.8rem;
    margin-bottom: 0.4rem;
}
.result-label {
    font-family: 'Syne', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}
.result-positive .result-label { color: #f87171; }
.result-negative .result-label { color: #34d399; }
.result-sub {
    font-size: 0.88rem;
    color: #9ca3af;
}

/* Status badge */
.badge {
    display: inline-block;
    background: rgba(52,211,153,0.15);
    border: 1px solid rgba(52,211,153,0.35);
    color: #34d399;
    border-radius: 999px;
    padding: 0.25rem 0.85rem;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.5px;
    margin-bottom: 1.2rem;
}

/* Detection tags */
.tags {
    display: flex;
    gap: 0.6rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 0.8rem;
}
.tag {
    border-radius: 999px;
    padding: 0.3rem 0.9rem;
    font-size: 0.8rem;
    font-weight: 500;
}
.tag-detected {
    background: rgba(96,165,250,0.15);
    border: 1px solid rgba(96,165,250,0.4);
    color: #93c5fd;
}
.tag-missing {
    background: rgba(107,114,128,0.15);
    border: 1px solid rgba(107,114,128,0.3);
    color: #6b7280;
}

/* Divider */
.divider {
    border: none;
    border-top: 1px solid rgba(255,255,255,0.07);
    margin: 1.5rem 0;
}

/* Spinner override */
.stSpinner > div {
    border-top-color: #a78bfa !important;
}
</style>
""", unsafe_allow_html=True)


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🗑️ Spill Detector</h1>
    <p>AI-powered dustbin &amp; spill detection in one click</p>
</div>
""", unsafe_allow_html=True)


# ── Load model ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    return load_model()

with st.spinner("Initialising model..."):
    model = get_model()

st.markdown('<div style="text-align:center"><span class="badge">✦ Model ready</span></div>', unsafe_allow_html=True)


# ── Upload card ────────────────────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="upload-label">Upload Image</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "",
    type=["jpg", "jpeg", "png", "bmp", "webp"],
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)


# ── Prediction ─────────────────────────────────────────────────────────────────
if uploaded_file is not None:

    img = Image.open(uploaded_file).convert("RGB")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.image(img, caption="", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
    img.save(tmp.name)
    tmp.close()

    with st.spinner("Analysing image..."):
        result = predict(model, tmp.name)

    os.unlink(tmp.name)

    # ── Determine individual detections for tags ───────────────────────────────
    # Re-run a quick check to get individual class flags for display
    from PIL import Image as _Img
    import tempfile as _tmp, os as _os
    _t = _tmp.NamedTemporaryFile(suffix=".jpg", delete=False)
    img.resize((512, 512)).save(_t.name)
    _t.close()
    _res = model(_t.name, imgsz=512, conf=0.2, device="cpu", verbose=False)
    _os.unlink(_t.name)

    dustbin_found = any(
        int(b.cls[0]) == 0
        for r in _res if r.boxes
        for b in r.boxes
    )
    spill_found = any(
        int(b.cls[0]) == 1
        for r in _res if r.boxes
        for b in r.boxes
    )

    # ── Result display ─────────────────────────────────────────────────────────
    if result == 1:
        st.markdown(f"""
        <div class="result-positive">
            <div class="result-icon">🚨</div>
            <div class="result-label">Hazard Detected — Score: 1</div>
            <div class="result-sub">Both a dustbin and a spill were found in the image.</div>
            <div class="tags">
                <span class="tag tag-detected">🗑️ Dustbin detected</span>
                <span class="tag tag-detected">💧 Spill detected</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        dustbin_tag = '<span class="tag tag-detected">🗑️ Dustbin detected</span>' if dustbin_found else '<span class="tag tag-missing">🗑️ No dustbin</span>'
        spill_tag   = '<span class="tag tag-detected">💧 Spill detected</span>'   if spill_found   else '<span class="tag tag-missing">💧 No spill</span>'

        st.markdown(f"""
        <div class="result-negative">
            <div class="result-icon">✅</div>
            <div class="result-label">All Clear — Score: 0</div>
            <div class="result-sub">Dustbin and spill not both present.</div>
            <div class="tags">
                {dustbin_tag}
                {spill_tag}
            </div>
        </div>
        """, unsafe_allow_html=True)