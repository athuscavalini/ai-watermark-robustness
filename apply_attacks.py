#!/usr/bin/env python3

from PIL import Image, ImageFilter
import numpy as np
from pathlib import Path
import io

def jpeg_compression(img, quality):
    """Compressão JPEG com qualidade variável"""
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=quality)
    buffer.seek(0)
    return Image.open(buffer)

def resize_attack(img, scale_factor=0.5):
    """Downscale seguido de upscale"""
    original_size = img.size
    # Downscale
    new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
    img_small = img.resize(new_size, Image.LANCZOS)
    # Upscale de volta
    img_restored = img_small.resize(original_size, Image.LANCZOS)
    return img_restored

def crop_attack(img, crop_percentage):
    """Crop central (remove bordas)"""
    width, height = img.size
    crop_size = crop_percentage / 100

    left = int(width * crop_size / 2)
    top = int(height * crop_size / 2)
    right = width - left
    bottom = height - top

    return img.crop((left, top, right, bottom))

def screenshot_simulation(img):
    """Simula screenshot: reencode + blur leve"""
    # Reencode como PNG
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_reencoded = Image.open(buffer)

    # Blur muito leve
    img_blurred = img_reencoded.filter(ImageFilter.GaussianBlur(radius=0.5))
    return img_blurred

def gaussian_noise(img, sigma=10):
    """Adiciona ruído gaussiano"""
    img_array = np.array(img)
    noise = np.random.normal(0, sigma, img_array.shape)
    noisy_img = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy_img)

def process_attacks(source_dir, output_base_dir):
    """
    Aplica todos os ataques em todas as imagens do diretório fonte
    """
    source_path = Path(source_dir)
    output_path = Path(output_base_dir)

    # Definir ataques
    attacks = {
        'jpeg_95': lambda img: jpeg_compression(img, 95),
        'jpeg_75': lambda img: jpeg_compression(img, 75),
        'jpeg_50': lambda img: jpeg_compression(img, 50),
        'jpeg_30': lambda img: jpeg_compression(img, 30),
        'resize_50': lambda img: resize_attack(img, 0.5),
        'resize_75': lambda img: resize_attack(img, 0.75),
        'crop_10': lambda img: crop_attack(img, 10),
        'crop_25': lambda img: crop_attack(img, 25),
        'crop_40': lambda img: crop_attack(img, 40),
        'screenshot': lambda img: screenshot_simulation(img),
        'noise_light': lambda img: gaussian_noise(img, sigma=5),
        'noise_medium': lambda img: gaussian_noise(img, sigma=10),
    }

    # Criar diretórios de saída
    for attack_name in attacks.keys():
        (output_path / attack_name).mkdir(parents=True, exist_ok=True)

    # Processar imagens
    images = list(source_path.glob('*.jpg')) + list(source_path.glob('*.png'))
    total = len(images)

    print(f"Processando {total} imagens com {len(attacks)} ataques...")
    print(f"Diretório fonte: {source_path.absolute()}")
    print(f"Diretório destino: {output_path.absolute()}\n")

    for idx, img_path in enumerate(images, 1):
        print(f"[{idx}/{total}] Processando: {img_path.name}")

        try:
            img = Image.open(img_path)

            # Converter para RGB se necessário
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Aplicar cada ataque
            for attack_name, attack_func in attacks.items():
                try:
                    attacked_img = attack_func(img.copy())
                    output_file = output_path / attack_name / img_path.name
                    attacked_img.save(output_file)
                except Exception as e:
                    print(f"  ✗ Erro no ataque {attack_name}: {e}")

            print(f"  ✓ {len(attacks)} ataques aplicados\n")

        except Exception as e:
            print(f"  ✗ Erro ao processar imagem: {e}\n")

    print("\n" + "="*60)
    print("Resumo:")
    print(f"  Imagens processadas: {total}")
    print(f"  Ataques por imagem: {len(attacks)}")
    print(f"  Total de imagens geradas: {total * len(attacks)}")
    print(f"  Diretório de saída: {output_path.absolute()}")
    print("="*60)

if __name__ == '__main__':
    import sys

    # Pode passar o diretório fonte como argumento ou usar seal/ por padrão
    source_dir = sys.argv[1] if len(sys.argv) > 1 else 'seal'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else f'{source_dir}_attacks'

    print("="*60)
    print("Simulação de Ataques para Teste de Robustez")
    print("="*60 + "\n")

    process_attacks(source_dir, output_dir)
