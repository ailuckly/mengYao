# 模型目录说明

## 目录用途

- `configs/`：保存类别配置、建议映射、数据集 yaml 配置。
- `checkpoints/`：保存训练完成后的模型权重。
- `scripts/`：保存训练脚本和命令行预测脚本。
- `exports/`：保存训练运行输出和导出模型。

## 训练前准备

1. 按 `data/README.md` 整理数据目录。
2. 根据真实类别修改 `model/configs/dataset.example.yaml`。
3. 将数据划分结果放到 `data/splits/train`、`data/splits/val`、`data/splits/test` 下。
4. 安装 `requirements.txt` 中的依赖。
5. 先阅读 `model/configs/final_class_mapping.json` 和 `docs/design/最终类别设计.md`，确认最终训练类别。

## 训练命令示例

```bash
python model/scripts/train.py \
  --data model/configs/dataset.example.yaml \
  --weights yolo11n.pt \
  --epochs 100 \
  --batch 16
```

## 预测命令示例

```bash
python model/scripts/predict.py \
  --source records/uploads/example.jpg \
  --weights model/checkpoints/best.pt \
  --save
```

## 数据整理脚本

当前已补充三类数据准备脚本：

- `prepare_indoor_yolo_dataset.py`
  将室内植物分类图转换为单主体 YOLO 检测格式。

- `prepare_plantdoc_disease_dataset.py`
  将 PlantDoc 的细粒度病害标签过滤并重映射为项目最终病害类别。

- `prepare_final_dataset.py`
  将植物类和病害类整理结果合并为最终训练集，并生成训练用 yaml。
