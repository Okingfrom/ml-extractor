from fastapi import FastAPI, HTTPException
from typing import Dict, List, Any, Union
import pandas as pd
from ..mapper import apply_mapping
from ..mapping_loader import load_mapping
from ..logging_utils import logger, timed

app = FastAPI(title="ML Extractor API", version="1.0.0")

# Load default mapping configuration
try:
    template_columns, mapping_config = load_mapping("config/mapping.yaml") 
    DEFAULT_MAPPING = mapping_config
    DEFAULT_TEMPLATE_COLUMNS = template_columns
    logger.info("Loaded mapping configuration from config/mapping.yaml")
except Exception as e:
    # Fallback mapping if config file unavailable
    DEFAULT_MAPPING = {"title": "title", "price": "price"}
    DEFAULT_TEMPLATE_COLUMNS = ["title", "price", "description", "brand", "sku", "color", "weight", "ean"]
    logger.warning(f"Failed to load mapping config, using fallback: {e}")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "1.0.0"}

@app.post("/map")
def map_records(data: Dict[str, Any]):
    """
    Map multiple product records using enrichment pipeline.
    Tolerant behavior: empty payload or non-list records treated as empty list.
    """
    stop_timer = timed("batch mapping")
    
    try:
        # Tolerant coercion: treat any non-list as empty list
        records_raw = data.get("records", [])
        if not isinstance(records_raw, list):
            records = []  # Coerce non-list to empty list (tolerant behavior)
        else:
            records = records_raw
        
        mapped_records = []
        for record in records:
            mapped_df = apply_mapping(record, DEFAULT_MAPPING, DEFAULT_TEMPLATE_COLUMNS)
            mapped_record = mapped_df.iloc[0].to_dict()
            mapped_records.append(mapped_record)
        
        stop_timer({"record_count": len(records)})
        return {"records": mapped_records}
        
    except Exception as e:
        logger.error(f"Error in batch mapping: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/map/single")  
def map_single_record(data: Dict[str, Any]):
    """Map a single product record using enrichment pipeline"""
    try:
        record = data.get("record", {})
        if not record:
            raise HTTPException(status_code=400, detail="No record provided")
            
        mapped_df = apply_mapping(record, DEFAULT_MAPPING, DEFAULT_TEMPLATE_COLUMNS)
        mapped_record = mapped_df.iloc[0].to_dict()
        
        logger.debug(f"Mapped single record: {len(record)} fields -> {len(mapped_record)} fields")
        return {"record": mapped_record}
        
    except HTTPException:
        raise  # Re-raise HTTPException as-is
    except Exception as e:
        logger.error(f"Error in single mapping: {e}")
        raise HTTPException(status_code=500, detail=str(e))
