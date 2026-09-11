# 喂食大肥鱼 ver2.0 技术文档

## 1. 文档说明

本文档依据当前项目源码、配置文件和容器编排文件整理，描述系统的实际功能、技术架构、运行方式、接口契约、数据处理流程和已知注意事项。

- 项目名称：喂食大肥鱼
- 当前版本标识：`1.0.0`（后端 FastAPI 应用在 `app/main.py` 中声明）
- 文档适用范围：本地 Windows 启动、Linux/Docker 部署、功能维护和接口调用
- 主要入口：`app/main.py`、`app/streamlit_app.py`
- 主要访问地址：前端 `http://localhost:8501`，API `http://localhost:8000`

> 说明：项目目录中包含 `.venv`、`__pycache__`、IDE 配置和已训练模型。本文档只关注运行所需源码、依赖、资源和部署文件。

## 2. 系统概述

“喂食大肥鱼”是一个面向交互式机器学习分析的 Web 应用，使用 Streamlit 提供蓝白主题的可视化界面，并由 FastAPI 提供数据分析 API。系统将 CSV 数据集“投喂”给桌宠角色“大肥鱼”，完成任务类型识别、特征预处理、模型训练、模型评估、图表生成和可选的 AI 分析报告。

系统还提供独立的猫狗图像识别页面：用户上传带有猫狗标签的 ZIP 训练集，系统从图片中提取轻量级颜色、降采样和边缘特征，训练传统机器学习分类器；训练完成后可以上传单张图片进行预测。

核心能力如下：

1. CSV 数据集上传、预览和编码兼容读取。
2. 自动或手动识别分类任务、回归任务。
3. 支持 KNN、SVM、线性回归、随机森林、XGBoost、决策树和逻辑回归。
4. 支持单模型分析和多模型集成分析。
5. 自动生成决策边界、学习曲线、验证曲线、混淆矩阵、ROC 曲线和特征重要性图。
6. 可调用 DeepSeek 或兼容 OpenAI Chat Completions 格式的接口生成中文分析报告。
7. 支持 Markdown 报告和 Word 文档报告导出。
8. 可选保存 `best` 和 `last` 两份传统机器学习模型及元数据。
9. 支持猫狗图片分类训练与单图预测。
10. 提供可拖动鲸鱼桌宠、对话、数据集抽屉、白饭投喂、好感度和新手教程等交互功能。

## 3. 总体架构

```text
浏览器
  |
  | HTTP/WebSocket-like Streamlit interaction
  v
Streamlit 前端 :8501
  |-- CSV 上传、模型配置、结果展示
  |-- 猫狗 ZIP/图片上传
  |-- 桌宠 iframe 注入与 localStorage 状态
  |
  | HTTP multipart/form-data / JSON
  v
FastAPI 后端 :8000
  |-- 数据读取与预处理
  |-- scikit-learn/XGBoost 模型训练
  |-- 指标和 Base64 图表生成
  |-- 模型序列化
  |-- DeepSeek HTTP 调用
  |-- Word 报告转换
  v
本地文件系统 / Docker volume
  |-- saved_models
  |-- data
  |-- results
  |
外部服务：DeepSeek Chat Completions API（可选）
```

### 3.1 服务职责

| 服务 | 实现 | 默认端口 | 职责 |
| --- | --- | ---: | --- |
| 前端 | Streamlit | 8501 | 页面渲染、参数收集、训练进度展示、结果下载、桌宠注入 |
| 后端 | FastAPI + Uvicorn | 8000 | 文件接收、机器学习流水线、图表、模型保存、AI 调用 |
| AI 服务 | DeepSeek Chat Completions | HTTPS | 生成分析报告和桌宠对话回复 |

### 3.2 请求方式

- 文件上传接口使用 `multipart/form-data`。
- 普通分析接口返回完整 JSON。
- 流式分析接口使用 Server-Sent Events（SSE），每条事件格式为 `data: {JSON}\n\n`。
- 桌宠对话使用 JSON 请求体。
- 图表以 Base64 PNG 字符串嵌入响应，报告中的图表也可以以内嵌 Data URI 形式出现。

## 4. 目录结构

```text
喂食大肥鱼 ver2.0/
├─ app/
│  ├─ main.py                  # FastAPI 应用、分析引擎、接口和图表
│  ├─ streamlit_app.py         # Streamlit 主页面和前端交互
│  ├─ task_detector.py         # 任务类型检测和模型能力字典
│  ├─ catdog_classifier.py     # 猫狗图片特征、训练、保存和预测
│  ├─ pet_component.py         # 桌宠 HTML/CSS/JavaScript 注入组件
│  ├─ requirements.txt         # Python 依赖和版本
│  ├─ start.sh                 # Linux/Docker 双服务启动脚本
│  └─ saved_models/            # 训练产物；目录可能包含历史模型
├─ deepseekchan/               # 桌宠、教程、上传按钮等图片和视频资源
├─ docker/
│  ├─ Dockerfile.api           # 后端镜像
│  └─ Dockerfile.frontend      # 前端镜像
├─ docker-compose.yml          # API 和前端双容器编排
├─ Start Up.bat                # Windows 交互式服务管理脚本
└─ TECHNICAL_DOCUMENTATION.md  # 本技术文档
```

### 4.1 代码模块职责

#### `app/main.py`

后端核心文件，包含：

- FastAPI 实例和 CORS 配置。
- `ModelFactory`：按模型名称和任务类型实例化模型。
- `AnalysisEngine`：数据预处理、指标计算和模型评估。
- 集成预测器：分类多数投票、回归均值融合。
- 图表生成函数和 Markdown/Word 报告转换器。
- DeepSeek 调用函数。
- CSV、数据分析、猫狗训练/预测、对话和健康检查 API。

#### `app/streamlit_app.py`

前端主程序。Streamlit 每次交互会重新执行脚本，因此大量使用 `st.session_state` 保存数据集、目标列、分析结果、训练日志、聊天记录和页面状态。

主要页面：

- “数据集分析”：CSV 上传、目标列选择、特征选择、任务类型、模型参数和分析结果。
- “图像识别”：猫狗 ZIP 训练、单图预测和识别结果展示。

#### `app/task_detector.py`

前后端共用的任务类型判断逻辑和模型字典，避免前端显示的可用模型与后端校验不一致。

#### `app/catdog_classifier.py`

猫狗图像分类的完整业务模块，包括 ZIP 文件名标签推断、图像特征化、模型训练、模型保存、最新模型查找和单图预测。

#### `app/pet_component.py`

通过 `streamlit.components.v1.html` 向浏览器父页面注入 HTML、CSS 和 JavaScript。除桌宠动画和气泡外，还包含拖动、对话、数据集抽屉、白饭小游戏、好感度、换装和新手教程逻辑。

## 5. 本地运行

### 5.1 环境要求

- Python：依赖锁定文件面向 Python 3.10；当前源码也应优先使用 Python 3.10。
- 操作系统：Windows、Linux 或 macOS；Windows 可使用项目自带批处理脚本。
- 浏览器：现代 Chromium、Firefox 或 Edge。
- 运行分析需要足够内存；XGBoost、大规模图片数据和 Base64 图表会增加内存占用。
- 若使用 AI 报告或桌宠云端对话，需要可访问 DeepSeek 或兼容接口。

### 5.2 Windows 启动

双击 `Start Up.bat`，选择：

- `1`：启动后端和前端。
- `2`：停止服务，并清理 8000/8501 端口进程。
- `3`：重启服务。
- `4`：检查端口状态。
- `5`：按 `app/requirements.txt` 安装依赖。
- `6`：删除 Python 字节码和 Streamlit 缓存。

脚本启动成功后访问：

- 前端：`http://localhost:8501`
- Swagger/OpenAPI：`http://localhost:8000/docs`
- 健康检查：`http://localhost:8000/api/health`

脚本当前通过系统 `python` 和 `pip` 调用，不会自动激活项目中的 `.venv`。如果机器上有多个 Python，建议先激活目标虚拟环境，或直接手动执行：

```powershell
cd "项目目录\app"
python -m pip install -r requirements.txt
python main.py
```

另开一个终端启动前端：

```powershell
cd "项目目录\app"
python -m streamlit run streamlit_app.py
```

### 5.3 Linux 启动

```bash
cd "项目目录/app"
python3 -m pip install -r requirements.txt
bash start.sh
```

`start.sh` 会安装依赖、后台启动 `python main.py` 和 Streamlit，并等待两个进程。生产环境不建议每次启动都在线安装依赖，建议提前构建虚拟环境或使用 Docker。

## 6. Docker 部署

### 6.1 启动

在项目根目录执行：

```bash
```

访问：

- 前端：`http://localhost:8501`
- API：`http://localhost:8000/docs`

停止：

```bash
```

### 6.2 容器配置

`docker-compose.yml` 定义两个服务：

- `api`：构建 `docker/Dockerfile.api`，暴露 8000，挂载 `data`、`results`、`saved_models`。
- `frontend`：构建 `docker/Dockerfile.frontend`，暴露 8501，通过 `API_BASE_URL=http://api:8000` 调用后端，并挂载 `saved_models`。

两个服务加入 `analytics-network` bridge 网络。API 容器健康检查请求 `/api/health`，前端健康检查请求 `/_stcore/health`。

### 6.3 Docker 环境变量

```text
DEEPSEEK_API_KEY=你的密钥
```

compose 中 API 服务支持从宿主环境读取 `DEEPSEEK_API_KEY`。前端通过 `API_BASE_URL` 指向 API 容器。前端源码中的分析请求目前仍有一处使用 `http://localhost:8000/api/analyze/stream` 的固定地址；在容器网络或非本机浏览器场景下，建议维护时统一改为 `_api_base_url()` 返回的地址。

## 7. 数据集分析功能

### 7.1 用户流程

1. 打开“数据集分析”页面。
2. 上传一个 CSV 文件。
3. 前端按 UTF-8、UTF-8-SIG、GB18030、GBK、GB2312、CP936、Latin-1 等编码尝试读取。
4. 选择目标列和特征列。
5. 选择自动检测、分类任务或回归任务。
6. 选择单模型或集成模式并调整参数。
7. 设置测试集比例、训练轮数和批次大小。
8. 可选启用 DeepSeek、模型保存和 Word 报告。
9. 点击“执行分析”。
10. 前端显示模拟训练曲线，同时连接 `/api/analyze/stream` 接收后端日志。
11. 后端完成训练、评估、图表生成和可选 AI 报告后返回结果。
12. 前端展示指标、图表、报告、日志和 JSON 下载按钮。

### 7.2 任务类型检测

`TaskTypeDetector` 使用以下规则：

- 样本数少于 10：返回 `unknown`。
- 数值目标列且唯一值不超过 15、唯一值比例小于 0.5：分类，置信度 0.9。
- 其他数值目标列：回归，置信度 0.9。
- 非数值列如果超过 80% 可转换为数值，会重新按数值规则检测。
- 不能转换的非数值列默认分类；唯一值不超过 15 时置信度 0.8，否则置信度 0.5。

自动检测只是启发式判断。计数、评分、离散编码和低基数连续变量可能被误判，用户可以在侧边栏手动覆盖任务类型。

### 7.3 数据预处理

后端 `AnalysisEngine.preprocess_data` 的处理顺序如下：

1. 检查目标列存在且数据集非空。
2. 对字符串目标列尝试删除非数字字符并转换为数值；有效比例大于 80% 时采用转换结果。
3. 删除含缺失值的行。
4. 去除目标列得到特征矩阵 `X`，并应用用户选择的特征子集。
5. 自动检测或使用手动任务类型。
6. 回归任务将目标列转换为数值；转换比例不足时降级为分类。
7. 分类目标使用 `LabelEncoder` 编码为非负整数。
8. 特征列按数值列和类别列划分。非数值列如果有超过 70% 的值可转数字，会被视为数值列。
9. 类别列使用 `LabelEncoder` 编码；只有一个唯一值的列会删除。
10. 数值列缺失值使用均值填充，然后使用 `StandardScaler` 标准化。
11. 最终尝试把所有列转换为数值，失败时再次标签编码，仍失败则置为 0。

预处理结果会返回列类型、特征数、样本数、类别编码信息和最终任务类型。当前保存的 `label_encoders` 只保存类别列表，并没有保存可直接用于线上新样本转换的完整预处理 Pipeline；模型复用时需要额外实现一致的特征处理。

### 7.4 支持的模型

| 标识 | 中文名 | 分类 | 回归 | 主要默认参数 |
| --- | --- | :---: | :---: | --- |
| `knn` | KNN | 是 | 是 | `n_neighbors=5` |
| `svm` | SVM/SVR | 是 | 是 | 分类 `kernel=rbf,C=1,probability=True` |
| `linear_regression` | 线性回归 | 否 | 是 | 无特殊参数 |
| `random_forest` | 随机森林 | 是 | 是 | `n_estimators=100,random_state=42` |
| `xgboost` | XGBoost | 是 | 是 | `n_estimators=100,random_state=42` |
| `decision_tree` | 决策树 | 是 | 是 | `random_state=42` |
| `logistic_regression` | 逻辑回归 | 是 | 否 | `max_iter=1000,random_state=42` |

模型参数由前端 JSON 传给后端，并与默认参数合并。`batch_size` 和 `epochs` 仅在模型参数中确实存在同名参数时才设置；上述 scikit-learn 模型通常不会使用这两个参数。因此前端显示的训练轮数和批次大小主要用于训练动画和结果元数据，不代表传统模型真的按 epoch/batch 训练。

### 7.5 单模型训练

后端先执行 `train_test_split`。分类任务在每类至少有两个样本时使用分层抽样。模型在训练集上拟合，然后在测试集上预测并计算指标。

### 7.6 集成训练

当 `model_types` 至少包含两个模型时进入集成模式：

- 分类：多个模型的预测结果逐样本多数投票。
- 回归：多个模型的预测结果按样本取平均。
- 每个子模型都会单独训练和评估，并在 `submodel_metrics` 中返回指标。
- 集成模式跳过学习曲线和验证曲线，因为这两类图表依赖单一 estimator 或单一参数扫描。
- 能提供 `feature_importances_` 或 `coef_` 的子模型，其重要性归一化后求平均。

## 8. 指标和图表

### 8.1 分类指标

- `accuracy`：准确率。
- `precision`：二分类使用 binary，多分类使用 weighted 平均。
- `recall`：二分类使用 binary，多分类使用 weighted 平均。
- `f1_score`：二分类使用 binary，多分类使用 weighted 平均。

### 8.2 回归指标

- `mse`：均方误差。
- `rmse`：均方根误差。
- `mae`：平均绝对误差。
- `r2_score`：决定系数。

### 8.3 自动图表

图表会保存为内存中的 PNG，并转换为 Base64 字符串，不会单独写入图片文件。

| 键 | 生成条件 | 内容 |
| --- | --- | --- |
| `decision_boundary` | 样本不少于 10 且特征不少于 2 | PCA 降至二维后绘制分类区域或回归等高线 |
| `learning_curve` | 非集成且交叉验证可用 | 训练样本数与训练/验证得分关系 |
| `accuracy_curve` | 非集成、样本数大于 20、模型有参数配置 | 扫描指定超参数的验证曲线 |
| `confusion_matrix` | 分类任务 | 测试集混淆矩阵热图 |
| `roc_curve` | 二分类且模型提供 `predict_proba` | ROC 和 AUC |
| `feature_importance` | 模型提供 `feature_importances_` 或 `coef_` | Top 15 特征重要性 |

决策边界图仅是 PCA 投影后的解释性可视化，不等价于原始高维空间的真实决策边界。

## 9. 模型保存

启用“保存模型”后，单模型模式会创建类似以下目录：

```text
app/saved_models/analysis_YYYYMMDD_HHMMSS/
├─ model_best.pkl
├─ model_last.pkl
└─ model_info.json
```

- `model_last.pkl`：当前请求直接训练完成的模型。
- `model_best.pkl`：通过最多若干个随机种子候选和交叉验证得分选出的模型，再在训练集上最终拟合。
- `model_info.json`：模型类型、任务类型、目标列、特征、指标、预处理摘要、保存时间和训练参数。

模型保存的“best”只在当前训练集和当前参数配置内比较，不是跨数据集的全局最优模型。集成模式不会进入 `best/last` 保存逻辑。

## 10. DeepSeek 集成与报告

### 10.1 分析报告

`call_deepseek` 使用 Chat Completions 请求格式：

- 默认模型：`deepseek-chat`。
- 默认超时：30 秒。
- 温度：0.7。
- 最大 token：2000。
- system 消息：专业数据分析专家。
- user 消息：模型信息、指标、数据概况、特征重要性、图表占位符和用户提示词。

如果 AI 在正文插入 `{{决策边界图}}` 等占位符，后端会替换成 Base64 图片 HTML；没有被正文使用的图表会追加到“相关图表附录”。

### 10.2 Word 报告

选择 Word 格式后，后端使用 `python-docx` 将 Markdown 报告转换成 `.docx`，支持：

- 标题、普通段落、粗体、斜体和代码样式。
- Markdown 列表。
- Markdown 表格及表头底色。
- Base64 内嵌图片。

生成的 Word 文件以 Base64 放在响应字段 `report_docx_base64` 中，由前端生成下载按钮。

### 10.3 桌宠对话

`/api/chat` 接收最近最多 20 条用户/助手消息，并添加“大肥鱼”人设 system prompt。前端主页面通常发送最近 12 条消息。桌宠要求只使用中文、称呼用户为“主人”、保持简短傲娇的鲸鱼少女语气。

## 11. 猫狗图像识别

### 11.1 训练集要求

上传 ZIP 内的图片必须满足以下任一条件：

- 位于名为 `cat`、`cats`、`猫` 的目录，表示猫。
- 位于名为 `dog`、`dogs`、`狗` 的目录，表示狗。
- 文件名中包含上述标签关键词。

支持格式：`.jpg`、`.jpeg`、`.png`、`.bmp`、`.webp`。默认最多读取 2000 张，可在前端调整。

### 11.2 特征提取

每张图片执行：

1. EXIF 方向校正、转 RGB、缩放到 `64 x 64`。
2. 归一化到 `[0, 1]`。
3. 按 `4 x 4` 区域池化，得到紧凑颜色特征。
4. 对三个颜色通道分别计算 16-bin 颜色直方图。
5. 计算灰度图的横向、纵向差分和边缘强度直方图。
6. 拼接为供传统机器学习模型使用的一维特征向量。

该实现不是 CNN 或迁移学习模型，优点是轻量、无需 GPU，缺点是对复杂姿态、背景和域变化的泛化能力有限。

### 11.3 训练与预测

支持 `random_forest`、`svm`、`logistic_regression` 和 `knn`。训练后保存：

```text
app/saved_models/catdog_YYYYMMDD_HHMMSS/
├─ catdog_model.pkl
└─ catdog_model_info.json
```

单图预测如果不传 `model_path`，会自动查找 `saved_models` 下最新修改的猫狗模型。返回预测类别、标签、置信度、类别概率、模型路径和图片 Base64 预览。

## 12. 桌宠功能与前端状态

桌宠由 `pet_component.py` 注入父页面，主要功能包括：

- 可拖动鲸鱼悬浮球和气泡菜单。
- 预设短对话和 DeepSeek 对话。
- 记忆桌宠位置、米饭库存和好感度。
- 白饭制作、拖动投喂桌宠、上传区域或页面图片。
- 数据集抽屉：数据预览、列信息、直方图、箱线图、目标关系、相关性热图和任务类型检测。
- 新手教程、封面、换装和“接米饭”小游戏。

浏览器 `localStorage` 使用若干键保存状态，例如：

- `ffp_rice_count`：白饭库存。
- `ffp_favor`：好感度。
- `ffp_rice_pos`：白饭悬浮球位置。
- `ffp_chat_main` / `ffp_chat_catdog`：不同页面的桌宠聊天记录。

桌宠与 Streamlit 主页面之间通过特殊哨兵文本通信，例如 `[[FFP_FEED]]token:index`。前端脚本将哨兵写入 Streamlit 输入框并触发提交，Streamlit 识别后生成投喂台词，不将哨兵作为正常用户消息发送给 AI。

## 13. API 参考

### 13.1 `GET /api/health`

健康检查。

响应示例：

```json
{"status":"healthy","service":"喂食大肥鱼"}
```

### 13.2 `POST /api/upload`

上传 CSV 并返回数据集摘要，不执行模型训练。

请求：`multipart/form-data`，字段 `file`。

响应字段：

- `status`
- `message`
- `columns`
- `shape`：`[行数, 列数]`
- `preview`：前 5 行记录

### 13.3 `POST /api/analyze`

执行完整分析并一次性返回结果。

必填字段：

- `file`：CSV 文件。
- `model_type`：模型标识。
- `target_column`：目标列名。

常用可选字段：

| 字段 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `test_size` | float | 0.2 | 测试集比例，必须大于 0 且小于 1 |
| `random_state` | int | 42 | 随机种子 |
| `parameters` | JSON 字符串 | `{}` | 单模型参数对象 |
| `use_deepseek_analysis` | bool | true | 是否生成 AI 报告 |
| `analysis_prompt` | string | null | 自定义分析要求 |
| `task_type_override` | string | null | `classification` 或 `regression` |
| `selected_features` | JSON 字符串 | null | 特征名数组 |
| `report_format` | string | `md` | `md` 或 `word` |
| `api_key` | string | null | AI API Key |
| `api_url` | string | null | Chat Completions 地址 |
| `api_model` | string | null | 模型名称 |
| `save_models` | bool | false | 是否保存模型 |
| `batch_size` | int | 32 | 训练过程参数/元数据 |
| `epochs` | int | 50 | 训练过程参数/元数据 |
| `save_dir` | string | `saved_models` | 模型保存目录 |
| `model_types` | JSON 字符串 | null | 至少两个模型时进入集成 |
| `parameters_list` | JSON 字符串 | null | 与 `model_types` 一一对应的参数数组 |

成功响应主要字段：

```json
{
  "status": "success",
  "model_type": "random_forest",
  "task_type": "classification",
  "ensemble": false,
  "submodel_metrics": [],
  "metrics": {},
  "plots": {},
  "feature_importance": {},
  "training_time": 0.0,
  "deepseek_analysis": null,
  "report_docx_base64": null,
  "model_save_info": null,
  "data_summary": {},
  "sample_predictions": []
}
```

### 13.4 `POST /api/analyze/stream`

参数与 `/api/analyze` 相同，响应媒体类型为 `text/event-stream`。

事件类型：

- `log`：`{"type":"log","line":"..."}`，转发后端标准输出日志。
- `error`：`{"type":"error","line":"..."}`。
- `result`：`{"type":"result","payload":{完整分析结果}}`。

### 13.5 `POST /api/catdog/train`

训练猫狗识别模型。

- `file`：ZIP 文件。
- `model_type`：`random_forest`、`svm`、`logistic_regression` 或 `knn`。
- `test_size`：测试集比例。
- `random_state`：随机种子。
- `parameters`：JSON 对象字符串。
- `save_dir`：保存目录。
- `max_images`：最多处理图片数。

### 13.6 `POST /api/catdog/predict`

使用猫狗模型预测单张图片。

- `file`：图片文件。
- `model_path`：可选，指定模型路径。
- `save_dir`：未指定模型路径时用于查找最新模型。

### 13.7 `POST /api/deepseek/query`

通用数据分析问答接口。

请求参数：`query`、可选 `api_key`、可选 `context`。此接口使用后端固定的 DeepSeek URL 和 `deepseek-chat` 模型。

### 13.8 `POST /api/chat`

桌宠多轮对话接口。

JSON 请求体：

```json
{
  "messages": [
    {"role":"user","content":"帮我解释准确率"},
    {"role":"assistant","content":"准确率是预测正确的比例哦"}
  ],
  "api_key": "可选"
}
```

服务会过滤非 `user`/`assistant` 角色消息，并只取最近 20 条。

## 14. 错误处理和故障排查

### 服务无法启动

- 检查 Python 版本和 `requirements.txt` 是否安装完成。
- 检查 8000、8501 端口是否被占用。
- Windows 使用启动菜单中的“检查状态”。
- Docker 使用 `docker compose logs api` 和 `docker compose logs frontend`。

### CSV 读取失败

- 确认文件确实是逗号分隔的 CSV。
- 检查列名是否包含目标列。
- 重新保存为 UTF-8 或 GB18030 编码。
- 检查文件是否为空、是否只有表头。

### 任务类型错误

- 样本数至少需要 10 条才能通过自动检测。
- 目标列为数值但唯一值很少时，可能被识别为分类。
- 在侧边栏手动指定分类或回归。

### 训练失败

- 检查所选模型是否支持当前任务类型。
- 分类任务需要足够的各类别样本，尤其是分层切分和交叉验证场景。
- 检查类别列、目标列和特征列清洗后是否还有可用值。
- KNN 的 `n_neighbors` 不应大于训练样本数。
- SVM、XGBoost 可能因参数或数据规模消耗较多时间和内存。

### 没有图表

图表函数对样本数、特征数、二分类条件和模型能力有约束。后端会捕获单个图表生成异常，不会因此终止整个分析；应优先查看训练终端日志。

### DeepSeek 调用失败

- 检查 API Key、API URL 和模型名称。
- 401：密钥无效。
- 402：账户余额不足。
- 429：请求频率受限。
- 超时或连接失败：检查网络和代理配置。
- 关闭 DeepSeek 后仍可执行模型训练、指标和图表分析。

### 猫狗识别没有识别到图片

- 检查 ZIP 内目录或文件名是否包含 `cat`/`dog`/`猫`/`狗`。
- 检查图片扩展名是否受支持。
- 检查 ZIP 是否损坏或图片内容无法被 Pillow 解码。
- 训练集必须同时包含猫和狗两类。

## 15. 安全与生产部署注意事项

以下事项是根据当前源码直接确认的风险或运维注意点，正式部署前应处理：

1. `app/main.py` 和 `app/streamlit_app.py` 当前存在硬编码的 DeepSeek API Key。该密钥不应继续保留在源码、镜像或版本库中，建议立即吊销并改为环境变量或仅由用户会话输入。
2. FastAPI CORS 当前允许任意来源、任意方法和任意请求头。生产环境应限制为实际前端域名，并重新评估 `allow_credentials=True` 与通配来源组合。
3. 模型保存路径由请求字段 `save_dir` 参与构造，生产环境应限制为允许的根目录，防止任意路径写入。
4. `joblib.load` 会反序列化 Python 对象，只能加载可信模型文件，不要让不可信用户上传或指定模型路径。
5. 上传文件没有在 API 层设置明确大小、压缩包解压数量或资源消耗限制。应增加 CSV/ZIP/图片大小限制、ZIP 炸弹防护和超时控制。
6. AI Key 会通过前端表单传给后端。应避免在日志、错误信息、浏览器历史和持久化状态中暴露密钥，并在反向代理层启用 HTTPS。
7. Docker 前端配置关闭了 XSRF 保护，且允许外部访问。仅适用于受信任的内网或演示环境，公网部署前需重新配置认证、CSRF 和反向代理。
8. `/api/chat`、`/api/deepseek/query` 和分析接口没有用户认证、限流或配额控制，公网暴露可能导致 API Key 滥用和计算资源耗尽。
9. 报告以 HTML/Markdown 形式渲染，AI 输出被前端以 `unsafe_allow_html=True` 展示。若接入不可信提示词或外部模型，应增加 Markdown/HTML 清洗。
10. 生产部署应使用固定的秘密管理方案、日志脱敏、HTTPS、身份认证和资源配额。

## 16. 测试建议

当前项目未发现独立的自动化测试目录。建议至少补充以下测试：

- `TaskTypeDetector`：空数据、少量样本、低基数数值、高基数数值、字符串数字和普通文本。
- CSV 编码读取：UTF-8、UTF-8-SIG、GBK、GB18030。
- 预处理：缺失值、常量列、类别列、目标列转换失败和特征选择。
- 每个模型在分类和回归任务下的支持校验。
- 集成分类多数投票和回归平均值。
- 图表生成在小样本和单特征场景下应优雅返回空结果。
- 猫狗 ZIP 标签推断、中文压缩包文件名、损坏图片和缺失类别。
- `/api/analyze/stream` 的 SSE `log`、`error`、`result` 事件顺序。
- Word 报告中的标题、表格和 Base64 图片转换。
- API Key 不应出现在日志、错误响应和提交记录中。

## 17. 后续维护建议

1. 将 DeepSeek 配置统一迁移到环境变量，并删除源码中的真实密钥。
2. 将数据预处理封装为可序列化的 sklearn Pipeline，与模型一起保存。
3. 将 `streamlit_app.py` 中固定的 API 地址统一替换为 `API_BASE_URL`。
4. 将模型参数校验改为 Pydantic schema，避免任意参数直接传入 estimator。
5. 将分析任务放入后台任务队列，避免同步请求长期占用 Web 请求线程。
6. 对大图表和 AI 报告增加大小上限，必要时改为对象存储或文件下载 URL。
7. 为 API 增加认证、限流、上传限制和审计日志。
8. 将桌宠巨型内嵌 HTML/JavaScript 拆分为独立静态资源，降低 `pet_component.py` 的维护成本。
9. 为猫狗识别增加真实数据增强、标准化和更强的视觉模型选项，并在报告中区分轻量特征模型和深度学习模型。

## 18. 版本与依赖清单

当前 `app/requirements.txt` 锁定的主要依赖：

| 依赖 | 版本 | 用途 |
| --- | --- | --- |
| FastAPI | 0.104.1 | 后端 API |
| Uvicorn | 0.24.0 | ASGI 服务 |
| pandas | 2.1.3 | 表格数据处理 |
| NumPy | 1.26.2 | 数值计算 |
| scikit-learn | 1.3.2 | 传统机器学习、指标和交叉验证 |
| XGBoost | 2.0.2 | 梯度提升模型 |
| Streamlit | 1.29.0 | Web 前端 |
| Plotly | 5.18.0 | 前端训练过程图表 |
| httpx | 0.25.2 | 异步 HTTP 和 DeepSeek 调用 |
| python-multipart | 0.0.6 | FastAPI 文件/表单解析 |
| Pydantic | 2.5.0 | FastAPI 数据模型依赖 |
| python-docx | 1.2.0 | Word 报告生成 |
| Pillow | 10.1.0 | 图片读取和预处理 |

源码还直接使用了 `matplotlib`、`seaborn`、`joblib`、`chardet` 等包，但它们目前没有全部显式列在 `requirements.txt` 中。部署前建议补齐直接依赖并重新验证全新环境安装。
