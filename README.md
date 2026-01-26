# 🚀 Gemini Usage Analytics

A high-performance visual dashboard for tracking your Gemini CLI usage, token consumption, and estimated API costs.

![Uploading image.png…]()

## ✨ Features

- **Project-Specific Tracking**: Automatically resolves cryptic project hashes to actual folder names using your `trustedFolders.json`.
- **Token Breakdown**: Detailed analysis of Input, Output, and Cached tokens.
- **Cost Estimation**: Estimates API spend based on real-time Gemini pricing models (3.0 Pro/Flash, 2.5 Pro/Flash, etc.).
- **Interactive Visuals**: Beautiful charts for daily spending trends, cost by model, and usage breakdown by project.
- **Zero Configuration**: Just run it, and it finds your Gemini logs automatically.

## 🚀 Quick Start

No installation required! Just run this command in your terminal:

```bash
npx github:ayman-beep/gemini-usage-stats
```

The dashboard will be generated and **automatically open in your default browser**.

## 🛠 Prerequisites

- **Python 3.x** must be installed and available in your system path.
- **Node.js** (for npx support).

## 📂 How it Works

The tool works by:
1. Scanning your local Gemini cache directory (`~/.gemini/tmp`).
2. Mapping project hashes to directory paths found in `~/.gemini/trustedFolders.json`.
3. Aggregating usage statistics from session JSON files.
4. Generating a responsive, Tailwind-powered HTML dashboard.

## 📄 License

MIT © Your Name
