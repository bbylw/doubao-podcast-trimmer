#!/usr/bin/env python3
"""
豆包播客音频剪辑脚本
自动检测并移除固定的片头片尾内容
"""

import wave
import sys
import os


def get_audio_info(filepath):
    """获取音频文件信息"""
    with wave.open(filepath, 'rb') as wav:
        n_channels = wav.getnchannels()
        sample_width = wav.getsampwidth()
        framerate = wav.getframerate()
        n_frames = wav.getnframes()
        duration = n_frames / framerate
        
        return {
            'channels': n_channels,
            'sample_width': sample_width,
            'framerate': framerate,
            'n_frames': n_frames,
            'duration': duration
        }


def compare_audio_segments(data1, data2, start1, start2, length):
    """比较两段音频数据是否相同"""
    if start1 + length > len(data1) or start2 + length > len(data2):
        return 0
    
    match_count = 0
    for i in range(length):
        if data1[start1 + i] == data2[start2 + i]:
            match_count += 1
    
    return match_count / length


def find_common_content(filepath1, filepath2):
    """找出两段音频的共同内容（固定片头片尾）"""
    with wave.open(filepath1, 'rb') as wav1:
        data1 = wav1.readframes(wav1.getnframes())
        params1 = wav1.getparams()
    
    with wave.open(filepath2, 'rb') as wav2:
        data2 = wav2.readframes(wav2.getnframes())
        params2 = wav2.getparams()
    
    sample_width = params1.sampwidth
    framerate = params1.framerate
    
    # 比较开头（最多前30秒）
    max_check_samples = min(30 * framerate, len(data1) // sample_width, len(data2) // sample_width)
    
    # 从头开始比较，找到连续相同的采样点
    header_match = 0
    for i in range(0, min(len(data1), len(data2)) // sample_width):
        idx1 = i * sample_width
        idx2 = i * sample_width
        if data1[idx1:idx1+sample_width] == data2[idx2:idx2+sample_width]:
            header_match += 1
        else:
            break
    
    # 从尾开始比较，找到连续相同的采样点
    tail_match = 0
    for i in range(1, min(len(data1), len(data2)) // sample_width + 1):
        idx1 = len(data1) - i * sample_width
        idx2 = len(data2) - i * sample_width
        if data1[idx1:idx1+sample_width] == data2[idx2:idx2+sample_width]:
            tail_match += 1
        else:
            break
    
    header_duration = header_match / framerate
    tail_duration = tail_match / framerate
    
    return {
        'header_samples': header_match,
        'header_duration': header_duration,
        'tail_samples': tail_match,
        'tail_duration': tail_duration,
        'framerate': framerate,
        'sample_width': sample_width
    }


def trim_audio(input_file, output_file, header_duration=7.0, tail_duration=10.0):
    """
    剪辑音频，移除固定的片头片尾
    
    Args:
        input_file: 输入音频文件路径
        output_file: 输出音频文件路径
        header_duration: 片头时长（秒），默认7秒
        tail_duration: 片尾时长（秒），默认10秒
    """
    with wave.open(input_file, 'rb') as wav_in:
        params = wav_in.getparams()
        framerate = wav_in.getframerate()
        n_frames = wav_in.getnframes()
        data = wav_in.readframes(n_frames)
        
        sample_width = params.sampwidth
        total_duration = n_frames / framerate
        
        # 计算要保留的起止帧
        start_frame = int(header_duration * framerate)
        end_frame = n_frames - int(tail_duration * framerate)
        
        # 确保有足够的音频内容
        if end_frame <= start_frame:
            print(f"错误: 音频时长不足，无法剪辑")
            return False
        
        # 提取中间部分
        start_byte = start_frame * sample_width * params.nchannels
        end_byte = end_frame * sample_width * params.nchannels
        trimmed_data = data[start_byte:end_byte]
        
        # 写入输出文件
        with wave.open(output_file, 'wb') as wav_out:
            wav_out.setparams(params)
            wav_out.writeframes(trimmed_data)
        
        new_duration = (end_frame - start_frame) / framerate
        print(f"剪辑完成: {input_file}")
        print(f"  原始时长: {total_duration:.2f}秒 ({total_duration/60:.2f}分钟)")
        print(f"  新时长: {new_duration:.2f}秒 ({new_duration/60:.2f}分钟)")
        print(f"  移除片头: {header_duration}秒")
        print(f"  移除片尾: {tail_duration}秒")
        print(f"  输出文件: {output_file}")
        
        return True


def main():
    if len(sys.argv) < 3:
        print("用法: python trim_podcast.py <输入文件1> <输入文件2> [输出目录]")
        print("  或: python trim_podcast.py --trim <输入文件> [输出文件] [--header 7.0] [--tail 10.0]")
        sys.exit(1)
    
    # 分析模式：找出共同内容
    if sys.argv[1] not in ['--trim', '-t']:
        file1 = sys.argv[1]
        file2 = sys.argv[2]
        
        if not os.path.exists(file1) or not os.path.exists(file2):
            print("错误: 文件不存在")
            sys.exit(1)
        
        print(f"分析两个音频文件的共同内容...")
        result = find_common_content(file1, file2)
        
        print(f"\n=== 分析结果 ===")
        print(f"片头相同内容: {result['header_samples']} 采样点 = {result['header_duration']:.2f}秒")
        print(f"片尾相同内容: {result['tail_samples']} 采样点 = {result['tail_duration']:.2f}秒")
        print(f"\n建议使用参数:")
        print(f"  --header {result['header_duration']:.2f}")
        print(f"  --tail {result['tail_duration']:.2f}")
    
    # 剪辑模式
    else:
        input_file = sys.argv[2]
        output_file = sys.argv[3] if len(sys.argv) > 3 else input_file.replace('.wav', '_trimmed.wav')
        
        header_duration = 7.0
        tail_duration = 10.0
        
        # 解析可选参数
        for i, arg in enumerate(sys.argv):
            if arg == '--header' and i + 1 < len(sys.argv):
                header_duration = float(sys.argv[i + 1])
            elif arg == '--tail' and i + 1 < len(sys.argv):
                tail_duration = float(sys.argv[i + 1])
        
        if not os.path.exists(input_file):
            print(f"错误: 文件不存在: {input_file}")
            sys.exit(1)
        
        trim_audio(input_file, output_file, header_duration, tail_duration)


if __name__ == '__main__':
    main()
