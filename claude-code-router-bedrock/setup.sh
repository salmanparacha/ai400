#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PROFILE="${AWS_PROFILE:-${1:-default}}"
REGION="${AWS_REGION:-${2:-ca-central-1}}"

export AWS_PROFILE="$PROFILE"
export AWS_REGION="$REGION"

echo "🚀 Bedrock Router Setup"
echo "======================="
echo ""

if ! command -v node >/dev/null 2>&1; then
  echo "❌ Node.js not found. Install Node.js 18+." >&2
  exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
  echo "❌ Node.js 18+ required. Current: $(node -v)" >&2
  exit 1
fi

if ! command -v aws >/dev/null 2>&1; then
  echo "❌ AWS CLI not found. Install AWS CLI and configure SSO." >&2
  exit 1
fi

if ! command -v ccr >/dev/null 2>&1; then
  echo "❌ claude-code-router (ccr) not found in PATH." >&2
  exit 1
fi

echo "✅ Node.js $(node -v) detected"
echo "✅ AWS CLI detected"
echo "✅ ccr detected"
echo ""

echo "🔐 Logging in via AWS SSO (profile: $PROFILE)..."
aws sso login --profile "$PROFILE"
echo "✅ SSO login ok"
echo ""

echo "📦 Installing dependencies..."
npm install
echo "✅ Dependencies installed"
echo ""

pkill -f "proxy-server.js" >/dev/null 2>&1 || true
nohup node "$SCRIPT_DIR/proxy-server.js" > /tmp/bedrock-proxy.log 2>&1 &

ccr restart

echo ""
echo "✨ Setup complete"
echo "Proxy log: /tmp/bedrock-proxy.log"
