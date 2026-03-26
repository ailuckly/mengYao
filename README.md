# 基于YOLOv11的家庭园艺植物识别系统

## 项目简介

本项目面向家庭园艺场景，完成常见家庭绿植类别识别、典型叶部病害与异常辅助识别，以及识别结果可视化展示。系统采用 `YOLOv11` 作为核心检测模型，后端基于 `Flask` 实现，前端采用多页面 Web 形式组织识别、历史记录、知识库和模型分析等模块。

## 项目结构

```text
MengYao/
├── backend/                 后端接口、推理服务与工具模块
├── frontend/                多页面模板、样式与前端脚本
├── model/
│   ├── configs/             类别映射、数据集配置
│   ├── checkpoints/         模型权重
│   ├── scripts/             训练、预测、数据处理脚本
│   └── exports/             训练导出结果
├── data/
│   ├── raw/                 原始公开数据
│   ├── processed/           中间整理结果
│   ├── annotations/         标注相关文件
│   └── splits/              最终训练集划分
├── docs/
│   ├── proposal/            开题报告
│   ├── analysis/            需求分析、训练结果分析
│   └── design/              总体设计、详细设计、测试方案等
├── notebooks/               Colab 训练 notebook
├── records/                 上传图、预测图、日志、本地历史记录数据库
├── tests/                   基础测试
└── README.md
```

## 核心功能

- 植物图片上传
- 家庭园艺植物类别识别
- 典型叶部病害与异常辅助识别
- 检测框结果图展示
- 基础养护建议返回
- SQLite 历史记录管理
- 植物与病害知识库展示
- 模型训练结果分析页面

## 页面结构

- `/` 首页
- `/detect` 识别页
- `/history` 历史记录页
- `/knowledge` 知识库页
- `/analysis` 模型分析页

## 模型结果

项目当前采用 `YOLOv11s` 训练结果作为默认演示模型，主要实验结果如下：

- 模型：`YOLOv11s`
- 最佳 epoch：`83`
- mAP50：`0.7279`
- mAP50-95：`0.6754`

分析文档见：

- `docs/analysis/模型训练结果分析.md`

## 启动方式

安装依赖：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

启动系统：

```bash
python -m backend.app
```

浏览器访问：

```text
http://127.0.0.1:5000
```

## 部署与迁移说明

### 1. 本地部署

在一台新的 Linux 或 macOS 设备上部署本项目时，建议按以下顺序执行：

1. 获取项目代码

```bash
git clone <your-repo-url>
cd MengYao
```

2. 创建虚拟环境并安装依赖

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. 检查关键文件

默认情况下，系统启动前建议确认以下文件存在：

- `model/checkpoints/best.pt`：正式推理模型权重
- `model/configs/label_advice.json`：类别与知识库配置
- `model/configs/training_summary.json`：模型分析页摘要配置
- `frontend/static/images/analysis/`：训练曲线图与混淆矩阵图

其中，`best.pt` 是真实模型推理的关键文件。如果该文件不存在，系统仍可启动，但会自动退回占位推理模式，仅用于流程演示。

4. 启动服务

```bash
python -m backend.app
```

5. 浏览器访问

```text
http://127.0.0.1:5000
```

系统首次启动时会自动完成以下初始化动作：

- 创建 `records/uploads/`
- 创建 `records/predictions/`
- 创建 `records/logs/`
- 初始化本地 SQLite 数据库 `records/app.db`

因此，新环境冷启动时不需要额外执行数据库迁移脚本。

### 2. 冷启动部署与历史迁移的区别

本项目支持两种部署方式：

#### 2.1 冷启动部署

如果只是希望在新机器上把系统跑起来，不要求保留旧识别记录，那么只需要：

- 保留项目代码
- 安装依赖
- 放入 `model/checkpoints/best.pt`
- 启动系统

这种方式下，系统会自动新建一个空的 `records/app.db`，历史记录从空状态开始。

#### 2.2 带历史记录的迁移部署

如果希望把旧环境中的识别历史、原图和结果图一起迁移到新机器，则必须成套复制以下内容：

- `records/app.db`
- `records/uploads/`
- `records/predictions/`

原因是：数据库中的历史记录保存了原图路径和结果图路径，如果只迁移 `app.db` 而不迁移图片目录，历史详情页将无法正常显示原图和结果图。

建议同时复制：

- `records/logs/`：如需保留运行日志
- `model/checkpoints/best.pt`：如需保持与旧环境一致的正式模型

### 3. 推荐迁移步骤

若从旧机器迁移到新机器，推荐按以下顺序进行：

1. 在新机器上完成项目代码同步和依赖安装
2. 暂不启动服务，先复制旧环境中的运行文件
3. 将以下文件和目录覆盖到新环境对应位置：

```text
model/checkpoints/best.pt
records/app.db
records/uploads/
records/predictions/
records/logs/        （可选）
frontend/static/images/analysis/   （如需保留分析页图表）
```

4. 启动服务：

```bash
python -m backend.app
```

5. 启动后检查以下页面：

- `/detect`：确认模型能正常推理
- `/history`：确认历史记录可见
- `/history/<id>`：确认原图和结果图能正常加载
- `/analysis`：确认训练曲线图和混淆矩阵图可见

### 4. 迁移后的检查项

迁移完成后，建议至少检查以下内容：

- `GET /health` 返回 `model_loaded=true` 时，说明真实模型加载成功
- 首页与识别页能正常打开
- 上传一张图片后可返回识别结果
- 历史记录页能看到旧记录或新生成记录
- 知识库页和模型分析页没有资源缺失

如果 `/health` 返回模型未加载，通常说明：

- `model/checkpoints/best.pt` 未复制到位
- `ultralytics` 依赖未安装成功
- 新环境的 Python 依赖不完整

### 5. 不建议直接迁移的内容

以下内容不建议作为“必须迁移项”处理：

- `data/raw/`
- `data/processed/`
- `data/annotations/`
- `data/splits/`
- `model/exports/`

这些目录主要用于训练和实验过程，不是系统运行的必要条件。若目标只是部署演示系统，可以不迁移上述训练中间数据，以减少迁移体积。

### 6. 建议的最小运行集

若只考虑“让系统在新机器正常运行”的最小文件集合，建议至少保留：

```text
backend/
frontend/
model/configs/
model/checkpoints/best.pt
requirements.txt
records/    （可为空，由系统自动初始化）
```

若还要保留历史记录和分析展示，则再额外保留：

```text
records/app.db
records/uploads/
records/predictions/
frontend/static/images/analysis/
```

## 测试方式

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

## 运行说明

- 默认模型权重：`model/checkpoints/best.pt`
- 本地历史记录数据库：`records/app.db`
- 若模型权重不存在，系统会退回占位推理模式，以保证页面流程仍可演示
