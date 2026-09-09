import base64
import io
import json
import os
import time
import zipfile
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC


CATDOG_CLASS_NAMES = {0: "猫", 1: "狗"}
CATDOG_LABEL_KEYWORDS = {
    "cat": 0,
    "cats": 0,
    "猫": 0,
    "dog": 1,
    "dogs": 1,
    "狗": 1,
}
SUPPORTED_IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


def _resolve_dir(save_dir: str) -> str:
    base_dir = save_dir or "saved_models"
    if not os.path.isabs(base_dir):
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), base_dir)
    return base_dir


def _fix_zip_name(name: str) -> str:
    """还原 Windows 压缩工具按 GBK 存储的中文条目名（zipfile 默认按 cp437 解码会产生乱码）。"""
    try:
        return name.encode('cp437').decode('gbk')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return name


def _infer_label(path: str) -> Optional[int]:
    parts = [p.lower() for p in path.replace("\\", "/").split("/") if p]
    for part in parts[:-1]:
        clean = part.strip().lower()
        if clean in CATDOG_LABEL_KEYWORDS:
            return CATDOG_LABEL_KEYWORDS[clean]
    filename = parts[-1] if parts else path.lower()
    for key, label in CATDOG_LABEL_KEYWORDS.items():
        if key in filename:
            return label
    return None


def image_bytes_to_features(contents: bytes, image_size: Tuple[int, int] = (64, 64)) -> np.ndarray:
    """Convert one image into compact color + edge features for lightweight ML models."""
    with Image.open(io.BytesIO(contents)) as img:
        img = ImageOps.exif_transpose(img).convert("RGB").resize(image_size)
        arr = np.asarray(img, dtype=np.float32) / 255.0
        gray = arr.mean(axis=2)
        gx = np.diff(gray, axis=1, append=gray[:, -1:])
        gy = np.diff(gray, axis=0, append=gray[-1:, :])
        edge = np.sqrt(gx * gx + gy * gy)

        pooled = arr.reshape(16, 4, 16, 4, 3).mean(axis=(1, 3)).ravel()
        color_hist = []
        for ch in range(3):
            hist, _ = np.histogram(arr[:, :, ch], bins=16, range=(0.0, 1.0), density=True)
            color_hist.extend(hist.astype(np.float32))
        edge_hist, _ = np.histogram(edge, bins=16, range=(0.0, max(0.2, float(edge.max()))), density=True)
        return np.concatenate([pooled, np.asarray(color_hist, dtype=np.float32), edge_hist.astype(np.float32)])


def load_catdog_zip(contents: bytes, max_images: int = 2000) -> Tuple[np.ndarray, np.ndarray, Dict[str, int], List[str]]:
    X, y, label_counts, skipped = [], [], {"猫": 0, "狗": 0}, []
    with zipfile.ZipFile(io.BytesIO(contents)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(SUPPORTED_IMAGE_SUFFIXES) and not n.endswith("/")]
        for name in names[:max_images]:
            fixed_name = _fix_zip_name(name)
            label = _infer_label(fixed_name)
            if label is None:
                skipped.append(fixed_name)
                continue
            try:
                img_bytes = zf.read(name)
                X.append(image_bytes_to_features(img_bytes))
                y.append(label)
                label_counts[CATDOG_CLASS_NAMES[label]] += 1
            except (UnidentifiedImageError, OSError, ValueError):
                skipped.append(fixed_name)
    if not X:
        raise ValueError("未在ZIP中识别到猫狗图片。请使用 cat/猫 和 dog/狗 文件夹，或文件名包含 cat/dog。")
    return np.vstack(X), np.asarray(y, dtype=int), label_counts, skipped


def make_catdog_model(model_type: str, params: Optional[Dict] = None):
    params = params or {}
    if model_type == "svm":
        defaults = {"C": 2.0, "kernel": "rbf", "probability": True, "random_state": 42}
        defaults.update(params)
        return SVC(**defaults)
    if model_type == "knn":
        defaults = {"n_neighbors": 5}
        defaults.update(params)
        return KNeighborsClassifier(**defaults)
    if model_type == "logistic_regression":
        defaults = {"C": 1.0, "max_iter": 1000, "random_state": 42}
        defaults.update(params)
        return LogisticRegression(**defaults)
    defaults = {"n_estimators": 160, "max_depth": None, "random_state": 42, "n_jobs": -1}
    defaults.update(params)
    return RandomForestClassifier(**defaults)


def save_catdog_model(model, info: Dict, save_dir: str = "saved_models") -> str:
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(_resolve_dir(save_dir), f"catdog_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)
    model_path = os.path.join(out_dir, "catdog_model.pkl")
    joblib.dump(model, model_path)
    info.update({
        "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model_file": os.path.basename(model_path),
    })
    with open(os.path.join(out_dir, "catdog_model_info.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    return out_dir


def find_latest_catdog_model(save_dir: str = "saved_models") -> Optional[str]:
    base_dir = _resolve_dir(save_dir)
    if not os.path.isdir(base_dir):
        return None
    candidates = []
    for name in os.listdir(base_dir):
        model_path = os.path.join(base_dir, name, "catdog_model.pkl")
        if name.startswith("catdog_") and os.path.isfile(model_path):
            candidates.append((os.path.getmtime(model_path), model_path))
    if not candidates:
        return None
    return sorted(candidates, reverse=True)[0][1]


def train_catdog_classifier(contents: bytes, model_type: str = "random_forest", test_size: float = 0.2,
                            random_state: int = 42, parameters: Optional[Dict] = None,
                            save_dir: str = "saved_models", max_images: int = 2000) -> Dict:
    if not 0 < test_size < 1:
        raise ValueError("test_size 必须介于 0 和 1 之间")
    X, y, label_counts, skipped = load_catdog_zip(contents, max_images=max_images)
    if len(set(y.tolist())) < 2:
        raise ValueError("训练集必须同时包含猫和狗两类图片")
    stratify = y if min(np.bincount(y)) >= 2 else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=stratify
    )
    model = make_catdog_model(model_type, parameters)
    start = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start
    y_pred = model.predict(X_test)
    metrics = {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
    }
    cm = confusion_matrix(y_test, y_pred, labels=[0, 1]).tolist()
    info = {
        "model_type": model_type,
        "task_type": "catdog_image_classification",
        "classes": CATDOG_CLASS_NAMES,
        "total_images": int(len(y)),
        "train_images": int(len(y_train)),
        "test_images": int(len(y_test)),
        "label_counts": label_counts,
        "skipped_images": int(len(skipped)),
        "metrics": metrics,
    }
    out_dir = save_catdog_model(model, info, save_dir=save_dir)
    return {
        "status": "success",
        "model_type": model_type,
        "task_type": "catdog_image_classification",
        "metrics": metrics,
        "confusion_matrix": cm,
        "label_counts": label_counts,
        "total_images": int(len(y)),
        "train_images": int(len(y_train)),
        "test_images": int(len(y_test)),
        "skipped_images": int(len(skipped)),
        "training_time": round(train_time, 2),
        "model_save_info": {
            "save_dir": out_dir,
            "model_file": "catdog_model.pkl",
            "saved_at": info["saved_at"],
        },
    }


def predict_catdog_image(contents: bytes, model_path: Optional[str] = None, save_dir: str = "saved_models") -> Dict:
    path = model_path or find_latest_catdog_model(save_dir=save_dir)
    if not path or not os.path.isfile(path):
        raise FileNotFoundError("未找到猫狗识别模型，请先上传训练ZIP并完成训练")
    model = joblib.load(path)
    X = image_bytes_to_features(contents).reshape(1, -1)
    pred = int(model.predict(X)[0])
    confidence = None
    probabilities = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)[0]
        classes = [int(c) for c in model.classes_]
        probabilities = {CATDOG_CLASS_NAMES[c]: float(proba[i]) for i, c in enumerate(classes)}
        confidence = float(max(proba))
    return {
        "status": "success",
        "prediction": CATDOG_CLASS_NAMES[pred],
        "prediction_label": pred,
        "confidence": confidence,
        "probabilities": probabilities,
        "model_path": path,
        "image_preview": base64.b64encode(contents).decode("utf-8"),
    }
