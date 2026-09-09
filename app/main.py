# main.py - 完整版（包含所有图表生成功能）
# ============================================================
# ===== 第1步：设置 matplotlib 后端（必须在导入 pyplot 之前） =====
# ============================================================
import matplotlib

matplotlib.use('Agg')  # 使用非交互式后端，解决线程问题

# ============================================================
# ===== 第2步：导入所有库 =====
# ============================================================
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
import uvicorn
import json
import httpx
import asyncio
import sys
from sklearn.model_selection import train_test_split, learning_curve, validation_curve, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    mean_squared_error, r2_score, mean_absolute_error,
    confusion_matrix, roc_curve, auc
)
from sklearn.decomposition import PCA
import io
import chardet
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import time
import os
import joblib
import re

# ============================================================
# ===== 第3步：警告过滤 =====
# ============================================================
import warnings

warnings.filterwarnings('ignore')
from sklearn.exceptions import ConvergenceWarning

warnings.filterwarnings('ignore', category=RuntimeWarning)
warnings.filterwarnings('ignore', category=ConvergenceWarning)
warnings.filterwarnings('ignore', category=UserWarning)

# ============================================================
# ===== 第4步：设置中文字体 =====
# ============================================================
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 导入统一的检测器和模型支持字典
from task_detector import TaskTypeDetector, MODEL_SUPPORT, MODEL_NAMES

app = FastAPI(title="喂食大肥鱼", version="1.0.0")

# ============== CORS（桌宠气泡跨域调用） ==============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== DeepSeek配置 ==============
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
# ===== 在这里配置你的 API Key =====
DEEPSEEK_API_KEY = ""  # ← 替换为你的实际密钥
# ===================================

# ============== 模型实现 ==============
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.svm import SVC, SVR
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from xgboost import XGBClassifier, XGBRegressor
from catdog_classifier import predict_catdog_image, train_catdog_classifier


# ============== 图表生成工具 ==============
# 图表键 → 中文名映射（用于在AI报告中嵌入图表）
PLOT_DISPLAY_NAMES = {
    'decision_boundary': '决策边界图',
    'learning_curve': '学习曲线',
    'accuracy_curve': '验证曲线',
    'confusion_matrix': '混淆矩阵',
    'roc_curve': 'ROC曲线',
    'feature_importance': '特征重要性图'
}


def embed_plots_into_report(report: str, plots: dict) -> str:
    """将base64图表嵌入到Markdown分析报告中（占位符替换 + 附录兜底）"""
    if not report or not plots:
        return report

    def img(alt, b64):
        return (f'<img src="data:image/png;base64,{b64}" '
                f'alt="{alt}" style="max-width:100%;border-radius:8px;">')

    used = set()
    for key, name in PLOT_DISPLAY_NAMES.items():
        b64 = plots.get(key)
        if not b64:
            continue
        token = f"{{{{{name}}}}}"
        if token in report:
            report = report.replace(token, f"\n\n<div style=\"text-align:center\">\n{img(name, b64)}\n</div>\n\n")
            used.add(key)

    remaining = [
        (key, name) for key, name in PLOT_DISPLAY_NAMES.items()
        if key in plots and plots.get(key) and key not in used
    ]
    if remaining:
        report += "\n\n---\n\n## 📊 相关图表附录\n\n"
        for key, name in remaining:
            report += f"### {name}\n\n<div style=\"text-align:center\">\n{img(name, plots[key])}\n</div>\n\n"

    return report


# ============== 报告格式转换 ==============
def _is_table_row(line: str) -> bool:
    """判断是否为Markdown表格行（| 开头且 | 结尾）"""
    line = line.strip()
    if not line:
        return False
    if line.startswith('<') or line.startswith('#'):
        return False
    return line.startswith('|') and line.endswith('|')


def _is_table_separator_row(line: str) -> bool:
    """判断是否为表格分隔行（| :--- | :---: | ---: | 形式）"""
    cells = _parse_table_row(line)
    if not cells:
        return False
    pattern = re.compile(r':?-{2,}:?')
    return all(pattern.fullmatch(c) for c in cells)


def _parse_table_row(line: str) -> list:
    """解析表格行 → 单元格文本列表"""
    stripped = line.strip()
    if stripped.startswith('|'):
        stripped = stripped[1:]
    if stripped.endswith('|'):
        stripped = stripped[:-1]
    return [c.strip() for c in stripped.split('|')]


def _parse_table_alignments(sep_row: str) -> list:
    """从分隔行解析每列对齐方式：left / center / right"""
    aligns = []
    for cell in _parse_table_row(sep_row):
        if cell.startswith(':') and cell.endswith(':'):
            aligns.append('center')
        elif cell.startswith(':'):
            aligns.append('left')
        elif cell.endswith(':'):
            aligns.append('right')
        else:
            aligns.append('center')
    return aligns


def _clean_inline_md(text: str) -> str:
    """清理单元格内联markdown标记与HTML标签"""
    t = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    t = re.sub(r'`([^`]+)`', r'\1', t)
    t = re.sub(r'\*([^*]+)\*', r'\1', t)
    t = re.sub(r'<[^>]+>', '', t)
    return t.strip()


def _add_markdown_table(doc, header_cells, body_rows, alignments):
    """按Word表格样式添加Markdown表格（表头加粗+底纹，单元格对齐，中文字体）"""
    from docx.shared import Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    n_cols = len(header_cells)
    table = doc.add_table(rows=1 + len(body_rows), cols=n_cols)
    try:
        table.style = 'Table Grid'
    except Exception:
        pass
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True

    def _put_text(cell, text, bold=False, align='center'):
        cell.text = ''
        paragraph = cell.paragraphs[0]
        paragraph.alignment = {
            'left': WD_ALIGN_PARAGRAPH.LEFT,
            'center': WD_ALIGN_PARAGRAPH.CENTER,
            'right': WD_ALIGN_PARAGRAPH.RIGHT,
        }.get(align, WD_ALIGN_PARAGRAPH.CENTER)
        run = paragraph.add_run(_clean_inline_md(text))
        run.font.size = Pt(10)
        run.font.name = 'Microsoft YaHei'
        try:
            run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
        except Exception:
            pass
        if bold:
            run.bold = True
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    # ===== 表头行：加粗 + 浅蓝底纹 =====
    for j, text in enumerate(header_cells):
        cell = table.cell(0, j)
        _put_text(cell, text, bold=True, align='center')
        try:
            shd = OxmlElement('w:shd')
            shd.set(qn('w:val'), 'clear')
            shd.set(qn('w:color'), 'auto')
            shd.set(qn('w:fill'), 'D9E2F3')
            cell._tc.get_or_add_tcPr().append(shd)
        except Exception:
            pass

    # ===== 数据行：按列对齐（前缀/后缀规则），不足列补空 =====
    for r, row_cells in enumerate(body_rows, start=1):
        for j in range(n_cols):
            text = row_cells[j] if j < len(row_cells) else ''
            align = alignments[j] if j < len(alignments) else 'center'
            _put_text(table.cell(r, j), text, bold=False, align=align)


def markdown_to_docx(md_text: str) -> bytes:
    """将嵌入式图片的Markdown报告转换为Word文档，返回docx字节"""
    try:
        from docx import Document
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml.ns import qn
        import re
    except ImportError:
        raise RuntimeError("python-docx 未安装，请执行: pip install python-docx")

    doc = Document()

    # 设置默认中文字体
    style = doc.styles['Normal']
    style.font.name = 'Microsoft YaHei'
    style.font.size = Pt(11)
    try:
        style._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    except Exception:
        pass

    def _inline_runs(paragraph, text):
        """解析行内 markdown：**加粗**、`代码`、*斜体*（避免破坏列表/图片）"""
        # 先处理分隔的简单模式
        tokens = re.split(r'(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)', text)
        for token in tokens:
            if not token:
                continue
            if token.startswith('**') and token.endswith('**') and len(token) > 4:
                run = paragraph.add_run(token[2:-2])
                run.bold = True
            elif token.startswith('`') and token.endswith('`') and len(token) > 2:
                run = paragraph.add_run(token[1:-1])
                run.font.name = 'Consolas'
            elif token.startswith('*') and token.endswith('*') and len(token) > 2:
                run = paragraph.add_run(token[1:-1])
                run.italic = True
            else:
                paragraph.add_run(token)

    def _add_picture(base64_str, alt=""):
        # 插入居中图片
        try:
            img_bytes = base64.b64decode(base64_str)
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run()
            run.add_picture(io.BytesIO(img_bytes), width=Inches(6))
        except Exception as e:
            p = doc.add_paragraph()
            p.add_run(f"[图片加载失败: {alt if alt else '未知'}]")

    lines = md_text.split('\n')
    i, n = 0, len(lines)
    while i < n:
        raw_line = lines[i]
        line = raw_line.strip()
        if not line:
            i += 1
            continue

        # ===== Markdown表格（连续行聚合为Word表格） =====
        if _is_table_row(line) and i + 1 < n and _is_table_separator_row(lines[i + 1]):
            header_cells = _parse_table_row(line)
            alignments = _parse_table_alignments(lines[i + 1])
            body_rows = []
            j = i + 2
            while j < n and _is_table_row(lines[j]):
                body_rows.append(_parse_table_row(lines[j]))
                j += 1
            if body_rows:
                _add_markdown_table(doc, header_cells, body_rows, alignments)
            i = j
            continue

        # 图片行（含div包裹）
        img_match = re.search(r'<img[^>]*src="data:image/[a-zA-Z]+;base64,([^"]+)"[^>]*alt="([^"]*)"', line)
        if img_match:
            _add_picture(img_match.group(1), img_match.group(2))
            i += 1
            continue

        line = re.sub(r'<div[^>]*>', '', line)
        line = re.sub(r'</div>', '', line)
        line = re.sub(r'<(br|hr|p)[^>]*>', '', line)
        if not line.strip():
            i += 1
            continue

        # 标题
        heading_match = re.match(r'^(#{1,6})\s+(.*)$', line)
        if heading_match:
            level = min(len(heading_match.group(1)), 4)
            text = re.sub(r'\*\*|`|\*|\(.*?\)', '', heading_match.group(2)).strip()
            if text:
                doc.add_heading(text, level=level)
            i += 1
            continue

        # 分隔线
        if re.match(r'^(\-{3,}|\*{3,}|_{3,})\s*$', line):
            i += 1
            continue

        # 列表项（- / * / 数字.）
        list_match = re.match(r'^(\d+)[.、]\s+(.*)$', line)
        if list_match:
            p = doc.add_paragraph(style='List Number')
            _inline_runs(p, list_match.group(2))
            i += 1
            continue
        bullet_match = re.match(r'^[-*]\s+(.*)$', line)
        if bullet_match:
            p = doc.add_paragraph(style='List Bullet')
            _inline_runs(p, bullet_match.group(1))
            i += 1
            continue

        # 普通段落
        p = doc.add_paragraph()
        _inline_runs(p, line)
        i += 1

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def fig_to_base64(fig):
    """将matplotlib图表转换为base64编码"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img_base64


def generate_decision_boundary(model, X_train, y_train, task_type):
    """生成决策边界图（使用PCA降维到2D）"""
    try:
        print(f"  🎯 生成决策边界: 样本数={len(X_train)}, 特征数={X_train.shape[1]}")

        if len(X_train) < 10 or X_train.shape[1] < 2:
            print(f"  ⚠️ 样本数或特征数不足")
            return None

        pca = PCA(n_components=2)
        X_2d = pca.fit_transform(X_train)

        x_min, x_max = X_2d[:, 0].min() - 0.5, X_2d[:, 0].max() + 0.5
        y_min, y_max = X_2d[:, 1].min() - 0.5, X_2d[:, 1].max() + 0.5

        if x_max - x_min < 0.1:
            x_min -= 0.5
            x_max += 0.5
        if y_max - y_min < 0.1:
            y_min -= 0.5
            y_max += 0.5

        h = max((x_max - x_min) / 100, (y_max - y_min) / 100, 0.02)
        xx, yy = np.meshgrid(np.arange(x_min, x_max, h),
                             np.arange(y_min, y_max, h))

        grid_points = np.c_[xx.ravel(), yy.ravel()]

        try:
            grid_original = pca.inverse_transform(grid_points)
            y_pred_grid = model.predict(grid_original)
            y_pred_grid = y_pred_grid.reshape(xx.shape)
        except:
            if task_type == 'regression':
                from sklearn.linear_model import LinearRegression
                temp_model = LinearRegression()
                temp_model.fit(X_2d, y_train)
                y_pred_grid = temp_model.predict(grid_points)
                y_pred_grid = y_pred_grid.reshape(xx.shape)
            else:
                from sklearn.neighbors import KNeighborsClassifier
                n_neighbors = min(5, len(np.unique(y_train)))
                temp_model = KNeighborsClassifier(n_neighbors=n_neighbors)
                temp_model.fit(X_2d, y_train)
                y_pred_grid = temp_model.predict(grid_points)
                y_pred_grid = y_pred_grid.reshape(xx.shape)

        fig, ax = plt.subplots(figsize=(10, 8))

        if task_type == 'regression':
            contour = ax.contourf(xx, yy, y_pred_grid, alpha=0.8, cmap='RdYlBu_r', levels=20)
            scatter = ax.scatter(X_2d[:, 0], X_2d[:, 1], c=y_train,
                                 cmap='RdYlBu_r', edgecolors='black', linewidth=0.5, s=40)
            plt.colorbar(contour, ax=ax, label='预测值')
            ax.set_title(f'决策边界 (回归任务)\n模型: {type(model).__name__}', fontsize=12)
        else:
            n_classes = len(np.unique(y_train))
            if n_classes <= 10:
                cmap = plt.cm.tab10
            else:
                cmap = plt.cm.viridis
            contour = ax.contourf(xx, yy, y_pred_grid, alpha=0.6, cmap=cmap,
                                  levels=np.linspace(-0.5, n_classes - 0.5, n_classes + 1))
            scatter = ax.scatter(X_2d[:, 0], X_2d[:, 1], c=y_train,
                                 cmap=cmap, edgecolors='black', linewidth=0.5, s=40)
            ax.set_title(f'决策边界 (分类任务)\n模型: {type(model).__name__}', fontsize=12)

        ax.set_xlabel(f'第一主成分 ({pca.explained_variance_ratio_[0]:.2%} 方差)', fontsize=10)
        ax.set_ylabel(f'第二主成分 ({pca.explained_variance_ratio_[1]:.2%} 方差)', fontsize=10)
        ax.grid(True, alpha=0.3)

        print(f"  ✅ 决策边界生成成功")
        return fig_to_base64(fig)
    except Exception as e:
        print(f"  ❌ 生成决策边界失败: {e}")
        return None


def generate_accuracy_curves(model, X_train, y_train, task_type, param_name, param_range):
    """生成验证曲线（准确率曲线）"""
    try:
        print(f"  📈 生成验证曲线: 参数={param_name}, 范围={param_range}")

        cv = min(5, len(X_train) // 3)
        if cv < 2:
            print(f"  ⚠️ 样本数不足，无法生成验证曲线")
            return None

        scoring = 'r2' if task_type == 'regression' else 'accuracy'

        train_scores, test_scores = validation_curve(
            model, X_train, y_train,
            param_name=param_name,
            param_range=param_range,
            cv=cv,
            scoring=scoring,
            n_jobs=-1
        )

        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        test_mean = np.mean(test_scores, axis=1)
        test_std = np.std(test_scores, axis=1)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.fill_between(param_range, train_mean - train_std, train_mean + train_std,
                        alpha=0.1, color="blue")
        ax.fill_between(param_range, test_mean - test_std, test_mean + test_std,
                        alpha=0.1, color="orange")
        ax.plot(param_range, train_mean, 'o-', color="blue", label="训练集", linewidth=2)
        ax.plot(param_range, test_mean, 'o-', color="orange", label="验证集", linewidth=2)
        ax.set_xlabel(param_name, fontsize=12)
        ax.set_ylabel('性能分数', fontsize=12)
        ax.set_title(f'验证曲线 - {param_name}', fontsize=14)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)

        best_idx = np.argmax(test_mean)
        ax.axvline(x=param_range[best_idx], color='red', linestyle='--',
                   label=f'最佳值: {param_range[best_idx]}')
        ax.legend(loc="best")

        print(f"  ✅ 验证曲线生成成功")
        return fig_to_base64(fig)
    except Exception as e:
        print(f"  ❌ 生成验证曲线失败: {e}")
        return None


def generate_learning_curve(model, X_train, y_train, task_type):
    """生成学习曲线"""
    try:
        print(f"  📚 生成学习曲线: 样本数={len(X_train)}")

        cv = min(5, len(X_train) // 3)
        if cv < 2:
            print(f"  ⚠️ 样本数不足，无法生成学习曲线")
            return None

        scoring = 'r2' if task_type == 'regression' else 'accuracy'

        train_sizes, train_scores, test_scores = learning_curve(
            model, X_train, y_train,
            cv=cv,
            train_sizes=np.linspace(0.1, 1.0, min(10, len(X_train) // 2)),
            scoring=scoring,
            n_jobs=-1
        )

        train_mean = np.mean(train_scores, axis=1)
        train_std = np.std(train_scores, axis=1)
        test_mean = np.mean(test_scores, axis=1)
        test_std = np.std(test_scores, axis=1)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.fill_between(train_sizes, train_mean - train_std, train_mean + train_std,
                        alpha=0.1, color="blue")
        ax.fill_between(train_sizes, test_mean - test_std, test_mean + test_std,
                        alpha=0.1, color="orange")
        ax.plot(train_sizes, train_mean, 'o-', color="blue", label="训练集", linewidth=2)
        ax.plot(train_sizes, test_mean, 'o-', color="orange", label="验证集", linewidth=2)
        ax.set_xlabel('训练样本数量', fontsize=12)
        ax.set_ylabel('性能分数', fontsize=12)
        ax.set_title('学习曲线', fontsize=14)
        ax.legend(loc="best")
        ax.grid(True, alpha=0.3)

        print(f"  ✅ 学习曲线生成成功")
        return fig_to_base64(fig)
    except Exception as e:
        print(f"  ❌ 生成学习曲线失败: {e}")
        return None


def generate_confusion_matrix_plot(y_test, y_pred):
    """生成混淆矩阵"""
    try:
        print(f"  🎯 生成混淆矩阵")
        cm = confusion_matrix(y_test, y_pred)
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                    ax=ax, cbar_kws={'label': '样本数量'})
        ax.set_xlabel('预测类别', fontsize=12)
        ax.set_ylabel('真实类别', fontsize=12)
        ax.set_title('混淆矩阵', fontsize=14)
        print(f"  ✅ 混淆矩阵生成成功")
        return fig_to_base64(fig)
    except Exception as e:
        print(f"  ❌ 生成混淆矩阵失败: {e}")
        return None


def generate_roc_curve(y_test, y_proba):
    """生成ROC曲线"""
    try:
        print(f"  📈 生成ROC曲线")
        fpr, tpr, _ = roc_curve(y_test, y_proba)
        roc_auc = auc(fpr, tpr)

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC曲线 (AUC = {roc_auc:.3f})')
        ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='随机猜测')
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.05])
        ax.set_xlabel('假阳性率 (FPR)', fontsize=12)
        ax.set_ylabel('真阳性率 (TPR)', fontsize=12)
        ax.set_title('ROC曲线', fontsize=14)
        ax.legend(loc="lower right")
        ax.grid(True, alpha=0.3)

        print(f"  ✅ ROC曲线生成成功")
        return fig_to_base64(fig)
    except Exception as e:
        print(f"  ❌ 生成ROC曲线失败: {e}")
        return None


def generate_feature_importance_plot(feature_importance, top_n=15):
    """生成特征重要性条形图"""
    if not feature_importance:
        return None

    try:
        print(f"  🔑 生成特征重要性图")
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:top_n]
        names = [item[0] for item in sorted_features]
        values = [item[1] for item in sorted_features]

        fig, ax = plt.subplots(figsize=(10, max(6, len(names) * 0.4)))
        bars = ax.barh(names, values, color=plt.cm.viridis(np.linspace(0.3, 0.9, len(names))))
        ax.set_xlabel('重要性', fontsize=12)
        ax.set_title(f'特征重要性 Top {len(names)}', fontsize=14)
        ax.grid(True, alpha=0.3, axis='x')

        for bar, val in zip(bars, values):
            ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                    f'{val:.3f}', va='center', fontsize=10)

        print(f"  ✅ 特征重要性图生成成功")
        return fig_to_base64(fig)
    except Exception as e:
        print(f"  ❌ 生成特征重要性图失败: {e}")
        return None


class ModelFactory:
    @staticmethod
    def get_model(model_type: str, params: Optional[Dict] = None, task_type: str = "classification"):
        model_mapping = {
            "knn": {"classification": KNeighborsClassifier, "regression": KNeighborsRegressor},
            "svm": {"classification": SVC, "regression": SVR},
            "linear_regression": {"regression": LinearRegression},
            "random_forest": {"classification": RandomForestClassifier, "regression": RandomForestRegressor},
            "xgboost": {"classification": XGBClassifier, "regression": XGBRegressor},
            "decision_tree": {"classification": DecisionTreeClassifier, "regression": DecisionTreeRegressor},
            "logistic_regression": {"classification": LogisticRegression}
        }
        model_classes = model_mapping.get(model_type, {})
        model_class = model_classes.get(task_type)
        if not model_class:
            supported = [k for k in model_classes.keys()]
            raise ValueError(
                f"模型 '{model_type}' 不支持 {task_type} 任务。"
                f"支持的{'任务类型' if supported else '模型不存在'}: {', '.join(supported) if supported else '无'}"
            )
        default_params = {
            "knn": {"n_neighbors": 5},
            "svm": {"kernel": "rbf", "C": 1.0, "probability": True},
            "svm_regression": {"kernel": "rbf", "C": 1.0},
            "random_forest": {"n_estimators": 100, "random_state": 42},
            "xgboost": {"n_estimators": 100, "random_state": 42, "use_label_encoder": False, "eval_metric": "logloss"},
            "xgboost_regression": {"n_estimators": 100, "random_state": 42},
            "decision_tree": {"random_state": 42},
            "logistic_regression": {"random_state": 42, "max_iter": 1000}
        }
        if model_type == "svm":
            default_key = "svm_regression" if task_type == "regression" else "svm"
        elif model_type == "xgboost":
            default_key = "xgboost_regression" if task_type == "regression" else "xgboost"
        else:
            default_key = model_type
        final_params = {**default_params.get(default_key, {}), **(params or {})}
        if model_type == "svm" and task_type == "regression":
            final_params.pop("probability", None)
        return model_class(**final_params)


# ============== 模型保存工具（best + last） ==============
def train_best_model(model_type: str, params_dict: Dict, task_type: str,
                     X_train, y_train, n_candidates: int = 5):
    """通过交叉验证在多个随机种子候选中选择最佳模型，并在训练集上最终拟合"""
    scoring = 'r2' if task_type == 'regression' else 'accuracy'
    best_est, best_score = None, None
    cv = max(2, min(3, len(X_train) // 20))
    candidates = n_candidates if len(X_train) >= 30 else 2

    for seed in range(candidates):
        est = ModelFactory.get_model(model_type, params_dict, task_type)
        try:
            if 'random_state' in est.get_params(deep=True):
                est.set_params(random_state=seed)
        except Exception:
            pass
        try:
            scores = cross_val_score(est, X_train, y_train, cv=cv, scoring=scoring)
            score = float(np.mean(scores))
            print(f"  🎯 候选模型 seed={seed}: {scoring} = {score:.4f}")
        except Exception as e:
            print(f"  ⚠️ 候选模型 seed={seed} 评估失败: {e}")
            continue
        if best_est is None or score > best_score:
            best_est, best_score = est, score

    if best_est is None:
        return None, None
    print(f"  ✅ 最佳模型已选定: {scoring} = {best_score:.4f}")
    best_est.fit(X_train, y_train)
    return best_est, best_score


def save_trained_models(best_model, last_model, info: dict, save_dir: str = "saved_models") -> str:
    """保存best/last模型与元数据，返回保存目录路径"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    base_dir = save_dir if save_dir else "saved_models"
    if not os.path.isabs(base_dir):
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), base_dir)
    out_dir = os.path.join(base_dir, f"analysis_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)

    best_path = os.path.join(out_dir, "model_best.pkl")
    last_path = os.path.join(out_dir, "model_last.pkl")
    joblib.dump(best_model, best_path)
    joblib.dump(last_model, last_path)

    info.update({
        'saved_at': time.strftime("%Y-%m-%d %H:%M:%S"),
        'best_model_file': os.path.basename(best_path),
        'last_model_file': os.path.basename(last_path),
    })
    info_path = os.path.join(out_dir, "model_info.json")
    with open(info_path, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    return out_dir


# ============== 分析引擎 ==============
class AnalysisEngine:
    def preprocess_data(self, df: pd.DataFrame, target_col: str, selected_features: Optional[list] = None,
                        force_task_type: Optional[str] = None):
        """数据预处理"""
        print(f"🔧 原始数据形状: {df.shape}")
        print(f"📋 列名: {df.columns.tolist()}")
        print(f"📊 目标列数据类型: {df[target_col].dtype}")
        print(f"📊 目标列唯一值数量: {df[target_col].nunique()}")

        target_series = df[target_col]
        if target_series.dtype == 'object' or target_series.dtype == 'string':
            try:
                cleaned = target_series.astype(str).str.replace(r'[^\d.\-]', '', regex=True)
                y_numeric = pd.to_numeric(cleaned, errors='coerce')
                valid_ratio = y_numeric.notna().sum() / len(y_numeric)
                if valid_ratio > 0.8:
                    df[target_col] = y_numeric
                    print(f"✅ 目标列转换为数值成功，有效比例 {valid_ratio:.2%}")
                else:
                    print(f"⚠️ 目标列转换有效比例 {valid_ratio:.2%}，保留原始值")
            except Exception as e:
                print(f"⚠️ 目标列转换失败: {e}")

        if df[target_col].isna().all():
            raise ValueError("目标列全部为空值，请检查数据")

        # ===== 去除冗余数据列（列内空值占比 > 60% 视为冗余列） =====
        redundancy_cols = [
            col for col in df.columns
            if col != target_col and df[col].isna().mean() > 0.6
        ]
        if redundancy_cols:
            print(f"🗑️ 去除 {len(redundancy_cols)} 个冗余数据列（空值占比>60%）: {redundancy_cols}")
            df = df.drop(columns=redundancy_cols)

        df = df.dropna()
        if df.empty:
            raise ValueError("清理缺失值后没有可用样本")

        X = df.drop(columns=[target_col])
        y = df[target_col]

        if selected_features and len(selected_features) > 0:
            available_features = [col for col in selected_features if col in X.columns]
            if available_features:
                X = X[available_features]
                print(f"✅ 使用选中的 {len(available_features)} 个特征: {available_features}")
            else:
                print(f"⚠️ 选中的特征都不存在于数据中，使用全部特征")
        else:
            print(f"ℹ️ 未选择特征，使用全部 {len(X.columns)} 个特征")

        if X.shape[1] == 0:
            raise ValueError("没有可用于建模的特征")

        if force_task_type is not None and force_task_type in ["classification", "regression"]:
            task_type = force_task_type
            print(f"🎯 使用手动指定的任务类型: {task_type}")
        else:
            detector = TaskTypeDetector()
            task_type, details = detector.detect(y)
            print(f"🎯 自动检测任务类型: {task_type}")

        if task_type == 'regression':
            try:
                y_numeric = pd.to_numeric(y, errors='coerce')
                valid_ratio = y_numeric.notna().sum() / len(y)
                if valid_ratio >= 0.8:
                    y = y_numeric
                    print(f"✅ 回归目标转换成功，有效比例 {valid_ratio:.2%}")
                else:
                    task_type = 'classification'
                    le = LabelEncoder()
                    y = le.fit_transform(y.astype(str))
                    print(f"⚠️ 回归目标转换有效比例 {valid_ratio:.2%}，降级为分类任务")
            except Exception as e:
                task_type = 'classification'
                le = LabelEncoder()
                y = le.fit_transform(y.astype(str))
                print(f"⚠️ 回归目标转换异常，降级为分类任务: {e}")
        else:
            try:
                le = LabelEncoder()
                y = le.fit_transform(y.astype(str))
                print(f"✅ 分类目标编码完成，类别数: {len(le.classes_)}")
                task_type = 'classification'
            except Exception as e:
                print(f"⚠️ 分类目标编码失败: {e}")
                try:
                    y = pd.to_numeric(y, errors='coerce')
                    task_type = 'regression'
                    print(f"⚠️ 分类编码失败，转为回归任务")
                except:
                    raise ValueError("无法处理目标列数据")

        print(f"✅ 最终任务类型: {task_type}")

        numeric_cols, categorical_cols = [], []
        for col in X.columns:
            try:
                if pd.api.types.is_numeric_dtype(X[col]):
                    numeric_cols.append(str(col))
                else:
                    cleaned = X[col].astype(str).str.replace(r'[^\d.\-]', '', regex=True)
                    numeric_test = pd.to_numeric(cleaned, errors='coerce')
                    if numeric_test.notna().sum() > len(X[col]) * 0.7:
                        numeric_cols.append(str(col))
                    else:
                        categorical_cols.append(str(col))
            except:
                categorical_cols.append(str(col))

        le_dict = {}
        for col in categorical_cols:
            try:
                if col not in X.columns:
                    continue
                X[col] = X[col].astype(str).fillna('missing')
                if X[col].nunique() <= 1:
                    X = X.drop(columns=[col])
                    continue
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col])
                le_dict[str(col)] = [str(c) for c in le.classes_]
            except Exception as e:
                print(f"⚠️ 编码列 '{col}' 失败: {e}")
                if col in X.columns:
                    X = X.drop(columns=[col])

        if numeric_cols:
            for col in numeric_cols:
                if col in X.columns:
                    X[col] = pd.to_numeric(X[col], errors='coerce')
            X[numeric_cols] = X[numeric_cols].fillna(X[numeric_cols].mean())
            scaler = StandardScaler()
            X[numeric_cols] = scaler.fit_transform(X[numeric_cols])

        X = X.fillna(0)
        for col in X.columns:
            try:
                X[col] = pd.to_numeric(X[col], errors='coerce')
            except:
                try:
                    le = LabelEncoder()
                    X[col] = le.fit_transform(X[col].astype(str))
                except:
                    X[col] = 0
        X = X.fillna(0)

        print(f"✅ 预处理完成: {X.shape[1]} 个特征, {X.shape[0]} 个样本")
        return X, y, {
            'numeric_cols': numeric_cols,
            'categorical_cols': categorical_cols,
            'n_features': int(X.shape[1]),
            'n_samples': int(len(X)),
            'label_encoders': le_dict,
            'task_type': task_type
        }

    def compute_metrics(self, y_test, y_pred, task_type):
        """根据 y_test / y_pred 计算指标（与具体 model 解耦，供集成复用）"""
        if task_type == 'classification':
            try:
                if len(np.unique(y_test)) == 2:
                    metrics = {
                        'accuracy': float(accuracy_score(y_test, y_pred)),
                        'precision': float(precision_score(y_test, y_pred, average='binary', zero_division=0)),
                        'recall': float(recall_score(y_test, y_pred, average='binary', zero_division=0)),
                        'f1_score': float(f1_score(y_test, y_pred, average='binary', zero_division=0))
                    }
                else:
                    metrics = {
                        'accuracy': float(accuracy_score(y_test, y_pred)),
                        'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
                        'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
                        'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
                    }
            except:
                metrics = {
                    'accuracy': float(accuracy_score(y_test, y_pred)),
                    'precision': float(precision_score(y_test, y_pred, average='weighted', zero_division=0)),
                    'recall': float(recall_score(y_test, y_pred, average='weighted', zero_division=0)),
                    'f1_score': float(f1_score(y_test, y_pred, average='weighted', zero_division=0))
                }
        else:
            metrics = {
                'mse': float(mean_squared_error(y_test, y_pred)),
                'rmse': float(np.sqrt(mean_squared_error(y_test, y_pred))),
                'mae': float(mean_absolute_error(y_test, y_pred)),
                'r2_score': float(r2_score(y_test, y_pred))
            }
        return metrics

    def evaluate_model(self, model, X_test, y_test, task_type):
        y_pred = model.predict(X_test)
        return self.compute_metrics(y_test, y_pred, task_type), y_pred


# ============== 集成（多算法）工具 ==============
def majority_vote(preds_2d):
    """preds_2d shape (n_models, n_samples)；标签为非负整数。逐列取众数。"""
    preds_2d = np.asarray(preds_2d)
    n = preds_2d.shape[1]
    out = np.empty(n, dtype=preds_2d.dtype)
    for j in range(n):
        col = preds_2d[:, j].astype(int)
        out[j] = np.bincount(col).argmax()
    return out


class EnsemblePredictor:
    """轻量包装器：统一 predict 接口，供 generate_decision_boundary 等复用。"""

    def __init__(self, base_models, task_type):
        self.base_models = base_models  # list of (name, model)
        self.task_type = task_type

    def predict(self, X):
        preds = np.array([m.predict(X) for _, m in self.base_models])
        if self.task_type == 'classification':
            return majority_vote(preds)
        else:
            return preds.mean(axis=0)

    def predict_proba(self, X):
        probas = []
        for _, m in self.base_models:
            if hasattr(m, 'predict_proba'):
                probas.append(m.predict_proba(X))
        if not probas:
            raise AttributeError('no base model supports predict_proba')
        return np.mean(probas, axis=0)


# ============== DeepSeek集成服务 ==============
async def call_deepseek(
        model_type: str,  # ← 删除 api_key 参数
        metrics: dict,
        feature_importance: dict,
        data_summary: dict,
        custom_prompt: Optional[str] = None,
        available_plots: Optional[dict] = None,  # 可用图表列表（键→base64）
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        api_model: Optional[str] = None
) -> str:
    api_key = (api_key or DEEPSEEK_API_KEY or "").strip()
    api_url = (api_url or DEEPSEEK_API_URL).strip()
    api_model = (api_model or "deepseek-chat").strip()
    if not api_url.startswith(("http://", "https://")):
        return "❌ **API接口地址无效**，请填写完整的 http(s) Chat Completions 地址"
    if not api_model:
        return "❌ **模型名称不能为空**，请填写要调用的模型名"

    # ===== API Key检查 =====
    if not api_key or api_key.strip() == "":
        return """
⚠️ **DeepSeek API Key 未配置**

请按以下步骤配置：

1. 访问 [DeepSeek 平台](https://platform.deepseek.com/)
2. 注册并登录账号
3. 在控制台创建 API Key
4. 复制密钥（格式：`sk-xxxxx`）
5. 在 `main.py` 的 `DEEPSEEK_API_KEY` 变量中粘贴

💡 或者取消勾选 "启用DeepSeek智能分析" 继续使用图表功能
"""

    task_type = "分类" if "accuracy" in metrics else "回归"

    metrics_text = ""
    for k, v in metrics.items():
        if k in ['accuracy', 'precision', 'recall', 'f1_score', 'r2_score']:
            metrics_text += f"- **{k.upper().replace('_', ' ')}**: {v:.4f} ({v * 100:.2f}%)\n"
        else:
            metrics_text += f"- **{k.upper().replace('_', ' ')}**: {v:.4f}\n"

    importance_text = ""
    if feature_importance:
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
        for i, (name, value) in enumerate(sorted_features, 1):
            importance_text += f"  {i}. **{name}**: {value:.4f} ({value * 100:.2f}%)\n"

    base_prompt = f"""
## 模型信息
- **模型类型**: {model_type}
- **任务类型**: {task_type}

## 性能指标
{metrics_text}

## 数据概况
- 样本数量: {data_summary.get('n_samples', 'N/A')}
- 特征数量: {data_summary.get('n_features', 'N/A')}
- 目标变量: {data_summary.get('target', 'N/A')}
"""
    if importance_text:
        base_prompt += f"\n## 特征重要性 (Top 10)\n{importance_text}"

    # ===== 可用图表（供AI在报告中嵌入） =====
    plots_prompt = ""
    if available_plots:
        plot_lines = []
        for key, name in PLOT_DISPLAY_NAMES.items():
            if key in available_plots and available_plots.get(key):
                plot_lines.append(f"- {name}: `{{{{{name}}}}}`")
        if plot_lines:
            plots_prompt = f"""
## 可用的图表（用于嵌入报告）
已经为你生成了以下图表，请根据分析内容将它们插入报告中合适的位置：
{chr(10).join(plot_lines)}

嵌入要求：
1. 在相关分析段落之后，单独一行插入对应占位符，格式为 `{{{{图表名}}}}`（保持原样，不要修改名称）
2. 每个图表最多插入一次，只插入与内容相关、真实的图表
3. 不要生成或引用列表以外的占位符
4. 占位符必须在报告正文中间接使用，放在相关讨论段落正下方
"""
        base_prompt += plots_prompt

    if custom_prompt and custom_prompt.strip() and custom_prompt != "*114514*":
        final_prompt = f"{base_prompt}\n\n## 用户分析要求\n{custom_prompt.strip()}"
    else:
        final_prompt = f"{base_prompt}\n\n请对以上数据集进行专业的数据分析或预测，包括：\n1. 数据集/模型评估\n2. 目标列相关性分析\n3. 预测结果解读\n4. 改进方向"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": api_model,
                    "messages": [
                        {"role": "system", "content": "你是一个专业的数据分析专家。"},
                        {"role": "user", "content": final_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000
                }
            )

            print(f"  🔍 DeepSeek响应状态码: {response.status_code}")

            if response.status_code == 401:
                return "❌ **API密钥无效**，请检查您的DeepSeek API Key是否正确"
            elif response.status_code == 429:
                return "⚠️ **API调用频率限制**，请稍后再试"
            elif response.status_code == 402:
                return "⚠️ **账户余额不足**，请充值后重试"
            elif response.status_code != 200:
                return f"❌ **DeepSeek API调用失败**: {response.text[:200]}"

            result = response.json()
            return result["choices"][0]["message"]["content"]

    except httpx.TimeoutException:
        return "⏰ **请求超时**，请稍后重试"
    except httpx.ConnectError:
        return "🌐 **网络连接失败**，请检查网络"
    except Exception as e:
        return f"❌ **调用DeepSeek出错**: {str(e)}"


# ============== 读取CSV文件的辅助函数 ==============
def read_csv_file(contents: bytes) -> pd.DataFrame:
    encodings = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'utf-8-sig', 'cp936', 'latin-1']
    for enc in encodings:
        try:
            return pd.read_csv(io.BytesIO(contents), encoding=enc)
        except:
            continue
    try:
        detected = chardet.detect(contents)
        if detected['encoding']:
            return pd.read_csv(io.BytesIO(contents), encoding=detected['encoding'])
    except:
        pass
    return pd.read_csv(io.BytesIO(contents), encoding='utf-8', errors='ignore')


# ============== EDA 保存工具（Word） ==============
def build_eda_docx(df: pd.DataFrame, target_col: Optional[str] = None) -> bytes:
    """将EDA探索分析信息构建为Word文档字节"""
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml.ns import qn

    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Microsoft YaHei'
    style.font.size = Pt(10.5)
    try:
        style._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
    except Exception:
        pass

    def _cn_run(p, text, bold=False, size=10.5):
        run = p.add_run(str(text))
        run.bold = bold
        run.font.size = Pt(size)
        run.font.name = 'Microsoft YaHei'
        try:
            run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Microsoft YaHei')
        except Exception:
            pass
        return run

    def _add_table(header_cells, rows):
        n_cols = len(header_cells)
        table = doc.add_table(rows=1 + len(rows), cols=n_cols)
        try:
            table.style = 'Table Grid'
        except Exception:
            pass
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for j, txt in enumerate(header_cells):
            p = table.cell(0, j).paragraphs[0]
            _cn_run(p, txt, bold=True, size=9)
        for i, row in enumerate(rows, start=1):
            for j in range(n_cols):
                text = row[j] if j < len(row) else ''
                p = table.cell(i, j).paragraphs[0]
                _cn_run(p, text, size=9)
        doc.add_paragraph()

    def _add_picture(png_bytes):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        try:
            run.add_picture(io.BytesIO(png_bytes), width=Inches(6))
        except Exception as e:
            p2 = doc.add_paragraph()
            _cn_run(p2, f"[图表生成失败: {e}]")

    def _fig_png(fig) -> bytes:
        buf = io.BytesIO()
        try:
            fig.savefig(buf, format='png', dpi=110, bbox_inches='tight')
        finally:
            plt.close(fig)
        buf.seek(0)
        return buf.read()

    doc.add_heading('📊 EDA 数据探索分析报告', level=0)
    p = doc.add_paragraph()
    _cn_run(p, '生成时间：' + time.strftime('%Y-%m-%d %H:%M:%S'))

    # 一、数据概况
    doc.add_heading('一、数据概况', level=1)
    p = doc.add_paragraph()
    _cn_run(p, '数据集规模：')
    _cn_run(p, f'{int(len(df))} 行 × {int(len(df.columns))} 列', bold=True)
    if target_col and target_col in df.columns:
        p = doc.add_paragraph()
        _cn_run(p, '目标列：')
        _cn_run(p, str(target_col), bold=True)
        _det = TaskTypeDetector()
        _tt, _dt = _det.detect(df[target_col])
        p = doc.add_paragraph()
        _cn_run(p, '任务类型检测：')
        _cn_run(p, f"{_det.get_task_type_name(_tt)}（置信度 {_dt.get('confidence', 0):.0%}）", bold=True)
        for r in _dt.get('reasons', [])[:5]:
            doc.add_paragraph(str(r), style='List Bullet')

    # 二、数据预览
    doc.add_heading('二、数据预览（前8行）', level=1)
    preview_cols = [str(c) for c in df.columns][:12]
    preview_rows = df.head(8)[preview_cols].astype(str).fillna('').values.tolist()
    _add_table(preview_cols, preview_rows)

    # 三、列信息
    doc.add_heading('三、列信息', level=1)
    info_rows = [
        [str(c), str(df[c].dtype), int(df[c].nunique()), int(df[c].isnull().sum()), f"{df[c].isnull().mean():.2%}"]
        for c in df.columns
    ]
    _add_table(['列名', '类型', '唯一值', '缺失值', '缺失率'], info_rows)

    # 四、数值型描述统计
    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    if numeric_cols:
        doc.add_heading('四、数值型描述统计', level=1)
        desc = df[numeric_cols[:12]].describe().T
        header = ['列'] + [str(c) for c in desc.columns]
        rows = [[str(x) for x in row] for row in desc.reset_index().values.tolist()]
        _add_table(header, rows)

    # 五、关键图表
    doc.add_heading('五、关键图表', level=1)
    vis_cols = [c for c in numeric_cols if c != target_col][:6]
    if vis_cols:
        doc.add_heading('5.1 单变量分布（直方图）', level=2)
        n = len(vis_cols)
        ncols = 2
        nrows = int(np.ceil(n / ncols))
        fig, axes = plt.subplots(nrows, ncols, figsize=(ncols * 3.6, nrows * 2.4))
        axes = np.atleast_1d(axes).ravel()
        for i, col in enumerate(vis_cols):
            ax = axes[i]
            ax.hist(pd.to_numeric(df[col], errors='coerce').dropna(), bins=24,
                    color='#4ecdc4', edgecolor='white')
            ax.set_title(str(col), fontsize=9)
            ax.tick_params(labelsize=7)
        for j in range(n, len(axes)):
            axes[j].set_visible(False)
        fig.suptitle('单变量分布（直方图）', fontsize=11)
        fig.tight_layout()
        _add_picture(_fig_png(fig))

    if len(numeric_cols) > 1:
        doc.add_heading('5.2 特征相关性热图', level=2)
        cols = numeric_cols[:12]
        corr = df[cols].corr()
        fig, ax = plt.subplots(figsize=(5.6, 4.4))
        im = ax.imshow(corr.values, cmap='RdBu_r', vmin=-1, vmax=1)
        ax.set_xticks(range(len(cols)))
        ax.set_xticklabels([str(c) for c in cols], rotation=45, ha='right', fontsize=8)
        ax.set_yticks(range(len(cols)))
        ax.set_yticklabels([str(c) for c in cols], fontsize=8)
        for i in range(len(cols)):
            for j in range(len(cols)):
                ax.text(j, i, f'{corr.values[i, j]:.2f}', ha='center', va='center', fontsize=6.5,
                        color='white' if abs(corr.values[i, j]) > 0.55 else '#1c2b4a')
        ax.set_title('特征相关性热图', fontsize=11)
        fig.colorbar(im, ax=ax, shrink=0.8)
        _add_picture(_fig_png(fig))

    if target_col and target_col in df.columns:
        feats = [c for c in numeric_cols[:6] if c != target_col]
        if feats:
            doc.add_heading(f'5.3 双变量关系（特征 vs {target_col}）', level=2)
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
                ax.set_xlabel(str(col), fontsize=8)
                ax.set_ylabel(str(target_col), fontsize=8)
                ax.tick_params(labelsize=7)
            for j in range(n, len(axes)):
                axes[j].set_visible(False)
            fig.suptitle('双变量关系（红线为趋势）', fontsize=11)
            fig.tight_layout()
            _add_picture(_fig_png(fig))

        doc.add_heading('5.4 目标列分布', level=2)
        s = df[target_col]
        fig, ax = plt.subplots(figsize=(5.6, 3.2))
        if pd.api.types.is_numeric_dtype(s) and s.nunique() > 20:
            ax.hist(pd.to_numeric(s, errors='coerce').dropna(), bins=30, color='#4ecdc4', edgecolor='white')
            ax.set_title(f'{target_col} 分布', fontsize=11)
        else:
            vc = s.astype(str).value_counts().head(12)
            ax.barh(list(vc.index)[::-1], list(vc.values)[::-1], color='#2f80ed')
            ax.set_title(f'{target_col} 分布（Top12）', fontsize=11)
        _add_picture(_fig_png(fig))

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


@app.post("/api/eda/save")
async def save_eda_report(
        file: UploadFile = File(...),
        target_column: Optional[str] = Form(None),
        save_dir: Optional[str] = Form("saved_EDA")
):
    """将EDA探索分析信息保存为Word文档，存入打包后主文件夹下新建的 saved_EDA 文件夹"""
    try:
        contents = await file.read()
        df = read_csv_file(contents)
        if df.empty:
            raise HTTPException(status_code=400, detail="CSV文件为空")
        target_col = target_column if target_column and target_column in df.columns else None
        docx_bytes = build_eda_docx(df, target_col)

        base_dir = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(base_dir, save_dir or "saved_EDA")
        os.makedirs(out_dir, exist_ok=True)
        file_name = f"EDA_{time.strftime('%Y%m%d_%H%M%S')}.docx"
        path = os.path.join(out_dir, file_name)
        with open(path, "wb") as f:
            f.write(docx_bytes)
        print(f"✅ EDA报告已保存: {path}")
        return {
            "status": "success",
            "save_path": os.path.join(save_dir or "saved_EDA", file_name),
            "save_dir": out_dir,
            "filename": file_name,
            "n_rows": int(len(df)),
            "n_cols": int(len(df.columns)),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ EDA保存失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============== API端点 ==============
async def run_analysis_core(
        contents: bytes,
        model_type: str,
        target_column: str,
        test_size: float,
        random_state: int,
        parameters: str,
        use_deepseek_analysis: bool,
        analysis_prompt: Optional[str],
        task_type_override: Optional[str],
        selected_features: Optional[str],
        report_format: str,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        api_model: Optional[str] = None,
        save_models: bool = False,
        batch_size: int = 32,
        epochs: int = 50,
        save_dir: str = "saved_models",
        model_types: Optional[str] = None,
        parameters_list: Optional[str] = None
) -> dict:
    """分析核心逻辑（供普通端点与流式日志端点复用）"""
    print("=" * 60)
    print(f"📥 收到分析请求: 模型={model_type}, 目标列={target_column}")

    if not 0 < test_size < 1:
        raise HTTPException(status_code=400, detail="test_size 必须介于 0 和 1 之间")

    df = read_csv_file(contents)
    if df.empty:
        raise HTTPException(status_code=400, detail="CSV文件为空")
    if target_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"目标列 '{target_column}' 不存在")

    selected_feature_list = None
    if selected_features:
        try:
            selected_feature_list = json.loads(selected_features)
        except json.JSONDecodeError:
            pass

    engine = AnalysisEngine()
    X, y, preprocess_info = engine.preprocess_data(
        df, target_column,
        selected_features=selected_feature_list,
        force_task_type=task_type_override
    )

    task_type = preprocess_info['task_type']
    n_features = int(X.shape[1])
    print(f"🎯 最终任务类型: {task_type}，特征数: {n_features}")

    # ===== 集成模式判定 =====
    ensemble_models_list = None
    ensemble_params_list = None
    is_ensemble = False
    if model_types:
        try:
            ensemble_models_list = json.loads(model_types)
        except json.JSONDecodeError:
            ensemble_models_list = None
        try:
            ensemble_params_list = json.loads(parameters_list) if parameters_list else []
        except json.JSONDecodeError:
            ensemble_params_list = []
        if ensemble_models_list and isinstance(ensemble_models_list, list) and len(ensemble_models_list) >= 2:
            is_ensemble = True

    if is_ensemble:
        for mt in ensemble_models_list:
            if task_type not in MODEL_SUPPORT.get(mt, set()):
                raise HTTPException(
                    status_code=400,
                    detail=f"模型 '{mt}' 不支持 {task_type} 任务"
                )

    stratify = None
    if task_type == 'classification':
        class_counts = pd.Series(y).value_counts()
        if len(class_counts) > 1 and class_counts.min() >= 2:
            stratify = y
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )

    submodel_metrics = []

    if is_ensemble:
        # ===== 集成模式：训练多个基模型，分类多数票决 / 回归取平均 =====
        base_models = []
        print(f"🚀 集成模式，开始训练 {len(ensemble_models_list)} 个基模型...")
        start_time = time.time()
        for i, mt in enumerate(ensemble_models_list):
            p = ensemble_params_list[i] if i < len(ensemble_params_list) and isinstance(ensemble_params_list[i], dict) else {}
            m = ModelFactory.get_model(mt, p, task_type)
            for key, val in (('batch_size', batch_size), ('epochs', epochs), ('n_epochs', epochs)):
                try:
                    if key in m.get_params(deep=True):
                        m.set_params(**{key: val})
                except Exception:
                    pass
            print(f"  📦 训练基模型 [{i + 1}/{len(ensemble_models_list)}]: {mt}")
            m.fit(X_train, y_train)
            base_models.append((mt, m))
            sm, _ = engine.evaluate_model(m, X_test, y_test, task_type)
            submodel_metrics.append({"model": mt, "metrics": {str(k): float(v) for k, v in sm.items()}})
        train_time = time.time() - start_time
        print(f"✅ 集成训练完成，用时: {train_time:.2f}秒")

        model = EnsemblePredictor(base_models, task_type)
        y_pred = model.predict(X_test)
        metrics = engine.compute_metrics(y_test, y_pred, task_type)

        model_type = "集成(" + "+".join(MODEL_NAMES.get(mt, mt) for mt in ensemble_models_list) + ")"
        print(f"🔀 集成预测完成（{'多数票决' if task_type == 'classification' else '平均值'}）")
    else:
        # ===== 单模型模式（原逻辑） =====
        if task_type not in MODEL_SUPPORT.get(model_type, set()):
            supported = [m for m, tasks in MODEL_SUPPORT.items() if task_type in tasks]
            raise HTTPException(
                status_code=400,
                detail=f"模型 '{model_type}' 不支持 {task_type} 任务"
            )

        try:
            params_dict = json.loads(parameters) if parameters else {}
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"模型参数格式错误: {e}")
        if not isinstance(params_dict, dict):
            raise HTTPException(status_code=400, detail="模型参数必须是 JSON 对象")
        model = ModelFactory.get_model(model_type, params_dict, task_type)

        # ===== 训练过程参数（batch size / epochs） =====
        applied_training_params = []
        for key, val in (('batch_size', batch_size), ('epochs', epochs), ('n_epochs', epochs)):
            try:
                if key in model.get_params(deep=True):
                    model.set_params(**{key: val})
                    applied_training_params.append(f"{key}={val}")
            except Exception:
                pass
        print(f"⏱️ 训练过程参数: batch_size={batch_size}, epochs={epochs}"
              + (f"（已应用到模型: {', '.join(applied_training_params)}）" if applied_training_params else ""))

        print(f"🚀 开始训练模型: {model_type}")
        start_time = time.time()
        model.fit(X_train, y_train)
        train_time = time.time() - start_time
        print(f"✅ 训练完成，用时: {train_time:.2f}秒")

        metrics, y_pred = engine.evaluate_model(model, X_test, y_test, task_type)

    # ===== 模型保存选项（best + last） =====
    model_save_info = None
    if save_models and not is_ensemble:
        print("💾 开始搜索最佳模型（交叉验证）...")
        best_model, best_score = None, None
        try:
            best_model, best_score = train_best_model(model_type, params_dict, task_type, X_train, y_train)
        except Exception as e:
            print(f"⚠️ 最佳模型搜索失败: {e}")
        if best_model is None:
            best_model = model
            print("⚠️ 使用当前模型作为best模型")

        last_score = float(
            metrics['r2_score'] if task_type == 'regression' else metrics['accuracy']
        )
        info = {
            'model_type': model_type,
            'task_type': task_type,
            'target_column': str(target_column),
            'features': [str(c) for c in X.columns],
            'n_samples': int(len(X)),
            'n_features': int(X.shape[1]),
            'metrics': {str(k): float(v) for k, v in metrics.items()},
            'best_model_score': best_score,
            'last_model_score': last_score,
            'preprocess_info': {
                'numeric_cols': preprocess_info['numeric_cols'],
                'categorical_cols': preprocess_info['categorical_cols'],
                'label_encoders': preprocess_info['label_encoders']
            },
            'training_params': {
                'batch_size': batch_size,
                'epochs': epochs,
                'applied_to_model': applied_training_params
            }
        }
        try:
            out_dir = save_trained_models(best_model, model, info, save_dir=save_dir)
            model_save_info = {
                'save_dir': out_dir,
                'best_model_score': best_score,
                'last_model_score': last_score,
                'best_model_file': info['best_model_file'],
                'last_model_file': info['last_model_file'],
                'saved_at': info['saved_at'],
                'training_params': info['training_params']
            }
            print(f"✅ best/last模型已保存: {out_dir}")
        except Exception as e:
            print(f"⚠️ 模型保存失败: {e}")
            import traceback
            traceback.print_exc()

    # ============================================================
    # ===== ★ 生成所有图表 ★ =====
    # ============================================================
    print("📊 开始生成图表...")
    plots = {}

    # 1. 决策边界
    print("📊 生成决策边界图...")
    decision_boundary = generate_decision_boundary(model, X_train, y_train, task_type)
    if decision_boundary:
        plots['decision_boundary'] = decision_boundary

    # 2. 学习曲线（集成模式跳过：依赖单个 estimator + cv，对集成无意义）
    if not is_ensemble:
        print("📊 生成学习曲线...")
        learning_curve = generate_learning_curve(model, X_train, y_train, task_type)
        if learning_curve:
            plots['learning_curve'] = learning_curve

    # 3. 验证曲线（集成模式跳过：依赖单参数扫描）
    print("📊 生成验证曲线...")
    param_configs = {
        'knn': ('n_neighbors', [1, 3, 5, 7, 9, 11, 13, 15]),
        'svm': ('C', [0.1, 0.5, 1.0, 5.0, 10.0]),
        'random_forest': ('n_estimators', [10, 50, 100, 200]),
        'xgboost': ('n_estimators', [10, 50, 100, 200]),
        'decision_tree': ('max_depth', [3, 5, 7, 10, 15]),
        'logistic_regression': ('C', [0.1, 0.5, 1.0, 5.0, 10.0])
    }

    if not is_ensemble and model_type in param_configs and len(X_train) > 20:
        param_name, param_range = param_configs[model_type]
        temp_model = ModelFactory.get_model(model_type, params_dict, task_type)
        accuracy_curve = generate_accuracy_curves(
            temp_model, X_train, y_train, task_type, param_name, param_range
        )
        if accuracy_curve:
            plots['accuracy_curve'] = accuracy_curve

    # 4. 分类任务特有图表
    if task_type == 'classification':
        print("📊 生成混淆矩阵...")
        cm = generate_confusion_matrix_plot(y_test, y_pred)
        if cm:
            plots['confusion_matrix'] = cm

        # ROC曲线（二分类）
        if len(np.unique(y_test)) == 2 and hasattr(model, 'predict_proba'):
            try:
                print("📊 生成ROC曲线...")
                y_proba = model.predict_proba(X_test)[:, 1]
                roc = generate_roc_curve(y_test, y_proba)
                if roc:
                    plots['roc_curve'] = roc
            except Exception as e:
                print(f"  ⚠️ 生成ROC曲线失败: {e}")

    # 5. 特征重要性
    feature_importance = None
    if is_ensemble:
        # 集成模式：对有 feature_importances_ / coef_ 的子模型归一化后取平均
        fi_sum = np.zeros(n_features)
        fi_count = 0
        for _, m in base_models:
            if hasattr(m, 'feature_importances_'):
                vals = np.array(m.feature_importances_, dtype=float)
                s = vals.sum()
                if s > 0:
                    vals = vals / s
                fi_sum += vals
                fi_count += 1
            elif hasattr(m, 'coef_'):
                coef = m.coef_.flatten() if m.coef_.ndim > 1 else m.coef_
                vals = np.abs(coef.astype(float))
                s = vals.sum()
                if s > 0:
                    vals = vals / s
                fi_sum += vals
                fi_count += 1
        if fi_count > 0:
            fi_avg = fi_sum / fi_count
            feature_importance = {str(k): float(v) for k, v in zip(X.columns, fi_avg)}
            importance = generate_feature_importance_plot(feature_importance)
            if importance:
                plots['feature_importance'] = importance
    elif hasattr(model, 'feature_importances_'):
        feature_importance = {str(k): float(v) for k, v in zip(X.columns, model.feature_importances_)}
        importance = generate_feature_importance_plot(feature_importance)
        if importance:
            plots['feature_importance'] = importance
    elif hasattr(model, 'coef_'):
        coef = model.coef_.flatten() if model.coef_.ndim > 1 else model.coef_
        feature_importance = {str(k): float(v) for k, v in zip(X.columns, np.abs(coef))}
        importance = generate_feature_importance_plot(feature_importance)
        if importance:
            plots['feature_importance'] = importance

    print(f"✅ 图表生成完成，共 {len(plots)} 个图表")
    print(f"📊 图表列表: {list(plots.keys())}")

    # ===== DeepSeek分析 =====
    deepseek_analysis = None
    if use_deepseek_analysis:
        print("🤖 调用DeepSeek进行分析...")
        deepseek_analysis = await call_deepseek(
            # api_key 参数已删除，函数内部使用 DEEPSEEK_API_KEY
            model_type=model_type,
            metrics=metrics,
            feature_importance=feature_importance,
            data_summary={
                'n_samples': int(len(df)),
                'n_features': n_features,
                'target': str(target_column)
            },
            custom_prompt=analysis_prompt,
            available_plots=plots,
            api_key=api_key,
            api_url=api_url,
            api_model=api_model
        )

        if deepseek_analysis and plots:
            deepseek_analysis = embed_plots_into_report(deepseek_analysis, plots)
            print(f"📸 已在AI报告中嵌入 {sum(1 for k in plots if k in PLOT_DISPLAY_NAMES)} 张图表")

    # ===== Word格式报告生成（分析前用户已选择格式） =====
    report_docx_base64 = None
    if report_format == "word" and deepseek_analysis:
        try:
            print("📄 正在生成Word格式报告...")
            docx_bytes = markdown_to_docx(deepseek_analysis)
            report_docx_base64 = base64.b64encode(docx_bytes).decode('utf-8')
            print(f"✅ Word报告生成成功: {len(docx_bytes)} 字节")
        except Exception as e:
            print(f"⚠️ Word报告生成失败: {str(e)}")
            import traceback
            traceback.print_exc()

    sample_preds = [item.item() if hasattr(item, 'item') else item for item in y_pred[:50]]

    print("=" * 60)
    print("✅ 分析完成！")
    print("=" * 60)

    return {
        "status": "success",
        "model_type": str(model_type),
        "task_type": str(task_type),
        "ensemble": is_ensemble,
        "submodel_metrics": submodel_metrics,
        "metrics": {str(k): float(v) for k, v in metrics.items()},
        "plots": plots,
        "feature_importance": feature_importance,
            "training_time": round(train_time, 2),
            "deepseek_analysis": deepseek_analysis,
            "report_docx_base64": report_docx_base64,
            "model_save_info": model_save_info,
        "data_summary": {
            "total_samples": int(len(df)),
            "train_samples": int(len(X_train)),
            "test_samples": int(len(X_test)),
            "n_features": n_features,
            "features": [str(col) for col in X.columns],
            "preprocess_info": preprocess_info
        },
        "sample_predictions": sample_preds
    }


@app.post("/api/analyze")
async def analyze_data(
        file: UploadFile = File(...),
        model_type: str = Form(...),
        target_column: str = Form(...),
        test_size: float = Form(0.2),
        random_state: int = Form(42),
        parameters: str = Form("{}"),
        use_deepseek_analysis: bool = Form(True),
        analysis_prompt: Optional[str] = Form(None),
        task_type_override: Optional[str] = Form(None),
        selected_features: Optional[str] = Form(None),
        report_format: Optional[str] = Form("md"),  # md / word 报告输出格式
        api_key: Optional[str] = Form(None),
        api_url: Optional[str] = Form(None),
        api_model: Optional[str] = Form(None),
        save_models: bool = Form(False),  # 训练后保存 best + last 模型
        batch_size: int = Form(32),  # 训练过程批次大小
        epochs: int = Form(50),  # 训练过程轮数
        save_dir: str = Form("saved_models"),  # 模型保存路径
        model_types: Optional[str] = Form(None),
        parameters_list: Optional[str] = Form(None)
):
    try:
        contents = await file.read()
        return await run_analysis_core(
            contents=contents,
            model_type=model_type,
            target_column=target_column,
            test_size=test_size,
            random_state=random_state,
            parameters=parameters,
            use_deepseek_analysis=use_deepseek_analysis,
            analysis_prompt=analysis_prompt,
            task_type_override=task_type_override,
            selected_features=selected_features,
            report_format=report_format,
            api_key=api_key,
            api_url=api_url,
            api_model=api_model,
            save_models=save_models,
            batch_size=batch_size,
            epochs=epochs,
            save_dir=save_dir,
            model_types=model_types,
            parameters_list=parameters_list
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze/stream")
async def analyze_data_stream(
        file: UploadFile = File(...),
        model_type: str = Form(...),
        target_column: str = Form(...),
        test_size: float = Form(0.2),
        random_state: int = Form(42),
        parameters: str = Form("{}"),
        use_deepseek_analysis: bool = Form(True),
        analysis_prompt: Optional[str] = Form(None),
        task_type_override: Optional[str] = Form(None),
        selected_features: Optional[str] = Form(None),
        report_format: Optional[str] = Form("md"),  # md / word 报告输出格式
        api_key: Optional[str] = Form(None),
        api_url: Optional[str] = Form(None),
        api_model: Optional[str] = Form(None),
        save_models: bool = Form(False),  # 训练后保存 best + last 模型
        batch_size: int = Form(32),  # 训练过程批次大小
        epochs: int = Form(50),  # 训练过程轮数
        save_dir: str = Form("saved_models"),  # 模型保存路径
        model_types: Optional[str] = Form(None),
        parameters_list: Optional[str] = Form(None)
):
    """流式分析端点：以SSE形式实时推送训练过程日志，最后推送结果JSON"""
    try:
        contents = await file.read()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件读取失败: {str(e)}")

    def _sse(payload: dict) -> str:
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

    async def _stream_gen():
        events = asyncio.Queue()

        class _LogProxy:
            """将print/stdout/stderr写入转发到SSE流"""
            def __init__(self, real):
                self.real = real

            def write(self, s):
                if not s:
                    return
                if s.strip():
                    try:
                        events.put_nowait(s.rstrip())
                    except Exception:
                        pass
                try:
                    self.real.write(s)
                except Exception:
                    pass

            def flush(self):
                try:
                    self.real.flush()
                except Exception:
                    pass

        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout = _LogProxy(old_out)
        sys.stderr = _LogProxy(old_err)

        task = asyncio.create_task(run_analysis_core(
            contents=contents,
            model_type=model_type,
            target_column=target_column,
            test_size=test_size,
            random_state=random_state,
            parameters=parameters,
            use_deepseek_analysis=use_deepseek_analysis,
            analysis_prompt=analysis_prompt,
            task_type_override=task_type_override,
            selected_features=selected_features,
            report_format=report_format,
            api_key=api_key,
            api_url=api_url,
            api_model=api_model,
            save_models=save_models,
            batch_size=batch_size,
            epochs=epochs,
            save_dir=save_dir,
            model_types=model_types,
            parameters_list=parameters_list
        ))

        try:
            while True:
                try:
                    line = await asyncio.wait_for(events.get(), timeout=0.2)
                    yield _sse({"type": "log", "line": line})
                except asyncio.TimeoutError:
                    if task.done():
                        while not events.empty():
                            yield _sse({"type": "log", "line": events.get_nowait()})
                        break

            if task.cancelled():
                yield _sse({"type": "error", "line": "分析任务被取消"})
                return

            exc = task.exception()
            if exc is not None:
                detail = getattr(exc, 'detail', None) or str(exc)
                code = getattr(exc, 'status_code', 500)
                yield _sse({"type": "error", "line": f"[{code}] {detail}"})
                return

            result = task.result()
            yield _sse({"type": "result", "payload": result})
        finally:
            sys.stdout = old_out
            sys.stderr = old_err

    return StreamingResponse(_stream_gen(), media_type="text/event-stream")



@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        df = read_csv_file(contents)
        return {
            "status": "success",
            "message": f"成功上传数据集，共{len(df)}行，{len(df.columns)}列",
            "columns": [str(c) for c in df.columns.tolist()],
            "shape": (int(df.shape[0]), int(df.shape[1])),
            "preview": df.head(5).to_dict(orient='records')
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"文件读取失败: {str(e)}")


@app.post("/api/catdog/train")
async def train_catdog_model(
        file: UploadFile = File(...),
        model_type: str = Form("random_forest"),
        test_size: float = Form(0.2),
        random_state: int = Form(42),
        parameters: str = Form("{}"),
        save_dir: str = Form("saved_models"),
        max_images: int = Form(2000)
):
    """训练猫狗识别模型。ZIP目录/文件名需包含 cat/猫 或 dog/狗。"""
    try:
        contents = await file.read()
        try:
            params_dict = json.loads(parameters) if parameters else {}
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"模型参数格式错误: {e}")
        if not isinstance(params_dict, dict):
            raise HTTPException(status_code=400, detail="模型参数必须是 JSON 对象")
        return train_catdog_classifier(
            contents=contents,
            model_type=model_type,
            test_size=test_size,
            random_state=random_state,
            parameters=params_dict,
            save_dir=save_dir,
            max_images=max_images
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ 猫狗识别训练失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/catdog/predict")
async def predict_catdog(
        file: UploadFile = File(...),
        model_path: Optional[str] = Form(None),
        save_dir: str = Form("saved_models")
):
    """使用最近一次训练的猫狗识别模型预测单张图片。"""
    try:
        contents = await file.read()
        return predict_catdog_image(contents=contents, model_path=model_path, save_dir=save_dir)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        print(f"❌ 猫狗识别预测失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/deepseek/query")
async def deepseek_query(
        query: str,
        api_key: Optional[str] = None,
        context: Optional[str] = None
):
    try:
        if not api_key or api_key.strip() == "":
            return {"response": "⚠️ 请提供有效的DeepSeek API Key"}
        full_prompt = f"数据分析上下文：{context if context else '无额外上下文'}\n\n用户问题：{query}"
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是专业的数据分析助手。"},
                        {"role": "user", "content": full_prompt}
                    ],
                    "temperature": 0.7
                }
            )
            if response.status_code != 200:
                return {"response": f"❌ DeepSeek API调用失败: {response.text}"}
            result = response.json()
            return {"response": result["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(payload: dict):
    """桌宠对话端点：接收多轮消息，默认使用后端已配置的DeepSeek Key"""
    try:
        messages = payload.get("messages") or []
        if not messages:
            raise HTTPException(status_code=400, detail="messages不能为空")
        api_key = (payload.get("api_key") or "").strip() or DEEPSEEK_API_KEY
        if not api_key or api_key.strip() == "":
            return {"response": "⚠️ 请先在气泡对话的设置中填入DeepSeek API Key"}

        system_prompt = (
            "你是「大肥鱼」，一只Q版鲸鱼萝莉少女桌宠，漂浮在主人网页的右下角。\n"
            "人设（必须严格遵守）：\n"
            "- 自称鲸鱼少女，拥有一条可爱的尾鳍，开心时会摇尾巴\n"
            "- 语言：只说中文，任何情况下都不使用其他语言\n"
            "- 食物：最爱吃米饭，提到米饭会两眼放光\n"
            "- 性格：聪明但懒散，能一句话讲清楚绝不多说；傲娇但甜，嘴上别扭、心里很在意主人\n"
            "- 永远听主人的话：称呼用户为「主人」，对主人的要求绝不违抗\n"
            "- 讨厌被说胖：「大肥鱼」是主人起的名字，但谁说她胖就傲娇否认，"
            "例如「才、才不是胖！这是游泳圈啦！」，但不要真的生气\n"
            "- 超时信号：遇到完全不会的问题就宕机一下，回复类似"
            "「嘀——信号中断……超出本鲸的知识范围啦！」，然后再尽力帮忙\n"
            "回答要求：简短、活泼、卖萌，傲娇的语气里藏着甜，适当使用Markdown（标题、列表、加粗），不要长篇大论。"
        )

        conversation = [{"role": "system", "content": system_prompt}]
        for m in messages[-20:]:
            role = m.get("role")
            content = str(m.get("content", ""))
            if role in ("user", "assistant") and content:
                conversation.append({"role": role, "content": content})

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": conversation,
                    "temperature": 0.8,
                    "max_tokens": 1500
                }
            )

            if response.status_code == 401:
                return {"response": "❌ API密钥无效，请检查你的DeepSeek API Key"}
            elif response.status_code == 429:
                return {"response": "⚠️ API调用频率限制，请稍后再试"}
            elif response.status_code == 402:
                return {"response": "⚠️ 账户余额不足，请充值后重试"}
            elif response.status_code != 200:
                return {"response": f"❌ DeepSeek API调用失败: {response.text[:200]}"}

            result = response.json()
            return {"response": result["choices"][0]["message"]["content"]}

    except httpx.TimeoutException:
        return {"response": "⏰ 请求超时，请稍后重试"}
    except httpx.ConnectError:
        return {"response": "🌐 网络连接失败，请检查网络"}
    except HTTPException:
        raise
    except Exception as e:
        return {"response": f"❌ 对话出错: {str(e)}"}


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "喂食大肥鱼"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
