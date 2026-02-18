# Image Watermark Evaluation

This project evaluates how well SynthID and SEAL models resist to common transformations that might be used to remove or obscure them. Two systems are compared:

The evaluation covers simple attacks (JPEG compression, cropping, resizing, noise, screenshot) and composite attacks simulating real-world sharing scenarios (social media, viral repost, thumbnail pipelines).

## Setup

### Requirements

```bash
pip install google-genai videoseal Pillow pandas torchvision
```
### External data

The following are **not included** in this repository due to size or licensing:

- **Flickr8k dataset** — required by `apply_seal_watermark.py` and `detect_watermark.py` (baseline negatives). Download from [Kaggle](https://www.kaggle.com/datasets/adityajn105/flickr8k) and place under `flickr8k/`:
  ```
  flickr8k/
  ├── captions.txt
  └── Images/
  ```

## Reproducing the experiments

### 1. Generate Gemini images (SynthID)

Images are already provided in `gemini/`. To regenerate from scratch, you need a Gemini API key and the Flickr8k captions:

```bash
export GEMINI_API_KEY=your_key_here
python generate_gemini_images.py
```

This generates 20 images in `gemini/`, each carrying a SynthID watermark.

### 2. Embed SEAL watermark

Images are already provided in `seal/`. To regenerate:

```bash
python apply_seal_watermark.py
```

Reads 20 images from `flickr8/Images/`, embeds a SEAL watermark via VideoSeal, and saves results to `seal/`.

### 3. Apply attacks

Attack images are already provided. To regenerate:

```bash
# Simple attacks (JPEG, crop, resize, noise, screenshot)
python apply_attacks.py

# Composite attacks (social media, screenshot+crop, viral repost, etc.)
python apply_combined_attacks.py
```

Both scripts operate on the `gemini/` and `seal/` directories and output to `gemini_attacks/`, `seal_attacks/`, `gemini_combined_attacks/`, and `seal_combined_attacks/`.

### 4. Evaluate SEAL detection

```bash
python detect_watermark.py
```

Evaluates all image sets (original, attacked) and prints detection rates. Requires `flickr8/Images/` for the false positive baseline.

Results are saved to `watermark_detection_results.csv`.

### 5. Evaluate SynthID detection

SynthID detection was performed manually via the Gemini API (prompting the model to assess whether an image carries an AI watermark).
