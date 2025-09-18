# Project Structure for Development Agents

This document provides a high-level overview of how the ML Extractor codebase is organized by development agent responsibilities.

## Directory Structure by Agent Role

```
ml-extractor/
├── 📁 Backend Engineer Focus Areas
│   ├── src/
│   │   ├── mapper.py              # Core ML Template Processor
│   │   ├── mapping_loader.py      # Configuration handling
│   │   ├── file_reader.py         # File processing
│   │   ├── data_mapper.py         # Data transformation
│   │   ├── validation.py          # Data validation (Phase 3+)
│   │   └── api/                   # API layer (Phase 1+)
│   │       ├── app.py             # FastAPI application
│   │       └── routes/            # Route handlers
│   ├── tests/
│   │   ├── test_cli_map.py        # CLI integration tests
│   │   └── test_api_*.py          # API tests (Phase 1+)
│   └── config/                    # Configuration files
│
├── 🎨 Frontend Engineer Focus Areas
│   └── frontend/
│       ├── src/
│       │   ├── App.js             # Main application
│       │   ├── main.jsx           # Entry point
│       │   ├── pages/             # 6-step wizard pages
│       │   │   ├── MLMappingWizard.js
│       │   │   ├── FileUpload.js
│       │   │   ├── ProductDataAnalysis.js
│       │   │   └── MappingConfig.js
│       │   └── components/        # Reusable components
│       ├── package.json           # Dependencies
│       └── vite.config.js         # Build configuration
│
├── 🤖 ML Engineer Focus Areas
│   ├── src/
│   │   ├── enrichment/            # Core ML logic
│   │   │   ├── __init__.py        # Orchestration
│   │   │   ├── brand.py           # Brand detection
│   │   │   ├── sku.py             # SKU recognition
│   │   │   ├── color.py           # Color extraction
│   │   │   ├── weight.py          # Weight parsing
│   │   │   └── ean.py             # EAN validation
│   │   └── ai/                    # AI modules (Phase 4+)
│   ├── tests/
│   │   └── test_enrich_*.py       # Enrichment tests
│   └── samples/                   # Test data and templates
│
└── 📚 Shared Documentation
    ├── docs/
    │   ├── DEVELOPMENT_AGENTS.md   # This document
    │   └── PROJECT_STRUCTURE.md   # You are here
    ├── README.md                  # Project overview
    ├── ROADMAP.md                 # Development phases
    ├── AI_GUARDRAILS.md           # Architecture guidelines
    └── CONTRIBUTING.md            # Contribution guidelines
```

## Phase-Based Development Flow

### Phase 0 (Current) - Baseline Stabilization
```
🤖 ML Engineer: Enrich modules + tests
📁 Backend Engineer: Core mapper + CLI tests  
🎨 Frontend Engineer: React foundation
```

### Phase 1 - API Development
```
📁 Backend Engineer: FastAPI app + /health, /map endpoints
🤖 ML Engineer: API integration for enrichment
🎨 Frontend Engineer: API consumption preparation
```

### Phase 2 - UI-API Integration
```
🎨 Frontend Engineer: React calls to /map endpoint
📁 Backend Engineer: API refinement based on UI needs
🤖 ML Engineer: Enrichment optimization
```

### Phase 3 - Validation & Metadata
```
📁 Backend Engineer: Validation logic + metadata tracking
🤖 ML Engineer: _meta field integration in enrichments
🎨 Frontend Engineer: Display validation warnings
```

## Agent Collaboration Points

### Backend ↔ ML Engineer
- **Data Flow**: Raw data → Enrichment → Mapping → API Response
- **Integration Points**: 
  - `apply_enrichments()` function calls
  - Metadata format (`_meta` field structure)
  - Error handling and fallbacks

### Backend ↔ Frontend Engineer  
- **API Contracts**: REST endpoints for data processing
- **Data Formats**: JSON request/response structures
- **Integration Points**:
  - `/api/health` - System status
  - `/api/map` - Batch processing
  - `/api/map/single` - Single record processing

### Frontend ↔ ML Engineer
- **Visualization**: Display enrichment results and confidence
- **User Feedback**: ML accuracy indicators in UI
- **Integration Points**:
  - Enrichment result display
  - Confidence level visualization
  - Error state handling

## Development Workflow

### 1. Feature Planning
```
1. Identify which agent(s) are primary for the feature
2. Define integration points with other agents
3. Create focused plan following roadmap phase
4. Get approval from affected agents
```

### 2. Implementation
```
Primary Agent: Implements core feature
Secondary Agents: Provide integration support
All Agents: Review changes affecting their areas
```

### 3. Testing
```
Unit Tests: Each agent tests their components
Integration Tests: Cross-agent functionality
End-to-End Tests: Full workflow validation
```

### 4. Documentation
```
API Changes: Backend Engineer updates API docs
UI Changes: Frontend Engineer updates user guides  
ML Changes: ML Engineer updates enrichment docs
```

## Quick Start by Role

### Backend Engineer
```bash
# Set up environment
pip install -r requirements.txt

# Run core tests
PYTHONPATH=. python tests/test_cli_map.py

# Start development (Phase 1+)
# Create src/api/app.py and implement /health endpoint
```

### Frontend Engineer
```bash
# Set up frontend
cd frontend
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### ML Engineer
```bash
# Set up environment
pip install -r requirements.txt

# Test enrichment modules
PYTHONPATH=. python tests/test_enrich_brand.py

# Interactive testing
python -c "
from src.enrichment import apply_enrichments
result = apply_enrichments({'title': 'Sony Headphones'})
print(result)
"
```

## Communication Channels

### Daily Sync Points
- **Morning**: Review roadmap phase status
- **Implementation**: Use GitHub issues for coordination
- **Evening**: Ensure integration tests pass

### Code Review Process
1. **Self-Review**: Agent reviews own changes
2. **Cross-Review**: At least one other agent reviews
3. **Integration Check**: Verify no breaking changes
4. **Merge**: Only after all agents approve

---

*This structure ensures clear separation of concerns while maintaining effective collaboration between development agents.*