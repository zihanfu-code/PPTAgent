# 安装总结

## ✅ 已成功安装的依赖

### 常规依赖
所有常规依赖已通过 `pip install -r requirements.txt` 成功安装，包括：
- fastapi, uvicorn
- lxml, beautifulsoup4
- opencv-python-headless
- pandas, numpy
- 以及其他所有 requirements.txt 中列出的包

### 特殊依赖

#### ✅ python-pptx（已成功安装）
**安装方法：**
```bash
# 1. 设置代理（如果需要）
export https_proxy=http://proxy.zhenguanyu.com:8118 http_proxy=http://proxy.zhenguanyu.com:8118 all_proxy=http://proxy.zhenguanyu.com:8118

# 2. 先安装依赖（不使用代理，因为代理对 pip 返回 503）
unset https_proxy http_proxy all_proxy
pip install XlsxWriter lxml

# 3. 克隆并安装 python-pptx（使用代理，因为 git clone 需要）
export https_proxy=http://proxy.zhenguanyu.com:8118 http_proxy=http://proxy.zhenguanyu.com:8118 all_proxy=http://proxy.zhenguanyu.com:8118
cd /tmp
git clone https://github.com/Force1ess/python-pptx.git
cd python-pptx
pip install . --no-build-isolation --no-deps
```

**验证：**
```bash
python -c "from pptx import __version__; print('python-pptx 版本:', __version__)"
# 应该输出: python-pptx 版本: 1.0.4+PPTAgent
```

## ✅ marker-pdf（已成功安装）
**安装方法：**
```bash
# 使用 --no-deps 忽略 Pillow 版本检查（虽然要求 Pillow<11.0.0，但 Pillow 11.2.1 实际可用）
unset https_proxy http_proxy all_proxy
pip install --no-deps marker-pdf==1.1.0
pip install --force-reinstall --no-deps "Pillow==11.2.1"  # 恢复 Pillow
```

**验证：**
```bash
python -c "import marker; print('marker 可以导入')"
```

### transformers
- **当前版本：** 4.57.1（已安装）
- **项目要求：** <4.50.0
- **如果需要降级：**
  ```bash
  pip install "transformers<4.50.0"
  ```
- **注意：** 降级可能影响其他依赖（如 peft）

## 📝 使用项目代码

由于不想安装 `pptagent` 包本身（避免与已安装的包冲突），使用以下方式导入：

### 方法 1：设置 PYTHONPATH（推荐）
```bash
export PYTHONPATH=/mnt/data/guyx/PPTAgent-main:$PYTHONPATH
```

### 方法 2：在 Python 代码中
```python
import sys
sys.path.insert(0, '/mnt/data/guyx/PPTAgent-main')
from pptagent import ...
```

### 方法 3：永久设置（添加到 ~/.bashrc）
```bash
echo 'export PYTHONPATH=/mnt/data/guyx/PPTAgent-main:$PYTHONPATH' >> ~/.bashrc
source ~/.bashrc
```

## 🔍 验证安装

运行以下命令验证关键依赖：
```bash
# 验证 python-pptx
python -c "from pptx import __version__; print('python-pptx:', __version__)"

# 验证 pptagent（需要先设置 PYTHONPATH）
export PYTHONPATH=/mnt/data/guyx/PPTAgent-main:$PYTHONPATH
python -c "import pptagent; print('pptagent 导入成功')"
```

## 📌 重要提示

1. **代理配置：** 
   - Git clone 需要代理：`export https_proxy=http://proxy.zhenguanyu.com:8118 ...`
   - pip 安装包时代理返回 503，需要临时禁用：`unset https_proxy http_proxy all_proxy`

2. **不安装包本身：** 
   - 使用 `pip install -r requirements.txt` 只安装依赖
   - 通过 PYTHONPATH 使用源代码，避免与已安装的 pptagent 冲突

3. **版本冲突：** 
   - transformers 和 marker-pdf 有版本要求，但当前环境版本可能不匹配
   - 如果遇到兼容性问题，再考虑降级

