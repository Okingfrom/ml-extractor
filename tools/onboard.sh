#!/bin/bash

# ML Extractor - Development Team Onboarding Script
# Usage: ./onboard.sh [backend|frontend|ml]

set -e

ROLE=${1:-""}
PROJECT_ROOT=$(pwd)

echo "🚀 ML Extractor Development Team Onboarding"
echo "============================================"

if [ "$ROLE" = "" ]; then
    echo "Usage: ./onboard.sh [backend|frontend|ml]"
    echo ""
    echo "Available roles:"
    echo "  backend  - Backend Engineer (Python/API)"
    echo "  frontend - Frontend Engineer (React)"
    echo "  ml       - ML Engineer (Enrichment/AI)"
    echo ""
    exit 1
fi

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Check Node.js (for frontend)
if [ "$ROLE" = "frontend" ]; then
    if ! command -v npm &> /dev/null; then
        echo "❌ Node.js/npm is required for frontend development"
        exit 1
    fi
    echo "✅ Node.js found: $(node --version)"
    echo "✅ npm found: $(npm --version)"
fi

echo ""

# Role-specific setup
case $ROLE in
    "backend")
        echo "🔧 Setting up Backend Engineer environment..."
        echo "Installing Python dependencies..."
        pip install --user -r requirements.txt || echo "⚠️  Some dependencies may have failed - continuing..."
        
        echo "Running backend tests..."
        PYTHONPATH=. python tests/test_cli_map.py
        
        echo ""
        echo "🎉 Backend Engineer setup complete!"
        echo ""
        echo "📚 Next steps:"
        echo "1. Read: docs/DEVELOPMENT_AGENTS.md (Backend Engineer section)"
        echo "2. Review: src/mapper.py (core processor)"
        echo "3. Check roadmap: Phase 1 API development in ROADMAP.md"
        echo "4. Run tests: PYTHONPATH=. python tests/test_cli_map.py"
        echo ""
        echo "🔗 Key files for Backend Engineers:"
        echo "   - src/mapper.py (core ML template processor)"
        echo "   - src/mapping_loader.py (configuration handling)"
        echo "   - src/file_reader.py (file processing)"
        echo "   - Phase 1: Create src/api/app.py (FastAPI)"
        ;;
        
    "frontend")
        echo "🎨 Setting up Frontend Engineer environment..."
        cd frontend
        
        echo "Installing npm dependencies..."
        npm install
        
        echo "Testing build process..."
        npm run build
        
        cd "$PROJECT_ROOT"
        
        echo ""
        echo "🎉 Frontend Engineer setup complete!"
        echo ""
        echo "📚 Next steps:"
        echo "1. Read: docs/DEVELOPMENT_AGENTS.md (Frontend Engineer section)"
        echo "2. Review: frontend/src/App.js (main application)"
        echo "3. Check: frontend/src/pages/ (6-step wizard components)"
        echo "4. Start dev server: cd frontend && npm run dev"
        echo ""
        echo "🔗 Key files for Frontend Engineers:"
        echo "   - frontend/src/App.js (main React app)"
        echo "   - frontend/src/pages/MLMappingWizard.js (wizard UI)"
        echo "   - frontend/src/components/ (reusable components)"
        echo "   - Phase 2: API integration with backend"
        ;;
        
    "ml")
        echo "🤖 Setting up ML Engineer environment..."
        echo "Installing Python dependencies..."
        pip install --user -r requirements.txt || echo "⚠️  Some dependencies may have failed - continuing..."
        
        echo "Testing ML/enrichment modules..."
        for test_file in tests/test_enrich_*.py; do
            echo "  Testing $(basename $test_file)..."
            PYTHONPATH=. python "$test_file"
        done
        
        echo "Testing enrichment pipeline..."
        python3 -c "
from src.enrichment import apply_enrichments
result = apply_enrichments({'title': 'Sony WH-1000XM4 Headphones', 'price': '299.99'})
print('✅ Enrichment pipeline test:')
for key, value in result.items():
    print(f'   {key}: {value}')
"
        
        echo ""
        echo "🎉 ML Engineer setup complete!"
        echo ""
        echo "📚 Next steps:"
        echo "1. Read: docs/DEVELOPMENT_AGENTS.md (ML Engineer section)"
        echo "2. Review: src/enrichment/ (all enrichment modules)"
        echo "3. Study: Pattern recognition in existing modules"
        echo "4. Phase 4: Prepare for AI integration"
        echo ""
        echo "🔗 Key files for ML Engineers:"
        echo "   - src/enrichment/__init__.py (orchestration)"
        echo "   - src/enrichment/brand.py (brand detection)"
        echo "   - src/enrichment/sku.py (SKU recognition)"
        echo "   - Phase 4: Create src/ai/ (AI modules)"
        ;;
        
    *)
        echo "❌ Unknown role: $ROLE"
        exit 1
        ;;
esac

echo ""
echo "📋 General resources:"
echo "   - ROADMAP.md - Development phases and current status"
echo "   - AI_GUARDRAILS.md - Architecture guidelines"
echo "   - CONTRIBUTING.md - Code contribution guidelines"
echo "   - docs/ - Team documentation"
echo ""
echo "💬 Need help? Check the documentation or ask your team lead!"