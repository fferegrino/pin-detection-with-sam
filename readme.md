## 1. Create a Python virtual environment

```
python -m venv .venv
```

The Python version is `3.10.12`

## 2. Install torch

```
pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/nightly/cpu
```

According to [this guide](https://developer.apple.com/metal/pytorch/); for the record, the version I istalled is `2.3.0`

## 3. Install (and fix) *NumPy* on macOS

I found the answer [in this post](https://stackoverflow.com/a/47433969)

```
pip install numpy -I
```

The version I ended up having was `1.26.4`

## 3. Install *Segment Anything*

```
pip install 'git+https://github.com/facebookresearch/segment-anything.git'
```

## 4. Download model

```
wget -q https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
```

## 4. Install other tools

 - supervision
 - jupyter
 - jupyterlab
 - streamlit
 - streamlit-image-coordinates

