#!/usr/bin/env python3
"""
豆包播客剪辑器 - Doubao Podcast Trimmer
自动检测并移除豆包AI生成播客的固定片头片尾
"""

import wave
import sys
import os
import argparse
from pathlib import Path


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


def find_common_content(filepath1, filepath2):
    """
    找出两段音频的共同内容（固定片头片尾）
    通过逐采样点比较，找到完全一致的部分
    """
    with wave.open(filepath1, 'rb') as wav1:
        data1 = wav1.readframes(wav1.getnframes())
        params1 = wav1.getparams()
    
    with wave.open(filepath2, 'rb') as wav2:
        data2 = wav2.readframes(wav2.getnframes())
        params2 = wav2.getparams()
    
    sample_width = params1.sampwidth
    framerate = params1.framerate
    
    # 从头开始比较，找到连续相同的采样点（片头）
    header_match = 0
    max_check = min(len(data1), len(data2)) // sample_width
    for i in range(max_check):
        idx1 = i * sample_width
        idx2 = i * sample_width
        if data1[idx1:idx1+sample_width] == data2[idx2:idx2+sample_width]:
            header_match += 1
        else:
            break
    
    # 从尾开始比较，找到连续相同的采样点（片尾）
    tail_match = 0
    for i in range(1, max_check + 1):
        idx1 = len(data1) - i * sample_width
        idx2 = len(data2) - i * sample_width
        if idx1 < 0 or idx2 < 0:
            break
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
        'framerate': framerate
    }


def trim_audio(input_file, output_file, header_duration=7.0, tail_duration=10.0):
    """
    剪辑音频，移除固定的片头片尾
    
    Args:
        input_file: 输入音频文件路径
        output_file: 输出音频文件路径
        header_duration: 片头时长（秒），默认7秒
        tail_duration: 片尾时长（秒），默认10秒
    
    Returns:
        bool: 是否成功
    """
    try:
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
                print(f"❌ 错误: 音频时长不足，无法剪辑")
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
            removed_duration = total_duration - new_duration
            
            print(f"✅ 剪辑完成: {os.path.basename(input_file)}")
            print(f"   原始时长: {total_duration:.2f}秒 ({total_duration/60:.2f}分钟)")
            print(f"   新时长: {new_duration:.2f}秒 ({new_duration/60:.2f}分钟)")
            print(f"   移除内容: {removed_duration:.2f}秒 (片头{header_duration}s + 片尾{tail_duration}s)")
            print(f"   输出文件: {output_file}")
            
            return True
            
    except Exception as e:
        print(f"❌ 处理失败 {input_file}: {str(e)}")
        return False


def analyze_files(file1, file2):
    """分析两个音频文件的共同内容"""
    print(f"🔍 正在分析音频文件的共同内容...")
    print(f"   文件1: {file1}")
    print(f"   文件2: {file2}")
    print()
    
    result = find_common_content(file1, file2)
    
    print("📊 分析结果:")
    print(f"   采样率: {result['framerate']} Hz")
    print(f"   片头相同: {result['header_samples']} 采样点 = {result['header_duration']:.2f}秒")
    print(f"   片尾相同: {result['tail_samples']} 采样点 = {result['tail_duration']:.2f}秒")
    print()
    print("💡 建议使用参数:")
    print(f"   --header {result['header_duration']:.2f}")
    print(f"   --tail {result['tail_duration']:.2f}")


def batch_process(input_dir, output_dir, header_duration=7.0, tail_duration=10.0):
    """批量处理目录中的所有 WAV 文件"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    wav_files = list(input_path.glob("*.wav"))
    
    if not wav_files:
        print(f"❌ 在 {input_dir} 中没有找到 WAV 文件")
        return
    
    print(f"🎯 找到 {len(wav_files)} 个 WAV 文件，开始批量处理...")
    print(f"   片头剪辑: {header_duration}秒")
    print(f"   片尾剪辑: {tail_duration}秒")
    print()
    
    success_count = 0
    for wav_file in wav_files:
        output_file = output_path / f"{wav_file.stem}_trimmed.wav"
        if trim_audio(str(wav_file), str(output_file), header_duration, tail_duration):
            success_count += 1
        print()
    
    print(f"🎉 批量处理完成: {success_count}/{len(wav_files)} 个文件成功")


def main():
    parser = argparse.ArgumentParser(
        description='豆包播客剪辑器 - 自动移除固定片头片尾',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析两个文件的共同内容
  python doubao_trimmer.py analyze 1.wav 2.wav
  
  # 剪辑单个文件
  python doubao_trimmer.py trim input.wav -o output.wav
  
  # 批量处理
  python doubao_trimmer.py batch ./podcasts ./trimmed
  
  # 自定义剪辑时长
  python doubao_trimmer.py trim input.wav --header 6.5 --tail 9.8
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析两个音频文件的共同内容')
    analyze_parser.add_argument('file1', help='第一个音频文件')
    analyze_parser.add_argument('file2', help='第二个音频文件')
    
    # trim 命令
    trim_parser = subparsers.add_parser('trim', help='剪辑单个音频文件')
    trim_parser.add_argument('input', help='输入音频文件')
    trim_parser.add_argument('-o', '--output', help='输出文件路径 (默认: input_trimmed.wav)')
    trim_parser.add_argument('--header', type=float, default=7.0, help='片头剪辑时长 (秒), 默认: 7.0')
    trim_parser.add_argument('--tail', type=float, default=10.0, help='片尾剪辑时长 (秒), 默认: 10.0')
    
    # batch 命令
    batch_parser = subparsers.add_parser('batch', help='批量处理目录中的所有 WAV 文件')
    batch_parser.add_argument('input_dir', help='输入目录')
    batch_parser.add_argument('output_dir', help='输出目录')
    batch_parser.add_argument('--header', type=float, default=7.0, help='片头剪辑时长 (秒), 默认: 7.0')
    batch_parser.add_argument('--tail', type=float, default=10.0, help='片尾剪辑时长 (秒), 默认: 10.0')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'analyze':
        if not os.path.exists(args.file1) or not os.path.exists(args.file2):
            print("❌ 错误: 文件不存在")
            sys.exit(1)
        analyze_files(args.file1, args.file2)
    
    elif args.command == 'trim':
        if not os.path.exists(args.input):
            print(f"❌ 错误: 文件不存在: {args.input}")
            sys.exit(1)
        
        output = args.output or args.input.replace('.wav', '_trimmed.wav')
        trim_audio(args.input, output, args.header, args.tail)
    
    elif args.command == 'batch':
        if not os.path.exists(args.input_dir):
            print(f"❌ 错误: 目录不存在: {args.input_dir}")
            sys.exit(1)
        batch_process(args.input_dir, args.output_dir, args.header, args.tail)


if __name__ == '__main__':
    main()
