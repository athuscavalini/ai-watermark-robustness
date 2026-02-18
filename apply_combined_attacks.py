#!/usr/bin/env python3

from PIL import Image, ImageFilter
import numpy as np
from pathlib import Path
import io

# Importar funções de ataque do script anterior
def jpeg_compression(img, quality):
    """Compressão JPEG com qualidade variável"""
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=quality)
    buffer.seek(0)
    return Image.open(buffer).copy()

def resize_attack(img, scale_factor=0.5):
    """Downscale seguido de upscale"""
    original_size = img.size
    new_size = (int(img.width * scale_factor), int(img.height * scale_factor))
    img_small = img.resize(new_size, Image.LANCZOS)
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

    cropped = img.crop((left, top, right, bottom))
    # Resize de volta ao tamanho original para facilitar comparação
    return cropped.resize((width, height), Image.LANCZOS)

def screenshot_simulation(img):
    """Simula screenshot: reencode + blur leve"""
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_reencoded = Image.open(buffer).copy()
    img_blurred = img_reencoded.filter(ImageFilter.GaussianBlur(radius=0.5))
    return img_blurred

def gaussian_noise(img, sigma=10):
    """Adiciona ruído gaussiano"""
    img_array = np.array(img)
    noise = np.random.normal(0, sigma, img_array.shape)
    noisy_img = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy_img)

def process_combined_attacks(source_dir, output_base_dir):
    """
    Aplica combinações de ataques que simulam cenários reais
    """
    source_path = Path(source_dir)
    output_path = Path(output_base_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Definir cenários de ataques compostos (ordem importa!)
    combined_attacks = {
        # Cenário 1: Compartilhamento em redes sociais
        'social_light': [
            ('JPEG 75', lambda img: jpeg_compression(img, 75)),
            ('Screenshot', screenshot_simulation),
        ],
        'social_heavy': [
            ('JPEG 50', lambda img: jpeg_compression(img, 50)),
            ('Resize 75%', lambda img: resize_attack(img, 0.75)),
            ('JPEG 50', lambda img: jpeg_compression(img, 50)),
        ],

        # Cenário 2: Screenshot + manipulação
        'screenshot_crop': [
            ('Screenshot', screenshot_simulation),
            ('Crop 10%', lambda img: crop_attack(img, 10)),
            ('JPEG 75', lambda img: jpeg_compression(img, 75)),
        ],
        'screenshot_heavy': [
            ('Screenshot', screenshot_simulation),
            ('Crop 25%', lambda img: crop_attack(img, 25)),
            ('JPEG 50', lambda img: jpeg_compression(img, 50)),
        ],

        # Cenário 3: Ataque intencional (múltiplas transformações)
        'intentional_light': [
            ('Resize 75%', lambda img: resize_attack(img, 0.75)),
            ('Noise', lambda img: gaussian_noise(img, sigma=5)),
            ('JPEG 50', lambda img: jpeg_compression(img, 50)),
        ],
        'intentional_heavy': [
            ('Resize 50%', lambda img: resize_attack(img, 0.5)),
            ('Crop 10%', lambda img: crop_attack(img, 10)),
            ('Noise', lambda img: gaussian_noise(img, sigma=10)),
            ('JPEG 30', lambda img: jpeg_compression(img, 30)),
        ],

        # Cenário 4: Degradação progressiva (como imagem viral)
        'viral_repost': [
            ('JPEG 75', lambda img: jpeg_compression(img, 75)),
            ('Screenshot', screenshot_simulation),
            ('Crop 5%', lambda img: crop_attack(img, 5)),
            ('JPEG 65', lambda img: jpeg_compression(img, 65)),
            ('JPEG 50', lambda img: jpeg_compression(img, 50)),
        ],

        # Cenário 5: Resize extremo (thumbnail)
        'thumbnail': [
            ('Resize 25%', lambda img: resize_attack(img, 0.25)),
            ('JPEG 75', lambda img: jpeg_compression(img, 75)),
        ],

        # Cenário 6: Crop + compressão (típico de edição rápida)
        'crop_compress_light': [
            ('Crop 15%', lambda img: crop_attack(img, 15)),
            ('JPEG 60', lambda img: jpeg_compression(img, 60)),
        ],
        'crop_compress_heavy': [
            ('Crop 30%', lambda img: crop_attack(img, 30)),
            ('JPEG 40', lambda img: jpeg_compression(img, 40)),
        ],
    }

    # Criar subdiretórios
    for scenario_name in combined_attacks.keys():
        (output_path / scenario_name).mkdir(exist_ok=True)

    # Processar imagens
    images = list(source_path.glob('*.jpg')) + list(source_path.glob('*.png'))
    total = len(images)

    print(f"Processando {total} imagens com {len(combined_attacks)} cenários de ataque...")
    print(f"Diretório fonte: {source_path.absolute()}")
    print(f"Diretório destino: {output_path.absolute()}\n")

    for idx, img_path in enumerate(images, 1):
        print(f"[{idx}/{total}] Processando: {img_path.name}")

        try:
            img = Image.open(img_path)

            # Converter para RGB se necessário
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Aplicar cada cenário de ataque composto
            for scenario_name, attack_sequence in combined_attacks.items():
                try:
                    # Aplicar ataques em sequência
                    result_img = img.copy()
                    attack_names = []

                    for attack_name, attack_func in attack_sequence:
                        result_img = attack_func(result_img)
                        attack_names.append(attack_name)

                    # Salvar resultado
                    output_file = output_path / scenario_name / img_path.name
                    result_img.save(output_file, quality=95)

                    print(f"  ✓ {scenario_name}: {' → '.join(attack_names)}")

                except Exception as e:
                    print(f"  ✗ Erro no cenário {scenario_name}: {e}")

            print()

        except Exception as e:
            print(f"  ✗ Erro ao processar imagem: {e}\n")

    print("\n" + "="*60)
    print("Resumo:")
    print(f"  Imagens processadas: {total}")
    print(f"  Cenários de ataque composto: {len(combined_attacks)}")
    print(f"  Total de imagens geradas: {total * len(combined_attacks)}")
    print(f"  Diretório de saída: {output_path.absolute()}")
    print("="*60)

    # Imprimir descrição dos cenários
    print("\n" + "="*60)
    print("Descrição dos Cenários:")
    print("="*60)
    print("\n1. social_light: Compartilhamento básico em rede social")
    print("2. social_heavy: Múltiplos compartilhamentos + redimensionamento")
    print("3. screenshot_crop: Screenshot + edição leve")
    print("4. screenshot_heavy: Screenshot + edição pesada")
    print("5. intentional_light: Tentativa leve de remoção")
    print("6. intentional_heavy: Tentativa agressiva de remoção")
    print("7. viral_repost: Simulação de conteúdo viral (múltiplos reposts)")
    print("8. thumbnail: Redução extrema de tamanho")
    print("9. crop_compress_light: Edição rápida básica")
    print("10. crop_compress_heavy: Edição rápida agressiva")

if __name__ == '__main__':
    import sys

    source_dir = sys.argv[1] if len(sys.argv) > 1 else 'seal'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else f'{source_dir}_combined_attacks'

    print("="*60)
    print("Simulação de Ataques Compostos")
    print("="*60 + "\n")

    process_combined_attacks(source_dir, output_dir)
