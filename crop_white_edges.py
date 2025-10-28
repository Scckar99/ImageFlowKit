"""
图片白色边缘裁剪工具
自动检测并裁剪图片周围的白色空白区域
"""

import cv2
import numpy as np
from pathlib import Path
from PIL import Image
import sys
import io

# 设置Windows控制台输出编码为UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def imread_chinese(image_path):
    """
    读取包含中文路径的图片
    
    Args:
        image_path: 图片路径
        
    Returns:
        PIL Image对象
    """
    return Image.open(image_path)


def crop_white_edges(image, threshold=250, padding=10):
    """
    裁剪图片的白色边缘
    
    Args:
        image: PIL Image对象
        threshold: 白色阈值（0-255），像素值大于此值被认为是白色，默认250
        padding: 裁剪后保留的边距（像素），默认10
        
    Returns:
        PIL Image: 裁剪后的图片
    """
    # 转换为numpy数组
    img_array = np.array(image)
    
    # 如果是RGBA，转换为RGB
    if img_array.shape[-1] == 4:
        img_array = img_array[:, :, :3]
    
    # 转换为灰度图来检测白色区域
    if len(img_array.shape) == 3:
        gray = np.mean(img_array, axis=2)
    else:
        gray = img_array
    
    # 找到非白色像素的位置
    non_white_pixels = np.where(gray < threshold)
    
    if len(non_white_pixels[0]) == 0 or len(non_white_pixels[1]) == 0:
        # 如果整张图都是白色，返回原图
        print("  ⚠️  警告：未检测到非白色内容")
        return image
    
    # 获取内容区域的边界
    top = max(0, non_white_pixels[0].min() - padding)
    bottom = min(img_array.shape[0], non_white_pixels[0].max() + padding + 1)
    left = max(0, non_white_pixels[1].min() - padding)
    right = min(img_array.shape[1], non_white_pixels[1].max() + padding + 1)
    
    # 计算裁剪比例
    original_size = img_array.shape[0] * img_array.shape[1]
    cropped_size = (bottom - top) * (right - left)
    size_ratio = cropped_size / original_size * 100
    
    print(f"  原始尺寸: {img_array.shape[1]} × {img_array.shape[0]}")
    print(f"  内容区域: [{left}:{right}, {top}:{bottom}]")
    print(f"  裁剪后尺寸: {right - left} × {bottom - top}")
    print(f"  内容占比: {size_ratio:.1f}%")
    
    # 裁剪图片
    cropped_image = image.crop((left, top, right, bottom))
    
    return cropped_image


def batch_crop_white_edges(input_folder, output_folder, threshold=250, padding=10):
    """
    批量裁剪图片的白色边缘
    
    Args:
        input_folder: 输入文件夹路径
        output_folder: 输出文件夹路径
        threshold: 白色阈值（0-255）
        padding: 裁剪后保留的边距（像素）
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    # 创建输出文件夹
    output_path.mkdir(exist_ok=True)
    
    print(f"输入文件夹: {input_folder}")
    print(f"输出文件夹: {output_folder}")
    print(f"白色阈值: {threshold}")
    print(f"保留边距: {padding} 像素")
    print("=" * 70)
    
    # 获取所有图片文件
    image_files = (
        list(input_path.glob("*.png"))
        + list(input_path.glob("*.jpg"))
        + list(input_path.glob("*.jpeg"))
    )
    
    if not image_files:
        print(f"错误: 在 {input_folder} 中未找到图片文件")
        return
    
    print(f"找到 {len(image_files)} 张图片待处理\n")
    
    # 统计信息
    success_count = 0
    failed_count = 0
    
    # 处理每张图片
    for idx, img_file in enumerate(image_files, 1):
        print(f"[{idx}/{len(image_files)}] 处理: {img_file.name}")
        
        try:
            # 读取图片
            img = imread_chinese(str(img_file))
            
            # 裁剪白色边缘
            cropped_img = crop_white_edges(img, threshold=threshold, padding=padding)
            
            # 保存裁剪后的图片
            output_file = output_path / img_file.name
            cropped_img.save(output_file)
            
            print(f"  ✓ 保存至: {output_file}")
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ 处理失败: {e}")
            failed_count += 1
        
        print()
    
    # 显示统计结果
    print("=" * 70)
    print("处理完成！")
    print(f"总计: {len(image_files)} 张图片")
    print(f"  - 成功: {success_count} 张")
    print(f"  - 失败: {failed_count} 张")
    print(f"\n所有图片已保存至: {output_path.absolute()}")


def process_single_image(image_path, output_path=None, threshold=250, padding=10):
    """
    处理单张图片
    
    Args:
        image_path: 输入图片路径
        output_path: 输出图片路径（如果为None，则在原文件名后加_cropped）
        threshold: 白色阈值（0-255）
        padding: 裁剪后保留的边距（像素）
    """
    img_path = Path(image_path)
    
    if not img_path.exists():
        print(f"错误: 图片不存在: {image_path}")
        return
    
    # 生成输出路径
    if output_path is None:
        output_path = img_path.parent / f"{img_path.stem}_cropped{img_path.suffix}"
    else:
        output_path = Path(output_path)
    
    print(f"处理图片: {img_path.name}")
    print("=" * 70)
    
    try:
        # 读取图片
        img = imread_chinese(str(img_path))
        
        # 裁剪白色边缘
        cropped_img = crop_white_edges(img, threshold=threshold, padding=padding)
        
        # 保存裁剪后的图片
        cropped_img.save(output_path)
        
        print(f"✓ 保存至: {output_path}")
        print(f"\n处理完成！")
        
    except Exception as e:
        print(f"✗ 处理失败: {e}")


def main():
    """主函数"""
    print("=" * 70)
    print("图片白色边缘自动裁剪工具")
    print("=" * 70)
    print()
    
    # 使用方式1：处理单张图片
    # process_single_image(
    #     "output/1.png",
    #     threshold=250,
    #     padding=10
    # )
    
    # 使用方式2：批量处理文件夹
    batch_crop_white_edges(
        input_folder="output",
        output_folder="output_cropped",
        threshold=250,  # 白色阈值：像素值大于250被认为是白色
        padding=10      # 保留10像素的边距
    )


if __name__ == "__main__":
    main()