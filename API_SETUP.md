# API Configuration Guide

This guide shows you how to configure the AI Code Generator with different LLM providers.

## Quick Setup

You only need to set up **ONE** of the following options in your `.env` file.

---

## Option 1: OpenRouter (Recommended for flexibility)

[OpenRouter](https://openrouter.ai/) provides access to multiple models from different providers with a single API key.

### Setup:

1. Get API key from [openrouter.ai](https://openrouter.ai/)
2. Add to `.env`:

```env
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_API_KEY=sk-or-v1-your-key-here
OPENAI_MODEL=anthropic/claude-3.5-sonnet
```

### Popular Models on OpenRouter:

```env
# Anthropic Claude
OPENAI_MODEL=anthropic/claude-3.5-sonnet
OPENAI_MODEL=anthropic/claude-3-opus

# OpenAI
OPENAI_MODEL=openai/gpt-4-turbo
OPENAI_MODEL=openai/gpt-4
OPENAI_MODEL=openai/gpt-3.5-turbo

# Meta Llama
OPENAI_MODEL=meta-llama/llama-3-70b-instruct

# Google
OPENAI_MODEL=google/gemini-pro

# Mistral
OPENAI_MODEL=mistralai/mixtral-8x7b-instruct
```

**Benefits:**
- Access to 100+ models with one API key
- Pay-as-you-go pricing
- Automatic fallbacks
- Cost optimization

---

## Option 2: Anthropic Claude (Direct)

Use Anthropic's API directly for Claude models.

### Setup:

1. Get API key from [console.anthropic.com](https://console.anthropic.com/)
2. Add to `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929
```

### Available Models:

```env
# Latest Sonnet (recommended)
ANTHROPIC_MODEL=claude-sonnet-4-5-20250929

# Claude 3.5 Sonnet
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Claude 3 Opus (most capable)
ANTHROPIC_MODEL=claude-3-opus-20240229

# Claude 3 Haiku (fastest, cheapest)
ANTHROPIC_MODEL=claude-3-haiku-20240307
```

**Benefits:**
- Direct access to Claude
- Official API support
- Latest features first

---

## Option 3: OpenAI (Direct)

Use OpenAI's official API.

### Setup:

1. Get API key from [platform.openai.com](https://platform.openai.com/api-keys)
2. Add to `.env`:

```env
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo
```

### Available Models:

```env
# GPT-4 Turbo (recommended)
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MODEL=gpt-4-1106-preview

# GPT-4
OPENAI_MODEL=gpt-4

# GPT-3.5 Turbo (cheaper)
OPENAI_MODEL=gpt-3.5-turbo
```

**Benefits:**
- Official OpenAI models
- Established ecosystem
- Wide adoption

---

## Option 4: Local Models with vLLM

Run models locally using [vLLM](https://github.com/vllm-project/vllm) for complete privacy and no API costs.

### Setup:

1. Install and run vLLM server:

```bash
# Install vLLM
pip install vllm

# Run a model (example: Llama 2 70B)
vllm serve meta-llama/Llama-2-70b-chat-hf \
  --host 0.0.0.0 \
  --port 8000
```

2. Add to `.env`:

```env
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=dummy
OPENAI_MODEL=meta-llama/Llama-2-70b-chat-hf
```

### Recommended Models for Code Generation:

```env
# Code Llama (specialized for code)
OPENAI_MODEL=codellama/CodeLlama-34b-Instruct-hf

# Llama 2
OPENAI_MODEL=meta-llama/Llama-2-70b-chat-hf

# Mistral
OPENAI_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1

# DeepSeek Coder (excellent for code)
OPENAI_MODEL=deepseek-ai/deepseek-coder-33b-instruct
```

**Benefits:**
- Complete privacy (no data sent externally)
- No API costs
- Full control over model
- No rate limits

---

## Option 5: Other OpenAI-Compatible Services

Many services provide OpenAI-compatible APIs:

### Groq (Fast inference)

```env
OPENAI_BASE_URL=https://api.groq.com/openai/v1
OPENAI_API_KEY=gsk_your-key-here
OPENAI_MODEL=mixtral-8x7b-32768
```

### Together AI

```env
OPENAI_BASE_URL=https://api.together.xyz/v1
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=mistralai/Mixtral-8x7B-Instruct-v0.1
```

### Anyscale

```env
OPENAI_BASE_URL=https://api.endpoints.anyscale.com/v1
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=meta-llama/Llama-2-70b-chat-hf
```

---

## Advanced Configuration

### Temperature Control

Adjust creativity vs. consistency:

```env
# More deterministic (recommended for code)
LLM_TEMPERATURE=0.0

# Balanced (default)
LLM_TEMPERATURE=0.7

# More creative
LLM_TEMPERATURE=1.0
```

### Token Limits

Control response length:

```env
# Default (good for most code)
LLM_MAX_TOKENS=8192

# For smaller responses
LLM_MAX_TOKENS=4096

# For larger projects
LLM_MAX_TOKENS=16384
```

---

## Cost Comparison

Approximate costs per 1M tokens (as of 2024):

| Provider | Model | Input | Output |
|----------|-------|-------|--------|
| Anthropic | Claude 3.5 Sonnet | $3 | $15 |
| OpenAI | GPT-4 Turbo | $10 | $30 |
| OpenAI | GPT-3.5 Turbo | $0.50 | $1.50 |
| OpenRouter | (varies) | $0.20-$30 | $0.60-$90 |
| Local vLLM | Any | **$0** | **$0** |

*Prices vary; check provider websites for current pricing.*

---

## Troubleshooting

### "No API configuration found"

Make sure you've set **either**:
- `OPENAI_BASE_URL` + `OPENAI_API_KEY`, **or**
- `ANTHROPIC_API_KEY`

### Connection errors

1. Check your internet connection
2. Verify the base URL is correct
3. Test your API key with curl:

```bash
# Test OpenRouter
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Test Anthropic
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY"
```

### Model not found

- Verify the model name is correct
- Check if you have access to that model
- Try a different model from the same provider

### Rate limits

- Anthropic/OpenAI: Wait and retry (they have built-in rate limits)
- OpenRouter: Increase rate limits in your account
- Local: No rate limits!

---

## Best Practices

### For Development

Use cheaper/faster models:
```env
# OpenRouter with Claude 3 Haiku
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=anthropic/claude-3-haiku
```

### For Production

Use more capable models:
```env
# OpenRouter with Claude 3.5 Sonnet
OPENAI_BASE_URL=https://openrouter.ai/api/v1
OPENAI_MODEL=anthropic/claude-3.5-sonnet
```

### For Privacy

Use local models:
```env
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_MODEL=deepseek-ai/deepseek-coder-33b-instruct
```

---

## Switching Providers

To switch providers, just update your `.env` file:

```bash
# Stop the current session
# Edit .env with new provider settings
# Restart the application

python main.py  # CLI
# or
python app.py   # Web
```

The system automatically detects and uses the new configuration!

---

## Need Help?

- Check the main [README.md](README.md) for general setup
- See [QUICKSTART.md](QUICKSTART.md) for a quick guide
- Review [.env.example](.env.example) for configuration templates

**Ready to generate code!** 🚀
