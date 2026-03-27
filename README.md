# 豆包播客剪辑器 (Doubao Podcast Trimmer)

[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)]()

> 🎙️ 自动检测并剪辑豆包AI生成播客的固定片头片尾，让你的播客更干净专业！

[English](#english) | [中文](#中文)

---

## 中文

### 📖 项目介绍

豆包播客剪辑器是一个专门用于处理豆包AI生成播客音频的开源工具。豆包（字节跳动旗下的AI对话产品）生成的播客音频在每个节目的开头和结尾都有固定的音乐和介绍内容。这个工具可以自动检测并移除这些重复内容，只保留核心节目内容。

> 🤖 **开发工具**: 本项目由 [百度文心快码 (Baidu Comate)](https://comate.baidu.com/) AI 编程助手辅助开发

### ✨ 功能特点

- 🔍 **智能检测** - 自动分析音频文件的共同内容，找出固定片头片尾
- ✂️ **精准剪辑** - 基于实际分析结果，精确移除重复内容
- 🎯 **豆包优化** - 专门针对豆包播客音频结构优化（片头约7秒，片尾约10秒）
- 📦 **批量处理** - 支持批量处理多个音频文件
- 🚀 **简单易用** - 命令行工具和Python API双重支持
- 🎵 **保持质量** - 输出音频保持原始采样率和音质

### 📋 系统要求

- Python 3.7 或更高版本
- 无需额外依赖（使用Python标准库 `wave` 模块）

### 🚀 快速开始

#### 安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/doubao-podcast-trimmer.git
cd doubao-podcast-trimmer

# 无需安装依赖，开箱即用！
```

#### 基础用法

**1. 单文件剪辑（推荐）**

```bash
python doubao_trimmer.py input.wav output.wav
```

**2. 批量处理**

```bash
python batch_trim.py ./input_folder ./output_folder
```

**3. 分析两个音频的共同内容**

```bash
python doubao_trimmer.py --analyze 1.wav 2.wav
```

### 📖 使用示例

#### 示例 1：剪辑单个文件

```bash
$ python doubao_trimmer.py podcast_1.wav podcast_1_clean.wav

✅ 剪辑完成！
   原始时长: 614.77秒 (10.25分钟)
   新时长:   597.77秒 (9.96分钟)
   移除内容: 17.0秒 (片头7秒 + 片尾10秒)
```

#### 示例 2：Python API 调用

```python
from doubao_trimmer import DoubaoPodcastTrimmer

# 创建剪辑器实例
trimmer = DoubaoPodcastTrimmer()

# 剪辑单个文件
trimmer.trim('input.wav', 'output.wav')

# 或使用自定义参数
trimmer.trim(
    input_file='input.wav',
    output_file='output.wav',
    header_duration=7.0,   # 片头时长（秒）
    tail_duration=10.0     # 片尾时长（秒）
)
```

#### 示例 3：批量处理

```python
from batch_trim import batch_process

# 批量处理文件夹中的所有 WAV 文件
batch_process(
    input_dir='./raw_podcasts',
    output_dir='./trimmed_podcasts',
    header_duration=7.0,
    tail_duration=10.0
)
```

### 🔧 高级用法

#### 自定义剪辑参数

如果你的豆包播客音频的片头片尾时长不同，可以自定义参数：

```bash
python doubao_trimmer.py input.wav output.wav --header 6.5 --tail 9.5
```

#### 分析模式

找出两个音频文件的共同内容：

```bash
$ python doubao_trimmer.py --analyze 1.wav 2.wav

=== 分析结果 ===
片头相同内容: 168000 采样点 = 7.00秒
片尾相同内容: 240000 采样点 = 10.00秒

建议使用参数:
  --header 7.00
  --tail 10.00
```

### 📊 技术细节

#### 豆包播客音频结构

基于对豆包生成播客的分析，其音频结构如下：

| 部分 | 时长 | 内容 |
|------|------|------|
| 片头 | ~7.0秒 | 固定开场音乐/品牌介绍 |
| 主体 | 可变 | 实际播客内容（约8-10分钟） |
| 片尾 | ~10.0秒 | 固定结束音乐/广告 |

#### 处理流程

1. **加载音频** - 使用标准库 `wave` 读取 WAV 文件
2. **验证时长** - 确保音频足够长（至少17秒）
3. **计算剪辑点** - 根据片头片尾时长计算起止帧
4. **提取内容** - 保留中间部分的核心内容
5. **导出保存** - 保持原始格式输出

#### 支持的格式

- ✅ WAV 格式（16bit/24bit，单声道/立体声）
- ❌ MP3、M4A 等格式（建议先转换为 WAV）

### 🛠️ 转换其他格式

如果你需要处理 MP3 或 M4A 文件，可以先转换为 WAV：

```bash
# 使用 ffmpeg（推荐）
ffmpeg -i input.mp3 -ar 24000 -ac 1 output.wav

# 批量转换
for f in *.mp3; do ffmpeg -i "$f" -ar 24000 -ac 1 "${f%.mp3}.wav"; done
```

### 🤝 贡献指南

我们欢迎所有形式的贡献！

#### 提交 Issue

如果你发现了 bug 或有新功能建议，请提交 issue：

1. 检查是否已有相关 issue
2. 创建新 issue 并详细描述问题
3. 提供复现步骤（如果是 bug）

#### 提交 Pull Request

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

#### 开发计划

- [ ] 支持 MP3、M4A 等更多音频格式
- [ ] 图形用户界面 (GUI)
- [ ] 更智能的片头片尾检测算法
- [ ] 支持其他AI播客平台（如混元、GPT等）

### 📄 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。

### 🙏 致谢

- 感谢豆包AI提供的优质播客生成服务
- 感谢所有贡献者和用户的支持
- **特别感谢**：[百度文心快码 Comate](https://comate.baidu.com/) - 本项目由 Comate AI 编程助手辅助开发

---

## English

### 📖 Introduction

**Doubao Podcast Trimmer** is an open-source tool specifically designed for processing AI-generated podcast audio from Doubao (ByteDance's AI chat product). Doubao-generated podcast audio contains fixed intro/outro music at the beginning and end of each episode. This tool automatically detects and removes these repetitive parts, keeping only the core content.

### ✨ Features

- 🔍 **Smart Detection** - Automatically analyze common content between audio files
- ✂️ **Precise Trimming** - Remove repetitive content based on actual analysis
- 🎯 **Doubao Optimized** - Specifically optimized for Doubao podcast structure (~7s intro, ~10s outro)
- 📦 **Batch Processing** - Support batch processing of multiple audio files
- 🚀 **Easy to Use** - Both CLI and Python API support
- 🎵 **Quality Preserved** - Output maintains original sample rate and quality

### 📋 Requirements

- Python 3.7 or higher
- No additional dependencies (uses Python standard library `wave` module)

### 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/doubao-podcast-trimmer.git
cd doubao-podcast-trimmer

# Trim a single file
python doubao_trimmer.py input.wav output.wav

# Batch process
python batch_trim.py ./input_folder ./output_folder
```

### 📖 Usage

See [中文](#中文) section for detailed documentation.

### 🙏 Acknowledgments

- Thanks to Doubao AI for providing excellent podcast generation services
- Thanks to all contributors and users for their support
- **Special thanks**: [Baidu Comate](https://comate.baidu.com/) - This project was developed with the assistance of Comate AI programming assistant

### 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 📞 联系方式

- 项目主页: https://github.com/yourusername/doubao-podcast-trimmer
- Issue 反馈: https://github.com/yourusername/doubao-podcast-trimmer/issues
- 邮箱: your.email@example.com

---


<p align="center">Made with ❤️ for the podcast community</p>
