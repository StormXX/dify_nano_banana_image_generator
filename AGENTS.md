# AGENTS.md - Nano Banana Generator Dify 插件

## 项目概述

这是一个 Dify 工具插件，集成了 Google Gemini 的 **Nano Banana** 图像编辑能力。插件只暴露 **Edit Image** 工具，不提供 text-to-image 工具。

### 支持的模型

| 模型            | Gemini 模型 ID               | 特点                                             |
| --------------- | ---------------------------- | ------------------------------------------------ |
| Nano Banana     | `gemini-2.5-flash-image`     | 快速高效，最多 3 张输入图                        |
| Nano Banana 2   | `gemini-3.1-flash-image`     | 通用高效，最高 4K，最多 14 张输入图              |
| Nano Banana Pro | `gemini-3-pro-image`         | 高质量，最高 4K，Thinking 推理，最多 14 张输入图 |

插件沿用 `0.0.2` 的简单 `generateContent` 请求结构：单一 `v1beta` REST 端点、无 Google Search、无 Interactions API、无 endpoint fallback。

### 功能

- **图片编辑** (`edit_image`) - 提供图片文件 + 文字指令编辑图片

## 项目结构

```
nano_banana_generator/
├── manifest.yaml              # 插件元数据
├── main.py                    # Dify 插件入口
├── requirements.txt           # Python 依赖
├── _assets/icon.svg           # 插件图标
├── provider/
│   ├── nano_banana.yaml       # Provider 配置（Gemini API Key 凭证）
│   └── nano_banana.py         # 凭证验证（调用 Gemini models 端点）
└── tools/
    ├── base.py                # 共用基类（Gemini REST API 封装）
    ├── edit_image.yaml        # 图片编辑工具参数定义
    └── edit_image.py          # 图片编辑工具实现
```

## API 信息

### 端点

使用 Google Gemini 官方 REST API:

```
POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
```

### 认证

使用 `x-goog-api-key` 请求头传递 Gemini API Key。API Key 从 [Google AI Studio](https://aistudio.google.com/apikey) 获取。

### 工作方式

Gemini 图像生成是 **同步 API**：发送请求后直接返回结果（base64 编码的图片 inline_data）。不同于异步 API，无需轮询任务状态。

### 请求结构

```json
{
  "contents": [
    {
      "parts": [
        { "text": "prompt text" },
        { "inline_data": { "mime_type": "image/png", "data": "<base64>" } }
      ]
    }
  ],
  "generationConfig": {
    "responseModalities": ["TEXT", "IMAGE"],
    "imageConfig": {
      "aspectRatio": "16:9",
      "imageSize": "2K"
    }
  }
}
```

## 开发与调试

### 前置条件

- Python >= 3.12
- Dify 插件脚手架: `brew tap langgenius/dify && brew install dify`
- Gemini API Key: https://aistudio.google.com/apikey

### 调试

```bash
# 配置 .env 后
python -m main
```

### 打包

```bash
dify plugin package ./nano_banana_generator
```

## 参考文档

- [Nano Banana 图像生成 - Google 官方文档](https://ai.google.dev/gemini-api/docs/image-generation)
- [Dify 插件开发文档](https://docs.dify.ai/zh/develop-plugin/dev-guides-and-walkthroughs/tool-plugin)
