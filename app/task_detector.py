# task_detector.py - 任务类型检测器 + 模型支持字典
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional

# ===== 统一模型支持字典（前后端共用） =====
MODEL_SUPPORT = {
    "knn": {"classification", "regression"},
    "svm": {"classification", "regression"},
    "linear_regression": {"regression"},
    "random_forest": {"classification", "regression"},
    "xgboost": {"classification", "regression"},
    "decision_tree": {"classification", "regression"},
    "logistic_regression": {"classification"}
}

MODEL_NAMES = {
    "knn": "KNN (K近邻)",
    "svm": "SVM (支持向量机)",
    "linear_regression": "线性回归",
    "random_forest": "随机森林",
    "xgboost": "XGBoost",
    "decision_tree": "决策树",
    "logistic_regression": "逻辑回归"
}

MODEL_INFO = {
    "knn": {
        "type": "both",
        "description": "KNN对数据缩放敏感，建议标准化特征。适合小数据集。",
        "advice": "💡 建议尝试不同的K值，使用交叉验证选择最优K。",
        "pros": "✅ 简单易懂，无需训练，适合多分类问题",
        "cons": "❌ 计算量大，对特征缩放敏感，维度灾难"
    },
    "svm": {
        "type": "both",
        "description": "SVM在高维空间表现好，核函数选择影响大。适合非线性问题。",
        "advice": "💡 尝试不同的核函数和C值，使用网格搜索调参。",
        "pros": "✅ 在高维空间表现优秀，核函数灵活",
        "cons": "❌ 对参数敏感，大数据集训练慢，不直接支持多分类"
    },
    "linear_regression": {
        "type": "regression",
        "description": "线性回归简单可解释，适合线性关系。需要满足线性假设。",
        "advice": "💡 检查残差是否满足正态性，考虑添加交互项。",
        "pros": "✅ 简单高效，可解释性强，训练快速",
        "cons": "❌ 只能处理线性关系，对异常值敏感"
    },
    "random_forest": {
        "type": "both",
        "description": "随机森林不易过拟合，能处理非线性关系。特征重要性可解释。",
        "advice": "💡 增加树的数量可提高稳定性，控制最大深度防过拟合。",
        "pros": "✅ 不易过拟合，能处理高维数据，提供特征重要性",
        "cons": "❌ 模型较大，训练慢，可解释性不如单棵树"
    },
    "xgboost": {
        "type": "both",
        "description": "XGBoost性能强大，但调参复杂。适合结构化数据。",
        "advice": "💡 调整学习率和树的数量，早停法防止过拟合。",
        "pros": "✅ 性能强大，支持GPU加速，处理缺失值",
        "cons": "❌ 调参复杂，容易过拟合，内存消耗大"
    },
    "decision_tree": {
        "type": "both",
        "description": "决策树可解释性强，但容易过拟合。建议剪枝。",
        "advice": "💡 限制最大深度，增加最小分裂样本数防过拟合。",
        "pros": "✅ 可解释性强，无需特征缩放，可处理混合数据",
        "cons": "❌ 容易过拟合，不稳定，对数据微小变化敏感"
    },
    "logistic_regression": {
        "type": "classification",
        "description": "逻辑回归用于分类，可解释性好。适合基线模型。",
        "advice": "💡 处理类别不平衡，使用正则化防止过拟合。",
        "pros": "✅ 简单高效，可解释性强，输出概率值",
        "cons": "❌ 只能处理线性可分问题，对异常值敏感"
    }
}


class TaskTypeDetector:
    """任务类型自动检测器（前后端完全一致）"""

    def __init__(self,
                 unique_threshold: int = 15,
                 ratio_threshold: float = 0.5,
                 min_samples: int = 10):
        self.unique_threshold = unique_threshold
        self.ratio_threshold = ratio_threshold
        self.min_samples = min_samples

    def detect(self, y: pd.Series) -> Tuple[str, Dict[str, Any]]:
        """
        检测任务类型
        返回: (任务类型, 检测详情)
        """
        total_count = len(y)
        unique_count = y.nunique()
        unique_ratio = unique_count / total_count if total_count > 0 else 0
        dtype = str(y.dtype)
        is_numeric = pd.api.types.is_numeric_dtype(y)

        task_type = None
        confidence = 0.0
        reasons = []

        # 1. 检查样本数量
        if total_count < self.min_samples:
            task_type = "unknown"
            reasons.append(f"样本数量不足 ({total_count} < {self.min_samples})")
            confidence = 0.0
            return task_type, self._build_details(y, task_type, confidence, reasons)

        # 2. 基于数据类型判断
        if is_numeric:
            reasons.append(f"数据类型: 数值型 ({dtype})")

            if unique_count <= self.unique_threshold and unique_ratio < self.ratio_threshold:
                task_type = "classification"
                confidence = 0.9
                reasons.append(f"唯一值少 ({unique_count}个) → 分类任务")
            else:
                task_type = "regression"
                confidence = 0.9
                reasons.append(f"唯一值多 ({unique_count}个) → 回归任务")
            return task_type, self._build_details(y, task_type, confidence, reasons)

        else:
            # 非数值类型
            reasons.append(f"数据类型: 非数值型 ({dtype})")

            # 尝试转换为数值
            try:
                y_numeric = pd.to_numeric(y, errors='coerce')
                valid_ratio = y_numeric.notna().sum() / total_count
                if valid_ratio > 0.8:
                    reasons.append(f"可转换为数值型 ({valid_ratio:.1%})，重新检测")
                    return self.detect(y_numeric)
            except:
                pass

            # 作为分类处理
            if unique_count <= self.unique_threshold:
                task_type = "classification"
                confidence = 0.8
                reasons.append(f"类别少 ({unique_count}个) → 分类任务")
            else:
                task_type = "classification"
                confidence = 0.5
                reasons.append("文本型数据 → 默认分类任务")

            return task_type, self._build_details(y, task_type, confidence, reasons)

    def _build_details(self, y, task_type, confidence, reasons) -> Dict[str, Any]:
        return {
            'task_type': task_type,
            'confidence': confidence,
            'reasons': reasons,
            'statistics': {
                'total_samples': len(y),
                'unique_values': y.nunique(),
                'unique_ratio': y.nunique() / len(y) if len(y) > 0 else 0,
                'dtype': str(y.dtype),
                'is_numeric': pd.api.types.is_numeric_dtype(y)
            },
            'sample_values': y.head(10).tolist()
        }

    def get_task_type_name(self, task_type: str) -> str:
        mapping = {
            'classification': '分类任务',
            'regression': '回归任务',
            'unknown': '未知任务'
        }
        return mapping.get(task_type, task_type)

    def get_task_type_icon(self, task_type: str) -> str:
        mapping = {
            'classification': '📊',
            'regression': '📈',
            'unknown': '❓'
        }
        return mapping.get(task_type, '❓')

    def get_recommended_models(self, task_type: str, max_models: int = 5) -> list:
        models = {
            'classification': [
                {'name': '逻辑回归', 'description': '适合基线模型，可解释性强'},
                {'name': '决策树', 'description': '可解释性强，适合小数据集'},
                {'name': '随机森林', 'description': '准确率高，不易过拟合'},
                {'name': 'XGBoost', 'description': '性能强大，适合竞赛'},
                {'name': 'SVM', 'description': '适合高维数据'},
                {'name': 'KNN', 'description': '简单直观，适合小数据集'}
            ],
            'regression': [
                {'name': '线性回归', 'description': '简单可解释，适合线性关系'},
                {'name': '决策树回归', 'description': '可解释性强，适合非线性'},
                {'name': '随机森林回归', 'description': '准确率高，不易过拟合'},
                {'name': 'XGBoost回归', 'description': '性能强大'},
                {'name': 'SVR', 'description': '适合非线性关系'},
                {'name': 'KNN回归', 'description': '简单直观'}
            ]
        }
        return models.get(task_type, [])[:max_models]