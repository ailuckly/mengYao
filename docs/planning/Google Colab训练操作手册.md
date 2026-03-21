# Google Colab 训练操作手册

## 1. 目标

本手册用于把当前项目迁移到 Google Colab 上运行 YOLOv11 训练。按照本手册完成后，你可以在没有本地 GPU 的情况下，直接在 Colab 中启动基线训练。

当前项目已经准备好的关键内容如下：

- 最终训练集：`data/splits/final_v1`
- 训练配置：`model/configs/final_dataset_v1.yaml`
- 训练脚本：`model/scripts/train.py`
- 项目依赖：`requirements.txt`

## 2. 需要提前知道的事

### 2.1 当前训练集体积

当前最终训练集 `final_v1` 约为 **4.2GB**。这意味着你不适合每次都手动拖拽大量散文件到 Colab，最佳方式是：

1. 本地先打包
2. 上传到 Google Drive
3. 在 Colab 中挂载 Drive 并解压

### 2.2 Colab 最推荐的使用方式

建议使用下面这种结构：

- `Google Drive` 保存项目 zip 和数据集 zip
- `Colab /content/workspace` 作为运行目录
- 训练输出保存回 `Drive`

这样即使 Colab 会话断开，你的代码包、数据包和权重结果也不会丢。

---

## 3. 本地准备步骤

### 3.1 打包项目代码

在项目根目录执行：

```bash
python model/scripts/package_project_for_colab.py
```

生成文件：

`model/exports/colab/project_bundle.zip`

这个包包含：

- `backend/`
- `frontend/`
- `model/`
- `requirements.txt`
- `README.md`

### 3.2 打包最终训练集

在项目根目录执行：

```bash
python model/scripts/package_dataset_for_colab.py
```

生成文件：

`model/exports/colab/final_dataset_v1_bundle.zip`

这个包包含：

- `data/splits/final_v1/`
- `model/configs/final_dataset_v1.yaml`

### 3.3 上传到 Google Drive

建议你在 Google Drive 中建立一个目录，例如：

```text
MyDrive/MengYao_Colab/
```

然后把下面两个文件上传进去：

- `project_bundle.zip`
- `final_dataset_v1_bundle.zip`

---

## 4. 新建 Colab 环境

### 4.1 创建 Notebook

打开 Google Colab，新建一个 notebook。

### 4.2 切换 GPU

点击：

`Runtime -> Change runtime type -> T4 GPU / GPU`

如果没有 GPU，可先切换到任意可用 GPU 类型。

### 4.3 验证 GPU

在第一个单元执行：

```python
!nvidia-smi
```

如果能看到显卡信息，说明 Colab GPU 已就绪。

---

## 5. Colab 中的完整操作流程

下面这些单元按顺序执行即可。

### 5.1 挂载 Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

执行后会弹出授权链接，按提示登录即可。

### 5.2 创建工作目录

```python
!mkdir -p /content/workspace
%cd /content/workspace
```

### 5.3 解压项目代码包

假设你把文件上传到了：

`MyDrive/MengYao_Colab/`

执行：

```python
!unzip -q /content/drive/MyDrive/MengYao_Colab/project_bundle.zip -d /content/workspace/project
```

### 5.4 解压数据集包

```python
!unzip -q /content/drive/MyDrive/MengYao_Colab/final_dataset_v1_bundle.zip -d /content/workspace/project
```

### 5.5 进入项目目录

```python
%cd /content/workspace/project
```

### 5.6 安装依赖

```python
!pip install -q -r requirements.txt
```

### 5.7 检查训练配置是否存在

```python
!ls model/configs
!ls data/splits/final_v1
```

你应该能看到：

- `final_dataset_v1.yaml`
- `train`
- `val`
- `test`

### 5.8 启动基线训练

第一轮建议不要直接跑太大，先用保守参数验证链路：

```python
!python model/scripts/train.py \
  --device 0 \
  --epochs 30 \
  --batch 16 \
  --imgsz 640 \
  --name colab_baseline_v1
```

如果这轮能正常开始训练，就说明整条链路已经打通。

---

## 6. 训练结果保存

训练输出默认会在：

```text
model/exports/train_runs/colab_baseline_v1/
```

为了避免 Colab 会话结束后丢失，训练结束后建议把输出目录压缩并拷回 Google Drive。

```python
!zip -qr colab_baseline_v1.zip model/exports/train_runs/colab_baseline_v1
!cp colab_baseline_v1.zip /content/drive/MyDrive/MengYao_Colab/
```

如果你只关心最优权重，也可以直接复制：

```python
!cp model/exports/train_runs/colab_baseline_v1/weights/best.pt /content/drive/MyDrive/MengYao_Colab/
!cp model/exports/train_runs/colab_baseline_v1/weights/last.pt /content/drive/MyDrive/MengYao_Colab/
```

---

## 7. 训练结束后本地怎么接回项目

下载或同步下面这些文件回本地：

- `best.pt`
- `last.pt`
- 训练结果目录压缩包

然后放回本地项目中的：

```text
model/checkpoints/best.pt
model/checkpoints/last.pt
```

这样当前 Web 系统就能自动从 mock 模式切换到 real 模式。

---

## 8. 常见问题

### 8.1 `ultralytics` 安装失败

先单独执行：

```python
!pip install ultralytics
```

再重新执行训练。

### 8.2 解压后找不到 `final_dataset_v1.yaml`

说明 zip 解压位置不对。检查是否解压到了：

```text
/content/workspace/project/model/configs/final_dataset_v1.yaml
```

### 8.3 训练时提示数据路径错误

当前 yaml 中的路径是相对路径，必须保证目录结构保持不变。也就是说：

```text
project/
├── model/configs/final_dataset_v1.yaml
└── data/splits/final_v1/
```

这两个相对位置不能变。

### 8.4 Colab 中断

中断后重新挂载 Drive，再把项目和数据重新解压即可。如果已经把 `best.pt` 保存到 Drive，就不会丢核心结果。

---

## 9. 我建议你第一次就这么跑

第一次不要追求最优结果，先验证训练能正常开始：

```python
!python model/scripts/train.py \
  --device 0 \
  --epochs 30 \
  --batch 16 \
  --imgsz 640 \
  --name colab_baseline_v1
```

确认无报错后，再开始第二轮正式训练：

```python
!python model/scripts/train.py \
  --device 0 \
  --epochs 100 \
  --batch 16 \
  --imgsz 640 \
  --name colab_full_v1
```

---

## 10. 当前状态说明

到本手册这一步，你已经具备：

- 可直接打包的项目代码
- 可直接打包的最终训练集
- 可直接在 Colab 运行的训练脚本
- 可直接复制执行的 Colab 命令

也就是说，**现在已经到“可以上 Colab 开始跑”的状态了**。下一步你只需要先在本地执行两个打包脚本，把 zip 上传到 Google Drive，然后照着第 5 节一步步执行即可。
