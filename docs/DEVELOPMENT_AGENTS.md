# Development Agents - Role Definitions

This document defines the three development agent roles for the ML Extractor project, their responsibilities, focus areas, and collaboration guidelines.

## Overview

The ML Extractor project is organized around three specialized development roles:

1. **Backend Engineer (Django/Python)** - Core ML Template Processor, data validation, and API endpoints
2. **Frontend Engineer (React)** - 6-step wizard UI and data visualization components  
3. **ML Engineer** - ML-based template detection, column analysis, and pattern recognition

## 1. Backend Engineer (Django/Python)

### Primary Responsibilities
- Core ML Template Processor development and maintenance
- Data validation logic and error handling
- API endpoint design and implementation
- Database integration (when applicable per roadmap phases)
- Integration with ML components

### Focus Areas & Files
**Core ML Template Processor:**
- `src/mapper.py` - Main mapping logic
- `src/mapping_loader.py` - Configuration and mapping resolution
- `src/file_reader.py` - File input processing
- `src/data_mapper.py` - Data transformation utilities

**API Development (Phase 1+):**
- `src/api/app.py` - FastAPI application (to be created)
- `src/api/routes/` - API route handlers (when needed)

**Data Validation (Phase 3+):**
- `src/validation.py` - Validation logic (to be created)
- Integration with enrichment modules for metadata tracking

**Testing:**
- `tests/test_cli_map.py` - CLI mapping tests
- `tests/test_api_*.py` - API endpoint tests (Phase 1+)

### Key Skills Required
- Python/Django expertise
- FastAPI for API development
- Data processing with pandas
- File format handling (Excel, CSV, PDF)
- Integration testing

### Collaboration Points
- Works with ML Engineer on enrichment integration
- Provides APIs for Frontend Engineer consumption
- Ensures data validation supports UI requirements

## 2. Frontend Engineer (React)

### Primary Responsibilities
- 6-step wizard UI implementation
- Data visualization components
- User experience and interface design
- Frontend state management
- API integration with backend

### Focus Areas & Files
**Main Application:**
- `frontend/src/App.js` - Main React application
- `frontend/src/main.jsx` - Application entry point
- `frontend/package.json` - Dependencies and scripts

**6-Step Wizard UI:**
- `frontend/src/pages/MLMappingWizard.js` - Main wizard component
- `frontend/src/pages/FileUpload.js` - File upload step
- `frontend/src/pages/ProductDataAnalysis.js` - Data analysis step
- `frontend/src/pages/MappingConfig.js` - Mapping configuration

**Data Visualization:**
- `frontend/src/components/` - Reusable UI components
- Data preview and mapping visualization components
- Results display and export interfaces

**Configuration:**
- `frontend/vite.config.js` - Build and development configuration
- `frontend/src/index.css` - Styling (keep minimal per guardrails)

### Key Skills Required
- React and modern JavaScript
- Vite build system
- REST API integration with axios
- Responsive UI design
- State management (avoid complex libraries per guardrails)

### Collaboration Points
- Consumes APIs provided by Backend Engineer
- Works with ML Engineer on result visualization
- Provides feedback on API design for usability

## 3. ML Engineer

### Primary Responsibilities
- ML-based template detection algorithms
- Column analysis and pattern recognition
- Data enrichment logic
- ML model integration (Phase 4+)
- Performance optimization for ML operations

### Focus Areas & Files
**Enrichment Modules:**
- `src/enrichment/__init__.py` - Main enrichment orchestration
- `src/enrichment/brand.py` - Brand detection and normalization
- `src/enrichment/sku.py` - SKU pattern recognition
- `src/enrichment/color.py` - Color extraction
- `src/enrichment/weight.py` - Weight/dimension parsing
- `src/enrichment/ean.py` - EAN/barcode validation

**ML Integration (Phase 4+):**
- `src/ai/` - AI/ML modules (to be created)
- Model integration with feature flags
- Fallback logic for ML failures

**Testing:**
- `tests/test_enrich_*.py` - Enrichment module tests
- ML model validation tests (Phase 4+)

### Key Skills Required
- Machine learning and pattern recognition
- Python data processing
- Regular expressions and text analysis
- Model integration and deployment
- Performance optimization

### Collaboration Points
- Provides enrichment APIs for Backend Engineer integration
- Works with Frontend Engineer on ML result visualization
- Ensures ML outputs are compatible with validation requirements

## Collaboration Guidelines

### Phase-Based Development
Follow the roadmap phases strictly:
- **Phase 0**: Focus on baseline testing and enrichment
- **Phase 1**: Backend Engineer leads API development
- **Phase 2**: Frontend Engineer leads UI-API integration
- **Phase 3**: All agents collaborate on validation and metadata
- **Phase 4+**: ML Engineer leads AI integration

### Communication Protocols
1. **API Contracts**: Backend Engineer defines APIs in consultation with Frontend Engineer
2. **Data Formats**: ML Engineer defines enrichment output formats for Backend integration
3. **UI Requirements**: Frontend Engineer provides requirements for API design
4. **Testing Strategy**: All agents contribute to integration testing

### Code Review Responsibilities
- **Backend Engineer**: Reviews API and core logic changes
- **Frontend Engineer**: Reviews UI/UX and integration changes
- **ML Engineer**: Reviews enrichment and AI-related changes
- **Cross-Review**: All major changes require review from at least one other role

### Conflict Resolution
1. Refer to AI_GUARDRAILS.md for architectural decisions
2. Prioritize current phase requirements over future planning
3. Keep changes minimal and focused per role responsibilities
4. Escalate to roadmap review if phase boundaries are unclear

## Development Environment Setup

### Backend Engineer Setup
```bash
pip install -r requirements.txt
# Run existing tests
PYTHONPATH=. python tests/test_enrich_brand.py
```

### Frontend Engineer Setup
```bash
cd frontend
npm install
npm run dev  # Development server
npm run build  # Production build
```

### ML Engineer Setup
```bash
pip install -r requirements.txt
# Test enrichment modules
PYTHONPATH=. python -c "from src.enrichment import apply_enrichments; print('ML modules loaded')"
```

## Success Metrics

### Backend Engineer
- API endpoints respond within 200ms for single record mapping
- 100% test coverage for validation logic
- Zero data loss during processing

### Frontend Engineer
- 6-step wizard completes in under 60 seconds
- Mobile-responsive design
- Accessible UI components

### ML Engineer
- >90% accuracy for brand detection
- Enrichment processing under 100ms per record
- Graceful fallbacks for edge cases

---

*Last Updated: December 2024*
*Version: 1.0 (Phase 0-1 Focus)*