# Nano Banana Image Generator - Dify Plugin

A Dify tool plugin for generating and editing images with Google Gemini's
[Nano Banana image generation models](https://ai.google.dev/gemini-api/docs/image-generation).

## Features

- Text-to-image generation with `Generate Image`
- Image editing with `Edit Image`
- Gemini API key credential validation
- Optional Google Search grounding for Gemini 3 image models
- Blob image output for Dify workflows and agents

## Models

| Plugin option | Gemini model ID | Best for |
| ------------- | --------------- | -------- |
| `nano_banana` | `gemini-2.5-flash-image` | Legacy Nano Banana, fast 1024px workflows, up to 3 input images |
| `nano_banana_2` | `gemini-3.1-flash-image` | Default all-around model, up to 14 reference images, 512/1K/2K/4K output |
| `nano_banana_pro` | `gemini-3-pro-image` | Highest quality, thinking, precise text rendering, Google Search grounding, up to 4K |

The previous `gemini-3-pro-image-preview` model is deprecated by Google and is
not used by this plugin release.

## Setup

1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Install this plugin in your Dify instance from GitHub or a `.difypkg`.
3. Configure the Gemini API Key in the plugin settings.

## Usage

Use **Generate Image** for text-to-image:

- **Prompt**: the image prompt
- **Model**: Nano Banana, Nano Banana 2, or Nano Banana Pro
- **Aspect Ratio**: optional output ratio
- **Image Size**: optional output resolution for Nano Banana 2 and Pro
- **Google Search Grounding**: optional for current facts or real-world data

Use **Edit Image** for image-to-image:

- **Input Images**: `Array[File]` from upstream Dify nodes
- **Edit Prompt**: natural-language edit instruction
- **Model**: Nano Banana supports up to 3 images; Nano Banana 2 and Pro support up to 14 reference images
- **Aspect Ratio / Image Size / Google Search Grounding**: optional output controls

## Development

Run the plugin locally:

```bash
python -m main
```

Package the plugin:

```bash
dify plugin package ./nano_banana_generator
```

## License

MIT
