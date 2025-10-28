"""
修复人工检查文件夹中的图片
将 output/manual_check 中的所有图片旋转180度
"""

from pathlib import Path
from PIL import Image
import sys


def rotate_images_180(input_folder="output/manual_check", output_folder="output"):
    """
    将人工检查文件夹中的图片旋转180度并移动到主输出文件夹

    Args:
        input_folder: manual_check文件夹路径
        output_folder: 主输出文件夹路径
    """
    manual_check_path = Path(input_folder)
    output_path = Path(output_folder)

    if not manual_check_path.exists():
        print(f"错误: 文件夹不存在: {manual_check_path}")
        return

    # 获取所有图片文件
    image_files = (
        list(manual_check_path.glob("*.png"))
        + list(manual_check_path.glob("*.jpg"))
        + list(manual_check_path.glob("*.jpeg"))
    )

    if not image_files:
        print(f"没有找到需要处理的图片")
        return

    print(f"找到 {len(image_files)} 张需要旋转的图片\n")

    for idx, img_file in enumerate(image_files, 1):
        print(f"[{idx}/{len(image_files)}] 处理: {img_file.name}")

        # 读取图片
        img = Image.open(img_file)

        # 旋转180度
        img_rotated = img.rotate(180, expand=True)

        # 保存到主输出文件夹
        output_file = output_path / img_file.name
        img_rotated.save(output_file)

        print(f"  ✓ 已旋转180度并保存至: {output_file}")

        # 删除原文件
        img_file.unlink()
        print(f"  ✓ 已删除原文件")
        print()

    print("=" * 70)
    print(f"完成！所有 {len(image_files)} 张图片已旋转180度并移动到主输出文件夹")

    # 检查manual_check文件夹是否为空
    remaining_files = list(manual_check_path.glob("*"))
    if not remaining_files:
        print(f"\nmanual_check 文件夹已清空")


def main():
    print("=" * 70)
    print("修复人工检查文件夹中的图片（旋转180度）")
    print("=" * 70)
    print()

    # 确认操作
    response = input("确认要将 manual_check 文件夹中的所有图片旋转180度吗？(y/n): ")

    if response.lower() == "y":
        rotate_images_180()
    else:
        print("操作已取消")


if __name__ == "__main__":
    main()
