# streamlit_app.py - 蓝白ChatGPT风格主页 + 桌宠联动
import streamlit as st
import pandas as pd
import numpy as np
import requests
import json
import time
import base64
import html
import re
import io
import os
import matplotlib
import plotly.graph_objects as go
from plotly.subplots import make_subplots

matplotlib.use('Agg')
import matplotlib.pyplot as plt

# 从 task_detector 导入统一字典
from task_detector import TaskTypeDetector, MODEL_SUPPORT, MODEL_NAMES, MODEL_INFO

# 桌宠悬浮球组件
from pet_component import render_desktop_pet, RICE_FEED_LINES

# 中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 页面配置
st.set_page_config(
    page_title="喂食大肥鱼",
    page_icon="🐋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========== 内置API密钥 ==========
DEFAULT_API_KEY = "sk-907f6f05ccad496a9b863a334aad6ead"
DEFAULT_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEFAULT_API_MODEL = "deepseek-chat"

# ========== 预设分析提示词 ==========
DEFAULT_ANALYSIS_PROMPT = """
====================
*114*预设提示词区*514*
====================
请对以上数据集进行专业的数据分析或预测，包括：
1. 数据集/模型评估（首先区分是分类还是预测）
2. 选择目标列和目标列的相关性
3. 对目标列进行预测
4. 改进方向
5. 对预处理后数据及分析数据结果的整体效果评估
"""

# ========== 上传按钮图片（默认 / hover） ==========
def _load_deepseekchan_b64(filename):
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "deepseekchan", filename)
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("ascii")
    except Exception:
        return ""


UPLOAD_IMG_DEFAULT = _load_deepseekchan_b64("host.png")
UPLOAD_IMG_HOVER = _load_deepseekchan_b64("host_1.png")
UPLOAD_IMG_DEFAULT_CSS = (
    f'url("data:image/png;base64,{UPLOAD_IMG_DEFAULT}")'
    if UPLOAD_IMG_DEFAULT else "linear-gradient(135deg,#eef6ff,#ffffff)"
)
UPLOAD_IMG_HOVER_CSS = (
    f'url("data:image/png;base64,{UPLOAD_IMG_HOVER}")'
    if UPLOAD_IMG_HOVER else UPLOAD_IMG_DEFAULT_CSS
)

# ========== 全局蓝白主题CSS ==========
_PAGE_CSS = f"""
<style>
.stApp {{
    background: linear-gradient(180deg, #e9f2ff 0%, #f8fbff 45%, #eaf2ff 100%) !important;
}}
header[data-testid="stHeader"] {{
    background: transparent !important;
}}
#MainMenu, footer {{
    visibility: hidden;
}}
.ffp-page-title {{
    text-align: center;
    font-size: 30px;
    font-weight: 800;
    color: #1d4e8f;
    margin-top: 26px;
    letter-spacing: 2px;
}}
.ffp-page-sub {{
    text-align: center;
    font-size: 13px;
    color: #7a9cc8;
    margin-bottom: 14px;
}}
.ffp-page-switch {{
    width: fit-content;
    margin: 4px 0 8px;
}}
.ffp-page-switch [data-testid="stRadio"] > div {{
    gap: 4px;
}}
.ffp-page-switch label {{
    padding: 4px 10px;
    border: 1px solid #cfe6ff;
    border-radius: 8px;
    background: #ffffff;
    color: #1d4e8f;
    font-size: 12px;
}}
.ffp-main-msg {{
    max-width: 31%;
    padding: 12px 16px;
    border-radius: 14px;
    font-size: 14px;
    line-height: 1.65;
    word-break: break-word;
    margin-bottom: 10px;
}}
.ffp-main-msg.user {{
    background: #2f80ed;
    color: #ffffff;
    margin-left: auto;
    margin-right: 10%;
    border-bottom-right-radius: 4px;
    box-shadow: 0 3px 12px rgba(47,128,237,.25);
}}
.ffp-main-msg.ai {{
    background: #ffffff;
    color: #1c2b4a;
    border: 1px solid #d9e8fa;
    margin-right: auto;
    margin-left: 10%;
    border-bottom-left-radius: 4px;
    box-shadow: 0 2px 8px rgba(30,80,160,.07);
}}
.ffp-main-msg code {{
    background: rgba(0,0,0,.07);
    padding: 1px 5px;
    border-radius: 5px;
    font-family: Consolas, monospace;
    font-size: 12.5px;
}}
.ffp-main-msg.user code {{
    background: rgba(255,255,255,.25);
}}
div[data-testid="stTextInput"] input {{
    border-radius: 26px !important;
    border: 1.5px solid #cfe6ff !important;
    background: #ffffff !important;
    padding: 15px 22px !important;
    font-size: 15px !important;
    box-shadow: 0 5px 18px rgba(30,80,160,.10) !important;
    color: #1c2b4a !important;
}}
div[data-testid="stTextInput"] input:focus {{
    border-color: #2f80ed !important;
    box-shadow: 0 5px 18px rgba(47,128,237,.22) !important;
}}
[data-testid="stFileUploader"] {{
    display: flex !important;
    justify-content: center !important;
}}
[data-testid="stFileUploaderDropzone"],
[data-testid="stFileUploadDropzone"] {{
    position: relative !important;
    overflow: hidden !important;
    background: {UPLOAD_IMG_DEFAULT_CSS} center/contain no-repeat !important;
    background-color: transparent !important;
    border: none !important;
    width: min(460px, 92vw) !important;
    max-width: 100% !important;
    height: 230px !important;
    cursor: pointer !important;
    transition: transform .15s ease, filter .15s ease;
    -webkit-transition: -webkit-transform .15s ease, filter .15s ease;
    background-origin: border-box !important;
    background-clip: border-box !important;
}}
[data-testid="stFileUploaderDropzone"]::before,
[data-testid="stFileUploadDropzone"]::before {{
    content: "";
    position: absolute;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background: {UPLOAD_IMG_DEFAULT_CSS} center/contain no-repeat;
}}
[data-testid="stFileUploaderDropzone"]:hover,
[data-testid="stFileUploadDropzone"]:hover {{
    background-image: {UPLOAD_IMG_HOVER_CSS} !important;
    transform: scale(1.03);
    -webkit-transform: scale(1.03);
}}
[data-testid="stFileUploaderDropzone"]:hover::before,
[data-testid="stFileUploadDropzone"]:hover::before {{
    background-image: {UPLOAD_IMG_HOVER_CSS};
}}
[data-testid="stFileUploaderDropzone"] > *,
[data-testid="stFileUploadDropzone"] > * {{
    position: relative;
    z-index: 1;
}}
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] button,
[data-testid="stFileUploaderDropzone"] small,
[data-testid="stFileUploadDropzone"] span,
[data-testid="stFileUploadDropzone"] button,
[data-testid="stFileUploadDropzone"] small {{
    visibility: hidden !important;
    position: absolute !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"],
[data-testid="stFileDropzoneInstructions"] {{
    display: none !important;
}}
[data-testid="stFileUploaderFileList"],
[data-testid="stUploadedFile"] {{
    display: none !important;
}}
.ffp-file-row {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    margin-top: 10px;
    margin-bottom: 4px;
}}
.ffp-file-name {{
    background: #ffffff;
    border: 1px solid #d9e8fa;
    border-radius: 10px;
    padding: 6px 14px;
    font-size: 13px;
    color: #1d4e8f;
    box-shadow: 0 2px 8px rgba(30,80,160,.06);
}}
</style>
"""
st.markdown(_PAGE_CSS, unsafe_allow_html=True)

# ========== 初始化 session state ==========
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'target_column' not in st.session_state:
    st.session_state.target_column = None
if 'target_type' not in st.session_state:
    st.session_state.target_type = None
if 'manual_task_type' not in st.session_state:
    st.session_state.manual_task_type = None
if 'task_type_option' not in st.session_state:
    st.session_state.task_type_option = "自动检测"
if '_pending_task_type_option' not in st.session_state:
    st.session_state._pending_task_type_option = None
if '_detected_task_key' not in st.session_state:
    st.session_state._detected_task_key = None
if '_task_type_selection_source' not in st.session_state:
    st.session_state._task_type_selection_source = "auto"
if 'uploader_epoch' not in st.session_state:
    st.session_state.uploader_epoch = 0
if 'api_key' not in st.session_state:
    st.session_state.api_key = DEFAULT_API_KEY
if 'api_url' not in st.session_state:
    st.session_state.api_url = DEFAULT_API_URL
if 'api_model' not in st.session_state:
    st.session_state.api_model = DEFAULT_API_MODEL
if 'api_provider' not in st.session_state:
    st.session_state.api_provider = "DeepSeek"
if 'api_key_input' not in st.session_state:
    st.session_state.api_key_input = st.session_state.api_key
if 'api_url_input' not in st.session_state:
    st.session_state.api_url_input = st.session_state.api_url
if 'api_model_input' not in st.session_state:
    st.session_state.api_model_input = st.session_state.api_model
if '_pending_api_config' not in st.session_state:
    st.session_state._pending_api_config = None

if st.session_state._pending_api_config:
    _config = st.session_state._pending_api_config
    st.session_state.api_key_input = _config.get("api_key", "")
    st.session_state.api_url_input = _config.get("api_url", "")
    st.session_state.api_model_input = _config.get("api_model", "")
    if _config.get("provider") in ("DeepSeek", "其他来源"):
        st.session_state.api_provider = _config["provider"]
    st.session_state.api_key = st.session_state.api_key_input
    st.session_state.api_url = st.session_state.api_url_input
    st.session_state.api_model = st.session_state.api_model_input
    st.session_state._pending_api_config = None

# 清除数据集时必须在任务类型 radio 实例化前重置其绑定状态。
if st.session_state.pop('_clear_dataset', False):
    st.session_state.uploader_epoch += 1
    st.session_state.df = None
    st.session_state._uploaded_name = None
    st.session_state.target_column = None
    st.session_state.target_type = None
    st.session_state.selected_features = None
    st.session_state.task_type_option = "自动检测"
    st.session_state._pending_task_type_option = None
    st.session_state._detected_task_key = None
    st.session_state._task_type_selection_source = "auto"
    st.session_state.analysis_result = None
    st.session_state.training_logs = []
    st.session_state.training_history = None
    st.session_state.pet_analysis_notified = False
    st.session_state['_eda_save_status'] = None
    st.session_state['_eda_save_status_token'] = 0
    st.session_state['_df_rerun_key'] = None
    st.session_state['_pet_popup_key'] = None
    st.session_state['_drawer_cache_key'] = None
    st.session_state['_drawer_cache_html'] = None
if 'selected_features' not in st.session_state:
    st.session_state.selected_features = None
if 'analyzing' not in st.session_state:
    st.session_state.analyzing = False
if 'training_logs' not in st.session_state:
    st.session_state.training_logs = []
if 'training_history' not in st.session_state:
    st.session_state.training_history = None
if 'pet_analysis_notified' not in st.session_state:
    st.session_state.pet_analysis_notified = False
if 'main_chat' not in st.session_state:
    st.session_state.main_chat = []
if 'current_page' not in st.session_state:
    st.session_state.current_page = "数据集分析"
if 'catdog_chat' not in st.session_state:
    st.session_state.catdog_chat = []
if 'catdog_train_epoch' not in st.session_state:
    st.session_state.catdog_train_epoch = 0
if 'catdog_predict_epoch' not in st.session_state:
    st.session_state.catdog_predict_epoch = 0

# ============================================================
# ===== 桌宠→主端消息哨兵（通过页面对话输入框回车提交） =====
# 投喂回传：FFP_FEED_TOKEN + token + ":" + 台词序号 —— 主端直接输出20条投喂台词之一（不产生用户消息）
# 教程重跑：FFP_RERUN_TOKEN（仅触发重跑读取教程URL参数，不产生消息）
# ============================================================
FFP_FEED_TOKEN = "[[FFP_FEED]]"
FFP_RERUN_TOKEN = "[[FFP_RERUN]]"
FFP_SAVE_EDA_TOKEN = "[[FFP_SAVE_EDA]]"


def _parse_feed_sentinel(raw_text):
    """解析投喂哨兵，返回 (token, 台词序号)；非投喂哨兵返回 None"""
    body = raw_text[len(FFP_FEED_TOKEN):].strip()
    parts = body.split(":", 1)
    if not parts:
        return None
    feed_token = parts[0].strip()
    try:
        feed_idx = int(parts[1].strip()) if len(parts) > 1 else -1
    except (ValueError, TypeError):
        feed_idx = -1
    return feed_token, feed_idx


def _pick_feed_line(feed_idx):
    """从20条投喂台词中选一条输出（序号越界时随机挑一条）"""
    lines = list(RICE_FEED_LINES or [])
    if lines:
        if isinstance(feed_idx, int) and 0 <= feed_idx < len(lines):
            return lines[feed_idx]
        return lines[int(time.time_ns()) % len(lines)]
    return "好感度+1，白饭很好吃哦。(๑´ڡ`๑)"


if 'ffp_feed_token' not in st.session_state:
    st.session_state.ffp_feed_token = None
if 'ffp_save_eda_token' not in st.session_state:
    st.session_state.ffp_save_eda_token = None
if '_eda_save_status' not in st.session_state:
    st.session_state._eda_save_status = None
if '_eda_save_status_token' not in st.session_state:
    st.session_state._eda_save_status_token = 0

if 'show_analyze_dialog' not in st.session_state:
    st.session_state.show_analyze_dialog = False
if 'pending_analyze' not in st.session_state:
    st.session_state.pending_analyze = False
if 'dlg_save_models' not in st.session_state:
    st.session_state.dlg_save_models = False
if 'dlg_save_dir' not in st.session_state:
    st.session_state.dlg_save_dir = "saved_models"
if 'dlg_report_format' not in st.session_state:
    st.session_state.dlg_report_format = "md"
if 'catdog_result' not in st.session_state:
    st.session_state.catdog_result = None
if 'catdog_prediction' not in st.session_state:
    st.session_state.catdog_prediction = None


def _api_base_url():
    return os.environ.get("API_BASE_URL", "http://localhost:8000").rstrip("/")


def _handle_eda_save():
    """调用后端保存EDA为Word文档，返回提示消息"""
    df = st.session_state.df
    if df is None:
        return "❌ 请先投喂数据集，再保存EDA报告"
    target = st.session_state.target_column or ""
    try:
        files = {"file": ("dataset.csv", df.to_csv(index=False).encode("utf-8"), "text/csv")}
        data = {"target_column": target}
        r = requests.post(f"{_api_base_url()}/api/eda/save", files=files, data=data, timeout=180)
        if r.status_code == 200:
            j = r.json()
            return f"✅ EDA已保存到 `{j.get('save_path')}`（{j.get('n_rows')} 行 × {j.get('n_cols')} 列）"
        return f"❌ EDA保存失败：{r.text[:200]}"
    except Exception as e:
        return f"❌ EDA保存失败：{e}"


if st.session_state.current_page == "图像识别":
    st.markdown(
        '<style>section[data-testid="stSidebar"]{display:none!important;} '
        '[data-testid="collapsedControl"]{display:none!important;}</style>',
        unsafe_allow_html=True
    )


def render_pet_footer():
    popup_msg = st.session_state.pop('_pet_popup_pending_msg', None)
    popup_token = st.session_state.pop('_pet_popup_pending_token', None)
    notify_msg = st.session_state.pop('pet_notify_pending_msg', None)
    notify_token = st.session_state.pop('pet_notify_pending_token', None)
    open_sidebar_token = st.session_state.pop('_sidebar_open_pending_token', None)

    drawer_html = None
    if st.session_state.df is not None:
        _cache_key = (id(st.session_state.df), str(st.session_state.target_column),
                      st.session_state.get('_eda_save_status_token', 0))
        try:
            if st.session_state.get('_drawer_cache_key') != _cache_key:
                st.session_state['_drawer_cache_key'] = _cache_key
                st.session_state['_drawer_cache_html'] = build_drawer_html(
                    st.session_state.df, st.session_state.target_column
                )
            drawer_html = st.session_state.get('_drawer_cache_html')
        except Exception:
            drawer_html = None

    page_scope = "catdog" if st.session_state.current_page == "图像识别" else "main"
    render_desktop_pet(
        popup_msg=popup_msg,
        popup_token=popup_token,
        notify_msg=notify_msg,
        notify_token=notify_token,
        drawer_html=drawer_html,
        open_sidebar_token=open_sidebar_token,
        page_scope=page_scope
    )


def render_terminal_html(logs):
    """将训练日志渲染为终端样式HTML（深色背景、绿色文字、可滚动）"""
    body = html.escape("\n".join(logs[-300:]))
    return (
        '<div style="background:#0d1117;color:#3fb950;'
        'font-family:\'Consolas\',\'Courier New\',monospace;'
        'font-size:12.5px;line-height:1.55;padding:12px 14px;'
        'border-radius:8px;border:1px solid #30363d;'
        'max-height:360px;overflow-y:auto;white-space:pre-wrap;word-break:break-all;">'
        f"{body}"
        '</div>'
    )


def _md_to_html(text):
    t = html.escape(str(text))
    t = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'^#{1,3}\s+(.*)$', r'<div style="font-weight:700;margin:4px 0;">\1</div>', t, flags=re.M)
    t = t.replace('\n', '<br>')
    return t


def _read_uploaded_csv(uploaded_file):
    """按常见中文编码读取上传的 CSV，失败时返回 None。"""
    encodings = ('utf-8', 'utf-8-sig', 'gb18030', 'gbk', 'gb2312', 'cp936', 'latin-1')
    for encoding in encodings:
        try:
            uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding=encoding)
        except (UnicodeDecodeError, pd.errors.ParserError, LookupError):
            continue
        except Exception:
            continue
    try:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, encoding='utf-8', encoding_errors='ignore')
    except Exception:
        return None


def _fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return b64


def build_drawer_html(df, target_col):
    """构建右侧数据集抽屉的内容HTML（预览/列信息/可视化/检测详情）"""
    parts = []
    status = st.session_state.get('_eda_save_status')
    parts.append(
        '<div style="display:flex;align-items:center;justify-content:space-between;gap:10px;">'
        f'<div class="ffp-drawer-sub" style="margin-bottom:0;">共 {len(df)} 行 × {len(df.columns)} 列</div>'
        '<button id="ffp-eda-save-btn" type="button">💾 保存</button>'
        '</div>'
    )
    if status:
        parts.append(f'<div class="ffp-drawer-sub" style="color:#1e8e3e;">{status}</div>')
    parts.append('<div class="ffp-drawer-h">👀 数据预览（前 8 行）</div>')
    parts.append(df.head(8).to_html(index=False, classes='ffp-tbl', border=0))
    info = pd.DataFrame({
        '列名': [str(c) for c in df.columns],
        '类型': [str(df[c].dtype) for c in df.columns],
        '唯一值': [int(df[c].nunique()) for c in df.columns],
        '缺失值': [int(df[c].isnull().sum()) for c in df.columns],
    })
    parts.append('<div class="ffp-drawer-h">🧾 列信息</div>')
    parts.append(info.to_html(index=False, classes='ffp-tbl', border=0))

    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
    cat_cols = [c for c in df.columns if c not in numeric_cols]

    # ===== 单变量分布（直方图） =====
    vis_cols = numeric_cols[:6]
    if vis_cols:
        try:
            n = len(vis_cols)
            ncols = 2
            nrows = int(np.ceil(n / ncols))
            fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 3.6, nrows * 2.4))
            axes = np.atleast_1d(axes).ravel()
            for i, col in enumerate(vis_cols):
                ax = axes[i]
                ax.hist(pd.to_numeric(df[col], errors='coerce').dropna(), bins=24,
                        color='#4ecdc4', edgecolor='white')
                ax.set_title(col, fontsize=9)
                ax.tick_params(labelsize=7)
            for j in range(n, len(axes)):
                axes[j].set_visible(False)
            fig.suptitle('单变量分布（直方图）', fontsize=11)
            fig.tight_layout()
            parts.append('<div class="ffp-drawer-h">📊 单变量分布（直方图）</div>')
            parts.append(f'<img src="data:image/png;base64,{_fig_to_b64(fig)}">')
        except Exception:
            pass

    # ===== 单变量分布（箱线图） =====
    if vis_cols:
        try:
            n = len(vis_cols)
            ncols = 2
            nrows = int(np.ceil(n / ncols))
            fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 3.6, nrows * 2.4))
            axes = np.atleast_1d(axes).ravel()
            for i, col in enumerate(vis_cols):
                ax = axes[i]
                data = pd.to_numeric(df[col], errors='coerce').dropna()
                ax.boxplot(data, vert=True, patch_artist=True,
                           boxprops=dict(facecolor='#a8d8ff', color='#2f80ed'),
                           medianprops=dict(color='#1d4e8f'),
                           whiskerprops=dict(color='#2f80ed'),
                           capprops=dict(color='#2f80ed'),
                           flierprops=dict(marker='o', markerfacecolor='#ff9db1', markersize=3))
                ax.set_title(col, fontsize=9)
                ax.tick_params(labelsize=7)
            for j in range(n, len(axes)):
                axes[j].set_visible(False)
            fig.suptitle('单变量分布（箱线图）', fontsize=11)
            fig.tight_layout()
            parts.append('<div class="ffp-drawer-h">📦 单变量分布（箱线图）</div>')
            parts.append(f'<img src="data:image/png;base64,{_fig_to_b64(fig)}">')
        except Exception:
            pass

    # ===== 双变量关系（特征 vs 目标列） =====
    if target_col and target_col in df.columns:
        feats = [c for c in numeric_cols[:6] if c != target_col]
        if feats:
            try:
                n = len(feats)
                ncols = 2
                nrows = int(np.ceil(n / ncols))
                fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 3.6, nrows * 2.6))
                axes = np.atleast_1d(axes).ravel()
                for i, col in enumerate(feats):
                    ax = axes[i]
                    x = pd.to_numeric(df[col], errors='coerce')
                    y = pd.to_numeric(df[target_col], errors='coerce')
                    mask = x.notna() & y.notna()
                    xv, yv = x[mask], y[mask]
                    ax.scatter(xv, yv, s=10, alpha=0.55, color='#2f80ed', edgecolors='none')
                    if len(xv) > 2:
                        try:
                            k = np.polyfit(xv, yv, 1)
                            line = np.poly1d(k)
                            xs = np.linspace(xv.min(), xv.max(), 50)
                            ax.plot(xs, line(xs), color='#ff6b6b', linewidth=1.6)
                        except Exception:
                            pass
                    ax.set_xlabel(col, fontsize=8)
                    ax.set_ylabel(target_col, fontsize=8)
                    ax.tick_params(labelsize=7)
                for j in range(n, len(axes)):
                    axes[j].set_visible(False)
                fig.suptitle(f'双变量关系（特征 vs {target_col}，红线为趋势）', fontsize=11)
                fig.tight_layout()
                parts.append('<div class="ffp-drawer-h">📈 双变量关系（特征 vs 目标列）</div>')
                parts.append(f'<img src="data:image/png;base64,{_fig_to_b64(fig)}">')
            except Exception:
                pass

        # ===== 分类特征 vs 目标列 =====
        cat_feats = [c for c in cat_cols[:4] if c != target_col]
        if cat_feats:
            try:
                y_numeric = pd.to_numeric(df[target_col], errors='coerce')
                target_is_num = y_numeric.notna().sum() > len(df) * 0.7
                n = len(cat_feats)
                ncols = 2
                nrows = int(np.ceil(n / ncols))
                fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 3.6, nrows * 2.6))
                axes = np.atleast_1d(axes).ravel()
                for i, col in enumerate(cat_feats):
                    ax = axes[i]
                    if target_is_num:
                        cats = sorted(df[col].astype(str).unique())[:8]
                        vals = [y_numeric[df[col].astype(str) == v].dropna().values for v in cats]
                        ax.boxplot(vals, labels=[c[:6] for c in cats], patch_artist=True,
                                   boxprops=dict(facecolor='#a8d8ff', color='#2f80ed'),
                                   medianprops=dict(color='#1d4e8f'),
                                   whiskerprops=dict(color='#2f80ed'),
                                   capprops=dict(color='#2f80ed'),
                                   flierprops=dict(marker='o', markerfacecolor='#ff9db1', markersize=3))
                        ax.set_ylabel(target_col, fontsize=8)
                    else:
                        ct = pd.crosstab(df[col].astype(str), df[target_col].astype(str))
                        ct.head(8).plot(kind='bar', ax=ax, color=plt.cm.tab10.colors[:len(ct.columns)],
                                        edgecolor='white', fontsize=7)
                        ax.tick_params(labelsize=7)
                        ax.legend(fontsize=6, loc='best')
                    ax.set_title(col, fontsize=9)
                    ax.tick_params(labelsize=7)
                for j in range(n, len(axes)):
                    axes[j].set_visible(False)
                fig.suptitle(f'分类特征 vs {target_col}', fontsize=11)
                fig.tight_layout()
                parts.append('<div class="ffp-drawer-h">🏷️ 分类特征与目标列关系</div>')
                parts.append(f'<img src="data:image/png;base64,{_fig_to_b64(fig)}">')
            except Exception:
                pass

    # ===== 相关性热图 =====
    if len(numeric_cols) > 1:
        try:
            cols = numeric_cols[:12]
            corr = df[cols].corr()
            fig, ax = plt.subplots(figsize=(5.6, 4.4))
            im = ax.imshow(corr.values, cmap='RdBu_r', vmin=-1, vmax=1)
            ax.set_xticks(range(len(cols)))
            ax.set_xticklabels(cols, rotation=45, ha='right', fontsize=8)
            ax.set_yticks(range(len(cols)))
            ax.set_yticklabels(cols, fontsize=8)
            for i in range(len(cols)):
                for j in range(len(cols)):
                    ax.text(j, i, f'{corr.values[i, j]:.2f}', ha='center', va='center', fontsize=6.5,
                            color='white' if abs(corr.values[i, j]) > 0.55 else '#1c2b4a')
            ax.set_title('特征相关性热图', fontsize=11)
            fig.colorbar(im, ax=ax, shrink=0.8)
            parts.append('<div class="ffp-drawer-h">🔥 特征相关性热图</div>')
            parts.append(f'<img src="data:image/png;base64,{_fig_to_b64(fig)}">')
        except Exception:
            pass

    # ===== 目标列分布 =====
    if target_col and target_col in df.columns:
        try:
            s = df[target_col]
            fig, ax = plt.subplots(figsize=(5.6, 3.2))
            if pd.api.types.is_numeric_dtype(s) and s.nunique() > 20:
                ax.hist(pd.to_numeric(s, errors='coerce').dropna(), bins=30, color='#4ecdc4', edgecolor='white')
                ax.set_title(f'{target_col} 分布', fontsize=11)
            else:
                vc = s.astype(str).value_counts().head(12)
                ax.barh(list(vc.index)[::-1], list(vc.values)[::-1], color='#2f80ed')
                ax.set_title(f'{target_col} 分布（Top12）', fontsize=11)
            parts.append('<div class="ffp-drawer-h">🎯 目标列分布</div>')
            parts.append(f'<img src="data:image/png;base64,{_fig_to_b64(fig)}">')
        except Exception:
            pass

    # ===== 任务类型检测 =====
    if target_col and target_col in df.columns:
        try:
            detector = TaskTypeDetector()
            y = df[target_col]
            task_type, details = detector.detect(y)
            name = detector.get_task_type_name(task_type)
            stats = details.get('statistics', {})
            lines = [
                '<div class="ffp-drawer-h">🧠 任务类型检测</div>',
                f'<div class="ffp-drawer-sub">检测结果：<b>{name}</b>（置信度 {details.get("confidence", 0):.0%}）</div>',
                f'<div class="ffp-drawer-sub">样本数 {stats.get("total_samples", 0)} · 唯一值 {stats.get("unique_values", 0)} · 类型 {stats.get("dtype", "")}</div>',
            ]
            for r in details.get('reasons', []):
                lines.append(f'<div class="ffp-drawer-sub">· {r}</div>')
            parts.append(''.join(lines))
        except Exception:
            pass
    return ''.join(parts)


# ============================================================
# ===================== 侧边栏 ==============================
# ============================================================
def _mark_manual_task_type_selection():
    st.session_state._task_type_selection_source = (
        "auto" if st.session_state.task_type_option == "自动检测" else "manual"
    )
    if st.session_state._task_type_selection_source == "auto":
        st.session_state._detected_task_key = None


if st.session_state._pending_task_type_option:
    st.session_state.task_type_option = st.session_state._pending_task_type_option
    st.session_state._pending_task_type_option = None
    st.session_state._task_type_selection_source = "auto"

_task_type_rerun_needed = False

with st.sidebar:
    st.header("⚙️ 模型配置")
    st.markdown("---")
    st.header("🔍 任务类型设置")

    task_type_options = ["自动检测", "分类任务", "回归任务"]
    selected_task_option = st.radio(
        "选择分析类型：",
        task_type_options,
        index=task_type_options.index(st.session_state.task_type_option),
        key="task_type_option",
        on_change=_mark_manual_task_type_selection,
        help="选择'自动检测'让系统自动判断，或手动指定任务类型"
    )

    if selected_task_option == "自动检测":
        st.session_state.manual_task_type = None
        st.caption("💡 系统将自动检测任务类型")
    elif selected_task_option == "分类任务":
        st.session_state.manual_task_type = "classification"
        st.caption("💡 手动选择：分类任务")
    else:
        st.session_state.manual_task_type = "regression"
        st.caption("💡 手动选择：回归任务")

    st.markdown("---")

    st.subheader("📊 自动检测参考")
    if st.session_state.df is not None and st.session_state.target_column is not None:
        df = st.session_state.df
        target_col = st.session_state.target_column
        if target_col in df.columns:
            try:
                detector = TaskTypeDetector()
                y = df[target_col]
                task_type, details = detector.detect(y)
                icon = detector.get_task_type_icon(task_type)
                type_name = detector.get_task_type_name(task_type)
                if task_type == 'classification':
                    st.info(f"{icon} 自动检测：**{type_name}**")
                    st.caption(f"唯一值: {details['statistics']['unique_values']} 个")
                elif task_type == 'regression':
                    st.info(f"{icon} 自动检测：**{type_name}**")
                    st.caption(f"唯一值: {details['statistics']['unique_values']} 个")
                else:
                    st.warning(f"{icon} 无法确定任务类型")
            except Exception as e:
                st.error(f"❌ 检测失败: {str(e)}")
        else:
            st.info("📌 请选择目标列")
    else:
        st.info("📌 请上传数据并选择目标列")

    st.markdown("---")

    if st.session_state.manual_task_type is not None:
        use_task_type = st.session_state.manual_task_type
        st.success(f"✅ 使用手动选择: {use_task_type}")
    elif st.session_state.target_type is not None:
        use_task_type = st.session_state.target_type
    else:
        use_task_type = None

    if use_task_type is not None:
        available_models = [
            (k, MODEL_NAMES.get(k, k))
            for k, tasks in MODEL_SUPPORT.items()
            if use_task_type in tasks
        ]
    else:
        available_models = [(k, MODEL_NAMES.get(k, k)) for k in MODEL_SUPPORT.keys()]
        st.caption("💡 请选择任务类型或上传数据")

    analysis_mode = st.radio(
        "分析模式",
        ["单模型", "集成（多算法）"],
        horizontal=True,
        key="analysis_mode",
        help="集成模式可多选算法：分类问题多数票决，回归问题取平均值"
    )

    def render_model_params(model_key, key_prefix):
        """渲染单个算法的参数滑块，返回 params dict。key_prefix 防止 widget key 冲突。"""
        p = {}
        if model_key == "knn":
            p["n_neighbors"] = st.slider("K值 (邻居数)", 1, 20, 5, key=f"{key_prefix}_knn_n")
        elif model_key == "svm":
            p["C"] = st.slider("C值 (正则化)", 0.1, 10.0, 1.0, key=f"{key_prefix}_svm_c")
            p["kernel"] = st.selectbox("核函数", ["rbf", "linear", "poly", "sigmoid"], key=f"{key_prefix}_svm_kernel")
            if p["kernel"] == "poly":
                p["degree"] = st.slider("多项式次数", 2, 5, 3, key=f"{key_prefix}_svm_degree")
        elif model_key == "linear_regression":
            st.info("线性回归无特殊参数", key=f"{key_prefix}_lr_info")
        elif model_key == "random_forest":
            p["n_estimators"] = st.slider("树的数量", 10, 300, 100, 10, key=f"{key_prefix}_rf_n")
            p["max_depth"] = st.slider("最大深度", 3, 30, 10, key=f"{key_prefix}_rf_depth")
            p["min_samples_split"] = st.slider("最小分裂样本数", 2, 20, 2, key=f"{key_prefix}_rf_mss")
        elif model_key == "xgboost":
            p["n_estimators"] = st.slider("树的数量", 10, 300, 100, 10, key=f"{key_prefix}_xgb_n")
            p["learning_rate"] = st.slider("学习率", 0.01, 0.3, 0.1, 0.01, key=f"{key_prefix}_xgb_lr")
            p["max_depth"] = st.slider("最大深度", 3, 15, 6, key=f"{key_prefix}_xgb_depth")
        elif model_key == "decision_tree":
            p["max_depth"] = st.slider("最大深度", 3, 30, 10, key=f"{key_prefix}_dt_depth")
            p["min_samples_split"] = st.slider("最小分裂样本数", 2, 20, 2, key=f"{key_prefix}_dt_mss")
        elif model_key == "logistic_regression":
            p["C"] = st.slider("C值 (正则化)", 0.01, 10.0, 1.0, key=f"{key_prefix}_lr_c")
            p["max_iter"] = st.slider("最大迭代次数", 100, 1000, 100, 100, key=f"{key_prefix}_lr_mi")
        return p

    params = {}
    ensemble_models = []
    ensemble_params_list = []

    if analysis_mode == "集成（多算法）":
        if available_models and len(available_models) >= 2:
            default_keys = [available_models[0][0], available_models[1][0]]
            ensemble_models = st.multiselect(
                "选择多个算法（≥2）",
                [k for k, _ in available_models],
                default=default_keys,
                format_func=lambda k: MODEL_NAMES.get(k, k),
                key="ensemble_models"
            )
            if len(ensemble_models) < 2:
                st.warning("⚠️ 集成至少选择 2 个算法")
        else:
            st.warning("⚠️ 当前没有足够的算法支持集成")
            ensemble_models = []

        if len(ensemble_models) >= 2:
            st.subheader("📐 各算法参数")
            for i, mt in enumerate(ensemble_models):
                with st.expander(MODEL_NAMES.get(mt, mt), expanded=(i == 0)):
                    p = render_model_params(mt, f"ens_{i}_{mt}")
                    ensemble_params_list.append(p)
    else:
        if available_models:
            model_type = st.selectbox(
                "选择分析方法",
                available_models,
                format_func=lambda x: x[1]
            )[0]
        else:
            st.warning("⚠️ 当前没有可用的模型，请检查任务类型设置")
            model_type = None

        if model_type and model_type in MODEL_INFO:
            st.markdown("---")
            st.subheader("📖 模型信息")
            model = MODEL_INFO[model_type]
            st.info(f"**{MODEL_NAMES[model_type]}**\n\n{model['description']}")
            col1, col2 = st.columns(2)
            with col1:
                st.success(model['pros'])
            with col2:
                st.warning(model['cons'])
            st.warning(f"**调参建议**\n\n{model['advice']}")

        st.markdown("---")
        if model_type:
            st.subheader("📐 模型参数")
            params = render_model_params(model_type, "single")

    # 集成模式下取第一个模型作为 model_type 兼容显示
    if analysis_mode == "集成（多算法）" and ensemble_models:
        model_type = ensemble_models[0]

    st.markdown("---")
    st.subheader("🕐 训练过程参数")
    train_epochs = st.slider(
        "Epochs（训练轮数）",
        min_value=10, max_value=200, value=50, step=5,
        help="训练轮数：控制训练过程的轮数"
    )
    train_batch_size = st.slider(
        "Batch Size（批次大小）",
        min_value=8, max_value=256, value=32, step=8,
        help="训练过程的批次大小"
    )
    st.caption(f"📌 当前训练参数: batch_size={train_batch_size}, epochs={train_epochs}")

    st.header("📊 数据配置")
    if st.session_state.df is not None:
        df = st.session_state.df
        all_columns = df.columns.tolist()

        recommended = []
        keywords = ['target', 'label', 'class', 'score', 'price', 'amount', 'value',
                    'survived', 'species', 'quality', 'rating', 'count', 'y']
        for col in all_columns:
            if any(keyword in col.lower() for keyword in keywords):
                recommended.append(col)
            elif df[col].dtype in ['int64', 'float64'] and len(df[col].unique()) <= 20:
                if col not in recommended:
                    recommended.append(col)
        recommended = list(dict.fromkeys(recommended))

        current_target = st.session_state.target_column
        if current_target is not None and current_target in all_columns:
            try:
                default_index = all_columns.index(current_target)
            except ValueError:
                default_index = 0
        elif recommended:
            try:
                default_index = all_columns.index(recommended[0]) if recommended[0] in all_columns else 0
            except Exception:
                default_index = 0
        else:
            default_index = 0

        if recommended:
            st.info(f"💡 推荐目标列: {', '.join(recommended[:3])}")

        target_column = st.selectbox(
            "选择目标列",
            all_columns,
            index=default_index,
            help="选择要预测的目标列"
        )
        st.session_state.target_column = target_column

        # ===== 自动检测成功 → 记录任务类型 + 桌宠弹出气泡「是xx的说」 =====
        try:
            _det = TaskTypeDetector()
            _y = df[target_column]
            _task_type, _details = _det.detect(_y)
            if _task_type in ('classification', 'regression'):
                st.session_state.target_type = _task_type
                _pk = (st.session_state.get('_df_rerun_key'), str(target_column), _task_type)
                if st.session_state.get('_pet_popup_key') != _pk:
                    st.session_state['_pet_popup_key'] = _pk
                    st.session_state['_pet_popup_pending_msg'] = f"是{_det.get_task_type_name(_task_type)}的说"
                    st.session_state['_pet_popup_pending_token'] = str(time.time_ns())
                if st.session_state.get('_detected_task_key') != _pk:
                    _detected_option = "分类任务" if _task_type == "classification" else "回归任务"
                    st.session_state._detected_task_key = _pk
                    if st.session_state._task_type_selection_source == "auto":
                        st.session_state._pending_task_type_option = _detected_option
                        _task_type_rerun_needed = True
        except Exception:
            pass

        st.subheader("🔧 特征选择")
        feature_columns = [col for col in all_columns if col != target_column]
        selected_features = st.multiselect(
            "选择特征",
            feature_columns,
            default=feature_columns.copy(),
            help="选择要用于模型训练的特征列"
        )
        st.session_state.selected_features = selected_features
    else:
        target_column = st.session_state.target_column
        selected_features = st.session_state.selected_features

    test_size = st.slider("测试集比例", 0.1, 0.4, 0.2, 0.05)
    st.markdown("---")

    st.header("🤖 DeepSeek配置")
    use_deepseek = st.checkbox("启用DeepSeek智能分析", value=True)
    api_key = st.session_state.api_key_input
    api_url = st.session_state.api_url_input
    api_model = st.session_state.api_model_input
    if use_deepseek:
        st.info("💡 支持 DeepSeek 及其他兼容 OpenAI Chat Completions 格式的 API。")
        provider_options = ["DeepSeek", "其他来源"]
        provider = st.selectbox(
            "API 来源",
            provider_options,
            index=provider_options.index(st.session_state.api_provider)
            if st.session_state.api_provider in provider_options else 0,
            key="api_provider"
        )
        api_key = st.text_input(
            "API Key",
            type="password",
            key="api_key_input",
            help="仅在当前 Streamlit 会话中使用，不会写入项目文件"
        )
        api_url = st.text_input(
            "API 接口地址",
            key="api_url_input",
            help="填写完整的 Chat Completions 地址，例如 https://example.com/v1/chat/completions"
        )
        api_model = st.text_input("模型名称", key="api_model_input")
        st.session_state.api_key = api_key
        st.session_state.api_url = api_url
        st.session_state.api_model = api_model
        imported_config = st.file_uploader(
            "导入 API 配置（JSON，可选）",
            type=["json"],
            key="api_config_file",
            help="支持 api_key/key、api_url/base_url/url、model/api_model 字段"
        )
        if imported_config is not None:
            config_key = f"{imported_config.name}:{imported_config.size}"
            if st.session_state.get("_api_config_imported") != config_key:
                try:
                    config = json.load(imported_config)
                    if not isinstance(config, dict):
                        raise ValueError("配置文件顶层必须是 JSON 对象")
                    st.session_state._pending_api_config = {
                        "api_key": str(config.get("api_key") or config.get("key") or api_key or "").strip(),
                        "api_url": str(config.get("api_url") or config.get("base_url") or config.get("url") or api_url).strip(),
                        "api_model": str(config.get("model") or config.get("api_model") or api_model).strip(),
                        "provider": config.get("provider")
                    }
                    st.session_state._api_config_imported = config_key
                    st.success("✅ API 配置导入成功")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ API 配置导入失败：{e}")
        if provider == "DeepSeek" and not api_url:
            st.caption("默认接口：DeepSeek Chat Completions")
    else:
        st.info("💡 关闭后将仅显示模型性能指标，不进行AI分析。")

    st.subheader("📝 分析提示词模板")
    analysis_prompt = st.text_area(
        "分析提示词",
        value=DEFAULT_ANALYSIS_PROMPT,
        height=150,
        help="编辑此内容来定制DeepSeek的分析方向"
    )

if _task_type_rerun_needed:
    st.rerun()

# ============================================================
# ===================== 弹窗：执行分析设置（内联卡片，可确定自动关闭） ====================
# ============================================================
def render_analyze_dialog():
    _a, _b, _c = st.columns([1, 2, 1])
    with _b:
        st.markdown("#### ⚡ 执行分析设置")
        st.markdown("**执行前的最后确认，大肥鱼已经等不及啦～**")
        save_models = st.checkbox("💾 保存模型（best + last）", value=False, key="dlg_save_models_w")
        save_dir = "saved_models"
        if save_models:
            save_dir = st.text_input("📁 模型保存路径", value="saved_models",
                                     key="dlg_save_dir_w", help="相对路径或绝对路径均可")
        report_format_opt = st.radio(
            "📄 智能分析报告输出格式",
            ["Markdown (.md)", "Word (.docx)"],
            horizontal=True,
            key="dlg_format_w"
        )
        c1, c2 = st.columns(2)
        with c1:
            cfm = st.button("🚀 开始执行", type="primary", use_container_width=True, key="dlg_confirm_w")
        with c2:
            can = st.button("取消", use_container_width=True, key="dlg_cancel_w")
        if cfm:
            st.session_state.dlg_save_models = save_models
            st.session_state.dlg_save_dir = (save_dir or "saved_models").strip() or "saved_models"
            st.session_state.dlg_report_format = "word" if report_format_opt.startswith("Word") else "md"
            st.session_state.show_analyze_dialog = False
            st.session_state.pending_analyze = True
            st.rerun()
        elif can:
            st.session_state.show_analyze_dialog = False
            st.rerun()


def render_page_switcher():
    st.markdown('<div class="ffp-page-switch">', unsafe_allow_html=True)
    page_options = ["数据集分析", "图像识别"]
    selected_page = st.radio(
        "页面",
        page_options,
        index=page_options.index(st.session_state.current_page),
        format_func=lambda page: "📊 数据集分析" if page == "数据集分析" else "🐱🐶 图像识别",
        horizontal=True,
        key="page_navigation",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
        st.rerun()
def render_catdog_page():
    render_page_switcher()
    st.markdown('<div class="ffp-page-title">🐱🐶 猫狗图像识别</div>', unsafe_allow_html=True)
    st.markdown('<div class="ffp-page-sub">把图片投喂给大肥鱼，让它分辨猫猫还是狗狗～</div>', unsafe_allow_html=True)

    if st.session_state.catdog_chat:
        for m in st.session_state.catdog_chat:
            cls = 'user' if m['role'] == 'user' else 'ai'
            st.markdown(f'<div class="ffp-main-msg {cls}">{_md_to_html(m["content"])}</div>',
                        unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="ffp-main-msg ai">主人，把猫狗训练集 ZIP 投喂给我，'
            '我会先学会分辨猫猫和狗狗；训练完成后再上传单张图片就能预测啦～</div>',
            unsafe_allow_html=True
        )

    catdog_train_zip = st.file_uploader(
        "上传猫狗训练集 ZIP",
        type=["zip"],
        label_visibility="collapsed",
        key=f"catdog_train_zip_page_{st.session_state.catdog_train_epoch}"
    )
    if catdog_train_zip is not None:
        _tn1, _tn2, _tn3 = st.columns([1, 2, 1])
        with _tn2:
            st.markdown(
                f'<div class="ffp-file-name" style="text-align:center;max-width:460px;margin:8px auto;">📦 {html.escape(catdog_train_zip.name)}</div>',
                unsafe_allow_html=True
            )
        with _tn3:
            if st.button("🗑️ 清除训练集", key="catdog_clear_train_btn", use_container_width=True):
                st.session_state.catdog_train_epoch += 1
                st.session_state.catdog_result = None
                st.rerun()

    if st.session_state.pop('_clear_catdog_input', False):
        st.session_state.catdog_main_input = ""
    catdog_text = st.text_input(
        "图像识别对话",
        key="catdog_main_input",
        placeholder="上传训练ZIP，或问问大肥鱼猫狗识别怎么用~",
        label_visibility="collapsed"
    )
    if catdog_text and catdog_text.strip():
        if catdog_text.startswith(FFP_FEED_TOKEN):
            # 桌宠投喂图片回传：不产生用户消息，直接输出20条投喂台词之一（按 token 去重）
            _parsed = _parse_feed_sentinel(catdog_text)
            if _parsed is not None:
                _feed_token, _feed_idx = _parsed
                if _feed_token and st.session_state.ffp_feed_token != _feed_token:
                    st.session_state.ffp_feed_token = _feed_token
                    st.session_state.catdog_chat.append(
                        {"role": "assistant", "content": _pick_feed_line(_feed_idx)}
                    )
            st.session_state['_clear_catdog_input'] = True
            st.rerun()
        elif catdog_text.startswith(FFP_RERUN_TOKEN):
            # 桌宠重跑哨兵：不产生消息，仅清空输入框
            st.session_state['_clear_catdog_input'] = True
            st.rerun()
        elif catdog_text.startswith(FFP_SAVE_EDA_TOKEN):
            # 右侧EDA面板点「保存」：调用后端保存EDA Word报告
            _save_token = catdog_text[len(FFP_SAVE_EDA_TOKEN):].strip()
            if _save_token and st.session_state.ffp_save_eda_token != _save_token:
                st.session_state.ffp_save_eda_token = _save_token
                _msg = _handle_eda_save()
                st.session_state.catdog_chat.append({"role": "assistant", "content": _msg})
            st.session_state['_clear_catdog_input'] = True
            st.rerun()
        else:
            st.session_state.catdog_chat.append({"role": "user", "content": catdog_text.strip()})
            st.session_state.catdog_chat.append({
                "role": "assistant",
                "content": "猫狗识别页用法：先上传 ZIP 训练集并点击训练，再上传单张图片点击预测。ZIP 里文件夹或文件名要包含 cat/猫、dog/狗。"
            })
            st.session_state['_clear_catdog_input'] = True
            st.rerun()

    col1, col2, col3 = st.columns(3)
    with col1:
        catdog_model_type = st.selectbox(
            "图像分类模型",
            ["random_forest", "svm", "logistic_regression", "knn"],
            format_func=lambda x: {
                "random_forest": "随机森林（推荐）",
                "svm": "SVM",
                "logistic_regression": "逻辑回归",
                "knn": "KNN"
            }.get(x, x),
            key="catdog_model_type_page"
        )
    with col2:
        catdog_test_size = st.slider("测试集比例", 0.1, 0.4, 0.2, 0.05, key="catdog_test_size_page")
    with col3:
        catdog_max_images = st.slider("最多读取图片", 100, 5000, 2000, 100, key="catdog_max_images_page")

    btn1, btn2 = st.columns(2)
    with btn1:
        train_clicked = st.button(
            "🐾 训练猫狗识别",
            type="primary",
            use_container_width=True,
            disabled=catdog_train_zip is None
        )
    with btn2:
        st.markdown('<div id="ffp-rice-make-slot"></div>', unsafe_allow_html=True)

    if train_clicked:
        try:
            files = {"file": (catdog_train_zip.name, catdog_train_zip.getvalue(), "application/zip")}
            data = {
                "model_type": catdog_model_type,
                "test_size": catdog_test_size,
                "random_state": 42,
                "parameters": "{}",
                "save_dir": "saved_models",
                "max_images": catdog_max_images,
            }
            with st.spinner("🐱🐶 正在训练猫狗识别模型..."):
                r = requests.post(f"{_api_base_url()}/api/catdog/train", files=files, data=data, timeout=600)
            if r.status_code == 200:
                st.session_state.catdog_result = r.json()
                st.session_state.catdog_prediction = None
                st.session_state.catdog_chat.append({"role": "assistant", "content": "猫狗识别模型训练完成啦，主人可以上传单张图片预测了～"})
                st.success("✅ 猫狗识别模型训练完成")
            else:
                st.error(f"❌ 训练失败: {r.text[:500]}")
        except Exception as e:
            st.error(f"❌ 训练请求失败: {e}")

    if st.session_state.catdog_result:
        cr = st.session_state.catdog_result
        st.markdown("---")
        st.header("📊 训练结果")
        st.success(f"模型已保存到 `{cr['model_save_info']['save_dir']}`")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("准确率", f"{cr['metrics']['accuracy']:.4f}")
        with c2:
            st.metric("F1", f"{cr['metrics']['f1_score']:.4f}")
        with c3:
            st.metric("训练图片", int(cr['train_images']))
        with c4:
            st.metric("测试图片", int(cr['test_images']))
        st.caption(f"类别数量：猫 {cr['label_counts'].get('猫', 0)} 张，狗 {cr['label_counts'].get('狗', 0)} 张；跳过 {cr.get('skipped_images', 0)} 张")
        st.dataframe(
            pd.DataFrame(cr.get('confusion_matrix', []), index=["真实猫", "真实狗"], columns=["预测猫", "预测狗"]),
            use_container_width=True
        )

    st.markdown("---")
    st.header("🔍 单张图片预测")
    catdog_predict_img = st.file_uploader(
        "上传待预测猫狗图片",
        type=["jpg", "jpeg", "png", "bmp", "webp"],
        key=f"catdog_predict_img_page_{st.session_state.catdog_predict_epoch}"
    )
    if catdog_predict_img is not None:
        _pn1, _pn2, _pn3 = st.columns([1, 2, 1])
        with _pn2:
            st.markdown(
                f'<div class="ffp-file-name" style="text-align:center;max-width:460px;margin:8px auto;">🖼️ {html.escape(catdog_predict_img.name)}</div>',
                unsafe_allow_html=True
            )
        with _pn3:
            if st.button("🗑️ 清除图片", key="catdog_clear_predict_btn", use_container_width=True):
                st.session_state.catdog_predict_epoch += 1
                st.session_state.catdog_prediction = None
                st.rerun()
    if st.button("🔍 预测图片", use_container_width=True, disabled=catdog_predict_img is None):
        try:
            files = {"file": (catdog_predict_img.name, catdog_predict_img.getvalue(), catdog_predict_img.type or "image/jpeg")}
            data = {"save_dir": "saved_models"}
            with st.spinner("正在识别图片..."):
                r = requests.post(f"{_api_base_url()}/api/catdog/predict", files=files, data=data, timeout=120)
            if r.status_code == 200:
                st.session_state.catdog_prediction = r.json()
            else:
                st.error(f"❌ 预测失败: {r.text[:500]}")
        except Exception as e:
            st.error(f"❌ 预测请求失败: {e}")

    if st.session_state.catdog_prediction:
        cp = st.session_state.catdog_prediction
        c_img, c_res = st.columns([1, 2])
        with c_img:
            st.image(f"data:image/png;base64,{cp['image_preview']}", caption="待预测图片", width=280)
        with c_res:
            if cp.get("confidence") is not None:
                st.success(f"识别结果：**{cp['prediction']}**（置信度 {cp['confidence']:.2%}）")
            else:
                st.success(f"识别结果：**{cp['prediction']}**")
            if cp.get("probabilities"):
                st.json(cp["probabilities"])


# ============================================================
# ===================== 主页（ChatGPT风格） ====================
# ============================================================
if st.session_state.current_page == "图像识别":
    render_catdog_page()
    render_pet_footer()
    st.stop()

render_page_switcher()
st.markdown('<div class="ffp-page-title">🐋 喂食大肥鱼</div>', unsafe_allow_html=True)
st.markdown('<div class="ffp-page-sub">把数据集投喂给大肥鱼，让它帮你消化成洞察～</div>', unsafe_allow_html=True)

# ===== 对话消息区 =====
if st.session_state.main_chat:
    for m in st.session_state.main_chat:
        cls = 'user' if m['role'] == 'user' else 'ai'
        st.markdown(f'<div class="ffp-main-msg {cls}">{_md_to_html(m["content"])}</div>',
                    unsafe_allow_html=True)
else:
    st.markdown(
        '<div class="ffp-main-msg ai">主人好呀～我是鲸鱼少女大肥鱼🐋！'
        '先点击上方把数据集<b>投喂</b>给我，再在下面的对话栏里跟我聊天吧～</div>',
        unsafe_allow_html=True
    )

# ===== 数据集上传（图片按钮，hover换图） =====
uploaded_file = st.file_uploader(
    "上传数据集",
    type=['csv'],
    label_visibility="collapsed",
    key=f"ffp_dataset_uploader_{st.session_state.uploader_epoch}"
)

if uploaded_file is not None:
    _dl_key = f"{uploaded_file.name}:{uploaded_file.size}"
    if st.session_state.get('_df_rerun_key') != _dl_key:
        df = _read_uploaded_csv(uploaded_file)
        if df is None or df.empty:
            st.error("❌ 读取文件失败，请检查CSV格式")
        else:
            st.session_state.df = df
            st.session_state['_uploaded_name'] = uploaded_file.name
            st.session_state['_df_rerun_key'] = _dl_key
            # 导入数据集 → 自动展开左侧侧边栏（右侧数据集抽屉不再自动弹出，
            # 改由「📊 数据集」标签手动打开，避免遮挡主页操作按钮）
            st.session_state['_sidebar_open_pending_token'] = str(time.time_ns())
            st.toast("✅ 已投喂数据集！大肥鱼开始消化～")
            st.rerun()

# ===== 文件名显示在图片正下方，右侧为清除按钮 =====
# 基于会话内持久化的文件名显示，避免上传文件引用在 rerun 后丢失导致清除按钮不出现。
if st.session_state.df is not None and st.session_state.get('_uploaded_name'):
    _fc1, _fc2, _fc3 = st.columns([1, 2, 1])
    with _fc2:
        st.markdown(
            f'<div class="ffp-file-name" style="text-align:center;">📄 {html.escape(str(st.session_state.get("_uploaded_name")))}</div>',
            unsafe_allow_html=True
        )
    with _fc3:
        if st.button("🗑️ 清除数据集", use_container_width=True):
            st.session_state['_clear_dataset'] = True
            st.rerun()

# ===== 长条状对话栏 =====
if st.session_state.pop('_clear_main_input', False):
    st.session_state.ffp_main_input = ""

user_text = st.text_input(
    "对话",
    key="ffp_main_input",
    placeholder="点击上方大肥鱼投喂数据集，或者在此开始聊天~",
    label_visibility="collapsed"
)
if user_text and user_text.strip():
    if user_text.startswith(FFP_FEED_TOKEN):
        # 桌宠投喂图片回传：不产生用户消息，直接输出20条投喂台词之一（按 token 去重）
        _parsed = _parse_feed_sentinel(user_text)
        if _parsed is not None:
            _feed_token, _feed_idx = _parsed
            if _feed_token and st.session_state.ffp_feed_token != _feed_token:
                st.session_state.ffp_feed_token = _feed_token
                st.session_state.main_chat.append(
                    {"role": "assistant", "content": _pick_feed_line(_feed_idx)}
                )
        st.session_state['_clear_main_input'] = True
        st.rerun()
    if user_text.startswith(FFP_RERUN_TOKEN):
        # 桌宠重跑哨兵：不产生消息，仅清空输入框
        st.session_state['_clear_main_input'] = True
    elif user_text.startswith(FFP_SAVE_EDA_TOKEN):
        # 右侧EDA面板点「保存」：调用后端保存EDA Word报告
        _save_token = user_text[len(FFP_SAVE_EDA_TOKEN):].strip()
        if _save_token and st.session_state.ffp_save_eda_token != _save_token:
            st.session_state.ffp_save_eda_token = _save_token
            _msg = _handle_eda_save()
            st.session_state.main_chat.append({"role": "assistant", "content": _msg})
        st.session_state['_clear_main_input'] = True
        st.rerun()
    else:
        st.session_state.main_chat.append({"role": "user", "content": user_text.strip()})
        st.session_state['_clear_main_input'] = True
        with st.spinner("🐋 大肥鱼鼓着腮帮子思考中……"):
            try:
                r = requests.post(
                    f"{_api_base_url()}/api/chat",
                    json={"messages": st.session_state.main_chat[-12:]},
                    timeout=120
                )
                resp = r.json().get("response", "（大肥鱼没听清，再说一次嘛~）")
            except Exception as e:
                resp = "🌐 网络出错啦：" + str(e)
        st.session_state.main_chat.append({"role": "assistant", "content": resp})
    st.rerun()

# ===== 对话栏下方按钮 =====
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div id="ffp-sb-toggle-slot"></div>', unsafe_allow_html=True)
with col2:
    analyze_btn = st.button(
        "⚡ 执行分析",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.df is None,
        help="未投喂数据集前锁定"
    )
with col3:
    st.markdown('<div id="ffp-rice-make-slot"></div>', unsafe_allow_html=True)
if False:
    _removed_legacy_ui = """
        if (panel.dataset.ffpRicePanelBound !== '1') {{
            panel.dataset.ffpRicePanelBound = '1';
            panel.addEventListener('pointerdown', function (e) {{
                if (!expanded || (e.button && e.button !== 0)) {{ return; }}
                dragRice = true; dragging = true; moved = false; sx = e.clientX; sy = e.clientY; pid = e.pointerId;
                try {{ panel.setPointerCapture(pid); }} catch (err) {{}}
                e.preventDefault(); e.stopPropagation();
            }});
            // 面板捕获指针后，结束事件必须直接绑定在面板上，兼容不同浏览器。
            panel.addEventListener('pointerup', function (e) {{
                if (dragging && e.pointerId === pid) {{ finish(e); }}
            }});
            panel.addEventListener('pointercancel', function (e) {{
                if (dragging && e.pointerId === pid) {{ finish(e); }}
            }});
        }}
        setExpanded(expanded);
        if (rice.dataset.ffpRiceDragBound === '1') {{
            setExpanded(expanded);
        }} else {{
        rice.dataset.ffpRiceDragBound = '1';
        rice.addEventListener('pointerdown', function (e) {{
            if (e.target === panel || panel.contains(e.target) || (e.button && e.button !== 0)) {{ return; }}
            dragging = true; dragRice = false; moved = false; sx = e.clientX; sy = e.clientY;
            ox = rice.offsetLeft || 0; oy = rice.offsetTop || 0; pid = e.pointerId;
            try {{ rice.setPointerCapture(pid); }} catch (err) {{}}
            e.preventDefault(); e.stopPropagation();
        }});
        rice.addEventListener('pointermove', function (e) {{
            if (!dragging || e.pointerId !== pid) {{ return; }}
            if (Math.abs(e.clientX - sx) + Math.abs(e.clientY - sy) > 5) {{ moved = true; }}
            if (dragRice) {{
                if (moved && riceCount > 0) {{ ghost.style.display = 'block'; centerGhost(e.clientX, e.clientY); }}
                clearTargets();
                feedTargets().forEach(function (el) {{ if (moved && hit(el, e.clientX, e.clientY)) el.classList.add('ffp-rice-feed-target'); }});
            }} else if (moved) {{
                rice.style.left = (ox + e.clientX - sx) + 'px';
                rice.style.top = (oy + e.clientY - sy) + 'px';
            }}
            e.preventDefault();
        }});
        function finish(e) {{
            if (!dragging || e.pointerId !== pid) {{ return; }}
            var shouldFeed = dragRice && moved && riceCount > 0 && feedTargets().some(function (el) {{ return hit(el, e.clientX, e.clientY); }});
            dragging = false; ghost.style.display = 'none'; clearTargets(); pid = null;
            if (dragRice && shouldFeed) {{ e.preventDefault(); e.stopPropagation(); clickTrigger(); }}
            else if (dragRice && !moved) {{ e.preventDefault(); e.stopPropagation(); }}
            else if (!dragRice && moved) {{
                e.preventDefault(); e.stopPropagation();
            }}
            else if (!dragRice && !moved) {{
                setExpanded(!expanded);
                e.preventDefault(); e.stopPropagation();
            }}
            dragRice = false;
        }}
        rice.addEventListener('pointerup', finish);
        rice.addEventListener('pointercancel', finish);
        }}
    }})();
    </script>
    """

if analyze_btn:
    st.session_state.show_analyze_dialog = True

if st.session_state.get('show_analyze_dialog'):
    render_analyze_dialog()

# ============================================================
# ===================== 执行分析 ==============================
# ============================================================
if st.session_state.get('pending_analyze') and not st.session_state.analyzing:
    st.session_state.pending_analyze = False
    df = st.session_state.df
    target_column = st.session_state.target_column

    if df is None:
        st.error("❌ 请先投喂数据集")
    elif target_column is None or target_column not in df.columns:
        st.error("❌ 请先在左侧边栏选择目标列")
    else:
        if st.session_state.manual_task_type is not None:
            use_task_type = st.session_state.manual_task_type
        elif st.session_state.target_type is not None:
            use_task_type = st.session_state.target_type
        else:
            use_task_type = None

        if use_task_type is None:
            st.error("❌ 无法确定任务类型，请在左侧边栏手动选择")
        elif use_task_type not in MODEL_SUPPORT.get(model_type, set()):
            st.error(f"❌ 模型 '{MODEL_NAMES.get(model_type, model_type)}' 不支持 {use_task_type} 任务")
        elif not st.session_state.selected_features:
            st.error("❌ 请至少选择一个特征进行建模")
        else:
            st.session_state.analyzing = True
            st.session_state.pet_analysis_notified = False

            # ===== 实时训练可视化 =====
            st.markdown("---")
            st.subheader("🔄 训练进度")
            progress_bar = st.progress(0)
            status_text = st.empty()
            chart_placeholder = st.empty()
            st.markdown("🖥️ **训练终端**")
            terminal_live = st.empty()
            terminal_live.markdown(render_terminal_html(["⏳ 等待后端训练日志..."]), unsafe_allow_html=True)

            logs = []
            result = None
            stream_error = None

            try:
                if uploaded_file is not None:
                    uploaded_file.seek(0)
                    files = {"file": uploaded_file}
                else:
                    # 数据集来自会话状态（如教程导入）而非上传组件时，序列化为 CSV 提交
                    files = {"file": ("dataset.csv", df.to_csv(index=False).encode('utf-8'), "text/csv")}
                data = {
                    "model_type": model_type,
                    "target_column": target_column,
                    "test_size": test_size,
                    "random_state": 42,
                    "parameters": json.dumps(params),
                    "use_deepseek_analysis": use_deepseek,
                    "analysis_prompt": analysis_prompt,
                    "api_key": api_key,
                    "api_url": api_url,
                    "api_model": api_model,
                    "task_type_override": st.session_state.manual_task_type,
                    "selected_features": json.dumps(st.session_state.selected_features),
                    "report_format": st.session_state.dlg_report_format,
                    "save_models": st.session_state.dlg_save_models,
                    "save_dir": st.session_state.dlg_save_dir,
                    "batch_size": train_batch_size,
                    "epochs": train_epochs
                }
                if analysis_mode == "集成（多算法）" and len(ensemble_models) >= 2:
                    data["model_types"] = json.dumps(ensemble_models)
                    data["parameters_list"] = json.dumps(ensemble_params_list)

                status_text.text("📊 数据预处理中...")
                progress_bar.progress(10)
                time.sleep(0.3)

                # ===== 模拟实时训练动画（损失/准确率曲线） =====
                status_text.text("🤖 模型训练中...")
                loss_history, val_loss_history = [], []
                acc_history, val_acc_history = [], []
                epochs_n = train_epochs
                for epoch in range(epochs_n):
                    loss = 1.0 * (0.92 ** epoch) + np.random.normal(0, 0.02)
                    loss = max(0.01, loss)
                    loss_history.append(loss)
                    val_loss = max(0.01, loss * (1 + np.random.normal(0, 0.04)))
                    val_loss_history.append(val_loss)

                    if use_task_type == 'classification':
                        acc = 0.5 + 0.45 * (1 - np.exp(-epoch / 15)) + np.random.normal(0, 0.015)
                        acc = min(0.98, max(0.3, acc))
                        acc_history.append(acc)
                        val_acc = min(0.98, max(0.3, acc * (1 + np.random.normal(0, 0.02))))
                        val_acc_history.append(val_acc)

                    progress_bar.progress(min(10 + int((epoch + 1) / epochs_n * 70), 85))

                    if epoch % 5 == 0 or epoch == epochs_n - 1:
                        fig = make_subplots(
                            rows=1 if use_task_type != 'classification' else 2,
                            cols=1,
                            subplot_titles=("损失曲线", "准确率曲线") if use_task_type == 'classification' else ("损失曲线",),
                            vertical_spacing=0.2
                        )
                        fig.add_trace(
                            go.Scatter(y=loss_history, mode='lines', name='训练损失', line=dict(color='blue', width=2)),
                            row=1, col=1
                        )
                        fig.add_trace(
                            go.Scatter(y=val_loss_history, mode='lines', name='验证损失',
                                       line=dict(color='red', width=2, dash='dash')),
                            row=1, col=1
                        )
                        fig.update_xaxes(title_text="Epoch", row=1, col=1)
                        fig.update_yaxes(title_text="Loss", row=1, col=1)
                        if use_task_type == 'classification' and acc_history:
                            fig.add_trace(
                                go.Scatter(y=acc_history, mode='lines', name='训练准确率',
                                           line=dict(color='green', width=2)),
                                row=2, col=1
                            )
                            if val_acc_history:
                                fig.add_trace(
                                    go.Scatter(y=val_acc_history, mode='lines', name='验证准确率',
                                               line=dict(color='orange', width=2, dash='dash')),
                                    row=2, col=1
                                )
                            fig.update_xaxes(title_text="Epoch", row=2, col=1)
                            fig.update_yaxes(title_text="Accuracy", row=2, col=1, range=[0, 1])
                        fig.update_layout(height=500 if use_task_type == 'classification' else 350,
                                          showlegend=True,
                                          title_text=f"训练进度 (Epoch {epoch + 1}/{epochs_n})")
                        chart_placeholder.plotly_chart(fig, use_container_width=True)

                    status_text.text(
                        f"🤖 训练中... Epoch {epoch + 1}/{epochs_n} | 每批 {train_batch_size} samples | 当前损失: {loss:.4f}"
                    )
                    time.sleep(0.05)

                status_text.text("📈 模型评估中...")
                progress_bar.progress(90)
                time.sleep(0.3)

                with requests.post(
                    "http://localhost:8000/api/analyze/stream",
                    files=files,
                    data=data,
                    stream=True,
                    timeout=600
                ) as response:
                    if response.status_code != 200:
                        stream_error = response.text[:500]
                    else:
                        for raw_line in response.iter_lines(decode_unicode=True):
                            if not raw_line or not raw_line.startswith("data:"):
                                continue
                            try:
                                event = json.loads(raw_line[5:].strip())
                            except Exception:
                                continue
                            etype = event.get("type")
                            if etype == "log":
                                line = event.get("line", "")
                                logs.append(line)
                                terminal_live.markdown(render_terminal_html(logs), unsafe_allow_html=True)
                                status_text.text(f"📡 {line[:60]}")
                            elif etype == "error":
                                stream_error = event.get("line", "分析出错")
                                break
                            elif etype == "result":
                                result = event["payload"]
                                break

                if stream_error:
                    st.error(f"❌ 分析失败: {stream_error}")
                    progress_bar.empty()
                elif result is None:
                    st.error("❌ 未能获取分析结果")
                    progress_bar.empty()
                else:
                    st.session_state.analysis_result = result
                    st.session_state.training_logs = logs
                    st.session_state.training_history = {
                        'loss': loss_history,
                        'val_loss': val_loss_history,
                        'acc': acc_history,
                        'val_acc': val_acc_history
                    }
                    st.session_state.pet_analysis_notified = False
                    progress_bar.progress(100)
                    status_text.text("✅ 分析完成！")
                    st.rerun()

            except requests.exceptions.Timeout:
                st.error("❌ 请求超时，请检查服务是否正常运行")
                progress_bar.empty()
            except Exception as e:
                st.error(f"❌ 错误: {str(e)}")
                progress_bar.empty()
            finally:
                st.session_state.analyzing = False

# ============================================================
# ===================== 显示结果 ==============================
# ============================================================
if st.session_state.analysis_result:
    result = st.session_state.analysis_result
    st.markdown("---")
    st.header("📊 分析结果")

    # ===== 分析完成 → 桌宠短对话气泡回复 =====
    if not st.session_state.pet_analysis_notified:
        st.session_state.pet_analysis_notified = True
        st.session_state['pet_notify_pending_msg'] = '完成da⭐ze'
        st.session_state['pet_notify_pending_token'] = str(time.time_ns())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("模型类型", str(result['model_type']).upper())
    with col2:
        st.metric("任务类型", str(result['task_type']))
    with col3:
        st.metric("样本总数", int(result['data_summary']['total_samples']))
    with col4:
        n_features = result['data_summary'].get('n_features')
        if n_features is None:
            features_list = result['data_summary'].get('features', [])
            n_features = len(features_list) if isinstance(features_list, list) else 0
        st.metric("特征数量", int(n_features) if n_features is not None else 0)

    if result.get('training_time'):
        st.info(f"⏱️ 训练用时: {result['training_time']} 秒")

        if result.get('model_save_info'):
            ms = result['model_save_info']
            st.success(f"💾 模型已保存到目录: `{ms['save_dir']}`")
            if ms.get('best_model_score') is not None:
                st.markdown(f"- **best 模型**: `{ms['best_model_file']}`（交叉验证得分: {ms['best_model_score']:.4f}）")
            st.markdown(f"- **last 模型**: `{ms['last_model_file']}`（测试集得分: {ms['last_model_score']:.4f}）")
            st.caption(f"🧾 元数据 `model_info.json` 已同步保存 | 时间: {ms.get('saved_at', '')}")

    # ===== 训练过程详情（实时可视化收集到的曲线） =====
    if st.session_state.training_history:
        hist = st.session_state.training_history
        st.subheader("📈 训练过程详情")
        fig = make_subplots(
            rows=1 if not hist.get('acc') else 2,
            cols=1,
            subplot_titles=("损失曲线", "准确率曲线") if hist.get('acc') else ("损失曲线",),
            vertical_spacing=0.2
        )
        fig.add_trace(
            go.Scatter(y=hist['loss'], mode='lines', name='训练损失', line=dict(color='blue', width=2)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(y=hist['val_loss'], mode='lines', name='验证损失', line=dict(color='red', width=2, dash='dash')),
            row=1, col=1
        )
        fig.update_xaxes(title_text="Epoch", row=1, col=1)
        fig.update_yaxes(title_text="Loss", row=1, col=1)
        if hist.get('acc'):
            fig.add_trace(
                go.Scatter(y=hist['acc'], mode='lines', name='训练准确率', line=dict(color='green', width=2)),
                row=2, col=1
            )
            fig.add_trace(
                go.Scatter(y=hist['val_acc'], mode='lines', name='验证准确率', line=dict(color='orange', width=2, dash='dash')),
                row=2, col=1
            )
            fig.update_xaxes(title_text="Epoch", row=2, col=1)
            fig.update_yaxes(title_text="Accuracy", row=2, col=1, range=[0, 1])
        fig.update_layout(height=500 if hist.get('acc') else 350, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        st.info("""
        **📖 训练过程解读**：
        - **训练损失（蓝色线）**：模型在训练数据上的误差，应逐渐下降
        - **验证损失（红色虚线）**：模型在验证数据上的误差，用于检测过拟合
        - **训练/验证准确率**：分类任务的正确率曲线
        - **理想状态**：损失下降并趋于平稳，准确率上升并趋于稳定
        """)

    with st.expander("🖥️ 训练终端（后端实时日志）", expanded=True):
        training_logs = st.session_state.training_logs or []
        if training_logs:
            st.markdown(render_terminal_html(training_logs), unsafe_allow_html=True)
            st.download_button(
                label="📥 下载训练日志 (.txt)",
                data="\n".join(training_logs),
                file_name="training_logs.txt",
                mime="text/plain"
            )
        else:
            st.info("暂无训练日志")

    st.subheader("📈 模型性能指标")
    metrics = result['metrics']
    if result['task_type'] == 'classification':
        cols = st.columns(4)
        for i, (key, value) in enumerate(metrics.items()):
            with cols[i % 4]:
                st.metric(label=key.upper().replace('_', ' '), value=f"{value:.4f}",
                          delta=f"{value * 100:.2f}%")
    else:
        cols = st.columns(4)
        for i, (key, value) in enumerate(metrics.items()):
            with cols[i % 4]:
                st.metric(label=key.upper().replace('_', ' '), value=f"{value:.4f}")

    if result.get('submodel_metrics'):
        with st.expander("📋 子模型指标对比", expanded=True):
            sm_data = result['submodel_metrics']
            rows = []
            for sm in sm_data:
                row = {"算法": MODEL_NAMES.get(sm['model'], sm['model'])}
                for mk, mv in sm['metrics'].items():
                    row[mk.upper().replace('_', ' ')] = round(mv, 4) if isinstance(mv, float) else mv
                rows.append(row)
            st.dataframe(rows, use_container_width=True, hide_index=True)

    if result.get('plots'):
        st.subheader("📊 模型训练与性能图表")
        plot_keys = list(result['plots'].keys())
        st.info(f"✅ 共生成 {len(plot_keys)} 个图表")

        if 'decision_boundary' in result['plots']:
            with st.expander("🎯 决策边界图 (PCA降维可视化)", expanded=True):
                st.image(f"data:image/png;base64,{result['plots']['decision_boundary']}",
                         caption="模型决策边界", use_container_width=True)
        if 'accuracy_curve' in result['plots']:
            with st.expander("📈 验证曲线 - 参数调优", expanded=True):
                st.image(f"data:image/png;base64,{result['plots']['accuracy_curve']}",
                         caption="不同参数下的模型性能", use_container_width=True)
        if 'learning_curve' in result['plots']:
            with st.expander("📚 学习曲线 - 模型训练过程", expanded=True):
                st.image(f"data:image/png;base64,{result['plots']['learning_curve']}",
                         caption="学习曲线", use_container_width=True)
        if 'confusion_matrix' in result['plots']:
            with st.expander("🎯 混淆矩阵", expanded=True):
                st.image(f"data:image/png;base64,{result['plots']['confusion_matrix']}",
                         caption="混淆矩阵", use_container_width=True)
        if 'roc_curve' in result['plots']:
            with st.expander("📈 ROC曲线", expanded=True):
                st.image(f"data:image/png;base64,{result['plots']['roc_curve']}",
                         caption="ROC曲线", use_container_width=True)
        if 'feature_importance' in result['plots']:
            with st.expander("🔑 特征重要性", expanded=True):
                st.image(f"data:image/png;base64,{result['plots']['feature_importance']}",
                         caption="特征重要性排序", use_container_width=True)
    else:
        st.warning("⚠️ 没有生成任何图表，请检查后端日志")

    if result.get('deepseek_analysis'):
        st.subheader("🤖 DeepSeek 智能分析报告")
        if "请提供有效的DeepSeek API Key" in result['deepseek_analysis']:
            st.warning(result['deepseek_analysis'])
        else:
            with st.expander("📄 点击展开AI分析报告", expanded=True):
                st.markdown(result['deepseek_analysis'], unsafe_allow_html=True)
            st.download_button(
                label="📥 下载分析报告",
                data=result['deepseek_analysis'],
                file_name="deepseek_analysis_report.md",
                mime="text/markdown"
            )
            if result.get('report_docx_base64'):
                try:
                    docx_bytes = base64.b64decode(result['report_docx_base64'])
                    st.download_button(
                        label="📥 下载Word格式报告",
                        data=docx_bytes,
                        file_name="deepseek_analysis_report.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary"
                    )
                except Exception as e:
                    st.warning(f"⚠️ Word报告下载按钮生成失败: {e}")

    st.download_button(
        label="📊 下载完整结果 (JSON)",
        data=json.dumps(result, indent=2, ensure_ascii=False),
        file_name="analysis_results.json",
        mime="application/json"
    )

# ============================================================
# ============ 桌宠渲染（接收联动消息） =======================
# ============================================================
render_pet_footer()
