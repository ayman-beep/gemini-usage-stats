import os
import json
import glob
import hashlib
import webbrowser
from datetime import datetime
from collections import defaultdict

# Multi-CLI API Pricing (USD per 1M tokens) - Comprehensive 72+ model coverage
PRICING = {
    # ── Google Gemini models ──────────────────────────────────────────────
    "gemini-3-pro": {"input": 2.00, "output": 12.00, "cached": 0.20},
    "gemini-3-pro-preview": {"input": 2.00, "output": 12.00, "cached": 0.20},
    "gemini-3-pro-image-preview": {"input": 2.00, "output": 120.00, "cached": 0.20},
    "gemini-3-flash": {"input": 0.50, "output": 3.00, "cached": 0.05},
    "gemini-3-flash-preview": {"input": 0.50, "output": 3.00, "cached": 0.05},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00, "cached": 0.125},
    "gemini-2.5-flash": {"input": 0.30, "output": 1.20, "cached": 0.03},
    "gemini-2.5-flash-lite": {"input": 0.10, "output": 0.40, "cached": 0.01},
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40, "cached": 0.025},
    "gemini-2.0-flash-lite": {"input": 0.075, "output": 0.30, "cached": 0.02},
    "gemini-1.5-pro": {"input": 1.25, "output": 5.00, "cached": 0.3125},
    "gemini-1.5-flash": {"input": 0.075, "output": 0.30, "cached": 0.01875},

    # ── OpenAI / Codex CLI models ─────────────────────────────────────────
    # GPT-5.2 Variants
    "gpt-5.2": {"input": 1.75, "output": 14.00, "cached": 0.175},
    "gpt-5.2-instant": {"input": 1.75, "output": 14.00, "cached": 0.175},
    "gpt-5.2-thinking": {"input": 1.75, "output": 14.00, "cached": 0.175},
    "gpt-5.2-pro": {"input": 21.00, "output": 168.00, "cached": 2.10},
    "gpt-5.2-codex": {"input": 1.75, "output": 14.00, "cached": 0.175},
    # GPT-5.1 Variants
    "gpt-5.1": {"input": 1.25, "output": 10.00, "cached": 0.125},
    "gpt-5.1-codex-max": {"input": 1.25, "output": 10.00, "cached": 0.125},
    "gpt-5.1-codex-mini": {"input": 0.25, "output": 2.00, "cached": 0.025},
    "gpt-5-nano": {"input": 0.05, "output": 0.40, "cached": 0.005},
    # Legacy Codex models
    "gpt-5-codex": {"input": 0.50, "output": 1.50, "cached": 0.025},
    "gpt-5.3-codex": {"input": 0.30, "output": 1.20, "cached": 0.025},
    "gpt-4-codex": {"input": 2.00, "output": 6.00, "cached": 0.50},
    # o-series reasoning models
    "o3": {"input": 10.00, "output": 40.00, "cached": 2.50},
    "o3-mini": {"input": 1.10, "output": 4.40, "cached": 0.55},
    "o3-pro": {"input": 20.00, "output": 80.00, "cached": 5.00},
    "o4-mini": {"input": 1.10, "output": 4.40, "cached": 0.55},
    "o1": {"input": 15.00, "output": 60.00, "cached": 7.50},
    "o1-mini": {"input": 3.00, "output": 12.00, "cached": 1.50},
    "o1-pro": {"input": 150.00, "output": 600.00, "cached": 75.00},
    # GPT-4o family
    "gpt-4o": {"input": 2.50, "output": 10.00, "cached": 1.25},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60, "cached": 0.075},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00, "cached": 5.00},
    "gpt-4": {"input": 30.00, "output": 60.00, "cached": 15.00},

    # ── Anthropic / Claude models ─────────────────────────────────────────
    # cache_write = 1.25x input price, cached (cache_read) = 0.1x input price
    "claude-opus-4-6": {"input": 5.00, "output": 25.00, "cached": 0.50, "cache_write": 6.25},
    "claude-opus-4-5": {"input": 5.00, "output": 25.00, "cached": 0.50, "cache_write": 6.25},
    "claude-sonnet-4-5": {"input": 3.00, "output": 15.00, "cached": 0.30, "cache_write": 3.75},
    "claude-sonnet-4": {"input": 3.00, "output": 15.00, "cached": 0.30, "cache_write": 3.75},
    "claude-haiku-4-5": {"input": 1.00, "output": 5.00, "cached": 0.10, "cache_write": 1.25},
    "claude-opus-4-1": {"input": 15.00, "output": 75.00, "cached": 1.50, "cache_write": 18.75},
    "claude-3-7-sonnet": {"input": 3.00, "output": 15.00, "cached": 0.30, "cache_write": 3.75},
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00, "cached": 0.30, "cache_write": 3.75},
    "claude-3-5-haiku": {"input": 1.00, "output": 5.00, "cached": 0.10, "cache_write": 1.25},
    "claude-3-opus": {"input": 15.00, "output": 75.00, "cached": 1.50, "cache_write": 18.75},
    "claude-3-haiku": {"input": 0.25, "output": 1.25, "cached": 0.03, "cache_write": 0.30},

    # ── Meta Llama models (via API providers) ─────────────────────────────
    "llama-4-scout": {"input": 0.17, "output": 0.17, "cached": 0.017},
    "llama-4-maverick": {"input": 0.27, "output": 0.35, "cached": 0.027},
    "llama-3.3-70b": {"input": 0.18, "output": 0.18, "cached": 0.018},
    "llama-3.3-70b-instruct": {"input": 0.18, "output": 0.18, "cached": 0.018},
    "llama-3.1-405b": {"input": 1.79, "output": 1.79, "cached": 0.179},
    "llama-3.1-405b-instruct": {"input": 1.79, "output": 1.79, "cached": 0.179},
    "llama-3.1-70b": {"input": 0.18, "output": 0.18, "cached": 0.018},
    "llama-3.1-70b-instruct": {"input": 0.18, "output": 0.18, "cached": 0.018},
    "llama-3.1-8b": {"input": 0.06, "output": 0.06, "cached": 0.006},
    "llama-3.1-8b-instruct": {"input": 0.06, "output": 0.06, "cached": 0.006},

    # ── DeepSeek models ───────────────────────────────────────────────────
    "deepseek-r1": {"input": 0.55, "output": 2.19, "cached": 0.14},
    "deepseek-v3": {"input": 0.27, "output": 1.10, "cached": 0.07},
    "deepseek-chat": {"input": 0.27, "output": 1.10, "cached": 0.07},
    "deepseek-coder": {"input": 0.14, "output": 0.28, "cached": 0.014},
    "deepseek-reasoner": {"input": 0.55, "output": 2.19, "cached": 0.14},

    # ── Qwen models (Alibaba Cloud, via OpenRouter pricing) ─────────────
    "qwen-2.5-coder-32b": {"input": 0.16, "output": 0.16, "cached": 0.016},
    "qwen-2.5-coder-32b-instruct": {"input": 0.20, "output": 0.20, "cached": 0.02},
    "qwen-2.5-72b": {"input": 0.30, "output": 0.30, "cached": 0.03},
    "qwen-2.5-72b-instruct": {"input": 0.36, "output": 0.36, "cached": 0.036},
    "qwen-2.5-vl-72b-instruct": {"input": 0.40, "output": 0.40, "cached": 0.04},
    "qwen-2.5-vl-7b-instruct": {"input": 0.10, "output": 0.10, "cached": 0.01},
    "qwen-2.5-7b-instruct": {"input": 0.05, "output": 0.05, "cached": 0.005},
    "qwen-qwq-32b": {"input": 0.20, "output": 0.20, "cached": 0.02},
    "qwen-2.5-max": {"input": 1.60, "output": 6.40, "cached": 0.16},
    "qwen-2.5-plus": {"input": 0.40, "output": 1.20, "cached": 0.04},
    "qwen-3-235b": {"input": 0.50, "output": 2.00, "cached": 0.05},
    "qwen-3-235b-a22b": {"input": 0.20, "output": 0.60, "cached": 0.02},
    "qwen-3-30b-a3b": {"input": 0.05, "output": 0.15, "cached": 0.005},
    "qwen-3-32b": {"input": 0.20, "output": 0.20, "cached": 0.02},
    "qwen-3-8b": {"input": 0.05, "output": 0.05, "cached": 0.005},
    "qwen-3-4b": {"input": 0.02, "output": 0.02, "cached": 0.002},
    "qwen-3-0.6b": {"input": 0.01, "output": 0.01, "cached": 0.001},
    "qwen-max": {"input": 0.80, "output": 2.40, "cached": 0.08},

    # ── GPT-OSS models ───────────────────────────────────────────────────
    "gpt-oss-120b": {"input": 0, "output": 0, "cached": 0},

    # ── Moonshot AI / Kimi models ─────────────────────────────────────────
    "kimi-k2-5": {"input": 0.60, "output": 3.00, "cached": 0.15},
    "kimi-k2.5": {"input": 0.60, "output": 3.00, "cached": 0.15},
    "kimi-k2.5-free": {"input": 0.60, "output": 3.00, "cached": 0.15},
    "kimi-k2": {"input": 0.60, "output": 3.00, "cached": 0.15},
    "kimi-k1.5": {"input": 0.60, "output": 3.00, "cached": 0.15},

    # ── GLM / Zhipu models ────────────────────────────────────────────────
    "glm-4-7": {"input": 0.60, "output": 2.20, "cached": 0.11},
    "glm-4.7-free": {"input": 0.60, "output": 2.20, "cached": 0.11},
    "glm-4-6": {"input": 0.60, "output": 2.20, "cached": 0.11},
    "glm-4.6": {"input": 0.60, "output": 2.20, "cached": 0.11},
    "glm-5": {"input": 0.80, "output": 2.56, "cached": 0.08},

    # ── Minimax models ────────────────────────────────────────────────────
    "minimax-m2.5": {"input": 0.30, "output": 1.20, "cached": 0.03},
    "minimax-m2.5:free": {"input": 0.30, "output": 1.20, "cached": 0.03},
    "minimax-m2.1-free": {"input": 0.30, "output": 1.20, "cached": 0.03},
    "minimax-m2.1": {"input": 0.30, "output": 1.20, "cached": 0.03},
    "minimax-m2-5": {"input": 0.30, "output": 1.20, "cached": 0.03},

    # ── xAI / Grok models ────────────────────────────────────────────────
    "grok-code-fast-1": {"input": 0.20, "output": 1.50, "cached": 0.02},
    "grok-3": {"input": 0.20, "output": 1.50, "cached": 0.02},
    "grok-3-mini": {"input": 0.10, "output": 0.50, "cached": 0.01},
    "grok-2": {"input": 2.00, "output": 10.00, "cached": 0.50},

    # ── Mistral models ────────────────────────────────────────────────────
    "devstral-2512": {"input": 0.05, "output": 0.22, "cached": 0.005},
    "mistral-large-2411": {"input": 2.00, "output": 6.00, "cached": 0.50},
    "mistral-large": {"input": 2.00, "output": 6.00, "cached": 0.50},
    "mistral-small-2501": {"input": 0.10, "output": 0.30, "cached": 0.025},
    "mistral-small": {"input": 0.10, "output": 0.30, "cached": 0.025},
    "codestral": {"input": 0.30, "output": 0.90, "cached": 0.075},
    "mistral-medium": {"input": 2.70, "output": 8.10, "cached": 0.675},

    # ── Cohere models ─────────────────────────────────────────────────────
    "command-r-plus": {"input": 2.50, "output": 10.00, "cached": 0.625},
    "command-r": {"input": 0.15, "output": 0.60, "cached": 0.0375},

    # ── Novita hosted models ──────────────────────────────────────────────
    "novita-devstral-2512": {"input": 0.05, "output": 0.22, "cached": 0.005},
    "novita-minimax-m2.1": {"input": 0.30, "output": 1.20, "cached": 0.03},

    # ── Stealth / unknown models — no public API pricing ──────────────────
    "pony-alpha": {"input": 0, "output": 0, "cached": 0},
    "giga-potato": {"input": 0, "output": 0, "cached": 0},
}
DEFAULT_PRICING = {"input": 0, "output": 0, "cached": 0}

import re

def normalize_model_name(model):
    """Strip date suffixes (e.g. -20251001) and :free suffix from model names for pricing lookup."""
    # Remove trailing date like -20251001, -20251101, etc.
    normalized = re.sub(r'-\d{8}$', '', model)
    # Remove :free suffix (e.g. "kimi-k2.5:free" -> "kimi-k2.5")
    normalized = re.sub(r':free$', '', normalized)
    # Remove thinking suffix (e.g. "claude-sonnet-4.5 (thinking)" -> "claude-sonnet-4.5")
    normalized = re.sub(r'\s*\(thinking\)$', '', normalized, flags=re.IGNORECASE)
    # Remove high/low/medium suffixes (e.g. "gemini-3-pro (high)" -> "gemini-3-pro")
    normalized = re.sub(r'\s*\((high|low|medium)\)$', '', normalized, flags=re.IGNORECASE)
    # Replace spaces with hyphens for consistency (e.g. "Claude Sonnet 4.5" -> "claude-sonnet-4.5")
    normalized = normalized.replace(' ', '-').lower()
    return normalized

def get_cost(model, input_tokens, output_tokens, cached_tokens, cache_write_tokens=0):
    pricing = PRICING.get(model) or PRICING.get(normalize_model_name(model), DEFAULT_PRICING)
    # Subtract cached + cache_write tokens from total input to get billed non-cached input
    billed_input = max(0, input_tokens - cached_tokens - cache_write_tokens)
    cost = (billed_input / 1_000_000) * pricing["input"] + \
           (output_tokens / 1_000_000) * pricing["output"] + \
           (cached_tokens / 1_000_000) * pricing["cached"]
    # Add cache write cost if the model has separate cache_write pricing
    if cache_write_tokens > 0 and "cache_write" in pricing:
        cost += (cache_write_tokens / 1_000_000) * pricing["cache_write"]
    elif cache_write_tokens > 0:
        # Default: cache writes billed at regular input rate
        cost += (cache_write_tokens / 1_000_000) * pricing["input"]
    return cost

def get_project_map():
    home_dir = os.path.expanduser("~")
    trusted_file = os.path.join(home_dir, ".gemini", "trustedFolders.json")
    proj_map = {}
    trusted_paths = []

    if os.path.exists(trusted_file):
        try:
            with open(trusted_file, "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    trusted_paths = list(data.keys())
                else:
                    trusted_paths = data
        except Exception:
            pass

    for path in trusted_paths:
        # Gemini often uses the exact case of the path for hashing
        h_exact = hashlib.sha256(path.encode('utf-8')).hexdigest()
        proj_map[h_exact] = os.path.basename(path) or path
        
        # Fallback for some versions/platforms that might use lowercase
        h_lower = hashlib.sha256(path.lower().encode('utf-8')).hexdigest()
        if h_lower not in proj_map:
            proj_map[h_lower] = os.path.basename(path) or path

    # Additionally, try to map the current working directory
    current_dir = os.getcwd()
    current_dir_hash = hashlib.sha256(current_dir.encode('utf-8')).hexdigest()
    if current_dir_hash not in proj_map:
        proj_map[current_dir_hash] = os.path.basename(current_dir) or current_dir

    return proj_map

def read_gemini_data(stats_by_day, stats_by_project, model_usage, cli_usage):
    """Read Gemini CLI session data from ~/.gemini/tmp/"""
    home_dir = os.path.expanduser("~")
    gemini_tmp = os.path.join(home_dir, ".gemini", "tmp")
    
    if not os.path.exists(gemini_tmp):
        return
    
    proj_map = get_project_map()
    pattern = os.path.join(gemini_tmp, "*", "chats", "session-*.json")
    session_files = glob.glob(pattern)
    
    for file_path in session_files:
        try:
            project_hash = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for msg in data.get("messages", []):
                if msg.get("type") == "gemini" and "tokens" in msg:
                    tokens = msg["tokens"]
                    model = msg.get("model", "unknown")
                    ts = msg.get("timestamp")
                    i, o, c = tokens.get("input", 0), tokens.get("output", 0), tokens.get("cached", 0)
                    cost = get_cost(model, i, o, c)
                    
                    model_usage[model]["input"] += i
                    model_usage[model]["output"] += o
                    model_usage[model]["cost"] += cost
                    
                    cli_usage["Gemini CLI"]["input"] += i
                    cli_usage["Gemini CLI"]["output"] += o
                    cli_usage["Gemini CLI"]["cost"] += cost
                    
                    proj_name = proj_map.get(project_hash, project_hash[:8])
                    stats_by_project[proj_name]["input"] += i
                    stats_by_project[proj_name]["output"] += o
                    stats_by_project[proj_name]["cost"] += cost

                    if ts:
                        d = datetime.fromisoformat(ts.replace("Z", "+00:00")).strftime("%Y-%m-%d")
                        stats_by_day[d]["input"] += i
                        stats_by_day[d]["output"] += o
                        stats_by_day[d]["cached"] += c
                        stats_by_day[d]["cost"] += cost
        except: continue

def read_codex_data(stats_by_day, stats_by_project, model_usage, cli_usage):
    """Read Codex CLI session data from ~/.codex/sessions/"""
    home_dir = os.path.expanduser("~")
    codex_dir = os.path.join(home_dir, ".codex", "sessions")
    
    if not os.path.exists(codex_dir):
        return
    
    # Find all JSONL files in the sessions directory (YYYY/MM/DD structure)
    pattern = os.path.join(codex_dir, "**", "*.jsonl")
    session_files = glob.glob(pattern, recursive=True)
    
    # Track last seen model per session file (to associate token counts with models)
    last_model = {}
    
    for file_path in session_files:
        try:
            # Extract date from filename (format: rollout-YYYY-MM-DDThh-mm-ss-*.jsonl)
            filename = os.path.basename(file_path)
            date_str = filename.split("T")[0].replace("rollout-", "") if "T" in filename else datetime.now().strftime("%Y-%m-%d")
            
            # Extract project from path
            parts = file_path.split(os.sep)
            project = parts[-4] if len(parts) >= 4 else "codex-session"
            
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        event = json.loads(line.strip())
                        event_type = event.get("type")
                        payload = event.get("payload", {})
                        
                        # Track model from turn_context events
                        if event_type == "turn_context":
                            model = payload.get("model", "gpt-5.2-codex")
                            last_model[file_path] = model
                        
                        # Extract token usage from token_count events
                        elif event_type == "event_msg" and payload.get("type") == "token_count":
                            info = payload.get("info", {})
                            usage = info.get("last_token_usage", {})
                            
                            # Get the model (use last seen model or default)
                            model = last_model.get(file_path, "gpt-5.2-codex")
                            
                            i = usage.get("input_tokens", 0)
                            o = usage.get("output_tokens", 0)
                            c = usage.get("cached_input_tokens", 0)
                            
                            # Only count if there's actual usage
                            if i > 0 or o > 0:
                                cost = get_cost(model, i, o, c)
                                
                                model_usage[model]["input"] += i
                                model_usage[model]["output"] += o
                                model_usage[model]["cost"] += cost
                                
                                cli_usage["Codex CLI"]["input"] += i
                                cli_usage["Codex CLI"]["output"] += o
                                cli_usage["Codex CLI"]["cost"] += cost
                                
                                stats_by_project[project]["input"] += i
                                stats_by_project[project]["output"] += o
                                stats_by_project[project]["cost"] += cost
                                
                                stats_by_day[date_str]["input"] += i
                                stats_by_day[date_str]["output"] += o
                                stats_by_day[date_str]["cached"] += c
                                stats_by_day[date_str]["cost"] += cost
                    except:
                        continue
        except:
            continue

def read_opencode_data(stats_by_day, stats_by_project, model_usage, cli_usage):
    """Read Opencode CLI session data from ~/.local/share/opencode/"""
    home_dir = os.path.expanduser("~")
    opencode_dir = os.path.join(home_dir, ".local", "share", "opencode", "storage")
    
    if not os.path.exists(opencode_dir):
        return
    
    # Find all session JSON files
    session_pattern = os.path.join(opencode_dir, "session", "**", "*.json")
    session_files = glob.glob(session_pattern, recursive=True)
    
    for file_path in session_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                session = json.load(f)
            
            session_id = session.get("id", "unknown")
            project_hash = os.path.basename(os.path.dirname(file_path))
            
            # Get session creation time
            session_time = session.get("time", {})
            created_ts = session_time.get("created", 0)
            if created_ts:
                session_date = datetime.fromtimestamp(created_ts / 1000).strftime("%Y-%m-%d")
            else:
                session_date = datetime.now().strftime("%Y-%m-%d")
            
            # Look for message files
            msg_dir = os.path.join(opencode_dir, "message", session_id)
            if os.path.exists(msg_dir):
                msg_files = glob.glob(os.path.join(msg_dir, "*.json"))
                
                for msg_file in msg_files:
                    try:
                        with open(msg_file, "r", encoding="utf-8") as mf:
                            msg = json.load(mf)
                        
                        # Extract token usage from message (Opencode uses 'tokens' field)
                        tokens = msg.get("tokens", {})
                        if not tokens:
                            continue
                        
                        # Get model from modelID field
                        model = msg.get("modelID", "kimi-k2-5")
                        
                        i = tokens.get("input", 0)
                        o = tokens.get("output", 0)
                        cache = tokens.get("cache", {})
                        c = cache.get("read", 0) if isinstance(cache, dict) else 0
                        
                        # Only count if there's actual usage
                        if i > 0 or o > 0:
                            cost = get_cost(model, i, o, c)
                            
                            model_usage[model]["input"] += i
                            model_usage[model]["output"] += o
                            model_usage[model]["cost"] += cost
                            
                            cli_usage["Opencode CLI"]["input"] += i
                            cli_usage["Opencode CLI"]["output"] += o
                            cli_usage["Opencode CLI"]["cost"] += cost
                            
                            stats_by_project[project_hash]["input"] += i
                            stats_by_project[project_hash]["output"] += o
                            stats_by_project[project_hash]["cost"] += cost
                            
                            # Use message creation time if available, otherwise session date
                            msg_time = msg.get("time", {})
                            msg_created = msg_time.get("created", 0)
                            if msg_created:
                                d = datetime.fromtimestamp(msg_created / 1000).strftime("%Y-%m-%d")
                            else:
                                d = session_date
                            
                            stats_by_day[d]["input"] += i
                            stats_by_day[d]["output"] += o
                            stats_by_day[d]["cached"] += c
                            stats_by_day[d]["cost"] += cost
                    except:
                        continue
        except:
            continue

def read_ampcode_data(stats_by_day, stats_by_project, model_usage, cli_usage):
    """Read Ampcode CLI session data from ~/.local/share/amp/threads/"""
    home_dir = os.path.expanduser("~")
    ampcode_dir = os.path.join(home_dir, ".local", "share", "amp", "threads")
    
    if not os.path.exists(ampcode_dir):
        return
    
    # Find all thread JSON files
    thread_pattern = os.path.join(ampcode_dir, "*.json")
    thread_files = glob.glob(thread_pattern)
    
    for file_path in thread_files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                thread = json.load(f)
            
            thread_id = thread.get("id", "unknown")
            created_ts = thread.get("created", 0)
            
            # Determine project name from repo URL (group threads by repo)
            trees = thread.get("env", {}).get("initial", {}).get("trees", [])
            project_name = None
            for tree in trees:
                repo_url = tree.get("repository", {}).get("url", "")
                if repo_url:
                    # Extract repo name from URL (e.g. "https://github.com/user/repo" -> "repo")
                    project_name = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
                    break
                display = tree.get("displayName", "")
                if display:
                    project_name = display
                    break
            if not project_name:
                project_name = thread.get("title", thread_id) or thread_id
            
            # Convert timestamp to date
            if created_ts:
                thread_date = datetime.fromtimestamp(created_ts / 1000).strftime("%Y-%m-%d")
            else:
                thread_date = datetime.now().strftime("%Y-%m-%d")
            
            # Process messages in the thread
            messages = thread.get("messages", [])
            
            # Determine thread-level model from tags (fallback for messages without model)
            tags = thread.get("env", {}).get("initial", {}).get("tags", [])
            thread_model = None
            for tag in tags:
                if tag.startswith("model:") and tag != "model:undefined":
                    thread_model = tag.replace("model:", "")
                    break
            if not thread_model:
                thread_model = "claude-sonnet-4"  # default fallback
            
            # Helper to accumulate usage from a single usage dict
            def _acc_usage(usage, thread_model=thread_model):
                model = usage.get("model")
                if not model:
                    max_input = usage.get("maxInputTokens", 0)
                    if max_input >= 200000:
                        model = "gpt-5.1-codex-max"
                    else:
                        model = thread_model
                
                i = usage.get("totalInputTokens", 0) or (
                    usage.get("inputTokens", 0) +
                    usage.get("cacheCreationInputTokens", 0) +
                    usage.get("cacheReadInputTokens", 0)
                )
                o = usage.get("outputTokens", 0)
                c = usage.get("cacheReadInputTokens", 0)
                cw = usage.get("cacheCreationInputTokens", 0)
                
                if i == 0 and o == 0:
                    return
                
                cost = get_cost(model, i, o, c, cw)
                
                model_usage[model]["input"] += i
                model_usage[model]["output"] += o
                model_usage[model]["cost"] += cost
                
                cli_usage["Ampcode CLI"]["input"] += i
                cli_usage["Ampcode CLI"]["output"] += o
                cli_usage["Ampcode CLI"]["cost"] += cost
                
                stats_by_project[project_name]["input"] += i
                stats_by_project[project_name]["output"] += o
                stats_by_project[project_name]["cost"] += cost
                
                stats_by_day[thread_date]["input"] += i
                stats_by_day[thread_date]["output"] += o
                stats_by_day[thread_date]["cached"] += c
                stats_by_day[thread_date]["cost"] += cost
            
            # Calculate cost from message-level usage with API pricing
            for msg in messages:
                    try:
                        # Process assistant message top-level usage
                        if msg.get("role") == "assistant":
                            usage = msg.get("usage", {})
                            if usage:
                                _acc_usage(usage)
                        
                        # Process tool result inferences (e.g. painter/image generation)
                        # These are on user messages at content[].run.~debug.inferences[].usage
                        if msg.get("role") == "user":
                            for part in msg.get("content", []):
                                if not isinstance(part, dict):
                                    continue
                                run = part.get("run", {})
                                debug = run.get("~debug", {})
                                for inf in debug.get("inferences", []):
                                    inf_usage = inf.get("usage", {})
                                    if inf_usage:
                                        _acc_usage(inf_usage)
                    except:
                        continue
        except:
            continue

def read_cline_family_data(stats_by_day, stats_by_project, model_usage, cli_usage):
    """Read Cline, Roo Code, and Kilo Code task data from VS Code globalStorage."""
    home_dir = os.path.expanduser("~")
    appdata = os.environ.get("APPDATA", os.path.join(home_dir, "AppData", "Roaming"))
    
    # All possible IDE storage roots (VS Code, Insiders, Cursor, Windsurf, etc.)
    ide_roots = [
        os.path.join(appdata, "Code", "User", "globalStorage"),
        os.path.join(appdata, "Code - Insiders", "User", "globalStorage"),
        os.path.join(appdata, "Cursor", "User", "globalStorage"),
        os.path.join(appdata, "Windsurf", "User", "globalStorage"),
    ]
    
    # IDE to CLI mapping for tracking which IDE the extension data came from
    ide_to_cli = {
        os.path.join(appdata, "Code", "User", "globalStorage"): "VS Code",
        os.path.join(appdata, "Code - Insiders", "User", "globalStorage"): "VS Code Insiders",
        os.path.join(appdata, "Cursor", "User", "globalStorage"): "Cursor",
        os.path.join(appdata, "Windsurf", "User", "globalStorage"): "Windsurf",
    }
    
    # Extension IDs for each tool
    ext_ids = {
        "Cline": ["saoudrizwan.claude-dev"],
        "Roo Code": ["rooveterinaryinc.roo-cline", "rooveterinaryinc.roo-code-nightly"],
        "Kilo Code": ["kilocode.kilo-code"],
    }
    
    # Build all possible paths
    tools = {}
    for cli_name, ext_list in ext_ids.items():
        tools[cli_name] = []
        for root in ide_roots:
            for ext_id in ext_list:
                tools[cli_name].append(os.path.join(root, ext_id))
    
    for cli_name, paths in tools.items():
        for base_path in paths:
            # Method 1: Parse taskHistory.json (has per-task totals)
            history_file = os.path.join(base_path, "state", "taskHistory.json")
            if os.path.exists(history_file):
                try:
                    with open(history_file, "r", encoding="utf-8") as f:
                        tasks = json.load(f)
                    
                    for task in tasks:
                        ts = task.get("ts", 0)
                        if ts:
                            task_date = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                        else:
                            task_date = datetime.now().strftime("%Y-%m-%d")
                        
                        i = task.get("tokensIn", 0) or 0
                        o = task.get("tokensOut", 0) or 0
                        cw = task.get("cacheWrites", 0) or 0
                        cr = task.get("cacheReads", 0) or 0
                        cost = task.get("totalCost", 0) or 0
                        model = task.get("modelId") or task.get("model") or "unknown"
                        # Clean up provider-prefixed model names (e.g. "x-ai/grok-code-fast-1")
                        if "/" in model:
                            model = model.split("/", 1)[1]
                        
                        if i == 0 and o == 0:
                            continue
                        
                        # If cost is reported, use it directly; otherwise calculate
                        if not cost:
                            cost = get_cost(model, i, o, cr, cw)
                        
                        # Project from workspace directory
                        cwd = task.get("cwdOnTaskInitialization", "")
                        project = os.path.basename(cwd) if cwd else None
                        
                        # Only add to projects if we found an actual project directory
                        # Don't add CLI names (Cline, Roo Code, Kilo Code) as projects
                        if project and project != cli_name:
                            stats_by_project[project]["input"] += i
                            stats_by_project[project]["output"] += o
                            stats_by_project[project]["cost"] += cost
                        
                        model_usage[model]["input"] += i
                        model_usage[model]["output"] += o
                        model_usage[model]["cost"] += cost
                        
                        cli_usage[cli_name]["input"] += i
                        cli_usage[cli_name]["output"] += o
                        cli_usage[cli_name]["cost"] += cost
                        
                        # Also track by IDE (VS Code, Cursor, etc.)
                        ide_root = os.path.dirname(base_path)
                        if ide_root in ide_to_cli:
                            ide_name = ide_to_cli[ide_root]
                            cli_usage[ide_name]["input"] += i
                            cli_usage[ide_name]["output"] += o
                            cli_usage[ide_name]["cost"] += cost
                        
                        stats_by_day[task_date]["input"] += i
                        stats_by_day[task_date]["output"] += o
                        stats_by_day[task_date]["cached"] += cr
                        stats_by_day[task_date]["cost"] += cost
                except:
                    pass
                continue  # Don't double-count from ui_messages if taskHistory exists
            
            # Method 2: Fallback — parse individual task ui_messages.json files
            tasks_dir = os.path.join(base_path, "tasks")
            if not os.path.exists(tasks_dir):
                continue
            
            try:
                for task_id in os.listdir(tasks_dir):
                    task_path = os.path.join(tasks_dir, task_id)
                    if not os.path.isdir(task_path):
                        continue
                    
                    ui_file = os.path.join(task_path, "ui_messages.json")
                    if not os.path.exists(ui_file):
                        continue
                    
                    try:
                        with open(ui_file, "r", encoding="utf-8") as f:
                            messages = json.load(f)
                        
                        task_input = 0
                        task_output = 0
                        task_cache_reads = 0
                        task_cost = 0.0
                        task_date = None
                        task_model = "unknown"
                        
                        # Try to extract model from api_conversation_history.json first
                        api_history_file = os.path.join(task_path, "api_conversation_history.json")
                        if os.path.exists(api_history_file):
                            try:
                                with open(api_history_file, "r", encoding="utf-8") as af:
                                    api_history = json.load(af)
                                # Look for model in content field within messages
                                for msg in api_history:
                                    content = msg.get("content", "")
                                    # content can be a string or list of dicts
                                    if isinstance(content, list):
                                        for item in content:
                                            if isinstance(item, dict) and item.get("type") == "text":
                                                text = item.get("text", "")
                                                if "<model>" in text:
                                                    model_match = re.search(r'<model>([^<]+)</model>', text)
                                                    if model_match:
                                                        task_model = model_match.group(1).strip()
                                                        # Clean up provider-prefixed model names
                                                        if "/" in task_model:
                                                            task_model = task_model.split("/", 1)[1]
                                                        break
                                    elif isinstance(content, str) and "<model>" in content:
                                        model_match = re.search(r'<model>([^<]+)</model>', content)
                                        if model_match:
                                            task_model = model_match.group(1).strip()
                                            if "/" in task_model:
                                                task_model = task_model.split("/", 1)[1]
                                    if task_model != "unknown":
                                        break
                            except:
                                pass
                        
                        for msg in messages:
                            ts = msg.get("ts", 0)
                            if ts and not task_date:
                                task_date = datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d")
                            
                            say_type = msg.get("say", "")
                            if say_type in ("api_req_started", "deleted_api_reqs", "subagent_usage"):
                                try:
                                    usage_data = json.loads(msg.get("text", "{}"))
                                    task_input += usage_data.get("tokensIn", 0) or 0
                                    task_output += usage_data.get("tokensOut", 0) or 0
                                    task_cache_reads += usage_data.get("cacheReads", 0) or 0
                                    task_cost += usage_data.get("cost", 0) or 0
                                    # Kilo Code stores inferenceProvider instead of model
                                    # Only use if we haven't found model from api_conversation_history
                                    if task_model == "unknown" and usage_data.get("inferenceProvider"):
                                        task_model = usage_data["inferenceProvider"]
                                    # If still unknown, label by CLI + protocol
                                    if task_model == "unknown" and usage_data.get("apiProtocol"):
                                        task_model = cli_name + " (" + usage_data["apiProtocol"] + ")"
                                except:
                                    pass
                            
                            # Try to get model info (only if not already found)
                            if task_model == "unknown":
                                model_info = msg.get("modelInfo", {})
                                if model_info and model_info.get("modelId"):
                                    task_model = model_info["modelId"]
                        
                        if task_input == 0 and task_output == 0:
                            continue
                        
                        # If reported cost is 0, recalculate from API pricing
                        if not task_cost:
                            task_cache_writes = 0  # ui_messages doesn't separate cache writes reliably
                            task_cost = get_cost(task_model, task_input, task_output, task_cache_reads, task_cache_writes)
                        
                        if not task_date:
                            task_date = datetime.now().strftime("%Y-%m-%d")
                        
                        model_usage[task_model]["input"] += task_input
                        model_usage[task_model]["output"] += task_output
                        model_usage[task_model]["cost"] += task_cost
                        
                        cli_usage[cli_name]["input"] += task_input
                        cli_usage[cli_name]["output"] += task_output
                        cli_usage[cli_name]["cost"] += task_cost
                        
                        # Also track by IDE (VS Code, Cursor, etc.)
                        ide_root = os.path.dirname(base_path)
                        if ide_root in ide_to_cli:
                            ide_name = ide_to_cli[ide_root]
                            cli_usage[ide_name]["input"] += task_input
                            cli_usage[ide_name]["output"] += task_output
                            cli_usage[ide_name]["cost"] += task_cost
                        
                        # Get project from workspace directory (cwd) if available
                        # For Cline, this comes from taskHistory.json (cwdOnTaskInitialization)
                        # For Kilo Code/Roo Code, we try to find it in the messages
                        project = None
                        
                        # Try to get cwd from message metadata (some extensions store it differently)
                        for msg in messages:
                            # Check various possible locations for cwd
                            cwd = msg.get("cwd") or msg.get("workingDirectory") or msg.get("root")
                            if cwd:
                                project = os.path.basename(cwd) if cwd else None
                                break
                            # Check if there's a modelInfo with project info
                            model_info = msg.get("modelInfo", {})
                            if model_info and model_info.get("workspace"):
                                project = os.path.basename(model_info["workspace"]) if model_info["workspace"] else None
                                break
                        
                        # Only add to projects if we found an actual project directory
                        # Don't add CLI names (Cline, Roo Code, Kilo Code) as projects
                        if project and project != cli_name:
                            stats_by_project[project]["input"] += task_input
                            stats_by_project[project]["output"] += task_output
                            stats_by_project[project]["cost"] += task_cost
                        
                        stats_by_day[task_date]["input"] += task_input
                        stats_by_day[task_date]["output"] += task_output
                        stats_by_day[task_date]["cached"] += task_cache_reads
                        stats_by_day[task_date]["cost"] += task_cost
                    except:
                        continue
            except:
                continue

def generate_data():
    """Aggregate data from all CLI tools"""
    stats_by_day = defaultdict(lambda: {"input": 0, "output": 0, "cached": 0, "cost": 0.0})
    stats_by_project = defaultdict(lambda: {"input": 0, "output": 0, "cost": 0.0})
    model_usage = defaultdict(lambda: {"input": 0, "output": 0, "cost": 0.0})
    cli_usage = defaultdict(lambda: {"input": 0, "output": 0, "cost": 0.0})
    
    # Read data from all CLI tools
    read_gemini_data(stats_by_day, stats_by_project, model_usage, cli_usage)
    read_codex_data(stats_by_day, stats_by_project, model_usage, cli_usage)
    read_opencode_data(stats_by_day, stats_by_project, model_usage, cli_usage)
    read_ampcode_data(stats_by_day, stats_by_project, model_usage, cli_usage)
    read_cline_family_data(stats_by_day, stats_by_project, model_usage, cli_usage)
    
    sorted_days = sorted(stats_by_day.keys())
    # Sort projects by cost descending for the data structure
    sorted_projects = sorted(stats_by_project.items(), key=lambda x: x[1]["cost"], reverse=True)
    
    sorted_models = sorted(model_usage.items(), key=lambda x: x[1]["cost"], reverse=True)
    
    # Sort CLI usage by cost descending
    sorted_cli = sorted(cli_usage.items(), key=lambda x: x[1]["cost"], reverse=True)
    
    return {
        "days": sorted_days,
        "daily_costs": [stats_by_day[d]["cost"] for d in sorted_days],
        "daily_tokens": [stats_by_day[d]["input"] for d in sorted_days],
        "projects": [p for p, v in sorted_projects],
        "project_costs": [v["cost"] for v, p in [ (v, p) for p, v in sorted_projects ]],
        "project_tokens": [v["input"] for v, p in [ (v, p) for p, v in sorted_projects ]],
        "models": [m for m, v in sorted_models],
        "model_costs": [v["cost"] for m, v in sorted_models],
        "model_inputs": [v["input"] for m, v in sorted_models],
        "model_outputs": [v["output"] for m, v in sorted_models],
        "model_tokens": [v["input"] + v["output"] for m, v in sorted_models],
        "cli_names": [c for c, v in sorted_cli],
        "cli_costs": [v["cost"] for c, v in sorted_cli],
        "cli_inputs": [v["input"] for c, v in sorted_cli],
        "cli_outputs": [v["output"] for c, v in sorted_cli],
        "totals": {
            "cost": sum(v["cost"] for v in stats_by_day.values()),
            "input": sum(v["input"] for v in stats_by_day.values()),
            "output": sum(v["output"] for v in stats_by_day.values()),
            "cached": sum(v["cached"] for v in stats_by_day.values()),
            "avg_day": sum(v["cost"] for v in stats_by_day.values()) / max(len(sorted_days), 1)
        }
    }

def main():
    data = generate_data()
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI CLI Usage Dashboard - Gemini, Codex, Opencode & Cline</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #0f172a; color: #f8fafc; }}
        .glass {{ background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); }}
        .card-grad {{ background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); }}
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: transparent; }}
        ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 10px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #475569; }}
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
        <header class="mb-10 flex justify-between items-end">
            <div>
                <h1 class="text-4xl font-bold tracking-tight text-white mb-2">AI CLI <span class="text-blue-500">Analytics</span></h1>
                <p class="text-slate-400">Real-time usage and cost tracking for Gemini, Codex, Opencode & Cline, Roo Code, Kilo Code CLI</p>
            </div>
            <div class="text-right">
                <span class="text-xs font-semibold uppercase tracking-wider text-slate-500">Last Updated</span>
                <p class="text-sm font-medium text-slate-300">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
        </header>

        <!-- Stats Grid -->
        <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-10">
            <div class="glass p-6 rounded-2xl shadow-xl border-l-4 border-blue-500">
                <p class="text-sm text-slate-400 font-medium mb-1">Input Tokens</p>
                <h3 class="text-2xl font-bold text-white">{data['totals']['input']:,}</h3>
                <div class="mt-2 text-xs text-blue-400 font-medium">Context Sent</div>
            </div>
            <div class="glass p-6 rounded-2xl shadow-xl border-l-4 border-purple-500">
                <p class="text-sm text-slate-400 font-medium mb-1">Output Tokens</p>
                <h3 class="text-2xl font-bold text-white">{data['totals']['output']:,}</h3>
                <div class="mt-2 text-xs text-purple-400 font-medium">Responses Gen</div>
            </div>
            <div class="glass p-6 rounded-2xl shadow-xl border-l-4 border-emerald-500">
                <p class="text-sm text-slate-400 font-medium mb-1">Cached Tokens</p>
                <h3 class="text-2xl font-bold text-white">{data['totals']['cached']:,}</h3>
                <div class="mt-2 text-xs text-emerald-400 font-medium">Efficiency Savings</div>
            </div>
            <div class="glass p-6 rounded-2xl shadow-xl border-l-4 border-slate-500">
                <p class="text-sm text-slate-400 font-medium mb-1">Total Tokens</p>
                <h3 class="text-2xl font-bold text-white">{data['totals']['input'] + data['totals']['output']:,}</h3>
                <div class="mt-2 text-xs text-slate-400 font-medium">Combined Usage</div>
            </div>
            <div class="glass p-6 rounded-2xl shadow-xl border-l-4 border-amber-500">
                <p class="text-sm text-slate-400 font-medium mb-1">Total Cost</p>
                <h3 class="text-2xl font-bold text-white">${data['totals']['cost']:,.2f}</h3>
                <div class="mt-2 text-xs text-amber-400 font-medium">Est. API Spend</div>
            </div>
        </div>

        <!-- Charts Grid -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
            <div class="glass p-6 rounded-2xl">
                <h3 class="text-lg font-semibold mb-6">Daily Cost Trend</h3>
                <div style="height: 350px; position: relative;">
                    <canvas id="costChart"></canvas>
                </div>
            </div>
            <div class="glass p-6 rounded-2xl">
                <h3 class="text-lg font-semibold mb-6">Usage by Model</h3>
                <div style="height: 280px; position: relative;" class="mb-6">
                    <canvas id="modelChart"></canvas>
                </div>
                <div>
                    <table class="w-full text-left text-xs" style="table-layout: fixed;">
                        <thead class="text-slate-500 uppercase border-b border-slate-700">
                            <tr>
                                <th class="py-2" style="width: 22%;">Model</th>
                                <th class="py-2 text-right" style="width: 22%;">Input</th>
                                <th class="py-2 text-right" style="width: 22%;">Output</th>
                                <th class="py-2 text-right" style="width: 22%;">Total</th>
                                <th class="py-2 text-right" style="width: 12%;">Cost</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800">
                            {''.join([f"<tr><td class='py-1.5 font-medium text-slate-300 truncate' title='{m}'>{m}</td><td class='py-1.5 text-right text-slate-500'>{i:,}</td><td class='py-1.5 text-right text-slate-500'>{o:,}</td><td class='py-1.5 text-right text-slate-400'>{t:,}</td><td class='py-1.5 text-right text-blue-400 font-semibold'>${v:,.2f}</td></tr>" for m, i, o, t, v in sorted(zip(data['models'], data['model_inputs'], data['model_outputs'], data['model_tokens'], data['model_costs']), key=lambda x: x[4], reverse=True)])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div class="glass p-6 rounded-2xl">
                <h3 class="text-lg font-semibold mb-6">Usage Breakdown</h3>
                <div class="overflow-y-auto max-h-[400px]">
                    <canvas id="projectChart" style="height: {max(400, len(data['projects']) * 30)}px"></canvas>
                </div>
            </div>
            <div class="glass p-6 rounded-2xl overflow-hidden">
                <h3 class="text-lg font-semibold mb-4 px-2">All Projects</h3>
                <div class="max-h-[400px] overflow-y-auto">
                    <table class="w-full text-left text-sm" style="table-layout: fixed;">
                        <thead class="text-slate-500 uppercase text-xs border-b border-slate-700 sticky top-0 bg-[#1e293b] z-10">
                            <tr>
                                <th class="py-3 px-2" style="width: 50%;">Project</th>
                                <th class="py-3 px-2 text-right" style="width: 25%;">Tokens</th>
                                <th class="py-3 px-2 text-right" style="width: 25%;">Cost</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800">
                            {''.join([f"<tr><td class='py-3 px-2 font-medium truncate' title='{p}'>{p}</td><td class='py-3 px-2 text-right text-slate-400'>{c:,}</td><td class='py-3 px-2 text-right text-blue-400 font-semibold'>${v:,.2f}</td></tr>" for p, c, v in zip(data['projects'], data['project_tokens'], data['project_costs'])])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- CLI Comparison Section -->
        <div class="glass p-6 rounded-2xl mt-8">
            <h3 class="text-lg font-semibold mb-6">CLI Usage Comparison (Ranked by Cost)</h3>
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div style="height: 300px; position: relative;">
                    <canvas id="cliChart"></canvas>
                </div>
                <div>
                    <table class="w-full text-left text-sm" style="table-layout: fixed;">
                        <thead class="text-slate-500 uppercase text-xs border-b border-slate-700">
                            <tr>
                                <th class="py-3 px-2" style="width: 30%;">CLI Tool</th>
                                <th class="py-3 px-2 text-right" style="width: 25%;">Input</th>
                                <th class="py-3 px-2 text-right" style="width: 25%;">Output</th>
                                <th class="py-3 px-2 text-right" style="width: 20%;">Cost</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-800">
                            {''.join([f"<tr><td class='py-3 px-2 font-medium text-slate-300'>{c}</td><td class='py-3 px-2 text-right text-slate-500'>{i:,}</td><td class='py-3 px-2 text-right text-slate-500'>{o:,}</td><td class='py-3 px-2 text-right text-blue-400 font-semibold'>${v:,.2f}</td></tr>" for c, i, o, v in zip(data['cli_names'], data['cli_inputs'], data['cli_outputs'], data['cli_costs'])])}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        const ctxCost = document.getElementById('costChart').getContext('2d');
        new Chart(ctxCost, {{
            type: 'line',
            data: {{
                labels: {json.dumps(data['days'])},
                datasets: [{{
                    label: 'Daily Cost ($)',
                    data: {json.dumps(data['daily_costs'])},
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3,
                    pointRadius: 4,
                    pointBackgroundColor: '#3b82f6'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    y: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }},
                    x: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8', maxRotation: 45, minRotation: 30, autoSkip: true, maxTicksLimit: 15 }} }}
                }}
            }}
        }});

        const ctxModel = document.getElementById('modelChart').getContext('2d');
        new Chart(ctxModel, {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(data['models'])},
                datasets: [{{
                    data: {json.dumps(data['model_costs'])},
                    backgroundColor: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#6366f1'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ color: '#94a3b8', padding: 20, usePointStyle: true }} }}
                }},
                cutout: '70%'
            }}
        }});

        const ctxProj = document.getElementById('projectChart').getContext('2d');
        new Chart(ctxProj, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(data['projects'])},
                datasets: [{{
                    label: 'Cost by Project ($)',
                    data: {json.dumps(data['project_costs'])},
                    backgroundColor: '#3b82f6',
                    borderRadius: 8
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ grid: {{ color: 'rgba(255,255,255,0.05)' }}, ticks: {{ color: '#94a3b8' }} }},
                    y: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8' }} }}
                }}
            }}
        }});

        const ctxCli = document.getElementById('cliChart').getContext('2d');
        new Chart(ctxCli, {{
            type: 'bar',
            data: {{
                labels: {json.dumps(data['cli_names'])},
                datasets: [{{
                    label: 'Cost by CLI ($)',
                    data: {json.dumps(data['cli_costs'])},
                    backgroundColor: ['#3b82f6', '#ef4444', '#10b981', '#f59e0b'],
                    borderRadius: 8
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return '$' + context.parsed.x.toFixed(2);
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{ 
                        grid: {{ color: 'rgba(255,255,255,0.05)' }}, 
                        ticks: {{ 
                            color: '#94a3b8',
                            callback: function(value) {{ return '$' + value.toFixed(0); }}
                        }}
                    }},
                    y: {{ grid: {{ display: false }}, ticks: {{ color: '#94a3b8', font: {{ weight: 'bold' }} }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
    """
    # Write to a file in the temporary directory or current directory
    output_path = os.path.abspath("dashboard.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    print(f"[OK] Multi-CLI Dashboard generated: {output_path}")
    print(f"[INFO] Now tracking: Gemini CLI, Codex CLI, Opencode CLI, Ampcode CLI, Cline, Roo Code, and Kilo Code")
    webbrowser.open(f"file://{output_path}")

if __name__ == "__main__":
    main()
