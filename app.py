"""
=============================================================================
APLIKASI WEB ENKRIPSI & DEKRIPSI MODERN (TOPIK A: ENKRIPSI ALGORITMA MODERN)
Tugas UTS Keamanan Informasi
Framework: Python + Streamlit (Adaptive Theme & Responsive Mobile/Desktop UI)
Backend: crypto_utils.py, hybrid_crypto.py, image_encryption_demo.py
=============================================================================
"""

import streamlit as st
import time
import os
import tempfile
import base64
from PIL import Image
import io

# Import fungsi backend dari crypto_utils.py (logika tidak diubah sama sekali)
from crypto_utils import (
    encrypt_text,
    decrypt_text,
    encrypt_text_chacha,
    decrypt_text_chacha,
    encrypt_file,
    decrypt_file
)

# Import fungsi fitur pengayaan
from hybrid_crypto import generate_rsa_keypair, encrypt_hybrid, decrypt_hybrid
from image_encryption_demo import (
    buat_citra_demo,
    enkripsi_ecb,
    enkripsi_gcm,
    bytes_ke_citra
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
    # ---------------------------------------------------------------
    # Tema gelap/terang di sini dikontrol LANGSUNG oleh toggle
    # "Tampilan Aplikasi" di sidebar (via st.session_state), BUKAN
    # oleh menu Dark/Light bawaan Streamlit (titik tiga kanan atas)
    # ataupun tema OS/browser. Ini supaya hasilnya PASTI berubah saat
    # toggle di-klik, tidak tergantung pengaturan di luar aplikasi.
    # ---------------------------------------------------------------
    if "app_theme_mode" not in st.session_state:
        st.session_state["app_theme_mode"] = "☀️ Terang"

    is_dark = st.session_state["app_theme_mode"] == "🌙 Gelap"

    if is_dark:
        theme_vars = """
        --bg-main: #0a0f1c;
        --bg-dot: rgba(148, 197, 214, 0.07);
        --text-primary: #e6edf5;
        --text-secondary: #b9c4d4;
        --text-muted: #7c8aa5;
        --card-bg: #101827;
        --card-border: #1f2c42;
        --card-shadow: 0 8px 24px rgba(0, 0, 0, 0.45);
        --input-bg: #0d1420;
        --input-border: #26344c;
        --tab-text: #6b7a93;
        --tech-bg: #0c1220;
        --sidebar-bg: #0a1120;
        --sidebar-border: #1f2c42;
        --byte-salt-bg: #0e2a2c;
        --byte-salt-text: #5eead4;
        --byte-nonce-bg: #0d2338;
        --byte-nonce-text: #7dd3fc;
        --byte-cipher-bg: #131b32;
        --byte-cipher-text: #93c5fd;
        """
    else:
        theme_vars = """
        --bg-main: #f3f6fb;
        --bg-dot: rgba(15, 60, 90, 0.05);
        --text-primary: #0f172a;
        --text-secondary: #3b4a63;
        --text-muted: #6b7a93;
        --card-bg: #ffffff;
        --card-border: #dfe6f0;
        --card-shadow: 0 2px 10px rgba(15, 40, 70, 0.06);
        --input-bg: #ffffff;
        --input-border: #cdd7e5;
        --tab-text: #8b98af;
        --tech-bg: #eef2f8;
        --sidebar-bg: #ffffff;
        --sidebar-border: #e2e8f2;
        --byte-salt-bg: #e6fbf6;
        --byte-salt-text: #0f766e;
        --byte-nonce-bg: #eaf3fe;
        --byte-nonce-text: #175cd3;
        --byte-cipher-bg: #eef1fb;
        --byte-cipher-text: #3538cd;
        """

    css_template = """
    <style>
    /* Google Fonts Import - Technical / Dashboard Look */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Global Typography & Font Family */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* ---------------- SEMBUNYIKAN MENU BAWAAN STREAMLIT (TITIK TIGA) ----------------
       Menu "⋮" bawaan Streamlit punya pengaturan tema sendiri (terpisah dari toggle
       kita di sidebar) yang TIDAK BISA disinkronkan dengan variabel CSS custom di
       aplikasi ini (keterbatasan Streamlit, bukan bug kode kita). Supaya tidak ada
       2 kontrol tema yang membingungkan / tidak sinkron, menu ini disembunyikan
       sepenuhnya. Satu-satunya kontrol tema yang aktif adalah toggle di sidebar kiri.
       Ini murni tampilan (CSS), tidak menyentuh logika aplikasi sama sekali. */
    #MainMenu {
        visibility: hidden !important;
    }

    /* =================================================================
       CATATAN PENTING:
       Nilai warna tema (terang/gelap) di bawah ini DIISI DARI PYTHON
       (lihat theme_vars di atas), berdasarkan toggle sidebar. Bagian
       --accent, --accent-soft, --btn-bg, --btn-bg-hover, --btn-text
       SENGAJA tetap sama nilainya di kedua mode supaya warna tombol
       & aksen emas TIDAK PERNAH berubah walau tampilan diganti.
       Yang berubah hanya latar, kartu, dan warna teks dasar.
       ================================================================= */

    /* ---------------- CSS THEME VARIABLES (DIISI DARI PYTHON) ---------------- */
    :root {
    __THEME_VARS__

        /* --- FIXED deep navy + teal/cyan "dark tech" accent (tidak berubah per tema) --- */
        --accent: #14b8a6;
        --accent-2: #38bdf8;
        --accent-soft: rgba(20, 184, 166, 0.14);
        --btn-bg: #0f172a;
        --btn-bg-hover: #16233b;
        --btn-text: #5eead4;
    }

    /* Apply Background (dot-grid pattern - kesan dashboard teknis) */
    [data-testid="stAppViewContainer"] {
        background-color: var(--bg-main) !important;
        background-image: radial-gradient(var(--bg-dot) 1.2px, transparent 1.2px) !important;
        background-size: 22px 22px !important;
        color: var(--text-primary) !important;
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    /* ---------------- BREATHING ROOM FOR DEPLOY & 3 DOTS MENU ---------------- */
    .block-container {
        padding-top: 3.4rem !important;
        padding-bottom: 2.6rem !important;
        max-width: 1120px;
    }

    /* Dynamic Typography Overrides */
    .stMarkdown, p, span, label, .stCaption {
        color: var(--text-secondary) !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        letter-spacing: -0.2px;
    }

    /* ---------------- HERO DASHBOARD HEADER (GRADIENT TOP BAR, LAYOUT BARU) ---------------- */
    .hero-container {
        background: var(--card-bg);
        border: 1px solid var(--card-border);
        border-radius: 16px;
        padding: 0;
        margin-top: 6px;
        margin-bottom: 22px;
        box-shadow: var(--card-shadow);
        position: relative;
        overflow: hidden;
    }

    .hero-container::before {
        content: "";
        display: block;
        height: 4px;
        width: 100%;
        background: linear-gradient(90deg, var(--accent) 0%, var(--accent-2) 100%);
    }

    .hero-inner {
        padding: 22px 28px 24px 28px;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        flex-wrap: wrap;
        gap: 18px;
    }

    .hero-badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--accent-soft);
        color: var(--accent) !important;
        border: 1px solid var(--card-border);
        padding: 4px 12px;
        border-radius: 30px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .hero-title {
        color: var(--text-primary) !important;
        font-size: 1.85rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0 0 6px 0;
        line-height: 1.2;
    }

    .hero-subtitle {
        color: var(--text-muted) !important;
        font-size: 0.94rem;
        font-weight: 400;
        margin: 0;
        max-width: 620px;
    }

    .hero-tags {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
        justify-content: flex-end;
        align-items: center;
    }

    .tag-item {
        background: var(--tech-bg);
        color: var(--text-secondary) !important;
        border: 1px solid var(--card-border);
        padding: 4px 11px;
        border-radius: 8px;
        font-size: 0.72rem;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ---------------- NAVIGASI MODUL: SEGMENTED PILL TABS (HORIZONTAL, DI ATAS) ---------------- */
    .nav-radio-wrap div[role="radiogroup"] {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        background: var(--tech-bg);
        border: 1px solid var(--card-border);
        border-radius: 14px;
        padding: 6px;
        margin-bottom: 22px;
    }

    .nav-radio-wrap div[role="radiogroup"] label {
        background: transparent;
        border: 1px solid transparent;
        border-radius: 10px;
        padding: 9px 16px;
        margin: 0 !important;
        cursor: pointer;
        transition: all 0.15s ease;
    }

    .nav-radio-wrap div[role="radiogroup"] label:hover {
        background: var(--card-bg);
    }

    .nav-radio-wrap div[role="radiogroup"] label > div:first-child {
        display: none !important;
    }

    .nav-radio-wrap div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] p {
        color: var(--text-secondary) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    .nav-radio-wrap div[role="radiogroup"] label:has(input:checked) {
        background: var(--btn-bg) !important;
        border-color: var(--accent) !important;
    }

    .nav-radio-wrap div[role="radiogroup"] label:has(input:checked) div[data-testid="stMarkdownContainer"] p {
        color: var(--btn-text) !important;
    }

    /* ---------------- STREAMLIT TABS STYLING (UNDERLINE, MINIMAL) ---------------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 22px;
        background-color: transparent;
        padding: 0;
        border-radius: 0;
        border-bottom: 1px solid var(--card-border);
    }

    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 0;
        color: var(--tab-text) !important;
        font-weight: 500;
        font-size: 0.92rem;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        padding: 0 2px;
        transition: all 0.2s ease;
        background: transparent !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary) !important;
    }

    .stTabs [aria-selected="true"] {
        background: transparent !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        border-bottom: 2px solid var(--accent) !important;
        box-shadow: none;
    }

    /* ---------------- FORM INPUTS ---------------- */
    .stTextArea textarea, .stTextInput input {
        background-color: var(--input-bg) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.95rem !important;
        transition: all 0.15s ease !important;
    }

    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-soft) !important;
    }

    /* ---------------- HASIL DEKRIPSI (TEXTAREA DISABLED) TETAP TERBACA DI TEMA GELAP ----------------
       Browser/Streamlit secara default memberi warna abu-abu redup untuk textarea yang
       "disabled" (dipakai untuk menampilkan hasil dekripsi teks & hybrid). Warna redup itu
       tidak ikut variabel tema kita, jadi kalau tema gelap jadi nyaris tidak terbaca.
       Dipaksa di sini supaya tetap kontras & terbaca di kedua mode. */
    .stTextArea textarea:disabled,
    .stTextInput input:disabled {
        color: var(--text-primary) !important;
        -webkit-text-fill-color: var(--text-primary) !important;
        opacity: 1 !important;
        background-color: var(--input-bg) !important;
    }

    /* ---------------- BUTTONS (FIXED CHARCOAL + GOLD, TIDAK IKUT TEMA) ---------------- */
    div.stButton > button {
        width: 100%;
        background: var(--btn-bg) !important;
        color: var(--btn-text) !important;
        font-weight: 600 !important;
        font-size: 0.96rem !important;
        letter-spacing: 0.2px !important;
        border: 1px solid var(--accent) !important;
        border-radius: 10px !important;
        padding: 11px 22px !important;
        transition: background 0.15s ease !important;
        box-shadow: none !important;
        cursor: pointer !important;
    }

    div.stButton > button:hover {
        background: var(--btn-bg-hover) !important;
        border-color: var(--accent) !important;
        transform: none !important;
        box-shadow: none !important;
    }

    div.stDownloadButton > button {
        width: 100%;
        background: transparent !important;
        color: var(--accent) !important;
        font-weight: 600 !important;
        font-size: 0.94rem !important;
        border: 1px solid var(--accent) !important;
        border-radius: 10px !important;
        padding: 11px 22px !important;
        transition: all 0.15s ease !important;
        box-shadow: none !important;
    }

    div.stDownloadButton > button:hover {
        background: var(--accent-soft) !important;
        transform: none !important;
    }

    /* ---------------- TECHNICAL EXPANDER & CODE ---------------- */
    .streamlit-expanderHeader {
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.96rem !important;
        box-shadow: none !important;
    }

    .tech-panel-pro {
        background: var(--tech-bg);
        border: 1px solid var(--card-border);
        border-left: 3px solid var(--accent);
        border-radius: 12px;
        padding: 18px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.84rem;
        margin-top: 12px;
        margin-bottom: 18px;
    }

    .tech-row-pro {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 7px 0;
        border-bottom: 1px dashed var(--input-border);
    }

    .tech-row-pro:last-child {
        border-bottom: none;
    }

    .tech-label-pro {
        color: var(--text-muted);
    }

    .tech-val-pro {
        color: var(--accent);
        font-weight: 600;
    }

    /* Byte Header Layout Visual */
    .byte-diagram {
        display: flex;
        gap: 6px;
        margin-top: 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        font-weight: 500;
    }
    .byte-block {
        padding: 9px 12px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid var(--card-border);
    }
    .byte-salt {
        background: var(--byte-salt-bg);
        color: var(--byte-salt-text);
        flex: 1;
    }
    .byte-nonce {
        background: var(--byte-nonce-bg);
        color: var(--byte-nonce-text);
        flex: 1;
    }
    .byte-cipher {
        background: var(--byte-cipher-bg);
        color: var(--byte-cipher-text);
        flex: 2;
    }

    /* Metrics Card Adaptive */
    [data-testid="stMetric"] {
        background: var(--card-bg) !important;
        border: 1px solid var(--card-border) !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        box-shadow: none !important;
    }

    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stMetricValue"] {
        color: var(--accent) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
    }

    /* ---------------- SIDEBAR ADAPTIVE (LEBIH RAPAT) ---------------- */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
        border-right: 1px solid var(--sidebar-border) !important;
    }

    [data-testid="stSidebar"] hr {
        margin: 10px 0 !important;
        border-color: var(--sidebar-border) !important;
    }

    .sidebar-card-pro {
        background: var(--tech-bg);
        border: 1px solid var(--card-border);
        border-radius: 12px;
        padding: 14px 16px;
        margin-top: 14px;
    }

    .sidebar-card-title-pro {
        color: var(--accent);
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .member-item-pro {
        color: var(--text-secondary);
        font-size: 0.84rem;
        padding: 4px 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .pill-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: transparent;
        color: var(--accent);
        border: 1px solid var(--accent);
        padding: 3px 11px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 600;
    }

    .pill-badge-cyan {
        background: transparent;
        color: var(--text-secondary);
        border: 1px solid var(--card-border);
    }

    /* Footer */
    .footer-pro {
        text-align: center;
        color: var(--text-muted);
        font-size: 0.8rem;
        margin-top: 40px;
        padding: 18px;
        border-top: 1px solid var(--card-border);
    }

    /* ---------------- MOBILE RESPONSIVE MEDIA QUERIES ---------------- */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 4.2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .hero-inner {
            padding: 18px 16px !important;
            flex-direction: column !important;
        }
        .hero-tags {
            justify-content: flex-start !important;
            max-width: 100% !important;
        }
        .hero-title {
            font-size: 1.4rem !important;
        }
        .hero-subtitle {
            font-size: 0.86rem !important;
        }
        .nav-radio-wrap div[role="radiogroup"] {
            overflow-x: auto !important;
            flex-wrap: nowrap !important;
        }
        .nav-radio-wrap div[role="radiogroup"] label {
            white-space: nowrap !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px !important;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 0.8rem !important;
            height: 38px !important;
        }
        .byte-diagram {
            flex-direction: column !important;
        }
        div.stButton > button, div.stDownloadButton > button {
            padding: 10px 16px !important;
            font-size: 0.9rem !important;
        }
    }
    </style>
    """
    css_template = css_template.replace("__THEME_VARS__", theme_vars)
    st.markdown(css_template, unsafe_allow_html=True)

inject_custom_css()

# -----------------------------------------------------------------------------
# 3. HERO DASHBOARD BANNER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="hero-inner">
        <div>
            <div class="hero-badge-pill">🛡️ Tugas Proyek Aplikasi Kriptografi — Topik A</div>
            <div class="hero-title">CipherVault Studio Pro</div>
            <div class="hero-subtitle">Platform Enkripsi & Dekripsi Modern AEAD, Hybrid Encryption (RSA + AES), & Visualisasi Keamanan</div>
        </div>
        <div class="hero-tags">
            <span class="tag-item">🔑 Scrypt KDF</span>
            <span class="tag-item">⚡ AES-256-GCM</span>
            <span class="tag-item">🚀 ChaCha20</span>
            <span class="tag-item">🔐 RSA-2048</span>
            <span class="tag-item">🖼️ ECB vs GCM</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. NAVIGASI MODUL (TAB HORIZONTAL DI ATAS, BUKAN DI SIDEBAR)
# -----------------------------------------------------------------------------
st.markdown('<div class="nav-radio-wrap">', unsafe_allow_html=True)
selected_menu = st.radio(
    "Pilih Modul Aplikasi:",
    [
        "🔐 Enkripsi / Dekripsi Teks",
        "📁 Enkripsi / Dekripsi File",
        "🔑 Hybrid Encryption (RSA-OAEP + AES)",
        "🖼️ Demo Keamanan: ECB vs Mode Aman",
        "ℹ️ Tentang & Dokumentasi"
    ],
    index=0,
    horizontal=True,
    label_visibility="collapsed",
    key="selected_menu_nav"
)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4B. SIDEBAR: PANEL PENGATURAN & IDENTITAS KELOMPOK (BUKAN NAVIGASI LAGI)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Panel Pengaturan")

    st.radio(
        "🌗 Tampilan Aplikasi:",
        ["☀️ Terang", "🌙 Gelap"],
        horizontal=True,
        key="app_theme_mode",
        help="Ganti tampilan terang/gelap aplikasi ini (terpisah dari menu Streamlit bawaan)."
    )
    st.divider()
    st.markdown("### 🧭 Modul Aktif")

    menu_desc = {
        "🔐 Enkripsi / Dekripsi Teks": "Mengubah teks jadi ciphertext (dan sebaliknya) pakai enkripsi AEAD (AES-256-GCM / ChaCha20-Poly1305) agar isi pesan rahasia dan tidak bisa diubah diam-diam.",
        "📁 Enkripsi / Dekripsi File": "Mengenkripsi/dekripsi file biner (dokumen, gambar, dll.) memakai algoritma AEAD yang sama, jadi seluruh isi file ikut terlindungi.",
        "🔑 Hybrid Encryption (RSA-OAEP + AES)": "Menggabungkan RSA-OAEP untuk mengamankan kunci sesi dan AES-256-GCM untuk mengenkripsi datanya — pola yang umum dipakai di dunia nyata (mis. TLS).",
        "🖼️ Demo Keamanan: ECB vs Mode Aman": "Membandingkan secara visual mode ECB yang membocorkan pola gambar dengan AES-GCM yang aman.",
        "ℹ️ Tentang & Dokumentasi": "Penjelasan teknis algoritma & konsep kriptografi yang dipakai di aplikasi ini.",
    }

    st.markdown(f"""
    <div style="display:flex; gap:8px; margin-bottom:8px; flex-wrap:wrap;">
        <span class="pill-badge">🟢 {selected_menu.split()[1] if len(selected_menu.split()) > 1 else selected_menu}</span>
    </div>
    """, unsafe_allow_html=True)
    st.caption(menu_desc.get(selected_menu, ""))

    st.divider()
    
    # Identitas Kelompok UTS Keamanan Informasi
    st.markdown("""
    <div class="sidebar-card-pro">
        <div class="sidebar-card-title-pro">👥 KELOMPOK UTS KI</div>
        <div class="member-item-pro">🔑 <span>Topik A: Enkripsi Modern</span></div>
        <div class="member-item-pro">🧪 <span>KDF: Scrypt (N=16384, r=8, p=1)</span></div>
        <div class="member-item-pro">🛡️ <span>Cipher: AES-GCM & ChaCha20</span></div>
        <div class="member-item-pro">🔐 <span>Asimetris: RSA-OAEP 2048</span></div>
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
                <span class="tech-val-pro">{overhead_str}</span>
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
                index=0,
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
                index=0,
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
                index=0,
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
                index=0,
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
# 8. MODUL 3 (PENGAYAAN): HYBRID ENCRYPTION (RSA-OAEP + AES)
# -----------------------------------------------------------------------------
elif selected_menu == "🔑 Hybrid Encryption (RSA-OAEP + AES)":
    st.subheader("🔑 Hybrid Encryption System (RSA-OAEP 2048 + AES-256-GCM)")
    st.caption("Kombinasi Enkripsi Asimetris (RSA-OAEP) untuk enkripsi Session Key simetris dan Enkripsi Simetris (AES-256-GCM) untuk pengiriman data berkecepatan tinggi.")

    # Manajemen Session State Pasangan Kunci RSA
    if "rsa_private_key" not in st.session_state or "rsa_public_key" not in st.session_state:
        priv_k, pub_k = generate_rsa_keypair(2048)
        st.session_state["rsa_private_key"] = priv_k
        st.session_state["rsa_public_key"] = pub_k

    col_rsa_info, col_rsa_btn = st.columns([3, 1])
    with col_rsa_info:
        st.info("🔐 **Status Pasangan Kunci RSA Aktif:** Keypair RSA 2048-bit sudah siap di Memori Session State.", icon="ℹ️")
    with col_rsa_btn:
        if st.button("🔄 Generate RSA Keypair Baru"):
            priv_k, pub_k = generate_rsa_keypair(2048)
            st.session_state["rsa_private_key"] = priv_k
            st.session_state["rsa_public_key"] = pub_k
            st.success("✅ Kunci RSA 2048-bit baru berhasil digenerate!")

    tab_hybrid_enc, tab_hybrid_dec = st.tabs(["🔒 Enkripsi Hybrid", "🔓 Dekripsi Hybrid"])

    # --- TAB ENKRIPSI HYBRID ---
    with tab_hybrid_enc:
        plaintext_hybrid = st.text_area(
            "Teks Asli (Plaintext):",
            height=140,
            placeholder="Ketik pesan rahasia yang akan dienkripsi dengan Hybrid Scheme...",
            key="plaintext_hybrid"
        )

        if st.button("🚀 Enkripsi Hybrid Now", key="btn_hybrid_enc"):
            if not plaintext_hybrid.strip():
                st.warning("⚠️ Harap masukkan teks asli yang ingin dienkripsi!")
            else:
                try:
                    start_t = time.perf_counter()
                    res = encrypt_hybrid(plaintext_hybrid.encode("utf-8"), st.session_state["rsa_public_key"])
                    end_t = time.perf_counter()
                    proc_ms = (end_t - start_t) * 1000

                    ct_b64 = base64.b64encode(res["ciphertext"]).decode("utf-8")
                    nonce_b64 = base64.b64encode(res["nonce"]).decode("utf-8")
                    enc_key_b64 = base64.b64encode(res["encrypted_session_key"]).decode("utf-8")

                    st.success("✅ Enkripsi Hybrid Berhasil!")
                    
                    st.markdown("**1. Encrypted Session Key (RSA-OAEP Encrypted AES Key - Base64):**")
                    st.code(enc_key_b64, language="text")

                    st.markdown("**2. Nonce (12-Byte IV - Base64):**")
                    st.code(nonce_b64, language="text")

                    st.markdown("**3. Ciphertext Data (AES-256-GCM Encrypted - Base64):**")
                    st.code(ct_b64, language="text")

                    st.markdown("""
                    <div class="tech-panel-pro">
                        <div class="tech-row-pro">
                            <span class="tech-label-pro">🔑 Skema Enkripsi:</span>
                            <span class="tech-val-pro">Hybrid (RSA-OAEP 2048 + AES-256-GCM)</span>
                        </div>
                        <div class="tech-row-pro">
                            <span class="tech-label-pro">⚡ Waktu Eksekusi:</span>
                            <span class="tech-val-pro">{:.2f} ms</span>
                        </div>
                        <div class="tech-row-pro">
                            <span class="tech-label-pro">📥 Ukuran Plaintext:</span>
                            <span class="tech-val-pro">{} Byte</span>
                        </div>
                        <div class="tech-row-pro">
                            <span class="tech-label-pro">📤 Encrypted Session Key Size:</span>
                            <span class="tech-val-pro">{} Byte (256-bit AES Key wrapped in 2048-bit RSA)</span>
                        </div>
                    </div>
                    """.format(proc_ms, len(plaintext_hybrid.encode('utf-8')), len(res["encrypted_session_key"])), unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"❌ Kesalahan pada proses Enkripsi Hybrid: {str(e)}")

    # --- TAB DEKRIPSI HYBRID ---
    with tab_hybrid_dec:
        st.caption("Masukkan komponen Base64 hasil enkripsi hybrid di bawah ini:")

        enc_key_input = st.text_area("Encrypted Session Key (Base64):", height=80, key="enc_key_input")
        nonce_input = st.text_input("Nonce / IV (Base64):", key="nonce_input")
        ciphertext_hybrid_input = st.text_area("Ciphertext Data (Base64):", height=100, key="ciphertext_hybrid_input")

        if st.button("🔓 Dekripsi Hybrid Now", key="btn_hybrid_dec"):
            if not enc_key_input.strip() or not nonce_input.strip() or not ciphertext_hybrid_input.strip():
                st.warning("⚠️ Harap lengkapi ketiga field input (Encrypted Session Key, Nonce, dan Ciphertext Data)!")
            else:
                try:
                    start_t = time.perf_counter()
                    
                    enc_key_bytes = base64.b64decode(enc_key_input.strip())
                    nonce_bytes = base64.b64decode(nonce_input.strip())
                    ct_bytes = base64.b64decode(ciphertext_hybrid_input.strip())

                    decrypted_bytes = decrypt_hybrid(
                        ct_bytes,
                        nonce_bytes,
                        enc_key_bytes,
                        st.session_state["rsa_private_key"]
                    )
                    
                    end_t = time.perf_counter()
                    proc_ms = (end_t - start_t) * 1000
                    plaintext_out = decrypted_bytes.decode("utf-8")

                    st.success("✅ Dekripsi Hybrid Berhasil! RSA Private Key berhasil membongkar Session Key & AES-GCM mendekripsi data.")
                    st.text_area("Hasil Teks Asli (Plaintext):", value=plaintext_out, height=120, disabled=True)

                except ValueError as ve:
                    st.error(f"🛑 {str(ve)}")
                except Exception as e:
                    st.error("🛑 Dekripsi hybrid gagal: Format Base64 tidak valid, RSA Key mismatch, atau data telah diubah/rusak!")

# -----------------------------------------------------------------------------
# 9. MODUL 4 (PENGAYAAN): DEMO KEAMANAN (ECB VS MODE AMAN)
# -----------------------------------------------------------------------------
elif selected_menu == "🖼️ Demo Keamanan: ECB vs Mode Aman":
    st.subheader("🖼️ Demo Keamanan Visual Citra: ECB vs Mode Aman (AES-256-GCM)")
    st.caption("Visualisasi interaktif mengapa mode ECB (Electronic Codebook) BERBAHAYA & BOCOR POLA dibanding mode AEAD (AES-GCM).")

    col_up, col_pass = st.columns([2, 1])

    with col_up:
        uploaded_img = st.file_uploader(
            "Upload Citra Kustom (PNG/JPG/BMP) atau biarkan kosong untuk Citra Demo Default:",
            type=["png", "jpg", "jpeg", "bmp"],
            key="demo_img_upload"
        )
    with col_pass:
        demo_pass = st.text_input(
            "Password Kunci Demo:",
            type="password",
            placeholder="Masukkan password untuk demo...",
            key="demo_pass_input"
        )

    if st.button("🚀 Jalankan Demo Visualisasi Keamanan Now", key="btn_run_demo"):
        if not demo_pass:
            st.warning("⚠️ Harap masukkan password kunci demo terlebih dahulu!")
        else:
            try:
                with st.spinner("Memproses enkripsi ECB vs AES-GCM..."):
                    if uploaded_img is not None:
                        citra_asli = Image.open(uploaded_img).convert("RGB")
                        # Resize jika terlalu besar agar pemrosesan cepat
                        if citra_asli.width > 512 or citra_asli.height > 512:
                            citra_asli.thumbnail((512, 512))
                    else:
                        citra_asli = buat_citra_demo(256, 256)

                    data_piksel = citra_asli.tobytes()

                    start_t = time.perf_counter()
                    ciphertext_ecb, _ = enkripsi_ecb(data_piksel, demo_pass)
                    _, ciphertext_gcm_murni, _, _ = enkripsi_gcm(data_piksel, demo_pass)
                    end_t = time.perf_counter()

                    img_ecb = bytes_ke_citra(ciphertext_ecb, citra_asli.size, mode="RGB")
                    img_gcm = bytes_ke_citra(ciphertext_gcm_murni, citra_asli.size, mode="RGB")

                st.success(f"✅ Demo selesai diproses dalam {(end_t - start_t)*1000:.2f} ms!")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("#### 1. Citra Asli (Original)")
                    st.image(citra_asli, use_container_width=True)
                    st.caption("Pola citra bitmap dengan area warna berulang/solid.")

                with col2:
                    st.markdown("#### 2. Hasil ECB (BOCOR POLA)")
                    st.image(img_ecb, use_container_width=True)
                    st.caption("🔴 **VULNERABLE:** Pola asli MASIH TERLIHAT! Blok plaintext identik selalu menghasilkan ciphertext identik.")

                with col3:
                    st.markdown("#### 3. Hasil AES-GCM (AMAN)")
                    st.image(img_gcm, use_container_width=True)
                    st.caption("🟢 **SECURE:** Noise acak sempurna! Keystream unik per-blok dari Counter Mode menghilangkan seluruh korelasi visual.")

                st.divider()

                # Penjelasan Teknis
                with st.expander("🎓 Penjelasan Teknis & Analisis Kriptografi", expanded=True):
                    st.markdown("""
                    ### 💡 Kenapa Mode ECB Sangat Berbahaya?
                    1. **Deterministic Mapping:** Mode Electronic Codebook (ECB) mengenkripsi tiap blok 16-byte secara terpisah dengan rumus $C_i = E(K, P_i)$.
                    2. **Pola Bocor (Pattern Leakage):** Apabila data memiliki area warna solid atau struktur berulang (seperti piksel gambar), blok $P_i$ yang bernilai sama akan menghasilkan ciphertext $C_i$ yang bernilai sama pula.
                    3. **Dampak:** Penyerang dapat dengan mudah menganalisis kontur, bentuk, dan pola data tanpa perlu memecahkan kunci enkripsi!

                    ### 🛡️ Kenapa AES-GCM Menjamin Keamanan Visual & Data?
                    1. **Stream Encryption & Unique Keystream:** AES-GCM memanfaatkan mode Counter (CTR), di mana setiap blok di-XOR dengan keystream unik yang dihasilkan dari kombinasi (Key, Nonce, Counter).
                    2. **Indistinguishability:** Meskipun dua blok plaintext bernilai persis sama, hasil ciphertext akan bernilai acak sempurna (terlihat seperti *white noise*).
                    3. **Authenticated Encryption (AEAD):** Selain kerahasiaan visual, AES-GCM dilengkapi tag otentikasi GHASH untuk menjamin data tidak dapat diubah oleh peretas.
                    """)

            except Exception as e:
                st.error(f"❌ Gagal menjalankan demo keamanan: {str(e)}")

# -----------------------------------------------------------------------------
# 10. MODUL 5: TENTANG APLIKASI & DOKUMENTASI KRIPTOGRAFI
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

    # 4. Hybrid & Demo Visual
    with st.expander("🔐 4. Fitur Pengayaan: Hybrid Encryption & Demo Visual ECB"):
        st.markdown("""
        *   **Hybrid Encryption (RSA-OAEP + AES-GCM):**
            *   Menggabungkan efisiensi enkripsi simetris (AES) dengan fleksibilitas pertukaran kunci enkripsi asimetris (RSA).
            *   Session Key 256-bit dienkripsi dengan Public Key RSA pengirim/penerima menggunakan skema OAEP padding dengan SHA-256.
        *   **Visualisasi Keamanan Citra (ECB vs AES-GCM):**
            *   Membuktikan kelemahan mode ECB yang melestarikan korelasi piksel asli.
            *   Menunjukkan keunggulan mode AEAD yang mengubah citra menjadi derau acak (*noise*).
        """)

    # 5. Format Output Biner Header
    with st.expander("📦 5. Format Output & Susunan Header Binary"):
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
# 11. FOOTER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="footer-pro">
    🛡️ <strong>CipherVault Studio Pro Web Platform</strong> | Topik A: Enkripsi Algoritma Modern (Tugas UTS Keamanan Informasi)<br>
    Jalankan via Terminal: <code>streamlit run app.py</code>
</div>
""", unsafe_allow_html=True)