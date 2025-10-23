#!/bin/bash
# Demo Preparation Script
# Run this before your demo to ensure everything is ready

set -e

echo "🎯 Preparing Skills Demo..."
echo ""

# Check if Ollama is running
echo "1️⃣ Checking Ollama..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "   ⚠️  Ollama is not running. Starting in background..."
    ollama serve &
    sleep 3
else
    echo "   ✅ Ollama is running"
fi

# Check if gpt-oss:20b is available
echo ""
echo "2️⃣ Checking for gpt-oss:20b model..."
if ollama list | grep -q "gpt-oss:20b"; then
    echo "   ✅ gpt-oss:20b model is available"
else
    echo "   ⚠️  gpt-oss:20b not found. Pulling it now (this may take a few minutes)..."
    ollama pull gpt-oss:20b
fi

# Check Python environment
echo ""
echo "3️⃣ Checking Python environment..."
if [ -d ".venv" ]; then
    echo "   ✅ Virtual environment found"
else
    echo "   ⚠️  No .venv found. Creating one..."
    python -m venv .venv
fi

# Activate and install
echo ""
echo "4️⃣ Installing dependencies..."
source .venv/bin/activate 2>/dev/null || . .venv/bin/activate
uv pip install -e . > /dev/null 2>&1 || pip install -e . > /dev/null 2>&1
echo "   ✅ Dependencies installed"

# Run quick test
echo ""
echo "5️⃣ Running quick test..."
if pytest tests/test_skill_loader.py -v > /dev/null 2>&1; then
    echo "   ✅ Tests passing"
else
    echo "   ⚠️  Some tests failed (non-critical for demo)"
fi

# Count available skills
echo ""
echo "6️⃣ Skills available:"
SKILL_COUNT=$(ls .skills/*.md 2>/dev/null | wc -l)
echo "   📚 $SKILL_COUNT skills loaded:"
ls .skills/*.md | xargs -n 1 basename | sed 's/.md$//' | sed 's/^/      - /'

# Create demo files
echo ""
echo "7️⃣ Creating demo artifacts..."
cat > demo_code.py << 'EOF'
def calculate_discount(price, discount_percent):
    """Calculate discounted price."""
    if discount_percent > 100:
        discount_percent = 100
    if discount_percent < 0:
        discount_percent = 0
    discount = price * (discount_percent / 100)
    return price - discount

def process_order(items):
    """Calculate total price for order items."""
    total = 0
    for item in items:
        if item['quantity'] > 0:
            total += item['price'] * item['quantity']
    return total
EOF
echo "   ✅ Created demo_code.py"

# Create a clean git state for demo
if [ -d ".git" ]; then
    # Stash any current changes
    git stash push -u -m "Pre-demo stash" > /dev/null 2>&1 || true
    echo "   ✅ Git state cleaned (changes stashed)"
fi

# Print demo commands
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✨ READY FOR DEMO!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🎬 To start demo:"
echo "   1. Run: source .venv/bin/activate"
echo "   2. Run: skills --model gpt-oss:20b"
echo "   3. Follow DEMO.md script"
echo ""
echo "💡 Quick commands:"
echo "   - List skills:   Type '/skills' in interactive mode"
echo "   - Create skill:  'Create a skill called X that does Y'"
echo "   - Use skill:     Just describe what you want"
echo ""
echo "📖 Full script: cat DEMO.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
