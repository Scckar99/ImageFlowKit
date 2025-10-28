"""
图片方向矫正工具
基于参考图片的结构相似度（SSIM）方法自动检测并矫正图片方向
"""

import cv2
import numpy as np
from pathlib import Path
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import sys
import io

# 设置Windows控制台输出编码为UTF-8
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# 相似度差异阈值：如果最佳角度与次佳角度的相似度差异小于此值，标记为需要人工检查
SIMILARITY_THRESHOLD = 0.015  # 1.5%的差异阈值


def calculate_similarity(img1, img2):
    """
    计算两张图片的结构相似度

    Args:
        img1: 第一张图片（numpy数组）
        img2: 第二张图片（numpy数组）

    Returns:
        float: 相似度分数（0-1之间）
    """
    # 统一尺寸（缩小以加快计算速度）
    target_size = (400, 400)
    img1_resized = cv2.resize(img1, target_size)
    img2_resized = cv2.resize(img2, target_size)

    # 转为灰度图
    if len(img1_resized.shape) == 3:
        img1_gray = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
    else:
        img1_gray = img1_resized

    if len(img2_resized.shape) == 3:
        img2_gray = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)
    else:
        img2_gray = img2_resized

    # 计算结构相似度
    similarity = ssim(img1_gray, img2_gray)
    return similarity


def imread_chinese(image_path):
    """
    读取包含中文路径的图片

    Args:
        image_path: 图片路径

    Returns:
        numpy数组格式的图片（BGR格式）
    """
    # 使用PIL读取图片，然后转换为OpenCV格式
    img_pil = Image.open(image_path)
    img_rgb = np.array(img_pil)

    # 如果是RGBA，转换为RGB
    if img_rgb.shape[-1] == 4:
        img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_RGBA2RGB)

    # PIL是RGB，OpenCV是BGR，需要转换
    if len(img_rgb.shape) == 3:
        img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    else:
        img_bgr = img_rgb

    return img_bgr


def find_correct_rotation(image_path, reference_img):
    """
    通过与参考图片对比，找到正确的旋转角度

    Args:
        image_path: 待检测图片路径
        reference_img: 参考图片（numpy数组）

    Returns:
        tuple: (最佳角度, 最佳相似度, 相似度字典, 是否需要人工检查)
    """
    # 读取待检测图片（支持中文路径）
    try:
        test_img = imread_chinese(image_path)
    except Exception as e:
        print(f"  ✗ 无法读取图片: {image_path}, 错误: {e}")
        return 0, 0, {}, False

    # 尝试4个角度（0, 90, 180, 270度）
    best_angle = 0
    best_similarity = 0
    similarity_scores = {}

    for angle in [0, 90, 180, 270]:
        # 旋转图片
        if angle == 0:
            rotated = test_img
        elif angle == 90:
            rotated = cv2.rotate(test_img, cv2.ROTATE_90_CLOCKWISE)
        elif angle == 180:
            rotated = cv2.rotate(test_img, cv2.ROTATE_180)
        else:  # 270
            rotated = cv2.rotate(test_img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # 计算与参考图片的相似度
        similarity = calculate_similarity(reference_img, rotated)
        similarity_scores[angle] = similarity

        if similarity > best_similarity:
            best_similarity = similarity
            best_angle = angle

    # 检查相似度差异是否足够大
    sorted_similarities = sorted(similarity_scores.values(), reverse=True)
    second_best_similarity = (
        sorted_similarities[1] if len(sorted_similarities) > 1 else 0
    )
    similarity_diff = best_similarity - second_best_similarity

    # 如果最佳和次佳相似度太接近，标记为需要人工检查
    needs_manual_check = similarity_diff < SIMILARITY_THRESHOLD

    return best_angle, best_similarity, similarity_scores, needs_manual_check


def batch_correct_with_template(input_folder, output_folder, reference_image):
    """
    批量矫正图片方向

    Args:
        input_folder: 输入文件夹路径
        output_folder: 输出文件夹路径
        reference_image: 参考图片路径
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    manual_check_path = Path(output_folder) / "manual_check"

    # 创建输出文件夹
    output_path.mkdir(exist_ok=True)
    manual_check_path.mkdir(exist_ok=True)

    # 读取参考图片（支持中文路径）
    print(f"正在加载参考图片: {reference_image}")
    try:
        reference_img = imread_chinese(reference_image)
    except Exception as e:
        print(f"错误: 无法读取参考图片 {reference_image}")
        print(f"错误信息: {e}")
        return

    print(f"参考图片尺寸: {reference_img.shape[1]} x {reference_img.shape[0]}")
    print(f"输入文件夹: {input_folder}")
    print(f"输出文件夹: {output_folder}")
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
    corrected_count = 0
    already_correct_count = 0
    failed_count = 0
    manual_check_count = 0

    # 处理每张图片
    for idx, img_file in enumerate(image_files, 1):
        print(f"[{idx}/{len(image_files)}] 处理: {img_file.name}")

        # 查找最佳旋转角度
        angle, similarity, scores, needs_manual_check = find_correct_rotation(
            str(img_file), reference_img
        )

        # 显示所有角度的相似度
        print(f"  相似度分析:")
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        for deg in [0, 90, 180, 270]:
            marker = "★" if deg == angle else " "
            print(f"    {marker} {deg:3d}°: {scores[deg]:.4f}")

        # 显示相似度差异
        similarity_diff = sorted_scores[0][1] - sorted_scores[1][1]
        print(f"  相似度差异: {similarity_diff:.4f} (阈值: {SIMILARITY_THRESHOLD})")

        # 读取并旋转图片（使用PIL以保持高质量）
        img = Image.open(img_file)

        if angle != 0:
            # PIL的旋转是逆时针，OpenCV是顺时针，需要转换
            pil_angle = 360 - angle if angle != 0 else 0
            img_rotated = img.rotate(pil_angle, expand=True)
            corrected_count += 1
            status_msg = f"  ✓ 已矫正: 旋转 {angle}° (相似度: {similarity:.4f})"
        else:
            img_rotated = img
            already_correct_count += 1
            status_msg = f"  ✓ 方向正确: 无需旋转 (相似度: {similarity:.4f})"

        # 判断是否需要人工检查
        if needs_manual_check:
            manual_check_count += 1
            output_file = manual_check_path / img_file.name
            print(f"  ⚠️  警告: 多个角度相似度接近，建议人工检查！")
            print(status_msg)
            print(f"  保存至人工检查文件夹: {output_file}")
        else:
            output_file = output_path / img_file.name
            print(status_msg)
            print(f"  保存至: {output_file}")

        # 保存图片
        img_rotated.save(output_file)
        print()

    # 显示统计结果
    print("=" * 70)
    print("处理完成！")
    print(f"总计: {len(image_files)} 张图片")
    print(f"  - 已矫正: {corrected_count} 张")
    print(f"  - 本身正确: {already_correct_count} 张")
    print(f"  - 需要人工检查: {manual_check_count} 张 ⚠️")
    print(f"  - 失败: {failed_count} 张")
    print(f"\n所有图片已保存至: {output_path.absolute()}")

    if manual_check_count > 0:
        print(f"\n⚠️  注意：有 {manual_check_count} 张图片因相似度差异过小，已保存到：")
        print(f"   {manual_check_path.absolute()}")
        print(f"   请人工检查这些图片的方向是否正确！")


def main():
    """主函数"""
    # 配置参数
    reference_image = (
        "参考模板.png"
    )
    input_folder = "input"
    output_folder = "output"

    print("=" * 70)
    print("图片方向自动矫正工具")
    print("=" * 70)
    print()

    # 检查参考图片是否存在
    if not Path(reference_image).exists():
        print(f"错误: 参考图片不存在: {reference_image}")
        sys.exit(1)

    # 检查输入文件夹是否存在
    if not Path(input_folder).exists():
        print(f"错误: 输入文件夹不存在: {input_folder}")
        sys.exit(1)

    # 开始处理
    batch_correct_with_template(input_folder, output_folder, reference_image)


if __name__ == "__main__":
    main()
