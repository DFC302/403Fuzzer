# 403Fuzzer

A penetration testing tool for fuzzing 401/403 restricted endpoints to discover access control bypasses.

## Features

- **Header-based bypasses** - Tests X-Forwarded-For, X-Original-URL, X-Rewrite-URL, and other common bypass headers
- **Path normalization attacks** - URL encoding, path traversal, trailing slashes, and other path manipulation techniques
- **HTTP verb tampering** - Tests alternative methods (GET, POST, PUT, DELETE, HEAD, OPTIONS, TRACE, LOCK, CONNECT, PROPFIND)
- **Method override attacks** - X-HTTP-Method-Override headers and method parameters
- **HTTP protocol attacks** - Tests HTTP/1.0, HTTP/0.9 downgrade attacks
- **Parameter pollution** - Duplicate parameters, array notation, case variations, encoded delimiters
- **Trailing dot attack** - Absolute domain technique (example.com.)
- **Smart filtering** - Auto-mutes repetitive responses to reduce noise
- **Interaction logging** - Saves successful requests to SQLite for later analysis
- **OOB detection support** - Integrate with Burp Collaborator or interactsh

## Installation

```bash
git clone https://github.com/DFC302/403Fuzzer.git
cd 403Fuzzer

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```bash
# Basic usage
python3 bypassfuzzer.py -u https://example.com/admin

# With authentication
python3 bypassfuzzer.py -u https://example.com/admin -H "Authorization: Bearer TOKEN"

# From Burp request file
python3 bypassfuzzer.py -r request.txt

# Pipe URL via stdin
echo "https://example.com/admin" | python3 bypassfuzzer.py
```

## Usage

```
python3 bypassfuzzer.py -h
```

### Target Specification

| Flag | Description |
|------|-------------|
| `-u, --url` | Target URL |
| `-r, --request` | Load raw HTTP request from file (Burp format) |
| `-m, --method` | HTTP method: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS, TRACE |
| `-d, --data` | Request body data |
| `-H, --header` | Add custom header (repeatable) |
| `-c, --cookies` | Cookies to include |
| `--scheme` | URL scheme (default: https) |
| `-hv, --http-vers` | HTTP version (default: HTTP/1.1) |
| `-p, --proxy` | Proxy URL (e.g., http://127.0.0.1:8080) |

### Filtering Output

| Flag | Description |
|------|-------------|
| `-hc` | Hide response codes (comma-separated) |
| `-hl` | Hide response lengths (comma-separated) |
| `-sf, --smart` | Enable smart filter (auto-mutes after 8 repeats) |

### Skip Attack Types

| Flag | Description |
|------|-------------|
| `-sh, --skip-headers` | Skip header payload attacks |
| `-su, --skip-urls` | Skip path/URL attacks |
| `-std, --skip-td` | Skip trailing dot attack |
| `-sm, --skip-method` | Skip verb/method attacks |
| `-sp, --skip-protocol` | Skip HTTP protocol attacks |
| `-spp, --skip-pp` | Skip parameter pollution attacks |

### Parameter Pollution

| Flag | Description |
|------|-------------|
| `--target-param` | Target specific parameter(s) for pollution testing |

### Interaction Database

| Flag | Description |
|------|-------------|
| `--save-interactions` | Save responses matching status codes (default: 200) |
| `--idb` | Specify database file to use |
| `--display-by` | Query by: index or payload |
| `-di, --display-interactions` | Display specific interaction |

### OOB Detection

| Flag | Description |
|------|-------------|
| `--oob` | OOB server domain (Collaborator, interactsh, etc.) |

## Examples

```bash
# Test with POST method and body data
python3 bypassfuzzer.py -u https://example.com/api/admin -m POST -d "id=1"

# Hide 403 and 404 responses
python3 bypassfuzzer.py -u https://example.com/admin -hc 403,404

# Use smart filter to reduce noise
python3 bypassfuzzer.py -u https://example.com/admin --smart

# Proxy through Burp
python3 bypassfuzzer.py -u https://example.com/admin -p http://127.0.0.1:8080

# Only test header and path attacks
python3 bypassfuzzer.py -u https://example.com/admin -sm -sp -spp

# Test specific parameters for pollution
python3 bypassfuzzer.py -u "https://example.com/api?user=1&role=user" --target-param role

# Review saved interaction
python3 bypassfuzzer.py --display-by index -di 42
```

## Interactive Controls

Press **Enter** during a scan to pause/resume. While paused:

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `status` | Show current fuzzer state |
| `set smart=on` | Enable smart filter |
| `set save_interactions=[200,302]` | Change which responses to save |

## Credits

Originally created by [@intrudir](https://twitter.com/intrudir)

If this tool helped you find a bypass:
[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/O5O3ZVDGN)
