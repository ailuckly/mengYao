# 数据目录说明

## 目录结构

```text
data/
├── raw/
│   ├── archives/
│   └── public/
├── processed/
├── annotations/
└── splits/
    ├── train/
    │   ├── images/
    │   └── labels/
    ├── val/
    │   ├── images/
    │   └── labels/
    └── test/
        ├── images/
        └── labels/
```

## 使用约定

- `raw/archives/`：原始压缩包归档目录。
- `raw/public/`：公开数据集解压后的原始目录。
- `processed/`：清洗和重命名后的图片。
- `annotations/`：原始标注文件或导出中间文件。
- `splits/`：最终供 YOLO 训练使用的数据划分目录。

## 当前已下载的公开数据

目前已整理入库的公开数据如下：

- `raw/public/plantdoc_classification/`
  PlantDoc 原始分类版数据，适合做类别参考和后续筛选。

- `raw/public/plantdoc_yolo_v2_100x100/`
  已整理好的 YOLO 格式 PlantDoc 数据，当前最适合优先查看和后续作为检测训练基线。

- `raw/public/plant_leaf_diseases_augmented/`
  增强版叶片病害分类数据，适合作为病害补充，不建议直接当主训练集。

- `raw/public/indoor_augmented_plants/`
  增强版室内植物分类数据，适合作为植物类别补充，不建议直接当主训练集。

## 当前使用建议

现阶段建议优先处理：

1. `plantdoc_yolo_v2_100x100`
2. `plantdoc_classification`

暂时先不要直接把下面两套并入训练主集：

1. `plant_leaf_diseases_augmented`
2. `indoor_augmented_plants`

原因是它们都带有明显增强痕迹，适合补充，不适合直接做主数据源。

## 标注格式

YOLO 标注文件采用 `.txt` 格式，每行对应一个目标：

```text
class_id x_center y_center width height
```

所有坐标均使用归一化数值。

## 命名建议

- 图片文件名统一使用英文或拼音，不使用空格。
- 同一类别使用统一前缀，便于后期统计。
- 病害图片建议在文件名中保留病害类型关键词。
