"""
ML processing service - handles AI enhancement and intelligent data processing
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# OpenAI integration (if available)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# LangChain integration (if available)
try:
    from langchain.llms import OpenAI
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

class MLProcessorService:
    """Service for AI/ML enhanced data processing"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        
        if OPENAI_AVAILABLE and self.openai_api_key:
            openai.api_key = self.openai_api_key
    
    def enhance_data(self, data: List[Dict[str, Any]], mapping_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance data using AI/ML techniques
        
        Args:
            data: List of data records
            mapping_config: Configuration for AI enhancement
            
        Returns:
            Dictionary containing enhanced data and processing results
        """
        
        if not self._is_ai_available():
            return self._fallback_enhancement(data, mapping_config)
        
        try:
            enhanced_records = []
            processing_stats = {
                "total_records": len(data),
                "enhanced_records": 0,
                "failed_records": 0,
                "enhancement_types": []
            }
            
            ai_config = mapping_config.get("ai_enhancement", {})
            enhancement_types = ai_config.get("types", ["text_improvement", "data_completion"])
            
            for record in data:
                try:
                    enhanced_record = self._enhance_record(record, enhancement_types)
                    enhanced_records.append(enhanced_record)
                    processing_stats["enhanced_records"] += 1
                except Exception as e:
                    # Keep original record if enhancement fails
                    enhanced_records.append(record)
                    processing_stats["failed_records"] += 1
                    print(f"Enhancement failed for record: {str(e)}")
            
            processing_stats["enhancement_types"] = enhancement_types
            
            return {
                "enhanced_data": enhanced_records,
                "original_count": len(data),
                "enhanced_count": len(enhanced_records),
                "processing_stats": processing_stats,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"AI enhancement failed: {str(e)}")
    
    def _enhance_record(self, record: Dict[str, Any], enhancement_types: List[str]) -> Dict[str, Any]:
        """Enhance a single record"""
        
        enhanced_record = record.copy()
        
        for enhancement_type in enhancement_types:
            if enhancement_type == "text_improvement":
                enhanced_record = self._improve_text_fields(enhanced_record)
            elif enhancement_type == "data_completion":
                enhanced_record = self._complete_missing_data(enhanced_record)
            elif enhancement_type == "categorization":
                enhanced_record = self._auto_categorize(enhanced_record)
            elif enhancement_type == "price_optimization":
                enhanced_record = self._optimize_pricing(enhanced_record)
        
        return enhanced_record
    
    def _improve_text_fields(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Improve text fields using AI"""
        
        text_fields = ["title", "description", "name", "product_name"]
        enhanced_record = record.copy()
        
        for field in text_fields:
            if field in record and record[field]:
                original_text = str(record[field])
                
                if len(original_text) > 10:  # Only process meaningful text
                    try:
                        improved_text = self._call_openai_for_text_improvement(original_text)
                        if improved_text and improved_text != original_text:
                            enhanced_record[f"{field}_enhanced"] = improved_text
                    except Exception as e:
                        print(f"Text improvement failed for field {field}: {str(e)}")
        
        return enhanced_record
    
    def _complete_missing_data(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Complete missing data using AI inference"""
        
        enhanced_record = record.copy()
        
        # Try to infer missing category from title/description
        if not record.get("category") and (record.get("title") or record.get("description")):
            try:
                inferred_category = self._infer_category(record)
                if inferred_category:
                    enhanced_record["category_inferred"] = inferred_category
            except Exception as e:
                print(f"Category inference failed: {str(e)}")
        
        # Try to infer missing brand from title/description
        if not record.get("brand") and (record.get("title") or record.get("description")):
            try:
                inferred_brand = self._infer_brand(record)
                if inferred_brand:
                    enhanced_record["brand_inferred"] = inferred_brand
            except Exception as e:
                print(f"Brand inference failed: {str(e)}")
        
        return enhanced_record
    
    def _auto_categorize(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Automatically categorize products"""
        
        enhanced_record = record.copy()
        
        if record.get("title") or record.get("description"):
            try:
                category_suggestions = self._suggest_categories(record)
                if category_suggestions:
                    enhanced_record["suggested_categories"] = category_suggestions
            except Exception as e:
                print(f"Auto-categorization failed: {str(e)}")
        
        return enhanced_record
    
    def _optimize_pricing(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize pricing using market analysis"""
        
        enhanced_record = record.copy()
        
        if record.get("price") and (record.get("title") or record.get("category")):
            try:
                price_analysis = self._analyze_pricing(record)
                if price_analysis:
                    enhanced_record["price_analysis"] = price_analysis
            except Exception as e:
                print(f"Price optimization failed: {str(e)}")
        
        return enhanced_record
    
    def _call_openai_for_text_improvement(self, text: str) -> Optional[str]:
        """Call OpenAI API for text improvement"""
        
        if not OPENAI_AVAILABLE or not self.openai_api_key:
            return None
        
        try:
            prompt = f"""
            Improve the following product text by making it more professional, clear, and engaging while keeping the original meaning:
            
            Original: {text}
            
            Improved:
            """
            
            response = openai.ChatCompletion.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that improves product descriptions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            improved_text = response.choices[0].message.content.strip()
            return improved_text if len(improved_text) > 5 else None
            
        except Exception as e:
            print(f"OpenAI text improvement failed: {str(e)}")
            return None
    
    def _infer_category(self, record: Dict[str, Any]) -> Optional[str]:
        """Infer product category using AI"""
        
        if not OPENAI_AVAILABLE or not self.openai_api_key:
            return self._rule_based_category_inference(record)
        
        try:
            text = record.get("title", "") + " " + record.get("description", "")
            text = text.strip()
            
            if not text:
                return None
            
            prompt = f"""
            Based on the following product information, suggest the most appropriate category:
            
            Product: {text}
            
            Categories to choose from: Electronics, Clothing, Home & Garden, Sports & Outdoors, Health & Beauty, Automotive, Books, Toys & Games, Food & Beverages, Other
            
            Category:
            """
            
            response = openai.ChatCompletion.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that categorizes products."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0.1
            )
            
            category = response.choices[0].message.content.strip()
            return category if category in ["Electronics", "Clothing", "Home & Garden", "Sports & Outdoors", 
                                           "Health & Beauty", "Automotive", "Books", "Toys & Games", 
                                           "Food & Beverages", "Other"] else None
            
        except Exception as e:
            print(f"AI category inference failed: {str(e)}")
            return self._rule_based_category_inference(record)
    
    def _infer_brand(self, record: Dict[str, Any]) -> Optional[str]:
        """Infer product brand"""
        
        text = record.get("title", "") + " " + record.get("description", "")
        
        # Simple brand extraction using common patterns
        import re
        
        # Look for capitalized words that might be brands
        words = re.findall(r'\b[A-Z][a-z]+\b', text)
        
        # Common brand indicators
        brand_indicators = ["brand", "marca", "by", "de"]
        
        for word in words:
            if len(word) > 2 and word.lower() not in ["the", "and", "for", "with"]:
                return word
        
        return None
    
    def _suggest_categories(self, record: Dict[str, Any]) -> List[str]:
        """Suggest multiple categories"""
        
        # Rule-based category suggestions
        text = (record.get("title", "") + " " + record.get("description", "")).lower()
        
        categories = []
        
        category_keywords = {
            "Electronics": ["electronic", "digital", "computer", "phone", "tablet", "camera"],
            "Clothing": ["shirt", "pants", "dress", "shoe", "clothing", "apparel"],
            "Home & Garden": ["home", "garden", "furniture", "kitchen", "bathroom"],
            "Sports & Outdoors": ["sport", "outdoor", "fitness", "exercise", "bike"],
            "Health & Beauty": ["health", "beauty", "cosmetic", "skincare", "vitamin"],
            "Automotive": ["car", "auto", "vehicle", "tire", "engine"],
            "Books": ["book", "novel", "magazine", "guide", "manual"],
            "Toys & Games": ["toy", "game", "puzzle", "doll", "action figure"],
            "Food & Beverages": ["food", "drink", "snack", "beverage", "organic"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                categories.append(category)
        
        return categories[:3]  # Return top 3 suggestions
    
    def _analyze_pricing(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze pricing for optimization"""
        
        current_price = float(record.get("price", 0))
        
        # Simple pricing analysis (would be more sophisticated in practice)
        analysis = {
            "current_price": current_price,
            "suggested_range": {
                "min": round(current_price * 0.9, 2),
                "max": round(current_price * 1.1, 2)
            },
            "price_tier": "budget" if current_price < 50 else "premium" if current_price > 200 else "mid-range"
        }
        
        return analysis
    
    def _rule_based_category_inference(self, record: Dict[str, Any]) -> Optional[str]:
        """Fallback rule-based category inference"""
        
        text = (record.get("title", "") + " " + record.get("description", "")).lower()
        
        # Simple keyword-based categorization
        if any(word in text for word in ["phone", "computer", "electronic"]):
            return "Electronics"
        elif any(word in text for word in ["shirt", "dress", "clothing"]):
            return "Clothing"
        elif any(word in text for word in ["book", "novel"]):
            return "Books"
        else:
            return "Other"
    
    def _fallback_enhancement(self, data: List[Dict[str, Any]], mapping_config: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback enhancement when AI is not available"""
        
        enhanced_records = []
        
        for record in data:
            enhanced_record = record.copy()
            
            # Basic text cleaning
            for field in ["title", "description", "name"]:
                if field in record and record[field]:
                    # Basic text improvement
                    text = str(record[field])
                    improved_text = self._basic_text_improvement(text)
                    if improved_text != text:
                        enhanced_record[f"{field}_cleaned"] = improved_text
            
            # Basic category inference
            if not record.get("category"):
                inferred_category = self._rule_based_category_inference(record)
                if inferred_category:
                    enhanced_record["category_inferred"] = inferred_category
            
            enhanced_records.append(enhanced_record)
        
        return {
            "enhanced_data": enhanced_records,
            "original_count": len(data),
            "enhanced_count": len(enhanced_records),
            "processing_stats": {
                "total_records": len(data),
                "enhanced_records": len(enhanced_records),
                "failed_records": 0,
                "enhancement_types": ["basic_cleaning", "rule_based_inference"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _basic_text_improvement(self, text: str) -> str:
        """Basic text cleaning and improvement"""
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Capitalize first letter
        if text:
            text = text[0].upper() + text[1:]
        
        # Remove excessive punctuation
        import re
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        text = re.sub(r'[.]{2,}', '...', text)
        
        return text
    
    def _is_ai_available(self) -> bool:
        """Check if AI services are available"""
        return OPENAI_AVAILABLE and self.openai_api_key is not None
    
    def get_enhancement_capabilities(self) -> Dict[str, Any]:
        """Get available enhancement capabilities"""
        
        capabilities = {
            "ai_available": self._is_ai_available(),
            "enhancement_types": [
                {
                    "id": "text_improvement",
                    "name": "Text Improvement",
                    "description": "Improve product titles and descriptions",
                    "available": self._is_ai_available()
                },
                {
                    "id": "data_completion",
                    "name": "Data Completion",
                    "description": "Fill missing category and brand information",
                    "available": True  # Always available with fallback
                },
                {
                    "id": "categorization",
                    "name": "Auto Categorization",
                    "description": "Automatically suggest product categories",
                    "available": True
                },
                {
                    "id": "price_optimization",
                    "name": "Price Analysis",
                    "description": "Analyze and optimize pricing",
                    "available": True
                }
            ]
        }
        
        return capabilities
