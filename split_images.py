"""
图片三等分提取工具（只保存指定部分）
将包含三个并排内容的图片水平三等分，只保存指定的某一部分
"""

from pathlib import Path
from PIL import Image
import sys
import io

# 设置Windows控制台输出编码为UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def extract_part_from_image(image_path, output_folder, part_index=1, direction='horizontal'):
    """
    从三等分图片中提取指定部分并保存
    
    Args:
        image_path: 输入图片路径
        output_folder: 输出文件夹路径
        part_index: 要保存的部分索引（1, 2, 或 3）
                   水平方向：1=左边, 2=中间, 3=右边
                   垂直方向：1=上边, 2=中间, 3=下边
        direction: 分割方向
                  'horizontal' - 水平三等分
                  'vertical' - 垂直三等分
        
    Returns:
        str: 保存的文件路径
    """
    img_path = Path(image_path)
    output_path = Path(output_folder)
    
    # 创建输出文件夹
    output_path.mkdir(exist_ok=True, parents=True)
    
    # 读取图片
    image = Image.open(img_path)
    width, height = image.size
    
    print(f"  原始尺寸: {width} × {height}")
    
    # 验证part_index
    if part_index not in [1, 2, 3]:
        raise ValueError(f"part_index 必须是 1, 2, 或 3，当前值: {part_index}")
    
    # 计算要提取的部分
    i = part_index - 1  # 转换为0-based索引
    
    if direction == 'horizontal':
        # 水平三等分
        part_width = width // 3
        left = i * part_width
        right = (i + 1) * part_width if i < 2 else width
        
        # 裁剪指定部分
        extracted_image = image.crop((left, 0, right, height))
        print(f"  提取第 {part_index} 部分（{'左' if i==0 else '中' if i==1 else '右'}）: [{left}, 0, {right}, {height}]")
    
    else:  # vertical
        # 垂直三等分
        part_height = height // 3
        top = i * part_height
        bottom = (i + 1) * part_height if i < 2 else height
        
        # 裁剪指定部分
        extracted_image = image.crop((0, top, width, bottom))
        print(f"  提取第 {part_index} 部分（{'上' if i==0 else '中' if i==1 else '下'}）: [0, {top}, {width}, {bottom}]")
    
    # 生成输出文件名（不带part后缀，直接使用原文件名）
    output_file = output_path / img_path.name
    
    # 保存
    extracted_image.save(output_file)
    print(f"  提取尺寸: {extracted_image.size[0]} × {extracted_image.size[1]}")
    
    return output_file


def batch_extract_part(input_folder, output_folder, part_index=1, direction='horizontal'):
    """
    批量处理文件夹中的所有图片，只提取指定部分
    
    Args:
        input_folder: 输入文件夹路径
        output_folder: 输出文件夹路径
        part_index: 要保存的部分索引（1, 2, 或 3）
        direction: 分割方向，'horizontal'（水平）或 'vertical'（垂直）
    """
    input_path = Path(input_folder)
    
    position_name = {
        'horizontal': {1: '左边', 2: '中间', 3: '右边'},
        'vertical': {1: '上边', 2: '中间', 3: '下边'}
    }
    
    print(f"输入文件夹: {input_folder}")
    print(f"输出文件夹: {output_folder}")
    print(f"分割方向: {'水平三等分' if direction == 'horizontal' else '垂直三等分'}")
    print(f"提取部分: 第 {part_index} 部分（{position_name[direction][part_index]}）")
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
            output_file = extract_part_from_image(
                str(img_file), 
                output_folder, 
                part_index=part_index,
                direction=direction
            )
            
            print(f"  ✓ 保存至: {output_file.name}")
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
    print(f"\n所有图片已保存至: {Path(output_folder).absolute()}")


def main():
    """主函数"""
    print("=" * 70)
    print("图片三等分提取工具（单一部分提取）")
    print("=" * 70)
    print()
    
    # 使用方式1：处理单张图片
    # extract_part_from_image(
    #     "output_cropped/1.png",
    #     output_folder="output_split",
    #     part_index=2,              # 1=左边, 2=中间, 3=右边
    #     direction='horizontal'
    # )
    
    # 使用方式2：批量处理文件夹
    batch_extract_part(
        input_folder="output_cropped",    # 输入文件夹
        output_folder="output_split",     # 输出文件夹
        part_index=2,                     # 1=左边, 2=中间, 3=右边
        direction='horizontal'            # 'horizontal'（水平）或 'vertical'（垂直）
    )


if __name__ == "__main__":
    main()