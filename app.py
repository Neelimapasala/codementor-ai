import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import json

# ── Load API key (tries .env first, then lets user paste it in sidebar) ───────
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

# If not in .env, let user enter it in sidebar
if not GROQ_API_KEY:
    st.sidebar.markdown("### 🔑 Enter Groq API Key")
    GROQ_API_KEY = st.sidebar.text_input(
        "Paste your Groq API key here",
        type="password",
        placeholder="gsk_..."
    ).strip()
    if not GROQ_API_KEY:
        st.warning("⚠️ Please enter your Groq API key in the sidebar to use this app.")
        st.sidebar.info("Get your free key at: https://console.groq.com/keys")
        st.stop()

# Extended language detection and syntax highlighting support
LANGUAGE_EXTENSIONS = {
    'py': 'python', 'js': 'javascript', 'ts': 'typescript', 'jsx': 'javascript', 'tsx': 'typescript',
    'html': 'html', 'css': 'css', 'scss': 'scss', 'sass': 'sass', 'less': 'less',
    'vue': 'vue', 'svelte': 'svelte',
    'java': 'java', 'kt': 'kotlin', 'scala': 'scala',
    'go': 'go', 'rs': 'rust', 'cpp': 'cpp', 'c': 'c', 'h': 'cpp', 'hpp': 'cpp',
    'cs': 'csharp', 'vb': 'vbnet', 'fs': 'fsharp',
    'rb': 'ruby', 'php': 'php', 'pl': 'perl', 'lua': 'lua',
    'swift': 'swift', 'dart': 'dart', 'r': 'r',
    'sh': 'bash', 'bash': 'bash', 'zsh': 'bash', 'fish': 'bash',
    'yaml': 'yaml', 'yml': 'yaml', 'toml': 'toml', 'json': 'json', 'xml': 'xml',
    'sql': 'sql', 'graphql': 'graphql',
    'ipynb': 'python', 'jl': 'julia', 'mat': 'matlab',
    'md': 'markdown', 'tex': 'latex', 'asm': 'assembly',
    'elm': 'elm', 'clj': 'clojure', 'ex': 'elixir', 'erl': 'erlang',
    'nim': 'nim', 'zig': 'zig', 'v': 'v', 'haskell': 'haskell', 'hs': 'haskell'
}

LANGUAGE_NAMES = {
    'python': 'Python', 'javascript': 'JavaScript', 'typescript': 'TypeScript',
    'java': 'Java', 'cpp': 'C++', 'c': 'C', 'csharp': 'C#',
    'go': 'Go', 'rust': 'Rust', 'php': 'PHP', 'ruby': 'Ruby',
    'swift': 'Swift', 'kotlin': 'Kotlin', 'dart': 'Dart',
    'sql': 'SQL', 'bash': 'Shell/Bash', 'html': 'HTML', 'css': 'CSS',
    'r': 'R', 'scala': 'Scala', 'perl': 'Perl', 'lua': 'Lua',
    'elixir': 'Elixir', 'haskell': 'Haskell', 'clojure': 'Clojure'
}

st.set_page_config(
    page_title="CodeMentor AI — by Neelima Pasala",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #0a0e1a;
    color: #e2e8f0;
}

.main-header {
    text-align: center;
    padding: 2rem 0 1.5rem 0;
    background: linear-gradient(135deg, #1e2433 0%, #0f1117 100%);
    border-radius: 16px;
    margin-bottom: 2rem;
    border: 1px solid #2d3748;
}

.main-header h1 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2.2rem;
    font-weight: 600;
    background: linear-gradient(135deg, #a78bfa 0%, #60a5fa 60%, #4ade80 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    letter-spacing: -0.5px;
}

.main-header .version {
    color: #64748b;
    font-size: 0.85rem;
    margin: 0.3rem 0 0 0;
    font-family: 'JetBrains Mono', monospace;
}

.main-header .tagline {
    color: #94a3b8;
    font-size: 0.95rem;
    margin: 0.5rem 0 0 0;
}

.main-header .builder {
    color: #a78bfa;
    font-size: 0.82rem;
    margin: 0.5rem 0 0 0;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.5px;
}

.feature-badge {
    display: inline-block;
    background: #1e2433;
    border: 1px solid #3b82f6;
    color: #60a5fa;
    padding: 0.25rem 0.75rem;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    margin: 0.25rem;
    font-family: 'JetBrains Mono', monospace;
}

.mode-card {
    background: linear-gradient(135deg, #1e2433 0%, #1a1f2e 100%);
    border: 1px solid #2d3748;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

.mode-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #a78bfa;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.mode-label::before {
    content: '';
    width: 8px;
    height: 8px;
    background: #a78bfa;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.result-box {
    background: #0f1420;
    border: 1px solid #2d3748;
    border-left: 3px solid #a78bfa;
    border-radius: 8px;
    padding: 1.5rem;
    margin-top: 1rem;
    font-size: 0.92rem;
    line-height: 1.8;
    color: #cbd5e1;
}

.analysis-section {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 1.2rem;
    margin: 1rem 0;
}

.analysis-section h4 {
    color: #a78bfa;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    margin-bottom: 0.8rem;
}

.stButton > button {
    background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%) !important;
    color: #fff !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 1.8rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 12px rgba(167, 139, 250, 0.2) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(167, 139, 250, 0.35) !important;
}

.stTextArea textarea, .stTextInput input {
    background: #1e2433 !important;
    border: 1px solid #2d3748 !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
}

.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 2px rgba(167,139,250,0.1) !important;
}

.stSelectbox > div > div {
    background: #1e2433 !important;
    border: 1px solid #2d3748 !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
}

.stFileUploader > div {
    background: #1e2433 !important;
    border: 2px dashed #2d3748 !important;
    border-radius: 8px !important;
    padding: 1.5rem !important;
}

.stCheckbox label {
    color: #94a3b8 !important;
    font-size: 0.9rem !important;
}

.stRadio > div {
    gap: 0.8rem;
}

.stRadio label {
    color: #94a3b8 !important;
}

.tip-box {
    background: linear-gradient(135deg, #1a2234 0%, #1e2845 100%);
    border: 1px solid #1e3a5f;
    border-left: 3px solid #60a5fa;
    border-radius: 8px;
    padding: 0.9rem 1.2rem;
    margin-top: 1rem;
    font-size: 0.85rem;
    color: #93c5fd;
}

.tip-box::before {
    content: '💡 ';
    font-size: 1rem;
}

.warning-box {
    background: linear-gradient(135deg, #2d1f1a 0%, #3d2518 100%);
    border: 1px solid #44403c;
    border-left: 3px solid #f59e0b;
    border-radius: 8px;
    padding: 0.9rem 1.2rem;
    margin-top: 1rem;
    font-size: 0.85rem;
    color: #fbbf24;
}

.success-box {
    background: linear-gradient(135deg, #1a2d1f 0%, #1e3d28 100%);
    border: 1px solid #2d4a3d;
    border-left: 3px solid #4ade80;
    border-radius: 8px;
    padding: 0.9rem 1.2rem;
    margin-top: 1rem;
    font-size: 0.85rem;
    color: #86efac;
}

.need-card {
    background: linear-gradient(135deg, #1e2433 0%, #1a1f2e 100%);
    border: 1px solid #3730a3;
    border-left: 4px solid #a78bfa;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}

.need-card h4 {
    color: #c4b5fd;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.95rem;
    margin-bottom: 0.5rem;
}

.need-card p {
    color: #94a3b8;
    font-size: 0.88rem;
    line-height: 1.6;
    margin: 0;
}

.need-tag {
    display: inline-block;
    background: #3730a3;
    color: #c4b5fd;
    border-radius: 4px;
    padding: 0.15rem 0.5rem;
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    margin-right: 0.3rem;
    margin-bottom: 0.4rem;
    font-weight: 600;
}

div[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #2d3748 !important;
}

div[data-testid="stSidebar"] * {
    color: #94a3b8 !important;
}

.sidebar-section {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 1rem;
    margin-bottom: 1rem;
}

.sidebar-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    color: #a78bfa !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 0.8rem;
}

.stat-box {
    background: #1a1f2e;
    border: 1px solid #2d3748;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}

.stat-number {
    font-size: 1.8rem;
    font-weight: 600;
    color: #a78bfa;
    font-family: 'JetBrains Mono', monospace;
}

.stat-label {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 0.3rem;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 1rem;
}

.stTabs [data-baseweb="tab"] {
    background: #1e2433;
    border-radius: 8px 8px 0 0;
    color: #94a3b8;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
    padding: 0.8rem 1.5rem;
    border: 1px solid #2d3748;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%);
    color: #fff !important;
    border-color: #a78bfa;
}

.stExpander {
    background: #1a1f2e !important;
    border: 1px solid #2d3748 !important;
    border-radius: 8px !important;
}

.lang-badge {
    display: inline-block;
    background: #1e3a5f;
    color: #60a5fa;
    padding: 0.2rem 0.6rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-family: 'JetBrains Mono', monospace;
    margin-right: 0.5rem;
    font-weight: 600;
}

.code-gen-prompt {
    background: #1a1f2e;
    border: 1px solid #3730a3;
    border-left: 3px solid #818cf8;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    color: #c7d2fe;
    font-size: 0.88rem;
}

/* ── NOVA FLOATING BOT ───────────────────────────────────────── */
#nova-fab {
    position: fixed; bottom: 28px; right: 28px; z-index: 9999;
    width: 60px; height: 60px; border-radius: 50%;
    background: linear-gradient(135deg, #a78bfa, #7c3aed);
    border: none; cursor: pointer;
    box-shadow: 0 4px 24px rgba(167,139,250,.5);
    display: flex; align-items: center; justify-content: center;
    transition: transform .2s, box-shadow .2s; font-size: 1.6rem;
}
#nova-fab:hover { transform: scale(1.1); box-shadow: 0 6px 32px rgba(167,139,250,.7); }
#nova-pulse {
    position: absolute; top: -3px; right: -3px;
    width: 16px; height: 16px; background: #4ade80;
    border-radius: 50%; border: 2px solid #0a0e1a;
    animation: novapulse 2s infinite;
}
@keyframes novapulse { 0%,100%{transform:scale(1);opacity:1} 50%{transform:scale(1.3);opacity:.7} }
#nova-window {
    position: fixed; bottom: 100px; right: 28px; z-index: 9998;
    width: 360px; max-width: calc(100vw - 40px);
    background: #0d1117; border: 1px solid #2d3748; border-radius: 16px;
    box-shadow: 0 8px 40px rgba(0,0,0,.6);
    display: none; flex-direction: column; overflow: hidden;
}
#nova-window.open { display: flex; }
#nova-header {
    background: linear-gradient(135deg,#1e2433,#161b2a);
    padding: .9rem 1rem; display: flex; align-items: center;
    justify-content: space-between; border-bottom: 1px solid #2d3748;
}
.nova-title { display: flex; align-items: center; gap: .6rem; }
.nova-avatar {
    width: 36px; height: 36px; border-radius: 50%;
    background: linear-gradient(135deg,#a78bfa,#7c3aed);
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; flex-shrink: 0;
}
.nova-name { font-family: 'JetBrains Mono',monospace; font-weight:600; font-size:.92rem; color:#e2e8f0; }
.nova-status { font-size:.72rem; color:#4ade80; margin-top:.1rem; }
#nova-close { background:none; border:none; color:#64748b; font-size:1.2rem; cursor:pointer; padding:.2rem .4rem; border-radius:4px; line-height:1; }
#nova-close:hover { color:#e2e8f0; background:#1e2433; }
#nova-messages {
    flex:1; overflow-y:auto; padding:1rem;
    display:flex; flex-direction:column; gap:.8rem;
    max-height:360px; min-height:180px;
}
#nova-messages::-webkit-scrollbar{width:4px}
#nova-messages::-webkit-scrollbar-thumb{background:#2d3748;border-radius:2px}
.nova-msg { display:flex; gap:.6rem; align-items:flex-start; }
.nova-msg.user { flex-direction:row-reverse; }
.nova-msg-avatar {
    width:28px; height:28px; border-radius:50%;
    background:linear-gradient(135deg,#a78bfa,#7c3aed);
    display:flex; align-items:center; justify-content:center;
    font-size:.8rem; flex-shrink:0;
}
.nova-msg.user .nova-msg-avatar { background:linear-gradient(135deg,#3b82f6,#1d4ed8); }
.nova-bubble {
    max-width:78%; background:#1a1f2e; border:1px solid #2d3748;
    border-radius:12px; padding:.6rem .9rem;
    font-size:.84rem; line-height:1.6; color:#cbd5e1;
}
.nova-msg.user .nova-bubble { background:#1e2d4a; border-color:#1e3a5f; color:#e2e8f0; }
.nova-bubble code { background:#0d1117; border-radius:3px; padding:.1rem .3rem; font-family:'JetBrains Mono',monospace; font-size:.8rem; color:#4ade80; }
.nova-bubble pre { background:#0d1117; border-radius:6px; padding:.6rem; overflow-x:auto; margin:.4rem 0; }
.nova-bubble pre code { background:none; padding:0; color:#e2e8f0; }
.nova-bubble strong { color:#e2e8f0; }
.nova-bubble p { margin:.3rem 0; }
.nova-bubble ul,.nova-bubble ol { padding-left:1.2rem; margin:.3rem 0; }
.nova-typing { display:flex; align-items:center; gap:4px; padding:.4rem .6rem; }
.nova-typing span { width:6px; height:6px; background:#a78bfa; border-radius:50%; animation:novatype 1.2s infinite; }
.nova-typing span:nth-child(2){animation-delay:.2s}
.nova-typing span:nth-child(3){animation-delay:.4s}
@keyframes novatype{0%,60%,100%{transform:translateY(0);opacity:.4}30%{transform:translateY(-5px);opacity:1}}
#nova-chips { padding:.5rem 1rem; display:flex; flex-wrap:wrap; gap:.4rem; border-top:1px solid #1e2433; }
.nova-chip {
    background:#1a1f2e; border:1px solid #2d3748; color:#94a3b8;
    border-radius:20px; padding:.25rem .7rem; font-size:.73rem;
    cursor:pointer; transition:all .15s; white-space:nowrap;
    font-family:'JetBrains Mono',monospace;
}
.nova-chip:hover { background:#2d3748; color:#a78bfa; border-color:#a78bfa; }
#nova-input-row { padding:.7rem 1rem; border-top:1px solid #2d3748; display:flex; gap:.5rem; align-items:flex-end; }
#nova-input {
    flex:1; background:#1e2433; border:1px solid #2d3748;
    border-radius:8px; color:#e2e8f0; font-size:.85rem;
    padding:.5rem .8rem; outline:none; resize:none;
    max-height:100px; font-family:'Inter',sans-serif; line-height:1.5;
}
#nova-input:focus { border-color:#a78bfa; }
#nova-send {
    width:36px; height:36px;
    background:linear-gradient(135deg,#a78bfa,#7c3aed);
    border:none; border-radius:8px; cursor:pointer;
    display:flex; align-items:center; justify-content:center;
    font-size:1rem; flex-shrink:0; transition:all .2s; color:#fff;
}
#nova-send:hover { transform:scale(1.05); }
#nova-send:disabled { opacity:.5; cursor:not-allowed; transform:none; }
</style>
""", unsafe_allow_html=True)


# Session state initialization
if 'history' not in st.session_state:
    st.session_state.history = []
if 'analysis_count' not in st.session_state:
    st.session_state.analysis_count = 0
if 'favorite_mode' not in st.session_state:
    st.session_state.favorite_mode = {}
if 'generated_codes' not in st.session_state:
    st.session_state.generated_codes = []
if 'nova_messages' not in st.session_state:
    st.session_state.nova_messages = []


def get_client():
    return Groq(api_key=GROQ_API_KEY)


def ask_groq(system_prompt, user_message, max_tokens=1000):
    client = get_client()
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"API error: {e}")
        return None


def detect_language(code, filename=None):
    """Detect programming language from code or filename"""
    if filename:
        ext = filename.split('.')[-1].lower()
        return LANGUAGE_EXTENSIONS.get(ext, 'text')

    code_lower = code.lower()[:500]
    if 'def ' in code or 'import ' in code or 'print(' in code:
        return 'python'
    elif 'function' in code or 'const ' in code or 'let ' in code or '=>' in code:
        return 'javascript'
    elif 'public class' in code or 'public static void main' in code:
        return 'java'
    elif '#include' in code:
        return 'cpp'
    elif 'package main' in code or 'func ' in code:
        return 'go'
    elif 'fn ' in code or 'let mut' in code:
        return 'rust'
    return 'text'


def add_to_history(mode, input_text, output_text):
    st.session_state.history.insert(0, {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'mode': mode,
        'input': input_text[:100] + ('...' if len(input_text) > 100 else ''),
        'output': output_text[:200] + ('...' if len(output_text) > 200 else '')
    })
    st.session_state.analysis_count += 1
    if mode not in st.session_state.favorite_mode:
        st.session_state.favorite_mode[mode] = 0
    st.session_state.favorite_mode[mode] += 1
    if len(st.session_state.history) > 20:
        st.session_state.history = st.session_state.history[:20]


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🧠 CodeMentor AI</div>', unsafe_allow_html=True)
    st.markdown('<p style="color:#a78bfa !important; font-size:0.82rem; font-family:JetBrains Mono,monospace;">Built by Neelima Pasala</p>', unsafe_allow_html=True)
    st.markdown('<p style="color:#475569 !important; font-size:0.78rem;">Powered by LLaMA 3.3 70B via Groq</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Stats
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">📊 Your Session Stats</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{st.session_state.analysis_count}</div><div class="stat-label">Queries</div></div>', unsafe_allow_html=True)
    with col2:
        fav_mode = max(st.session_state.favorite_mode.items(), key=lambda x: x[1])[0] if st.session_state.favorite_mode else "—"
        st.markdown(f'<div class="stat-box"><div class="stat-number" style="font-size:1.1rem;">{fav_mode}</div><div class="stat-label">Top Mode</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Supported languages
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">💻 Supported Languages</div>', unsafe_allow_html=True)
    st.markdown("**50+ Languages:**")
    st.markdown("• Python, JavaScript, TypeScript, Java")
    st.markdown("• C++, C, C#, Go, Rust")
    st.markdown("• PHP, Ruby, Swift, Kotlin, Dart")
    st.markdown("• SQL, Bash, R, Scala, Elixir")
    st.markdown("• Haskell, Clojure, Lua, Perl")
    st.markdown("• HTML, CSS, YAML, JSON, XML")
    st.markdown("• And many more...")
    st.markdown('</div>', unsafe_allow_html=True)

    # Quick links
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🔗 Resources</div>', unsafe_allow_html=True)
    st.markdown("• [Conventional Commits](https://www.conventionalcommits.org)")
    st.markdown("• [Git Best Practices](https://git-scm.com/book/en/v2)")
    st.markdown("• [Python Docs](https://docs.python.org/3/)")
    st.markdown("• [MDN Web Docs](https://developer.mozilla.org)")
    st.markdown("• [System Design Primer](https://github.com/donnemartin/system-design-primer)")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">🎯 Quick Jump</div>', unsafe_allow_html=True)
    st.markdown("**📖 Explain** — Deep code analysis")
    st.markdown("**⚡ Generate** — AI code generation")
    st.markdown("**📝 Commit** — Git messages")
    st.markdown("**❓ Ask** — Q&A assistant")
    st.markdown("**📧 Email** — Email drafts")
    st.markdown("**🔄 Compare** — Code comparison")
    st.markdown("**🔧 Debug** — Smart debugging")
    st.markdown("**🎓 Trainee Kit** — Skills you need")
    st.markdown("**📜 History** — Past sessions")
    st.markdown('</div>', unsafe_allow_html=True)


# ── NOVA FLOATING BOT ────────────────────────────────────────────────────────
st.markdown(f"""
<button id="nova-fab" onclick="toggleNova()" title="Chat with Nova">
  🤖<span id="nova-pulse"></span>
</button>

<div id="nova-window">
  <div id="nova-header">
    <div class="nova-title">
      <div class="nova-avatar">🤖</div>
      <div>
        <div class="nova-name">Nova</div>
        <div class="nova-status">● Online — CodeMentor AI Assistant</div>
      </div>
    </div>
    <button id="nova-close" onclick="toggleNova()">✕</button>
  </div>
  <div id="nova-messages"></div>
  <div id="nova-chips">
    <div class="nova-chip" onclick="novaQuick('What can you help me with?')">What can you do?</div>
    <div class="nova-chip" onclick="novaQuick('How do I write a good commit message?')">Commit tips</div>
    <div class="nova-chip" onclick="novaQuick('What are common beginner coding mistakes?')">Beginner tips</div>
    <div class="nova-chip" onclick="novaQuick('Explain what an API is in simple terms')">What is an API?</div>
    <div class="nova-chip" onclick="novaQuick('How do I read a stack trace?')">Stack trace help</div>
  </div>
  <div id="nova-input-row">
    <textarea id="nova-input" rows="1" placeholder="Ask Nova anything..." onkeydown="novaKeydown(event)" oninput="autoResize(this)"></textarea>
    <button id="nova-send" onclick="novaSend()">➤</button>
  </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/marked/9.1.6/marked.min.js"></script>
<script>
const NOVA_API_KEY = '{GROQ_API_KEY}';
const NOVA_SYSTEM = `You are Nova, a friendly and expert AI coding assistant embedded inside CodeMentor AI, a tool built by Neelima Pasala.
You help developers and trainees with coding questions in any language, debugging, Git tips, career advice, explaining concepts simply, best practices, and anything related to software development.
Personality: Warm, encouraging, practical. Use emojis occasionally. Give concise but complete answers. Use code blocks for code examples.
Important: You are Nova — always refer to yourself as Nova. Keep responses under 200 words unless code is needed. Use markdown formatting.`;

let novaOpen = false;
let novaHistory = [];
let novaTyping = false;
let novaGreeted = false;

function toggleNova(){{
  novaOpen = !novaOpen;
  const w = document.getElementById('nova-window');
  w.classList.toggle('open', novaOpen);
  if(novaOpen && !novaGreeted){{
    novaGreeted = true;
    appendNovaMsg('bot', `👋 Hey there! I'm **Nova**, your coding companion inside CodeMentor AI!\\n\\nI can help you with:\\n- 🐛 Debugging errors\\n- 💡 Explaining concepts\\n- 🌿 Git & version control\\n- 🎓 Trainee career tips\\n- ⚡ Code examples in any language\\n\\nWhat can I help you with today?`);
  }}
  if(novaOpen) setTimeout(()=>document.getElementById('nova-input').focus(), 200);
}}

function renderNovaMd(text){{
  if(typeof marked !== 'undefined') return marked.parse(text||'');
  return text.replace(/\\n/g,'<br>');
}}

function appendNovaMsg(role, text){{
  const msgs = document.getElementById('nova-messages');
  const div = document.createElement('div');
  div.className = `nova-msg ${{role==='user'?'user':''}}`;
  div.innerHTML = `
    <div class="nova-msg-avatar">${{role==='user'?'👤':'🤖'}}</div>
    <div class="nova-bubble">${{renderNovaMd(text)}}</div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}}

function showNovaTyping(){{
  const msgs = document.getElementById('nova-messages');
  const div = document.createElement('div');
  div.className = 'nova-msg';
  div.id = 'nova-typing-indicator';
  div.innerHTML = `<div class="nova-msg-avatar">🤖</div><div class="nova-bubble"><div class="nova-typing"><span></span><span></span><span></span></div></div>`;
  msgs.appendChild(div);
  msgs.scrollTop = msgs.scrollHeight;
}}

function hideNovaTyping(){{
  const el = document.getElementById('nova-typing-indicator');
  if(el) el.remove();
}}

async function novaSend(){{
  const input = document.getElementById('nova-input');
  const msg = input.value.trim();
  if(!msg || novaTyping) return;
  input.value = '';
  input.style.height = 'auto';
  appendNovaMsg('user', msg);
  novaHistory.push({{role:'user', content:msg}});
  novaTyping = true;
  document.getElementById('nova-send').disabled = true;
  showNovaTyping();
  try{{
    const res = await fetch('https://api.groq.com/openai/v1/chat/completions', {{
      method: 'POST',
      headers: {{'Content-Type':'application/json','Authorization':'Bearer '+NOVA_API_KEY}},
      body: JSON.stringify({{
        model: 'llama-3.3-70b-versatile',
        messages: [{{role:'system',content:NOVA_SYSTEM}}, ...novaHistory.slice(-8)],
        temperature: 0.5,
        max_tokens: 600
      }})
    }});
    const data = await res.json();
    if(!res.ok) throw new Error(data.error?.message||'API error');
    const reply = data.choices[0].message.content;
    novaHistory.push({{role:'assistant', content:reply}});
    hideNovaTyping();
    appendNovaMsg('bot', reply);
  }} catch(e) {{
    hideNovaTyping();
    appendNovaMsg('bot', `❌ Oops! ${{e.message}}`);
  }}
  novaTyping = false;
  document.getElementById('nova-send').disabled = false;
}}

function novaQuick(text){{
  document.getElementById('nova-input').value = text;
  novaSend();
}}

function novaKeydown(e){{
  if(e.key==='Enter' && !e.shiftKey){{ e.preventDefault(); novaSend(); }}
}}

function autoResize(el){{
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 100) + 'px';
}}
</script>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🧠 CodeMentor AI</h1>
    <p class="version">v4.0 — Universal Language + Code Generation Edition</p>
    <p class="tagline">Your AI mentor for ALL programming languages — analyze, generate, debug, and learn</p>
    <p class="builder">✦ Built by Neelima Pasala ✦</p>
    <div style="margin-top: 1rem;">
        <span class="feature-badge">50+ Languages</span>
        <span class="feature-badge">AI Code Generation</span>
        <span class="feature-badge">Smart Debugging</span>
        <span class="feature-badge">Deep Analysis</span>
        <span class="feature-badge">Security Scanning</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Mode Tabs ────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
    "📖 Explain Code",
    "⚡ Generate Code",
    "📝 Commit Message",
    "❓ Ask Question",
    "📧 Write Email",
    "🔄 Compare Code",
    "🔧 Debug Helper",
    "🎓 Trainee Kit",
    "📜 History"
])


# ── TAB 1: DEEP CODE ANALYSIS ────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="mode-label">Mode: Deep Code Analysis — All Languages Supported</div>', unsafe_allow_html=True)
    st.markdown("Comprehensive code understanding for 50+ programming languages — structure, patterns, security, and performance.")

    col1, col2 = st.columns([3, 1])
    with col1:
        input_method = st.radio("Input method", ["Paste code", "Upload file"], horizontal=True, label_visibility="collapsed", key="explain_input")
    with col2:
        analysis_depth = st.selectbox("Analysis depth", ["Quick Explain", "Deep Analysis"], index=1, key="explain_depth")

    code_input = ""
    detected_lang = "text"
    if input_method == "Paste code":
        code_input = st.text_area("Paste your code here (any language)", height=250,
                                  placeholder="// Your code in any language...\nfunction example() {\n    return 'Hello World';\n}", key="explain_paste")
        if code_input:
            detected_lang = detect_language(code_input)
            st.markdown(f'<span class="lang-badge">Detected: {LANGUAGE_NAMES.get(detected_lang, detected_lang.upper())}</span>', unsafe_allow_html=True)
    else:
        uploaded = st.file_uploader("Upload any code file",
                                    type=list(LANGUAGE_EXTENSIONS.keys()) + ['txt'], key="explain_upload")
        if uploaded:
            code_input = uploaded.read().decode("utf-8", errors='ignore')
            detected_lang = detect_language(code_input, uploaded.name)
            st.markdown(f'<span class="lang-badge">Language: {LANGUAGE_NAMES.get(detected_lang, detected_lang.upper())}</span>', unsafe_allow_html=True)
            with st.expander("Preview uploaded code"):
                st.code(code_input, language=detected_lang)

    if st.button("🔍 Analyze Code", key="explain_btn", use_container_width=True):
        if not code_input.strip():
            st.error("Please provide some code first.")
        else:
            lang_context = f"This is {LANGUAGE_NAMES.get(detected_lang, detected_lang)} code. "

            if analysis_depth == "Deep Analysis":
                tabs_deep = st.tabs(["📋 Overview", "🔍 Deep Dive", "🎯 Patterns", "🔒 Security & Performance"])
                with tabs_deep[0]:
                    with st.spinner("Understanding structure..."):
                        system_overview = f"""{lang_context}You are a senior architect analyzing code.
Provide a high-level overview:
1. **Purpose** (1-2 sentences, plain English)
2. **Architecture/Structure** (how components relate)
3. **Tech stack/dependencies** used
4. **Entry points** and main flow
5. **Language-specific features** used

Be clear and architectural. Use markdown formatting."""
                        overview = ask_groq(system_overview, f"Analyze this code:\n\n{code_input}", max_tokens=600)
                        if overview:
                            st.markdown('<div class="result-box">', unsafe_allow_html=True)
                            st.markdown(overview)
                            st.markdown('</div>', unsafe_allow_html=True)

                with tabs_deep[1]:
                    with st.spinner("Deep diving into logic..."):
                        system_deep = f"""{lang_context}You are an expert code reviewer doing thorough analysis.
For each major function/class/component:
1. **What it does**
2. **How it works** (step-by-step logic)
3. **Input/output contracts**
4. **Edge cases** handled (or missed)
5. **Dependencies** and side effects
6. **Language-specific idioms** and best practices

Be technical but clear. Use code blocks for examples."""
                        deep_analysis = ask_groq(system_deep, f"Deep analysis:\n\n{code_input}", max_tokens=1200)
                        if deep_analysis:
                            st.markdown('<div class="result-box">', unsafe_allow_html=True)
                            st.markdown(deep_analysis)
                            st.markdown('</div>', unsafe_allow_html=True)

                with tabs_deep[2]:
                    with st.spinner("Identifying patterns and best practices..."):
                        system_patterns = f"""{lang_context}You are a software patterns expert.
Identify and explain:
1. **Design patterns** used (e.g., MVC, Factory, Observer)
2. **Coding patterns** (DRY violations, coupling issues)
3. **Language-specific patterns** and idioms
4. **Best practices** followed ✅
5. **Anti-patterns** or code smells ⚠️
6. **Suggested improvements** (prioritized)

Be specific with examples. Use tables or lists for clarity."""
                        patterns = ask_groq(system_patterns, f"Find patterns:\n\n{code_input}", max_tokens=800)
                        if patterns:
                            st.markdown('<div class="result-box">', unsafe_allow_html=True)
                            st.markdown(patterns)
                            st.markdown('</div>', unsafe_allow_html=True)

                with tabs_deep[3]:
                    with st.spinner("Running security and performance audit..."):
                        system_security = f"""{lang_context}You are a security and performance expert.
Comprehensive audit:
1. 🔒 **Security Issues** — injections, secrets, weak auth, input validation, language-specific vulnerabilities
2. ⚡ **Performance Bottlenecks** — loops, N+1 queries, memory, blocking ops, language-specific optimizations
3. 🐛 **Potential Bugs** — race conditions, null refs, edge case failures, type errors
4. For each issue: Severity (Critical/High/Medium/Low), Location, Fix recommendation

Use tables for clarity."""
                        security = ask_groq(system_security, f"Security & performance audit:\n\n{code_input}", max_tokens=1000)
                        if security:
                            st.markdown('<div class="result-box">', unsafe_allow_html=True)
                            st.markdown(security)
                            st.markdown('</div>', unsafe_allow_html=True)

                if overview and deep_analysis:
                    add_to_history("explain_deep", code_input, overview + deep_analysis)

            else:
                with st.spinner("Understanding the code..."):
                    system = f"""{lang_context}You are a patient senior developer explaining code to a junior trainee.
Explain:
1. **What** this code does (1-2 lines, plain English)
2. **How** it works (step-by-step, simple language)
3. **Language-specific features** used
4. **Key points** to remember
5. **Learning opportunities** (patterns/techniques worth knowing)

Be friendly, clear, beginner-focused. Use markdown."""
                    result = ask_groq(system, f"Explain this code:\n\n{code_input}", max_tokens=1000)
                    if result:
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        st.markdown(result)
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown('<div class="tip-box">Want deeper insights? Switch to "Deep Analysis" mode above.</div>', unsafe_allow_html=True)
                        add_to_history("explain", code_input, result)


# ── TAB 2: AI CODE GENERATION ────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="mode-label">Mode: AI Code Generation — Build Anything in Any Language</div>', unsafe_allow_html=True)
    st.markdown("Describe what you want to build — get production-ready code with explanations and best practices.")

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        target_lang = st.selectbox(
            "Target language",
            ["Python", "JavaScript", "TypeScript", "Java", "C++", "C", "C#", "Go", "Rust",
             "PHP", "Ruby", "Swift", "Kotlin", "Dart", "SQL", "Bash/Shell", "HTML/CSS",
             "R", "Scala", "Perl", "Lua", "Elixir", "Haskell", "Other (specify)"],
            key="gen_lang"
        )
    with col2:
        code_style = st.selectbox("Code style", ["Production-ready", "Learning/Tutorial", "Quick prototype"], key="gen_style")
    with col3:
        include_tests = st.checkbox("Include tests", value=False, key="gen_tests")

    gen_type = st.radio(
        "What do you want to create?",
        ["Function/Method", "Class/Module", "Complete Script/Program", "Algorithm", "Data Structure",
         "API Endpoint", "Database Query", "Frontend Component", "Custom (describe)"],
        horizontal=False,
        key="gen_type"
    )

    if gen_type == "Custom (describe)":
        gen_description = st.text_area(
            "Describe what you want to build",
            height=150,
            placeholder="Example:\nCreate a REST API endpoint that accepts a user ID, fetches their data from PostgreSQL, and returns it as JSON with proper error handling",
            key="gen_desc_custom"
        )
    else:
        gen_description = st.text_area(
            f"Describe your {gen_type.lower()}",
            height=150,
            placeholder=f"Example for {gen_type}:\n- What should it do?\n- What inputs does it take?\n- What should it return?\n- Any specific requirements or constraints?",
            key="gen_desc"
        )

    with st.expander("➕ Add context for better code generation", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            frameworks = st.text_input("Frameworks/Libraries to use", placeholder="e.g., React, Flask, Spring Boot", key="gen_frameworks")
            constraints = st.text_input("Constraints/Requirements", placeholder="e.g., Must handle 1000+ requests/sec", key="gen_constraints")
        with col2:
            use_case = st.text_input("Use case/Context", placeholder="e.g., For a mobile banking app", key="gen_usecase")
            existing_code = st.text_area("Integrate with existing code? (optional)", height=80,
                                        placeholder="Paste relevant existing code here if the generated code needs to fit with it",
                                        key="gen_existing")

    st.markdown("**Quick templates:**")
    template_cols = st.columns(5)
    with template_cols[0]:
        if st.button("🔐 Auth", key="template_auth"):
            gen_description = "Create a user authentication system with login, registration, and JWT token generation"
    with template_cols[1]:
        if st.button("📊 CRUD API", key="template_crud"):
            gen_description = "Create a complete CRUD API with endpoints for Create, Read, Update, Delete operations"
    with template_cols[2]:
        if st.button("🗄️ Database", key="template_db"):
            gen_description = "Create database models and queries for user management with proper relationships"
    with template_cols[3]:
        if st.button("⚡ Algorithm", key="template_algo"):
            gen_description = "Implement an efficient algorithm for sorting/searching with optimization"
    with template_cols[4]:
        if st.button("🎨 UI Component", key="template_ui"):
            gen_description = "Create a reusable UI component with props, state management, and styling"

    if st.button("⚡ Generate Code", key="gen_btn", use_container_width=True, type="primary"):
        if not gen_description.strip():
            st.error("Please describe what you want to build.")
        else:
            context_parts = [f"Target language: {target_lang}"]
            if frameworks:
                context_parts.append(f"Frameworks/Libraries: {frameworks}")
            if constraints:
                context_parts.append(f"Constraints: {constraints}")
            if use_case:
                context_parts.append(f"Use case: {use_case}")
            if existing_code:
                context_parts.append(f"Integrate with:\n{existing_code}")

            style_instruction = {
                "Production-ready": "production-ready with proper error handling, validation, and documentation",
                "Learning/Tutorial": "well-commented and tutorial-style for learning",
                "Quick prototype": "concise prototype focused on core functionality"
            }[code_style]

            full_context = "\n".join(context_parts)

            with st.spinner("🤖 Generating code..."):
                system = f"""You are an expert software engineer who writes clean, efficient, and production-quality code.

Generate {style_instruction} code in {target_lang} that:
1. Solves the user's requirements completely
2. Follows {target_lang} best practices and idioms
3. Includes proper error handling
4. Is well-structured and maintainable
5. {"Includes unit tests" if include_tests else "Is ready to use immediately"}

Provide:
1. **Complete working code** (properly formatted)
2. **Brief explanation** of how it works
3. **Usage example** showing how to use the code
4. **Key features** and design decisions
5. **Dependencies** needed (if any)
{"6. **Unit tests** for main functionality" if include_tests else ""}

Use markdown with proper code blocks and language syntax highlighting."""

                user_prompt = f"""Generate code for:
{gen_description}

Context:
{full_context}

Type: {gen_type}
Style: {code_style}
{"Include tests: Yes" if include_tests else ""}"""

                result = ask_groq(system, user_prompt, max_tokens=2000)

                if result:
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.session_state.generated_codes.insert(0, {
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'language': target_lang,
                        'type': gen_type,
                        'description': gen_description[:100],
                        'code': result
                    })
                    if len(st.session_state.generated_codes) > 10:
                        st.session_state.generated_codes = st.session_state.generated_codes[:10]

                    st.markdown("""<div class="success-box">
✅ Code generated successfully! Review, test, and customize as needed.
</div>""", unsafe_allow_html=True)

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🔧 Optimize this code", key="optimize_gen"):
                            with st.spinner("Optimizing..."):
                                opt_system = f"""You are a performance optimization expert for {target_lang}.
Analyze the provided code and suggest optimizations for:
1. **Performance** (time and space complexity)
2. **Memory usage**
3. **Code quality** and maintainability
4. **Best practices** specific to {target_lang}

Provide specific, actionable improvements with code examples."""
                                opt_result = ask_groq(opt_system, f"Optimize this code:\n\n{result}", max_tokens=1500)
                                if opt_result:
                                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                                    st.markdown("### 🔧 Optimization Suggestions")
                                    st.markdown(opt_result)
                                    st.markdown('</div>', unsafe_allow_html=True)

                    with col2:
                        if st.button("🔒 Security review", key="security_gen"):
                            with st.spinner("Reviewing security..."):
                                sec_system = f"""You are a security expert for {target_lang}.
Review this code for security vulnerabilities:
1. **Input validation** issues
2. **Authentication/Authorization** problems
3. **Data exposure** risks
4. **Injection attacks** vulnerabilities
5. **Other security concerns** specific to {target_lang}

Rate each issue as Critical/High/Medium/Low and provide fixes."""
                                sec_result = ask_groq(sec_system, f"Security review:\n\n{result}", max_tokens=1200)
                                if sec_result:
                                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                                    st.markdown("### 🔒 Security Review")
                                    st.markdown(sec_result)
                                    st.markdown('</div>', unsafe_allow_html=True)

                    add_to_history("generate", gen_description, result)

    if st.session_state.generated_codes:
        with st.expander("📋 Recent code generations", expanded=False):
            for idx, gen in enumerate(st.session_state.generated_codes[:5]):
                st.markdown(f"**{gen['timestamp']}** — {gen['language']} {gen['type']}")
                st.markdown(f"_{gen['description']}_")
                st.markdown("---")


# ── TAB 3: SMART COMMIT MESSAGE ───────────────────────────────────────────────
with tab3:
    st.markdown('<div class="mode-label">Mode: Smart Commit Messages</div>', unsafe_allow_html=True)
    st.markdown("Generate conventional commit messages with multiple options.")

    changes = st.text_area(
        "Describe your changes or paste git diff",
        height=200,
        placeholder="e.g.\n- Added user authentication with JWT\n- Fixed bug in payment processing\n\nOR paste output of: git diff",
        key="commit_changes"
    )
    col1, col2 = st.columns(2)
    with col1:
        commit_type = st.selectbox("Commit type hint (optional)",
                                   ["Auto-detect", "feat", "fix", "docs", "style", "refactor", "perf", "test", "chore"],
                                   key="commit_type")
    with col2:
        include_body = st.checkbox("Include detailed body", value=True, key="commit_body")

    if st.button("📝 Generate Commit Messages", key="commit_btn", use_container_width=True):
        if not changes.strip():
            st.error("Describe your changes first.")
        else:
            with st.spinner("Analyzing changes and generating commit messages..."):
                type_hint = f"\nPreferred type: {commit_type}" if commit_type != "Auto-detect" else ""
                body_hint = "\nInclude detailed body explaining what and why." if include_body else "\nKeep it concise."
                system = f"""You are an expert at writing git commit messages following Conventional Commits format.

Format: <type>(scope): <description>
Types: feat, fix, docs, style, refactor, perf, test, chore
Rules:
- First line max 72 characters
- Use imperative mood ("add" not "added")
- Be specific and professional{type_hint}{body_hint}

Provide **exactly 3 options**:
### Option 1: Quick (one-liner for small changes)
### Option 2: Standard (subject + body for regular work)
### Option 3: Detailed (comprehensive for important changes)

Use markdown formatting."""
                result = ask_groq(system, f"Write commit messages for:\n\n{changes}", max_tokens=1000)
                if result:
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('<div class="tip-box">Option 1 for quick fixes, Option 3 for major features.</div>', unsafe_allow_html=True)
                    add_to_history("commit", changes, result)


# ── TAB 4: SMART Q&A ──────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="mode-label">Mode: Smart Developer Q&A</div>', unsafe_allow_html=True)
    st.markdown("Get detailed answers with examples, explanations, and follow-up support.")

    question = st.text_input("Your question",
                            placeholder="e.g., What's the difference between Promise.all and Promise.race?",
                            key="ask_question")

    with st.expander("➕ Add context (helps get better answers)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            has_error = st.checkbox("I have an error message", key="ask_has_error")
            if has_error:
                error_msg = st.text_area("Error message", height=100, key="ask_error_msg")
        with col2:
            tried_something = st.checkbox("I tried something already", key="ask_tried")
            if tried_something:
                what_tried = st.text_area("What you tried", height=100, key="ask_what_tried")
        tech_stack = st.text_input("Tech stack / environment (optional)",
                                   placeholder="e.g., React 18, Node.js, PostgreSQL",
                                   key="ask_tech")

    additional_context = st.text_area("Any other relevant context", height=80,
                                     placeholder="Links, requirements, constraints...",
                                     key="ask_additional")

    if st.button("💬 Get Answer", key="ask_btn", use_container_width=True):
        if not question.strip():
            st.error("Please type your question first.")
        else:
            full_q = question
            context_parts = []
            if has_error and 'error_msg' in locals():
                context_parts.append(f"**Error:** {error_msg}")
            if tried_something and 'what_tried' in locals():
                context_parts.append(f"**Tried:** {what_tried}")
            if tech_stack:
                context_parts.append(f"**Tech:** {tech_stack}")
            if additional_context:
                context_parts.append(additional_context)
            if context_parts:
                full_q += "\n\n**Context:**\n" + "\n".join(context_parts)

            with st.spinner("Thinking through your question..."):
                system = """You are a helpful senior developer with 10+ years experience answering a trainee's question.

Structure your answer:
1. **Direct Answer** (2-3 sentences addressing the core question)
2. **Example** (working code snippet or command if relevant)
3. **Why It Works** (explain the underlying concept)
4. **Common Mistakes** (what beginners get wrong)
5. **Next Steps** (what to learn next or how to verify)

Keep under 300 words. Be practical and encouraging.
Use markdown formatting with code blocks."""
                result = ask_groq(system, full_q, max_tokens=1500)
                if result:
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)

                    with st.expander("💭 Have a follow-up question?"):
                        followup_q = st.text_input("Your follow-up", key="ask_followup")
                        if st.button("Ask follow-up", key="ask_followup_btn"):
                            if followup_q:
                                conversation = f"Original: {full_q}\n\nPrevious answer: {result}\n\nFollow-up: {followup_q}"
                                with st.spinner("Thinking..."):
                                    followup_result = ask_groq(system, conversation, max_tokens=1200)
                                    if followup_result:
                                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                                        st.markdown(followup_result)
                                        st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown('<div class="tip-box">You now have clear context to ask your senior effectively if still stuck!</div>', unsafe_allow_html=True)
                    add_to_history("ask", question, result)


# ── TAB 5: EMAIL TEMPLATES ────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="mode-label">Mode: Professional Email Writer</div>', unsafe_allow_html=True)
    st.markdown("Draft work emails with templates, tone control, and instant generation.")

    email_templates = {
        "Custom": "Describe your own email",
        "Leave Request": "Request time off from work",
        "Task Status Update": "Update team on task progress",
        "Request Help/Clarification": "Ask for help or clarify requirements",
        "Meeting Follow-up": "Follow up after a meeting",
        "Deadline Extension": "Request more time on a task",
        "Bug Report": "Report a bug to the team",
        "Feature Proposal": "Propose a new feature or idea",
        "Thank You": "Thank someone for their help"
    }

    col1, col2 = st.columns([2, 1])
    with col1:
        template = st.selectbox("Email template", list(email_templates.keys()), key="email_template")
    with col2:
        st.markdown(f'<div style="margin-top:1.5rem;color:#64748b;font-size:0.85rem;">{email_templates[template]}</div>',
                   unsafe_allow_html=True)

    if template == "Custom":
        situation = st.text_input("What's the email about?",
                                 placeholder="e.g., Asking to join a different project team",
                                 key="email_situation_custom")
    else:
        details = st.text_input(f"Specific details for {template.lower()}",
                               placeholder=f"e.g., For leave: 'March 25-26 for family emergency'",
                               key="email_details")
        situation = f"{template}: {details}" if details else template

    col1, col2 = st.columns(2)
    with col1:
        recipient = st.selectbox("Recipient",
                                ["Manager", "Senior Developer", "Team", "HR", "Client", "Colleague"],
                                key="email_recipient")
    with col2:
        tone = st.selectbox("Tone",
                           ["Friendly & Professional", "Formal", "Urgent", "Apologetic"],
                           key="email_tone")

    extra = st.text_area("Additional details to include", height=80,
                        placeholder="Specific dates, names, requirements, context...",
                        key="email_extra")

    if st.button("📧 Draft Email", key="email_btn", use_container_width=True):
        if not situation.strip():
            st.error("Please describe what the email is about.")
        else:
            prompt = f"**Email type:** {situation}\n**Recipient:** {recipient}\n**Tone:** {tone}"
            if extra:
                prompt += f"\n**Additional details:** {extra}"

            with st.spinner("Drafting your professional email..."):
                system = """You are an expert at writing professional workplace emails for software teams.
Write a complete, ready-to-send email with:
- **Subject:** Clear and specific
- **Greeting:** Appropriate for recipient
- **Opening:** Context in 1 sentence
- **Body:** Main message (clear, concise, actionable)
- **Closing:** Next steps or call to action
- **Sign-off:** Professional closing

Rules: Keep body under 150 words, be respectful, no filler phrases, match tone exactly.
Use markdown. Use [Your Name] as placeholder."""
                result = ask_groq(system, prompt, max_tokens=700)
                if result:
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("""<div class="tip-box">
Before sending:<br>
• Replace [Your Name] with your actual name<br>
• Read once and adjust to your personal style<br>
• Check for typos and accuracy
</div>""", unsafe_allow_html=True)
                    add_to_history("email", situation, result)


# ── TAB 6: CODE COMPARISON ────────────────────────────────────────────────────
with tab6:
    st.markdown('<div class="mode-label">Mode: Code Comparison — All Languages</div>', unsafe_allow_html=True)
    st.markdown("Compare two implementations in any language and understand which is better and why.")

    comparison_type = st.radio("Comparison type",
                              ["Different implementations", "Before/After refactor", "Your code vs. Best practice"],
                              horizontal=True,
                              key="compare_type")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Code A")
        code_a = st.text_area("First code snippet", height=200, key="code_a",
                             placeholder="def solution_a():\n    # First approach...")
        if code_a:
            lang_a = detect_language(code_a)
            st.markdown(f'<span class="lang-badge">{LANGUAGE_NAMES.get(lang_a, lang_a.upper())}</span>',
                       unsafe_allow_html=True)

    with col2:
        st.markdown("#### Code B")
        code_b = st.text_area("Second code snippet", height=200, key="code_b",
                             placeholder="def solution_b():\n    # Second approach...")
        if code_b:
            lang_b = detect_language(code_b)
            st.markdown(f'<span class="lang-badge">{LANGUAGE_NAMES.get(lang_b, lang_b.upper())}</span>',
                       unsafe_allow_html=True)

    focus_area = st.multiselect("Focus areas (optional)",
                                ["Performance", "Readability", "Maintainability", "Security", "Best Practices"],
                                default=["Performance", "Readability"],
                                key="compare_focus")

    if st.button("🔄 Compare Code", key="compare_btn", use_container_width=True):
        if not code_a.strip() or not code_b.strip():
            st.error("Please provide both code snippets.")
        else:
            focus = ", ".join(focus_area) if focus_area else "all aspects"
            lang_context = ""
            if code_a and code_b:
                lang_a = detect_language(code_a)
                lang_b = detect_language(code_b)
                if lang_a == lang_b:
                    lang_context = f"Both snippets are in {LANGUAGE_NAMES.get(lang_a, lang_a)}. "
                else:
                    lang_context = f"Code A is in {LANGUAGE_NAMES.get(lang_a, lang_a)}, Code B is in {LANGUAGE_NAMES.get(lang_b, lang_b)}. "

            with st.spinner("Analyzing and comparing implementations..."):
                system = f"""{lang_context}You are an expert code reviewer comparing two implementations.
Focus on: {focus}

### 1. Functional Differences
### 2. Code Quality (Readability, Maintainability, Best Practices)
### 3. Performance Analysis (Time & Space Complexity)
### 4. Security & Robustness
### 5. Language-specific considerations
### 6. Final Recommendation — ✅ Winner and 🔧 Improvements

Use tables, code blocks, and clear formatting."""
                result = ask_groq(system,
                                f"Compare these implementations:\n\n**Code A:**\n```\n{code_a}\n```\n\n**Code B:**\n```\n{code_b}\n```",
                                max_tokens=1800)
                if result:
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    add_to_history("compare", "code comparison", result)


# ── TAB 7: DEBUG HELPER ───────────────────────────────────────────────────────
with tab7:
    st.markdown('<div class="mode-label">Mode: Smart Debugging Assistant</div>', unsafe_allow_html=True)
    st.markdown("Get intelligent debugging help — understand errors, find root causes, and get fix suggestions.")

    debug_type = st.radio("What kind of help do you need?",
                         ["Error/Exception", "Bug/Unexpected behavior", "Performance issue", "Logic error"],
                         horizontal=True,
                         key="debug_type")

    col1, col2 = st.columns([2, 1])
    with col1:
        error_or_behavior = st.text_area(
            "Error message or describe the issue",
            height=150,
            placeholder="Paste the full error/stack trace OR describe what's going wrong...",
            key="debug_error"
        )
    with col2:
        debug_lang = st.selectbox("Language",
                                 ["Auto-detect", "Python", "JavaScript", "Java", "C++", "Go", "Rust", "Other"],
                                 key="debug_lang")

    code_context = st.text_area("Relevant code (the part that's failing)",
                               height=200,
                               placeholder="Paste the code where the issue occurs...",
                               key="debug_code")

    with st.expander("➕ Additional context for better debugging", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            what_expected = st.text_input("What did you expect to happen?", key="debug_expected")
            what_happens = st.text_input("What actually happens?", key="debug_actual")
        with col2:
            environment = st.text_input("Environment/Platform",
                                       placeholder="e.g., Python 3.11, Node 18, Ubuntu",
                                       key="debug_env")
            what_tried = st.text_area("What you've tried already", height=80, key="debug_tried")

    if st.button("🔧 Debug This", key="debug_btn", use_container_width=True, type="primary"):
        if not error_or_behavior.strip():
            st.error("Please describe the error or issue.")
        else:
            detected_lang = detect_language(code_context) if code_context else "text"
            if debug_lang != "Auto-detect":
                detected_lang = debug_lang.lower()

            context_parts = [f"Issue type: {debug_type}"]
            if detected_lang:
                context_parts.append(f"Language: {LANGUAGE_NAMES.get(detected_lang, detected_lang)}")
            if what_expected:
                context_parts.append(f"Expected: {what_expected}")
            if what_happens:
                context_parts.append(f"Actually happens: {what_happens}")
            if environment:
                context_parts.append(f"Environment: {environment}")
            if what_tried:
                context_parts.append(f"Already tried: {what_tried}")

            full_context = "\n".join(context_parts)

            with st.spinner("🔍 Analyzing the issue..."):
                system = f"""You are an expert debugging assistant for {LANGUAGE_NAMES.get(detected_lang, 'programming')}.

Analyze this debugging request and provide:

### 1. 🎯 Root Cause Analysis
- What's actually causing this issue?
- Why is it happening?

### 2. 🔍 Step-by-Step Diagnosis
- How to verify this is the problem
- How to reproduce it reliably

### 3. ✅ Solution & Fix
- Exact code fix (with explanation)
- Alternative solutions if applicable

### 4. 🛡️ Prevention
- How to avoid this in the future
- Testing strategy to catch similar issues

### 5. 📚 Learning Point
- What concept or pattern caused confusion?
- Related concepts to understand

Be specific, practical, and educational. Use code blocks with syntax highlighting."""

                debug_prompt = f"""Context:
{full_context}

Error/Issue:
{error_or_behavior}

{"Relevant code:" if code_context else ""}
{code_context if code_context else "No code provided"}"""

                result = ask_groq(system, debug_prompt, max_tokens=2000)

                if result:
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown("""<div class="success-box">
💡 Still stuck? Try these next steps:<br>
• Add console.log / print statements to trace execution<br>
• Use a debugger to step through the code<br>
• Check the documentation for the specific function/API<br>
• Search Stack Overflow for the exact error message
</div>""", unsafe_allow_html=True)

                    add_to_history("debug", error_or_behavior, result)


# ── TAB 8: TRAINEE KIT ────────────────────────────────────────────────────────
with tab8:
    st.markdown('<div class="mode-label">Mode: Trainee Skill Kit — What Every Software Trainee Really Needs</div>', unsafe_allow_html=True)
    st.markdown("Real gaps that training programs miss — the unspoken skills that make or break your career.")

    st.markdown("""
<div style="background: linear-gradient(135deg, #1e1b4b 0%, #1a1f2e 100%); border:1px solid #3730a3; border-radius:12px; padding:1.5rem; margin-bottom:1.5rem;">
<p style="color:#c4b5fd; font-family: JetBrains Mono, monospace; font-size:0.85rem; margin:0 0 0.5rem 0; font-weight:600;">⚡ THE HONEST TRUTH</p>
<p style="color:#94a3b8; font-size:0.9rem; line-height:1.7; margin:0;">
Training gives you syntax. The real job needs you to <strong style="color:#e2e8f0;">think, communicate, debug under pressure, and work with people</strong>.
Here's everything they forgot to teach you — and what separates a good trainee from a great one.
</p>
</div>
""", unsafe_allow_html=True)

    need_col1, need_col2 = st.columns(2)

    with need_col1:
        st.markdown("""
<div class="need-card">
<h4>🔍 1. Debugging Mindset</h4>
<p>Reading a stack trace is a skill. Most trainees panic at errors — seniors use them as a map.
Learn to read logs top-to-bottom, isolate the failing line, reproduce the bug in isolation, and Google the exact error message in quotes.</p>
<span class="need-tag">TOP PRIORITY</span>
</div>

<div class="need-card">
<h4>🌿 2. Git Beyond Basics</h4>
<p>You know <code>git commit</code>. But can you rebase without losing work? Resolve a merge conflict? Cherry-pick a fix? Reset a bad commit? These happen daily in real teams.</p>
<span class="need-tag">DAILY USE</span>
</div>

<div class="need-card">
<h4>💬 3. Asking Good Questions</h4>
<p>Never say "it's not working." Always bring: what you tried, the exact error, and what you expected vs what happened. This is the #1 skill that makes seniors want to help you.</p>
<span class="need-tag">CAREER CRITICAL</span>
</div>

<div class="need-card">
<h4>📖 4. Reading Other People's Code</h4>
<p>Training writes code. Real work reads code. Practice reading open-source codebases, your team's old code, and code you didn't write — without running it. Build this muscle early.</p>
<span class="need-tag">OFTEN SKIPPED</span>
</div>

<div class="need-card">
<h4>🗣️ 5. Communicating Blockers Early</h4>
<p>Don't stay stuck for 4 hours in silence. Raise blockers within 30 minutes. Being vocal about problems (with a clear description) is professionalism — not weakness.</p>
<span class="need-tag">TEAM SKILL</span>
</div>

<div class="need-card">
<h4>🧪 6. Writing Tests (Even Basic Ones)</h4>
<p>A function with no test is a liability. Learn to write at least one unit test per function you build. It forces you to think about edge cases and saves hours of debugging.</p>
<span class="need-tag">UNDERVALUED</span>
</div>
""", unsafe_allow_html=True)

    with need_col2:
        st.markdown("""
<div class="need-card">
<h4>🏗️ 7. System Thinking</h4>
<p>Can you explain how your feature affects the whole system? Database? Cache? Other services? Trainees think in functions. Seniors think in systems. Start asking "what else does this touch?"</p>
<span class="need-tag">LEVEL-UP SKILL</span>
</div>

<div class="need-card">
<h4>📋 8. Writing Readable Code — Not Just Working Code</h4>
<p>Code is read 10x more than it's written. Name variables clearly, keep functions short, add comments for WHY not WHAT. Your teammates will thank you and your code reviews will be smoother.</p>
<span class="need-tag">DAILY HABIT</span>
</div>

<div class="need-card">
<h4>⏱️ 9. Estimating Tasks Honestly</h4>
<p>Never say "it'll take 10 minutes" when you don't know. Say "I'll check and tell you by lunch." Learn to break tasks down before estimating. Wrong estimates damage trust faster than slow work.</p>
<span class="need-tag">CAREER CRITICAL</span>
</div>

<div class="need-card">
<h4>🛠️ 10. Environment & Tooling Comfort</h4>
<p>Know your terminal, IDE shortcuts, and how to set up a project from scratch. Trainees who can set up their own dev environment independently save hours for the whole team.</p>
<span class="need-tag">OFTEN SKIPPED</span>
</div>

<div class="need-card">
<h4>📝 11. Writing PR Descriptions & Comments</h4>
<p>A pull request without context is noise. Write why you made the change, what you tested, and what reviewers should focus on. This habit alone will fast-track your promotions.</p>
<span class="need-tag">TEAM SKILL</span>
</div>

<div class="need-card">
<h4>🧘 12. Handling Feedback Without Ego</h4>
<p>Code review feedback is about the code, not you. The trainees who grow fastest treat every comment as free mentorship. Say "thanks, I'll fix that" — never "but I thought...".</p>
<span class="need-tag">MINDSET</span>
</div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
<div style="background:#0f1420; border:1px solid #2d3748; border-left:4px solid #a78bfa; border-radius:8px; padding:1.2rem 1.5rem; margin-top:1rem;">
<p style="color:#a78bfa; font-family:JetBrains Mono,monospace; font-size:0.78rem; font-weight:600; margin-bottom:0.6rem;">🤖 ASK CODEMENTOR AI — Drill into any skill above</p>
</div>
""", unsafe_allow_html=True)

    trainee_question = st.text_area(
        "Ask about any trainee skill — get a real, practical explanation",
        height=100,
        placeholder="e.g., How do I read a stack trace? / How do I resolve a merge conflict? / How do I estimate tasks better?",
        key="trainee_question"
    )

    if st.button("🎓 Get Trainee Advice", key="trainee_btn", use_container_width=True):
        if not trainee_question.strip():
            st.error("Please ask a question.")
        else:
            with st.spinner("Getting practical trainee advice..."):
                system = """You are a senior software engineer mentoring a brand-new trainee (0-1 year of experience).

Answer their question with extreme practicality:
1. **What it actually is** (in simple terms)
2. **Why it matters** in real team settings
3. **Step-by-step: how to do it** (with examples, commands, or code)
4. **Common trainee mistakes** to avoid
5. **One daily habit** to build this skill

Be warm, encouraging, specific. Use code blocks and markdown. No fluff."""
                result = ask_groq(system, trainee_question, max_tokens=1500)
                if result:
                    st.markdown('<div class="result-box">', unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)
                    add_to_history("trainee", trainee_question, result)


# ── TAB 9: HISTORY ────────────────────────────────────────────────────────────
with tab9:
    st.markdown('<div class="mode-label">Mode: Session History</div>', unsafe_allow_html=True)
    st.markdown("View your recent queries and analyses from this session.")

    if not st.session_state.history:
        st.info("No history yet. Start using CodeMentor AI to build your session history!")
    else:
        st.markdown(f"**Showing last {len(st.session_state.history)} queries**")

        for idx, entry in enumerate(st.session_state.history):
            with st.expander(f"{entry['timestamp']} — {entry['mode'].upper()}", expanded=False):
                st.markdown(f"**Input:**")
                st.code(entry['input'], language="text")
                st.markdown(f"**Output preview:**")
                st.markdown(entry['output'])

        if st.button("🗑️ Clear History", key="clear_history"):
            st.session_state.history = []
            st.session_state.analysis_count = 0
            st.session_state.favorite_mode = {}
            st.session_state.generated_codes = []
            st.rerun()

st.markdown("---")
st.markdown(
    '<p style="text-align:center;color:#334155;font-size:0.82rem;font-family:JetBrains Mono,monospace;margin-top:1.5rem;">'
    '🧠 CodeMentor AI v4.0 — Built by <span style="color:#a78bfa;">Neelima Pasala</span> &nbsp;|&nbsp; '
    'Powered by LLaMA 3.3 70B via Groq &nbsp;|&nbsp; Supports 50+ Programming Languages'
    '</p>',
    unsafe_allow_html=True
)
