#!/usr/bin/env python3

from google import genai
from google.genai import types
from PIL import Image
import pandas as pd
from pathlib import Path
import time
import os

api_key = os.getenv('GEMINI_API_KEY')
client = genai.Client(api_key=api_key)

# Paths
captions_file = Path('flickr8/captions.txt')
output_dir = Path('gemini')
output_dir.mkdir(exist_ok=True)

print(f"Lendo captions de {captions_file}...")
df = pd.read_csv(captions_file)

# Agrupar por imagem e pegar a primeira caption de cada
unique_images = df.groupby('image').first().reset_index()

# Verificar imagens já geradas
already_generated = [f.name for f in output_dir.glob('*.jpg')]
print(f"Imagens já geradas: {len(already_generated)}")

# Filtrar imagens já geradas
unique_images = unique_images[~unique_images['image'].isin(already_generated)]

# Calcular quantas faltam para chegar a 20
target_total = 20
needed = target_total - len(already_generated)

if needed <= 0:
    print(f"Já temos {len(already_generated)} imagens. Nada a fazer.")
    exit(0)

# Selecionar apenas as imagens necessárias
unique_images = unique_images.sample(n=min(needed, len(unique_images)), random_state=42)

total_images = len(unique_images)

print(f"\nTotal de imagens a gerar: {total_images}")
print(f"Diretório de saída: {output_dir.absolute()}\n")
input("Pressione Enter para começar...")

success_count = 0
error_count = 0

for idx, row in unique_images.iterrows():
    image_name = row['image']
    caption = row['caption']
    output_path = output_dir / image_name

    # Pular se já existe
    if output_path.exists():
        print(f"[{idx+1}/{total_images}] Pulando (já existe): {image_name}")
        success_count += 1
        continue

    try:
        print(f"[{idx+1}/{total_images}] Gerando: {image_name}")
        print(f"  Caption: {caption[:80]}...")

        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=[caption],
        )

        # Salvar imagem
        image_saved = False
        for part in response.parts:
            if part.text is not None:
                pass  # Ignorar texto
            elif part.inline_data is not None:
                image = part.as_image()
                image.save(str(output_path))
                print(f"  ✓ Salva com sucesso\n")
                success_count += 1
                image_saved = True
                break

        if not image_saved:
            print(f"  ✗ Nenhuma imagem retornada\n")
            error_count += 1

        # Rate limiting
        time.sleep(1)

    except Exception as e:
        print(f"  ✗ Erro: {str(e)}\n")
        error_count += 1

        # Se for erro de rate limit, esperar mais
        if "quota" in str(e).lower() or "rate" in str(e).lower():
            print("  Aguardando 10 segundos...")
            time.sleep(10)

print("\n" + "="*60)
print("Resumo:")
print(f"  Imagens geradas com sucesso: {success_count}/{total_images}")
print(f"  Erros: {error_count}/{total_images}")
print(f"  Diretório de saída: {output_dir.absolute()}")
print("="*60)