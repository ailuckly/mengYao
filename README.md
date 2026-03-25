# 基于YOLOv11的家庭园艺植物识别系统

## 项目目录说明

```text
MengYao/
├── docs/
│   ├── source/
│   │   ├── official/
│   │   └── templates/
│   ├── proposal/
│   ├── planning/
│   ├── analysis/
│   └── design/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── annotations/
│   ├── splits/
│   └── README.md
├── model/
│   ├── configs/
│   ├── checkpoints/
│   ├── scripts/
│   ├── exports/
│   └── README.md
├── backend/
│   ├── routes/
│   ├── services/
│   ├── inference/
│   └── utils/
├── frontend/
│   ├── templates/
│   └── static/
├── notebooks/
├── tests/
├── records/
│   ├── uploads/
│   ├── predictions/
│   └── logs/
└── README.md
```

## 文档分类

- `docs/source/official/`
  学校原始文档、任务书、开题报告模板等正式材料。

- `docs/source/templates/`
  学校模板压缩包及解压后的模板目录。

- `docs/proposal/`
  开题报告相关文档。

- `docs/planning/`
  项目实现规划、实施计划等过程文档。

- `docs/analysis/`
  系统需求分析类文档。

- `docs/design/`
  系统总体设计、后续详细设计类文档。

- `tests/`
  接口和基础链路测试代码。

- `docs/planning/Google Colab训练操作手册.md`
  Colab 云端训练的完整操作说明。

- `notebooks/`
  可直接在 Colab 中打开的训练 notebook。

## 后续开发建议

1. 先补充 `docs/design/` 下的详细设计文档。
2. 再开始 `data/` 下的数据整理与标注。
3. 模型训练相关内容统一放在 `model/`。
4. 后端接口和推理服务写在 `backend/`。
5. 页面模板和静态资源写在 `frontend/`。
6. 运行过程中的上传图片、结果图和日志保存在 `records/`。

## 当前已实现内容

- 文档部分已完成开题报告、项目实现规划、系统需求分析、系统总体设计，以及后续说明书写作计划、详细设计、测试方案等基础文档。
- 代码部分已完成 Flask + H5 的最小系统骨架，可用于打通上传、识别、结果展示流程。
- 当前项目已整理出一版可用的真实模型权重，本地放在 `model/checkpoints/best.pt`，系统默认会优先加载该权重进行真实推理。
- 模型部分已补充训练脚本、预测脚本、Colab 训练 notebook、数据集配置样例和训练结果分析文档。

## 当前最佳训练结果

- 训练批次：`colab_pro_formal_v13`
- 使用模型：`YOLOv11s`
- 最佳 epoch：`83`
- mAP50：`0.7279`
- mAP50-95：`0.6754`

详细分析见：

- `docs/analysis/模型训练结果分析.md`

## 启动方式

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 启动系统：

```bash
python -m backend.app
```

3. 浏览器访问：

```text
http://127.0.0.1:5000
```

## 测试方式

```bash
python -m unittest discover -s tests -p 'test_*.py'
```
