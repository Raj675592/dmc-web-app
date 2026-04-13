import streamlit as st
from PIL import Image
from predict import load_model, predict
import tempfile
import os

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Spill & Dustbin Detector",
    page_icon="🗑️",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #0f0f1a 100%);
    min-height: 100vh;
}

#MainMenu, footer, header {visibility: hidden;}

/* Hero */
.hero {
    text-align: center;
    padding: 2rem 1rem 1.5rem;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    background: linear-gradient(90deg, #e0e0ff, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.3rem;
    letter-spacing: -1px;
}
.hero p {
    color: #9ca3af;
    font-size: 1rem;
    font-weight: 300;
    margin: 0;
}

/* Badge */
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
    margin-bottom: 1.5rem;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 1.8rem;
    backdrop-filter: blur(12px);
    height: 100%;
}

.section-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 1rem;
}

/* Divider between columns */
.col-divider {
    border-left: 1px solid rgba(255,255,255,0.07);
    height: 100%;
    margin: 0 auto;
}

/* File uploader */
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

/* Image */
[data-testid="stImage"] img {
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    width: 100% !important;
}

/* Placeholder box */
.placeholder {
    background: rgba(255,255,255,0.02);
    border: 2px dashed rgba(255,255,255,0.07);
    border-radius: 14px;
    height: 320px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #4b5563;
    font-size: 0.9rem;
    gap: 0.6rem;
}
.placeholder-icon {
    font-size: 2.5rem;
    opacity: 0.4;
}

/* Results */
.result-positive {
    background: linear-gradient(135deg, rgba(239,68,68,0.12), rgba(239,68,68,0.04));
    border: 1px solid rgba(239,68,68,0.35);
    border-radius: 16px;
    padding: 1.6rem;
    text-align: center;
    margin-top: 1rem;
}
.result-negative {
    background: linear-gradient(135deg, rgba(52,211,153,0.12), rgba(52,211,153,0.04));
    border: 1px solid rgba(52,211,153,0.35);
    border-radius: 16px;
    padding: 1.6rem;
    text-align: center;
    margin-top: 1rem;
}
.result-icon { font-size: 2.8rem; margin-bottom: 0.4rem; }
.result-label {
    font-family: 'Syne', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    margin-bottom: 0.3rem;
}
.result-positive .result-label { color: #f87171; }
.result-negative .result-label { color: #34d399; }
.result-sub { font-size: 0.85rem; color: #9ca3af; }

/* Tags */
.tags {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 0.9rem;
}
.tag {
    border-radius: 999px;
    padding: 0.28rem 0.85rem;
    font-size: 0.78rem;
    font-weight: 500;
}
.tag-detected {
    background: rgba(96,165,250,0.15);
    border: 1px solid rgba(96,165,250,0.4);
    color: #93c5fd;
}
.tag-missing {
    background: rgba(107,114,128,0.12);
    border: 1px solid rgba(107,114,128,0.25);
    color: #6b7280;
}

/* Score box */
.score-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    margin-top: 1rem;
}
.score-number {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    line-height: 1;
}
.score-positive { color: #f87171; }
.score-negative { color: #34d399; }
.score-desc {
    font-size: 0.78rem;
    color: #6b7280;
    margin-top: 0.3rem;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.stSpinner > div { border-top-color: #a78bfa !important; }
</style>
""", unsafe_allow_html=True)


# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🗑️ Spill & Dustbin Detector</h1>
    <p>AI-powered hazard detection — upload an image and get instant results</p>
</div>
""", unsafe_allow_html=True)


# ── Load model ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    return load_model()

with st.spinner("Initialising model..."):
    model = get_model()

st.markdown('<div style="text-align:center"><span class="badge">✦ Model ready</span></div>', unsafe_allow_html=True)


# ── Two column layout ──────────────────────────────────────────────────────────
left_col, divider_col, right_col = st.columns([10, 0.3, 10])

# ── LEFT: Upload ───────────────────────────────────────────────────────────────
with left_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📁 Upload Image</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "",
        type=["jpg", "jpeg", "png", "bmp", "webp"],
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        img = Image.open(uploaded_file).convert("RGB")
        st.image(img, caption="", use_container_width=True)
        st.markdown(f"""
        <div style="margin-top:0.8rem; color:#6b7280; font-size:0.8rem; text-align:center;">
            📄 {uploaded_file.name} &nbsp;|&nbsp; {img.size[0]}×{img.size[1]}px
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="placeholder">
            <span class="placeholder-icon">🖼️</span>
            <span>No image uploaded yet</span>
            <span style="font-size:0.78rem;">JPG, PNG, BMP, WEBP supported</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ── DIVIDER ────────────────────────────────────────────────────────────────────
with divider_col:
    st.markdown('<div class="col-divider"></div>', unsafe_allow_html=True)


# ── RIGHT: Output ──────────────────────────────────────────────────────────────
with right_col:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">📊 Detection Output</div>', unsafe_allow_html=True)

    if uploaded_file is None:
        st.markdown("""
        <div class="placeholder">
            <span class="placeholder-icon">🔍</span>
            <span>Results will appear here</span>
            <span style="font-size:0.78rem;">Upload an image on the left to begin</span>
        </div>
        """, unsafe_allow_html=True)

    else:
        # Save temp file and run prediction
        tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
        img.save(tmp.name)
        tmp.close()

        with st.spinner("Analysing image..."):
            result = predict(model, tmp.name)

            # Get individual detections for tags
            _res = model(tmp.name, imgsz=512, conf=0.2, device="cpu", verbose=False)

        os.unlink(tmp.name)

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

        # Score box
        score_class = "score-positive" if result == 1 else "score-negative"
        st.markdown(f"""
        <div class="score-box">
            <div class="score-number {score_class}">{result}</div>
            <div class="score-desc">Prediction Score</div>
        </div>
        """, unsafe_allow_html=True)

        # Result card
        dustbin_tag = '<span class="tag tag-detected">🗑️ Dustbin detected</span>' if dustbin_found else '<span class="tag tag-missing">🗑️ No dustbin</span>'
        spill_tag   = '<span class="tag tag-detected">💧 Spill detected</span>'   if spill_found   else '<span class="tag tag-missing">💧 No spill</span>'

        if result == 1:
            st.markdown(f"""
            <div class="result-positive">
                <div class="result-icon">🚨</div>
                <div class="result-label">Hazard Detected!</div>
                <div class="result-sub">Both dustbin and spill found in the image.</div>
                <div class="tags">{dustbin_tag}{spill_tag}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="result-negative">
                <div class="result-icon">✅</div>
                <div class="result-label">All Clear</div>
                <div class="result-sub">Dustbin and spill not both present.</div>
                <div class="tags">{dustbin_tag}{spill_tag}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)