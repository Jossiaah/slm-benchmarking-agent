import json
import re 
from typing import Any, Dict, Optional

class ResponseValidator:
    @staticmethod
    def extract_json(text: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to extract and parse a valid JSON object from a raw string.
        Handles common LLM mistakes like wrapping JSON in markdown code blocks.
        """
        try:
            #Direct path: strict JSON parsing
            return json.loads(text)
        except json.JSONDecodeError:
            # Fallback path: Regex search for hidden JSON blocks within text
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except json.JSONDecodeError:
                    return None
                return None
    @staticmethod
    def validate_schema(response_text: str, expected_schema_type: str) -> bool:
        """
        Grades the response based on the benchmarking prompt constraints.
        Returns true if the model followed instructions, False otherwise.
        """
        if expected_schema_type == "raw_text":
            # For raw code snippets, we ensure it isn't empty and contains text
            return len(response_text.strip()) > 0
        
        if expected_schema_type == "json":
            data = ResponseValidator.extract_json(response_text)
            if not data:
                return False
            
            # Specific validation check for our asset extraction benchmark prompt
            if "name" in data and "age" in data:
                return True
            
            return False 
        
        return False