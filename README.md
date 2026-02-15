# Nano Banana Image Editor - Dify Plugin

A Dify tool plugin for editing images using Google Gemini's [Nano Banana](https://ai.google.dev/gemini-api/docs/image-generation) image generation capabilities.

## Features

- ✏️ **Image Editing** — Edit existing images with natural language instructions
- 🔄 **Dual Model Support** — Switch between two Gemini models:

| Model           | Model ID                     | Best For                                        |
| --------------- | ---------------------------- | ----------------------------------------------- |
| Nano Banana     | `gemini-2.5-flash-image`     | Fast editing, low latency                       |
| Nano Banana Pro | `gemini-3-pro-image-preview` | High quality, 4K output, precise text rendering |

## Setup

1. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Install this plugin in your Dify instance (via GitHub or `.difypkg` upload)
3. Configure the Gemini API Key in the plugin settings

## Usage

In a Dify workflow or agent, use the **Edit Image** tool:

- **Input Images** — Accepts `Array[File]` from upstream nodes
- **Edit Prompt** — Natural language instruction (e.g. "Remove the background", "Make it look like a watercolor painting")
- **Model** — Choose Flash (fast) or Pro (high quality)
- **Aspect Ratio** — Optional, defaults to matching input
- **Image Size** — 1K / 2K / 4K (Pro model only)

## License

MIT
