# Google Colab 训练操作手册

## 1. 目标

本手册用于把当前项目迁移到 Google Colab 上运行 YOLOv11 训练，并支持在免费 Colab 中断后继续训练。

当前项目已经准备好的关键内容如下：

- 最终训练集：`data/splits/final_v1`
- 训练配置：`model/configs/final_dataset_v1.yaml`
- 训练脚本：`model/scripts/train.py`
- 断点续训支持：`--resume --resume-path`
- Colab notebook：`notebooks/colab_resume_train.ipynb`

## 2. 推荐使用方式

建议使用下面这种结构：

- `GitHub` 保存项目代码
- `Google Drive` 保存数据集 zip 和训练输出
- `Colab /content/workspace` 作为运行目录

这样即使 Colab 会话断开，代码重新拉一遍即可，数据和权重不会丢。

## 3. 需要提前准备的内容

### 3.1 代码仓库

把当前项目最新代码 push 到 GitHub 仓库，例如：

```text
https://github.com/ailuckly/mengYao.git
```

### 3.2 数据集压缩包

在项目根目录执行：

```bash
python model/scripts/package_dataset_for_colab.py
```

生成文件：

```text
model/exports/colab/final_dataset_v1_bundle.zip
```

### 3.3 上传到 Google Drive

建议在 Google Drive 中建立一个目录，例如：

```text
MyDrive/MengYao_Colab/
```

然后把下面这个文件上传进去：

- `final_dataset_v1_bundle.zip`

训练得到的 `best.pt`、`last.pt` 和训练目录也保存在这个目录下面。

## 4. Colab 中的完整流程

### 4.1 新建 Notebook 并切换 GPU

在 Colab 中打开：

`Runtime -> Change runtime type -> GPU`

### 4.2 验证 GPU

```python
!nvidia-smi
```

### 4.3 挂载 Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

### 4.4 拉取项目代码

```python
!mkdir -p /content/workspace
!git clone --depth 1 https://github.com/ailuckly/mengYao.git /content/workspace/project
%cd /content/workspace/project
```

### 4.5 解压数据集

```python
!unzip -q /content/drive/MyDrive/MengYao_Colab/final_dataset_v1_bundle.zip -d /content/workspace/project
```

### 4.6 安装依赖

```python
!pip install -q -r requirements.txt
```

### 4.7 生成 Colab 专用数据配置

```python
%%writefile /content/workspace/project/model/configs/final_dataset_v1_colab.yaml
path: /content/workspace/project/data/splits/final_v1
train: train/images
val: val/images
test: test/images

names:
  0: 银皇后类
  1: 网纹凤梨类
  2: 绿萝类
  3: 心叶蔓绿绒类
  4: Rhaphidophora类
  5: 金钱树类
  6: 叶斑类病害
  7: 枯萎/疫病类病害
  8: 白粉/霉变类病害
  9: 黄化/锈病/虫害类异常
```

### 4.8 启动正式训练

训练输出建议直接写到 Google Drive：

```python
!python model/scripts/train.py \
  --data /content/workspace/project/model/configs/final_dataset_v1_colab.yaml \
  --weights yolo11s.pt \
  --device 0 \
  --epochs 100 \
  --batch 32 \
  --imgsz 640 \
  --optimizer auto \
  --patience 30 \
  --workers 4 \
  --save-period 10 \
  --close-mosaic 10 \
  --seed 42 \
  --cos-lr \
  --project /content/drive/MyDrive/MengYao_Colab/train_runs \
  --name colab_pro_formal_v1
```

## 5. 断点续训

如果免费 Colab 因运行时长上限中断，重新打开一个会话后，仍然按第 4 节重新执行到依赖安装和 yaml 生成，然后直接续训：

```python
!python model/scripts/train.py \
  --resume \
  --resume-path /content/drive/MyDrive/MengYao_Colab/train_runs/colab_pro_formal_v1/weights/last.pt
```

## 6. 结果检查

训练后可在 Drive 中查看：

```python
!find /content/drive/MyDrive/MengYao_Colab/train_runs -name best.pt
!find /content/drive/MyDrive/MengYao_Colab/train_runs -name last.pt
```

如果需要本地联调，把 `best.pt` 下载回项目并放到：

```text
model/checkpoints/best.pt
```

## 7. 仓库中的现成 Notebook

仓库里已经提供了可直接在 Colab 打开的 notebook：

```text
notebooks/colab_resume_train.ipynb
```

它已经包含：

- 挂载 Google Drive
- 拉取 GitHub 仓库
- 解压数据集
- 生成 Colab 专用 yaml
- 正式训练
- 断点续训

## 8. 当前推荐

对你当前这个项目，最省钱的方案不是换平台，而是：

1. 首次训练直接把输出目录写到 Google Drive
2. 免费 Colab 中断后用 `last.pt` 继续训练
3. 正式实验优先使用 `yolo11s + 100 epoch`，中断时直接从 `last.pt` 续训

现在已经到“可以从仓库直接拉到 Colab 并断点续训”的状态了。
