---
name: doubao-podcast-trim
description: 自动剪辑豆包播客音频文件，移除固定的片头和片尾内容。Use when processing 豆包AI生成的播客音频文件 (.wav) to remove the repetitive intro/outro music. Automatically detects and trims approximately 7 seconds from the beginning and 10 seconds from the end of each audio file.
---

# 豆包播客剪辑

## 概述

自动检测并剪辑豆包AI生成的播客音频文件，移除固定的片头（约7秒）和片尾（约10秒）重复内容。

## 固定时长参数

基于豆包播客的音频结构分析：

| 位置 | 时长 | 说明 |
|------|------|------|
| 片头 | 7000ms (7秒) | 固定开场音乐/介绍 |
| 片尾 | 9950ms (约10秒) | 固定结束音乐/广告 |

## 使用方法

### Python 直接调用

```python
from pydub import AudioSegment

def trim_doubao_podcast(input_file, output_file):
    """剪辑豆包播客音频，移除固定首尾"""
    audio = AudioSegment.from_wav(input_file)
    
    # 移除开头7秒和结尾约10秒
    start_trim = 7000  # 7秒
    end_trim = 9950    # 约10秒
    
    if len(audio) > (start_trim + end_trim):
        trimmed = audio[start_trim:-end_trim]
        trimmed.export(output_file, format='wav')
        return trimmed
    else:
        raise ValueError(f"音频太短，无法剪辑。需要至少 {start_trim + end_trim}ms")
```

### 使用本 Skill 的脚本

运行内置脚本进行批量处理：

```bash
python scripts/trim_doubao_podcast.py input.wav output.wav
```

或使用 Python 代码：

```python
import subprocess

# 单文件处理
subprocess.run([
    'python', 'scripts/trim_doubao_podcast.py',
    'input.wav', 'output.wav'
])
```

### 批量处理

```python
import os
import subprocess

def batch_trim_doubao_podcasts(input_dir, output_dir):
    """批量处理豆包播客音频文件"""
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.endswith('.wav'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f'trimmed_{filename}')
            
            try:
                subprocess.run([
                    'python', 'scripts/trim_doubao_podcast.py',
                    input_path, output_path
                ], check=True)
                print(f'已处理: {filename}')
            except Exception as e:
                print(f'处理失败 {filename}: {e}')
```

## 处理流程

1. **加载音频**：使用 pydub 读取 WAV 文件
2. **验证时长**：确保音频长度 > 17秒（7秒开头 + 10秒结尾）
3. **剪辑处理**：移除开头7秒和结尾10秒
4. **导出保存**：保持原格式输出到指定路径

## 输出示例

```
原始文件: 614.77秒 (10.2分钟)
剪辑后:   597.83秒 (9.96分钟)
移除内容: 16.95秒 (7秒开头 + 9.95秒结尾)
```

## 注意事项

- 仅支持 WAV 格式音频文件
- 音频时长必须大于 17 秒才能进行剪辑
- 输出文件保持原始采样率和格式
- 豆包播客的固定首尾时长可能略有变化（±0.5秒），脚本使用经验值处理

## Resources

### scripts/

- `trim_doubao_podcast.py` - 核心剪辑脚本，提供命令行和模块调用接口
