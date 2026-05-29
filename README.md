# Nano Banana Image Editor - Dify Plugin

A Dify tool plugin for editing images using Google Gemini's
[Nano Banana image generation models](https://ai.google.dev/gemini-api/docs/image-generation).

## Features

- Image editing with `Edit Image`
- Gemini API key credential validation
- Blob image output for Dify workflows and agents

## Models

| Plugin option | Gemini model ID | Best for |
| ------------- | --------------- | -------- |
| `nano_banana` | `gemini-2.5-flash-image` | Fast editing, up to 3 input images |
| `nano_banana_2` | `gemini-3.1-flash-image` | General editing, up to 14 input images, 512/1K/2K/4K output |
| `nano_banana_pro` | `gemini-3-pro-image` | Highest quality editing, up to 14 input images, 1K/2K/4K output |

The plugin only exposes the **Edit Image** tool. It uses the same simple
`v1beta/models/{model}:generateContent` request shape as the original `0.0.2`
release, with Nano Banana 2 added as an edit model option.

## Setup

1. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).
2. Install this plugin in your Dify instance from GitHub or a `.difypkg`.
3. Configure the Gemini API Key in the plugin settings.

## Usage

Use **Edit Image** for image-to-image:

- **Input Images**: `Array[File]` from upstream Dify nodes
- **Edit Prompt**: natural-language edit instruction
- **Model**: Nano Banana, Nano Banana 2, or Nano Banana Pro
- **Aspect Ratio**: optional output ratio
- **Image Size**: optional output resolution for Nano Banana 2 and Pro

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
