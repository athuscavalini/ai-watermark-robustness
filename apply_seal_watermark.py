#!/usr/bin/env python3

import videoseal
from PIL import Image
import torchvision.transforms as T
import pandas as pd
from pathlib import Path
import random

# Load Seal model
print("Carregando modelo Seal...")
import os
# Usar caminho absoluto para o model card
model_card_path = Path(os.path.dirname(videoseal.__file__)) / 'cards' / 'videoseal_1.0.yaml'
print(f"Caminho do modelo: {model_card_path}")
model = videoseal.load(model_card_path)

# Paths
captions_file = Path('flickr8/captions.txt')
source_images_dir = Path('flickr8/Images')
output_dir = Path('seal')
output_dir.mkdir(exist_ok=True)

print(f"\nLendo captions de {captions_file}...")
df = pd.read_csv(captions_file)

# Obter lista de imagens únicas
unique_images = df['image'].unique().tolist()

# Selecionar 20 imagens aleatórias
random.seed(42)  # Para reprodutibilidade
selected_images = random.sample(unique_images, 20)

print(f"\nTotal de imagens selecionadas: {len(selected_images)}")
print(f"Diretório de saída: {output_dir.absolute()}\n")

success_count = 0
error_count = 0

for idx, image_name in enumerate(selected_images, 1):
    input_path = source_images_dir / image_name
    output_path = output_dir / image_name

    # Pular se já existe
    if output_path.exists():
        print(f"[{idx}/{len(selected_images)}] Pulando (já existe): {image_name}")
        success_count += 1
        continue

    try:
        print(f"[{idx}/{len(selected_images)}] Processando: {image_name}")

        # Carregar imagem
        img = Image.open(input_path)

        # Converter para RGB se necessário
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Converter para tensor
        img_tensor = T.ToTensor()(img).unsqueeze(0)

        # Aplicar watermark
        outputs = model.embed(img_tensor)

        # Salvar imagem com watermark
        watermarked_img = T.ToPILImage()(outputs["imgs_w"][0])
        watermarked_img.save(output_path)

        print(f"  ✓ Watermark aplicado com sucesso\n")
        success_count += 1

    except Exception as e:
        print(f"  ✗ Erro: {str(e)}\n")
        error_count += 1

print("\n" + "="*60)
print("Resumo:")
print(f"  Imagens processadas com sucesso: {success_count}/{len(selected_images)}")
print(f"  Erros: {error_count}/{len(selected_images)}")
print(f"  Diretório de saída: {output_dir.absolute()}")
print("="*60)
