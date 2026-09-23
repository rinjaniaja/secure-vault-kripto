"""
=============================================================================
APLIKASI WEB ENKRIPSI & DEKRIPSI MODERN (TOPIK A: ENKRIPSI ALGORITMA MODERN)
Tugas UTS Keamanan Informasi
Framework: Python + Streamlit (Adaptive Theme & Responsive Mobile/Desktop UI)
Backend: crypto_utils.py (AES-256-GCM & ChaCha20-Poly1305 dengan Scrypt KDF)
=============================================================================
"""

import streamlit as st
import time
import os
import tempfile
import base64

# Import fungsi backend dari crypto_utils.py (logika tidak diubah sama sekali)
from crypto_utils import (
    encrypt_text,
    decrypt_text,
    encrypt_text_chacha,
    decrypt_text_chacha,
    encrypt_file,
    decrypt_file
)

# -----------------------------------------------------------------------------
# 1. KONFIGURASI STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CipherVault Studio | Responsive Crypto Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. ADAPTIVE THEME (AUTO DARK/LIGHT) & RESPONSIVE MOBILE/DESKTOP CSS
# -----------------------------------------------------------------------------
def inject_custom_css():
    st.markdown("""
    <style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500;600;700&display=swap');

    /* Global Typography & Font Family */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ---------------- CSS THEME VARIABLES (DEFAULT LIGHT) ---------------- */
    :root {
        --bg-main: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 40%, #e2e8f0 100%);
        --text-primary: #0f172a;
        --text-secondary: #334155;
        --text-muted: #64748b;
        --card-bg: #ffffff;
        --card-border: #e2e8f0;
        --card-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        --input-bg: #ffffff;
        --input-border: #cbd5e1;
        --tab-bg: #e2e8f0;
        --tab-text: #475569;
        --tech-bg: #f8fafc;
        --sidebar-bg: #ffffff;
        --sidebar-border: #e2e8f0;
        --byte-salt-bg: #e0e7ff;
        --byte-salt-text: #3730a3;
        --byte-nonce-bg: #e0f2fe;
        --byte-nonce-text: #075985;
        --byte-cipher-bg: #dcfce7;
        --byte-cipher-text: #166534;
    }

    /* ---------------- DARK MODE SUPPORT (SYSTEM & STREAMLIT TOGGLE) ---------------- */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-main: radial-gradient(circle at 50% 0%, #171126 0%, #07090e 70%, #040508 100%);
            --text-primary: #f8fafc;
            --text-secondary: #cbd5e1;
            --text-muted: #94a3b8;
            --card-bg: #131722;
            --card-border: #2a324b;
            --card-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
            --input-bg: #0c1017;
            --input-border: #1e293b;
            --tab-bg: rgba(13, 17, 23, 0.75);
            --tab-text: #94a3b8;
            --tech-bg: #070a11;
            --sidebar-bg: #080c14;
            --sidebar-border: rgba(255, 255, 255, 0.08);
            --byte-salt-bg: #1e1b4b;
            --byte-salt-text: #c7d2fe;
            --byte-nonce-bg: #0c4a6e;
            --byte-nonce-text: #bae6fd;
            --byte-cipher-bg: #064e3b;
            --byte-cipher-text: #a7f3d0;
        }
    }

    [data-theme="dark"] {
        --bg-main: radial-gradient(circle at 50% 0%, #171126 0%, #07090e 70%, #040508 100%);
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-muted: #94a3b8;
        --card-bg: #131722;
        --card-border: #2a324b;
        --card-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
        --input-bg: #0c1017;
        --input-border: #1e293b;
        --tab-bg: rgba(13, 17, 23, 0.75);
        --tab-text: #94a3b8;
        --tech-bg: #070a11;
        --sidebar-bg: #080c14;
        --sidebar-border: rgba(255, 255, 255, 0.08);
        --byte-salt-bg: #1e1b4b;
        --byte-salt-text: #c7d2fe;
        --byte-nonce-bg: #0c4a6e;
        --byte-nonce-text: #bae6fd;
        --byte-cipher-bg: #064e3b;
        --byte-cipher-text: #a7f3d0;
    }

    /* Apply Background */
    [data-testid="stAppViewContainer"] {
        background: var(--bg-main) !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* ---------------- BREATHING ROOM FOR DEPLOY & 3 DOTS MENU ---------------- */
    .block-container {
        padding-top: 3.8rem !important;
        padding-bottom: 3rem !important;
        max-width: 1250px;
    }

    /* Dynamic Typography Overrides */
    .stMarkdown, p, span, label, .stCaption {
        color: var(--text-secondary) !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.3px;
    }

    /* ---------------- HERO DASHBOARD BANNER ---------------- */
    .hero-container {
        background: linear-gradient(135deg, #312e81 0%, #4338ca 40%, #0284c7 100%);
        border-radius: 20px;
        padding: 32px 38px;
        margin-top: 10px;
        margin-bottom: 26px;
        box-shadow: 0 16px 32px -8px rgba(67, 56, 202, 0.35);
        color: #ffffff !important;
        position: relative;
        overflow: hidden;
    }

    .hero-container::before {
        content: "";
        position: absolute;
        top: -50%; right: -10%; width: 350px; height: 350px;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0) 70%);
        border-radius: 50%;
    }

    .hero-badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.18);
        backdrop-filter: blur(10px);
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 5px 14px;
        border-radius: 30px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .hero-title {
        color: #ffffff !important;
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.8px;
        margin: 0 0 6px 0;
        line-height: 1.15;
    }

    .hero-subtitle {
        color: #e0e7ff !important;
        font-size: 1.05rem;
        font-weight: 400;
        margin: 0 0 16px 0;
        max-width: 800px;
    }

    .hero-tags {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }

    .tag-item {
        background: rgba(0, 0, 0, 0.22);
        color: #f0f9ff !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 600;
    }

    /* ---------------- STREAMLIT TABS STYLING ---------------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: var(--tab-bg);
        padding: 6px;
        border-radius: 14px;
        border: 1px solid var(--card-border);
    }

    .stTabs [data-baseweb="tab"] {
        height: 46px;
        border-radius: 10px;
        color: var(--tab-text) !important;
        font-weight: 600;
        font-size: 0.96rem;
        border: none !important;
        padding: 0 22px;
        transition: all 0.25s ease;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #4338ca 0%, #0284c7 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 14px rgba(67, 56, 202, 0.35);
    }

    /* ---------------- FORM INPUTS ---------------- */
    .stTextArea textarea, .stTextInput input {
        background-color: var(--input-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 12px !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.98rem !important;
        transition: all 0.2s ease !important;
    }

    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #4338ca !important;
        box-shadow: 0 0 0 3px rgba(67, 56, 202, 0.15) !important;
    }

    /* ---------------- BUTTONS ---------------- */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #4338ca 0%, #2563eb 50%, #0284c7 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.02rem !important;
        letter-spacing: 0.3px !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 6px 20px rgba(67, 56, 202, 0.3) !important;
        cursor: pointer !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 25px rgba(67, 56, 202, 0.45) !important;
        background: linear-gradient(135deg, #3730a3 0%, #1d4ed8 50%, #0369a1 100%) !important;
    }

    div.stDownloadButton > button {
        width: 100%;
        background: linear-gradient(135deg, #059669 0%, #0284c7 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 28px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 6px 20px rgba(5, 150, 105, 0.3) !important;
    }

    div.stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 25px rgba(2, 132, 199, 0.4) !important;
    }

    /* ---------------- TECHNICAL EXPANDER & CODE ---------------- */
    .streamlit-expanderHeader {
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 14px !important;
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: var(--card-shadow);
    }

    .tech-panel-pro {
        background: var(--tech-bg);
        border: 1px solid var(--card-border);
        border-left: 5px solid #4338ca;
        border-radius: 14px;
        padding: 20px;
        font-family: 'Fira Code', monospace;
        font-size: 0.88rem;
        margin-top: 14px;
        margin-bottom: 20px;
    }

    .tech-row-pro {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px dashed var(--input-border);
    }

    .tech-row-pro:last-child {
        border-bottom: none;
    }

    .tech-label-pro {
        color: var(--text-muted);
    }

    .tech-val-pro {
        color: #4338ca;
        font-weight: 600;
    }

    /* Byte Header Layout Visual */
    .byte-diagram {
        display: flex;
        gap: 6px;
        margin-top: 14px;
        font-family: 'Fira Code', monospace;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .byte-block {
        padding: 10px 14px;
        border-radius: 8px;
        text-align: center;
    }
    .byte-salt {
        background: var(--byte-salt-bg);
        color: var(--byte-salt-text);
        border: 1px solid rgba(199, 210, 254, 0.4);
        flex: 1;
    }
    .byte-nonce {
        background: var(--byte-nonce-bg);
        color: var(--byte-nonce-text);
        border: 1px solid rgba(186, 230, 253, 0.4);
        flex: 1;
    }
    .byte-cipher {
        background: var(--byte-cipher-bg);
        color: var(--byte-cipher-text);
        border: 1px solid rgba(187, 247, 208, 0.4);
        flex: 2;
    }

    /* Metrics Card Adaptive */
    [data-testid="stMetric"] {
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        box-shadow: var(--card-shadow) !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] {
        color: #4338ca !important;
        font-family: 'Fira Code', monospace !important;
        font-size: 1.4rem !important;
        font-weight: 700 !important;
    }

    /* ---------------- SIDEBAR ADAPTIVE ---------------- */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--sidebar-border) !important;
    }

    .sidebar-card-pro {
        background: var(--tech-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 18px;
        margin-top: 22px;
    }

    .sidebar-card-title-pro {
        color: #4338ca;
        font-size: 0.88rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .member-item-pro {
        color: var(--text-secondary);
        font-size: 0.88rem;
        padding: 5px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--byte-salt-bg);
        color: var(--byte-salt-text);
        border: 1px solid rgba(199, 210, 254, 0.4);
        padding: 5px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
    }

    .pill-badge-cyan {
        background: var(--byte-nonce-bg);
        color: var(--byte-nonce-text);
        border: 1px solid rgba(186, 230, 253, 0.4);
    }

    /* Footer */
    .footer-pro {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.85rem;
        margin-top: 50px;
        padding: 24px;
        border-top: 1px solid var(--card-border);
    }

    /* ---------------- MOBILE RESPONSIVE MEDIA QUERIES ---------------- */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 4.5rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .hero-container {
            padding: 22px 20px !important;
            border-radius: 16px !important;
            margin-bottom: 20px !important;
        }
        .hero-title {
            font-size: 1.7rem !important;
        }
        .hero-subtitle {
            font-size: 0.95rem !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px !important;
            padding: 4px !important;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0 14px !important;
            font-size: 0.85rem !important;
            height: 42px !important;
        }
        .byte-diagram {
            flex-direction: column !important;
        }
        div.stButton > button, div.stDownloadButton > button {
            padding: 12px 18px !important;
            font-size: 0.95rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# -----------------------------------------------------------------------------
# 3. HERO DASHBOARD BANNER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-badge-pill">🛡️ Tugas UTS Keamanan Informasi — Topik A</div>
    <div class="hero-title">CipherVault Studio Pro</div>
    <div class="hero-subtitle">Platform Enkripsi & Dekripsi Modern AEAD (AES-256-GCM & ChaCha20-Poly1305)</div>
    <div class="hero-tags">
        <span class="tag-item">🔑 Scrypt Key Derivation</span>
        <span class="tag-item">⚡ AES-256-GCM</span>
        <span class="tag-item">🚀 ChaCha20-Poly1305</span>
        <span class="tag-item">🎲 12-Byte Nonce</span>
        <span class="tag-item">🔒 Zero Storage Leak</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. SIDEBAR NAVIGATION & IDENTITAS KELOMPOK
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 📌 Navigasi Modul")
    
    selected_menu = st.radio(
        "Pilih Modul Aplikasi:",
        [
            "🔐 Enkripsi / Dekripsi Teks",
            "📁 Enkripsi / Dekripsi File",
            "ℹ️ Tentang & Dokumentasi"
        ],
        index=0
    )
    
    st.divider()
    st.markdown("### ⚡ Pengaturan Algoritma")
    
    selected_algo = st.selectbox(
        "Pilih Algoritma Kriptografi:",
        ["AES-256-GCM", "ChaCha20-Poly1305"],
        help="AES-256-GCM (Block Cipher AEAD) atau ChaCha20-Poly1305 (Stream Cipher AEAD)."
    )

    # Badges Status Active Mode
    algo_code = "AES-256-GCM" if selected_algo == "AES-256-GCM" else "ChaCha20-Poly1305"
    st.markdown(f"""
    <div style="display:flex; gap:8px; margin-top:12px; flex-wrap:wrap;">
        <span class="pill-badge">🟢 {selected_menu.split()[1]}</span>
        <span class="pill-badge pill-badge-cyan">⚡ {algo_code}</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    
    # Identitas Kelompok UTS Keamanan Informasi
    st.markdown("""
    <div class="sidebar-card-pro">
        <div class="sidebar-card-title-pro">👥 KELOMPOK UTS KI</div>
        <div class="member-item-pro">🔑 <span>Topik A: Enkripsi Modern</span></div>
        <div class="member-item-pro">🧪 <span>KDF: Scrypt (N=16384, r=8, p=1)</span></div>
        <div class="member-item-pro">🛡️ <span>Cipher: AES-GCM & ChaCha20</span></div>
        <div class="member-item-pro">📦 <span>Format: Salt+Nonce+Cipher+Tag</span></div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. HELPER FUNCTION: PANEL DETAIL TEKNIS (EXPANDER INTERAKTIF)
# -----------------------------------------------------------------------------
def render_technical_panel(algo_name, process_time_ms, input_size_bytes, output_size_bytes, mode="text"):
    """
    Menampilkan detail teknis eksekusi dalam bentuk expander interaktif.
    Mencakup algoritma, waktu eksekusi (ms), ukuran input/output, dan visualisasi susunan byte header.
    """
    with st.expander("🔍 Detail Teknis & Statistik Eksekusi Kriptografi (Klik untuk membuka)", expanded=True):
        overhead = output_size_bytes - input_size_bytes
        overhead_str = f"+{overhead} Byte" if overhead >= 0 else f"{overhead} Byte"
        
        st.markdown(f"""
        <div class="tech-panel-pro">
            <div class="tech-row-pro">
                <span class="tech-label-pro">🔑 Algoritma Kriptografi:</span>
                <span class="tech-val-pro">{algo_name}</span>
            </div>
            <div class="tech-row-pro">
                <span class="tech-label-pro">🧪 Key Derivation Function (KDF):</span>
                <span class="tech-val-pro">Scrypt (Salt: 16 Byte, Length: 32 Byte / 256-bit)</span>
            </div>
            <div class="tech-row-pro">
                <span class="tech-label-pro">⚡ Waktu Eksekusi:</span>
                <span class="tech-val-pro">{process_time_ms:.2f} ms</span>
            </div>
            <div class="tech-row-pro">
                <span class="tech-label-pro">📥 Ukuran Data Input:</span>
                <span class="tech-val-pro">{input_size_bytes:,} Byte</span>
            </div>
            <div class="tech-row-pro">
                <span class="tech-label-pro">📤 Ukuran Data Output:</span>
                <span class="tech-val-pro">{output_size_bytes:,} Byte</span>
            </div>
            <div class="tech-row-pro">
                <span class="tech-label-pro">📦 Overhead Header Binary:</span>
                <span class="tech-val-pro">{overhead_str} (Salt 16B + Nonce 12B + Tag 16B)</span>
            </div>
            
            <div style="margin-top:15px; font-weight:700;">Visualisasi Layout Structure Header Data Binary:</div>
            <div class="byte-diagram">
                <div class="byte-block byte-salt">Salt (16 Byte)</div>
                <div class="byte-block byte-nonce">Nonce (12 Byte)</div>
                <div class="byte-block byte-cipher">Ciphertext + Auth Tag (16B)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("⚡ Waktu Eksekusi", f"{process_time_ms:.2f} ms")
        with col2:
            st.metric("📥 Input Size", f"{input_size_bytes:,} B")
        with col3:
            st.metric("📤 Output Size", f"{output_size_bytes:,} B")
        with col4:
            st.metric("📊 Overhead Metadata", overhead_str if mode=="encrypt" else "0 B")

# -----------------------------------------------------------------------------
# 6. MODUL 1: ENKRIPSI & DEKRIPSI TEKS
# -----------------------------------------------------------------------------
if selected_menu == "🔐 Enkripsi / Dekripsi Teks":
    st.subheader("🔐 Modul Enkripsi & Dekripsi Teks Rahasia")
    st.caption("Amankan pesan teks rahasia menjadi ciphertext Base64 terotentikasi atau dekripsi pesan kembali ke bentuk semula.")

    tab_enc_text, tab_dec_text = st.tabs(["🔒 Enkripsi Teks", "🔓 Dekripsi Teks"])

    # --- TAB ENKRIPSI TEKS ---
    with tab_enc_text:
        col_in, col_opt = st.columns([2, 1])
        
        with col_opt:
            algo_text_enc = st.selectbox(
                "Pilih Algoritma Enkripsi:",
                ["AES-256-GCM", "ChaCha20-Poly1305"],
                index=0 if selected_algo == "AES-256-GCM" else 1,
                key="algo_text_enc"
            )
            pass_text_enc = st.text_input(
                "Password / Kunci Rahasia:",
                type="password",
                key="pass_text_enc",
                placeholder="Ketik password rahasia..."
            )
            
        with col_in:
            plaintext_input = st.text_area(
                "Teks Asli (Plaintext):",
                height=150,
                placeholder="Ketik atau tempel teks rahasia yang ingin dienkripsi di sini...",
                key="plaintext_input"
            )

        if st.button("🚀 Jalankan Enkripsi Teks Now", key="btn_enc_text"):
            if not plaintext_input.strip():
                st.warning("⚠️ Harap masukkan teks yang ingin dienkripsi!")
            elif not pass_text_enc:
                st.warning("⚠️ Harap masukkan password enkripsi!")
            else:
                try:
                    start_time = time.perf_counter()
                    
                    if algo_text_enc == "AES-256-GCM":
                        ciphertext_b64 = encrypt_text(plaintext_input, pass_text_enc)
                    else:
                        ciphertext_b64 = encrypt_text_chacha(plaintext_input, pass_text_enc)
                        
                    end_time = time.perf_counter()
                    process_time_ms = (end_time - start_time) * 1000

                    st.success("✅ Teks berhasil dienkripsi!")
                    
                    st.markdown("**Hasil Ciphertext (Format Base64):**")
                    st.code(ciphertext_b64, language="text")
                    
                    input_bytes = len(plaintext_input.encode('utf-8'))
                    output_bytes = len(ciphertext_b64.encode('utf-8'))
                    
                    render_technical_panel(
                        algo_name=algo_text_enc,
                        process_time_ms=process_time_ms,
                        input_size_bytes=input_bytes,
                        output_size_bytes=output_bytes,
                        mode="encrypt"
                    )

                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan teknis: {str(e)}")

    # --- TAB DEKRIPSI TEKS ---
    with tab_dec_text:
        col_cin, col_copt = st.columns([2, 1])
        
        with col_copt:
            algo_text_dec = st.selectbox(
                "Pilih Algoritma Dekripsi:",
                ["AES-256-GCM", "ChaCha20-Poly1305"],
                index=0 if selected_algo == "AES-256-GCM" else 1,
                key="algo_text_dec",
                help="Pastikan algoritma dekripsi sama dengan saat enkripsi dilakukan."
            )
            pass_text_dec = st.text_input(
                "Password / Kunci Dekripsi:",
                type="password",
                key="pass_text_dec",
                placeholder="Masukkan password untuk membuka..."
            )
            
        with col_cin:
            ciphertext_input = st.text_area(
                "Ciphertext (Format Base64):",
                height=150,
                placeholder="Tempel string Base64 terenkripsi di sini...",
                key="ciphertext_input"
            )

        if st.button("🔓 Jalankan Dekripsi Teks Now", key="btn_dec_text"):
            if not ciphertext_input.strip():
                st.warning("⚠️ Harap masukkan string Base64 ciphertext!")
            elif not pass_text_dec:
                st.warning("⚠️ Harap masukkan password dekripsi!")
            else:
                try:
                    start_time = time.perf_counter()
                    
                    if algo_text_dec == "AES-256-GCM":
                        decrypted_plain = decrypt_text(ciphertext_input.strip(), pass_text_dec)
                    else:
                        decrypted_plain = decrypt_text_chacha(ciphertext_input.strip(), pass_text_dec)
                        
                    end_time = time.perf_counter()
                    process_time_ms = (end_time - start_time) * 1000

                    st.success("✅ Dekripsi Berhasil! Otentikasi dan integritas data terverifikasi.")
                    
                    st.markdown("**Hasil Teks Asli (Plaintext):**")
                    st.text_area("Plaintext Hasil Dekripsi:", value=decrypted_plain, height=120, disabled=True)
                    
                    input_bytes = len(ciphertext_input.encode('utf-8'))
                    output_bytes = len(decrypted_plain.encode('utf-8'))
                    
                    render_technical_panel(
                        algo_name=algo_text_dec,
                        process_time_ms=process_time_ms,
                        input_size_bytes=input_bytes,
                        output_size_bytes=output_bytes,
                        mode="decrypt"
                    )

                except ValueError as ve:
                    st.error(f"🛑 {str(ve)}")
                except Exception as e:
                    st.error("🛑 Dekripsi gagal: Format Base64 tidak valid, password salah, atau data telah diubah!")

# -----------------------------------------------------------------------------
# 7. MODUL 2: ENKRIPSI & DEKRIPSI FILE
# -----------------------------------------------------------------------------
elif selected_menu == "📁 Enkripsi / Dekripsi File":
    st.subheader("📁 Modul Enkripsi & Dekripsi File Biner")
    st.caption("Amankan file biner (PDF, Gambar, Dokumen, Zip, dll) dengan enkripsi AEAD tingkat tinggi.")

    tab_enc_file, tab_dec_file = st.tabs(["🔒 Enkripsi File", "🔓 Dekripsi File"])

    # --- TAB ENKRIPSI FILE ---
    with tab_enc_file:
        col_f1, col_f2 = st.columns([2, 1])
        
        with col_f2:
            algo_file_enc = st.selectbox(
                "Pilih Algoritma File:",
                ["AES-256-GCM", "ChaCha20-Poly1305"],
                index=0 if selected_algo == "AES-256-GCM" else 1,
                key="algo_file_enc"
            )
            pass_file_enc = st.text_input(
                "Password File Enkripsi:",
                type="password",
                key="pass_file_enc",
                placeholder="Masukkan password..."
            )
            
        with col_f1:
            uploaded_file_enc = st.file_uploader(
                "Upload File untuk Dienkripsi:",
                type=None,
                key="uploaded_file_enc",
                help="Mendukung semua jenis file biner."
            )

        if st.button("🚀 Enkripsi File Sekarang", key="btn_file_enc"):
            if uploaded_file_enc is None:
                st.warning("⚠️ Harap upload file terlebih dahulu!")
            elif not pass_file_enc:
                st.warning("⚠️ Harap masukkan password enkripsi!")
            else:
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        input_path = os.path.join(tmpdir, uploaded_file_enc.name)
                        output_path = os.path.join(tmpdir, f"{uploaded_file_enc.name}.enc")
                        
                        with open(input_path, "wb") as f:
                            f.write(uploaded_file_enc.getbuffer())
                            
                        algo_param = "chacha" if algo_file_enc == "ChaCha20-Poly1305" else "aes"
                        
                        start_time = time.perf_counter()
                        encrypt_file(input_path, output_path, pass_file_enc, algorithm=algo_param)
                        end_time = time.perf_counter()
                        
                        process_time_ms = (end_time - start_time) * 1000
                        
                        with open(output_path, "rb") as f:
                            encrypted_bytes = f.read()
                            
                        input_size = len(uploaded_file_enc.getbuffer())
                        output_size = len(encrypted_bytes)
                        
                        st.success(f"✅ File '{uploaded_file_enc.name}' berhasil dienkripsi!")
                        
                        st.download_button(
                            label=f"⬇️ Unduh File Terenkripsi ({uploaded_file_enc.name}.enc)",
                            data=encrypted_bytes,
                            file_name=f"{uploaded_file_enc.name}.enc",
                            mime="application/octet-stream"
                        )
                        
                        render_technical_panel(
                            algo_name=f"{algo_file_enc} (Biner File)",
                            process_time_ms=process_time_ms,
                            input_size_bytes=input_size,
                            output_size_bytes=output_size,
                            mode="encrypt"
                        )

                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan saat memproses file: {str(e)}")

    # --- TAB DEKRIPSI FILE ---
    with tab_dec_file:
        col_fd1, col_fd2 = st.columns([2, 1])
        
        with col_fd2:
            algo_file_dec = st.selectbox(
                "Pilih Algoritma Dekripsi File:",
                ["AES-256-GCM", "ChaCha20-Poly1305"],
                index=0 if selected_algo == "AES-256-GCM" else 1,
                key="algo_file_dec"
            )
            pass_file_dec = st.text_input(
                "Password File Dekripsi:",
                type="password",
                key="pass_file_dec",
                placeholder="Masukkan password..."
            )
            
        with col_fd1:
            uploaded_file_dec = st.file_uploader(
                "Upload File Terenkripsi (.enc):",
                type=None,
                key="uploaded_file_dec"
            )

        if st.button("🔓 Dekripsi File Sekarang", key="btn_file_dec"):
            if uploaded_file_dec is None:
                st.warning("⚠️ Harap upload file terenkripsi terlebih dahulu!")
            elif not pass_file_dec:
                st.warning("⚠️ Harap masukkan password dekripsi!")
            else:
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        input_path = os.path.join(tmpdir, uploaded_file_dec.name)
                        
                        orig_name = uploaded_file_dec.name
                        if orig_name.endswith(".enc"):
                            out_name = orig_name[:-4]
                        else:
                            out_name = f"decrypted_{orig_name}"
                            
                        output_path = os.path.join(tmpdir, out_name)
                        
                        with open(input_path, "wb") as f:
                            f.write(uploaded_file_dec.getbuffer())
                            
                        algo_param = "chacha" if algo_file_dec == "ChaCha20-Poly1305" else "aes"
                        
                        start_time = time.perf_counter()
                        decrypt_file(input_path, output_path, pass_file_dec, algorithm=algo_param)
                        end_time = time.perf_counter()
                        
                        process_time_ms = (end_time - start_time) * 1000
                        
                        with open(output_path, "rb") as f:
                            decrypted_bytes = f.read()
                            
                        input_size = len(uploaded_file_dec.getbuffer())
                        output_size = len(decrypted_bytes)
                        
                        st.success(f"✅ File berhasil didekripsi! Integritas & otentikasi data terverifikasi.")
                        
                        st.download_button(
                            label=f"⬇️ Unduh File Hasil Dekripsi ({out_name})",
                            data=decrypted_bytes,
                            file_name=out_name,
                            mime="application/octet-stream"
                        )
                        
                        render_technical_panel(
                            algo_name=f"{algo_file_dec} (Biner File)",
                            process_time_ms=process_time_ms,
                            input_size_bytes=input_size,
                            output_size_bytes=output_size,
                            mode="decrypt"
                        )

                except ValueError as ve:
                    st.error(f"🛑 {str(ve)}")
                except Exception as e:
                    st.error("🛑 Dekripsi file gagal: Password salah, file corrupt, atau data telah diubah!")

# -----------------------------------------------------------------------------
# 8. MODUL 3: TENTANG APLIKASI & DOKUMENTASI KRIPTOGRAFI
# -----------------------------------------------------------------------------
elif selected_menu == "ℹ️ Tentang & Dokumentasi":
    st.subheader("ℹ️ Dokumentasi Teknis & Penjelasan Kriptografi Modern")
    st.caption("Materi dan konsep dasar keamanan informasi yang diimplementasikan dalam aplikasi ini.")

    # 1. Algoritma AEAD Modern
    with st.expander("🔑 1. Algoritma AEAD Modern (AES-256-GCM vs ChaCha20-Poly1305)", expanded=True):
        st.markdown("""
        Aplikasi ini mengimplementasikan dua algoritma standar industri berbasis **AEAD (Authenticated Encryption with Associated Data)**:
        
        *   **AES-256-GCM (Galois/Counter Mode):**
            *   Mengkombinasikan mode enkripsi simetris Counter (CTR) berukuran kunci 256-bit dengan otentikasi tag Galois (GHASH).
            *   Menyediakan dua aspek keamanan sekaligus: **Kerahasiaan (Confidentiality)** dan **Integritas/Otentikasi (Authenticity)**.
            *   Jika ada pihak ketiga yang mengedit 1 bit saja dari ciphertext, proses dekripsi akan langsung gagal dengan `InvalidTag`.
        
        *   **ChaCha20-Poly1305:**
            *   Algoritma Stream Cipher modern ciptaan Daniel J. Bernstein yang digabungkan dengan MAC Poly1305.
            *   Dirancang memiliki kinerja tinggi pada platform software/CPU yang tidak memiliki akselerasi hardware AES (misalnya perangkat mobile/ARM).
            *   Tahan terhadap serangan *Cache-Timing Side-Channel*.
        """)

    # 2. Key Derivation Function (Scrypt + Salt)
    with st.expander("🧪 2. Key Derivation Function (Scrypt KDF) & Pentingnya Salt"):
        st.markdown("""
        Password yang diketik manusia tidak bisa langsung digunakan sebagai kunci AES/ChaCha karena memiliki entropi rendah.
        
        *   **Scrypt KDF:**
            *   Menggunakan parameter $N=16384$ (cost factor), $r=8$ (block size), dan $p=1$ (parallelization) untuk menghasilkan kunci 256-bit (32 byte) acak murni.
            *   Scrypt dirancang khusus bersifat **Memory-Hard**, sehingga sangat lambat jika diserang dengan perangkat khusus seperti GPU Brute-Force atau ASIC.
        
        *   **Mengapa Salt (16 Byte Acak) Sangat Penting?**
            *   Salt adalah sekumpulan byte acak unik yang digabungkan dengan password saat proses penurunan kunci (`derive_key`).
            *   Mencegah serangan **Rainbow Table** (tabel hash terkomputasi). Dua user dengan password persis sama ("password123") akan menghasilkan kunci biner yang berbeda total karena Salt mereka acak dan berbeda.
        """)

    # 3. Nonce / IV Acak
    with st.expander("🎲 3. Peran Nonce / IV Acak (12 Byte) & Bahaya IV Reuse"):
        st.markdown(r"""
        *   **Nonce (Number used ONCE) / Initialization Vector (IV):**
            *   Setiap operasi enkripsi menghasilkan Nonce acak 12-byte (96-bit) yang unik menggunakan `os.urandom(12)`.
        
        *   **Bahaya IV Reuse Attack:**
            *   Jika kunci dan Nonce yang sama digunakan untuk mengenkripsi dua pesan yang berbeda, penyerang dapat melakukan operasi $XOR$ pada kedua ciphertext ($C_1 \oplus C_2 = P_1 \oplus P_2$).
            *   Hal ini membocorkan struktur plaintext tanpa perlu membobol kunci! Oleh karena itu, Nonce **wajib acak dan hanya digunakan satu kali**.
        """)

    # 4. Format Output Biner Header
    with st.expander("📦 4. Format Output & Susunan Header Binary"):
        st.markdown("""
        Hasil enkripsi teks maupun file dibungkus dalam susunan byte terstruktur:
        
        ```text
        +-----------------------+-----------------------+----------------------------------+
        |  Salt (Byte 0-15)     |  Nonce (Byte 16-27)   |  Ciphertext + Tag (Byte 28...end)|
        |      (16 Byte)        |      (12 Byte)        |       (Authentication Tag 16B)   |
        +-----------------------+-----------------------+----------------------------------+
        ```
        
        1. **Byte 0 s/d 15 (16B):** Salt acak untuk menurunkan kunci saat dekripsi.
        2. **Byte 16 s/d 27 (12B):** Nonce acak untuk menginisialisasi cipher.
        3. **Byte 28 s/d Selesai:** Ciphertext asli + 16-byte Authentication Tag di ujung data.
        
        *Pada modul teks, susunan biner ini dienkode ke format **Base64** agar mudah disalin dan ditransmisikan.*
        """)

# -----------------------------------------------------------------------------
# 9. FOOTER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="footer-pro">
    🛡️ <strong>CipherVault Studio Pro Web Platform</strong> | Topik A: Enkripsi Algoritma Modern (Tugas UTS Keamanan Informasi)<br>
    Jalankan via Terminal: <code>streamlit run app.py</code>
</div>
""", unsafe_allow_html=True)