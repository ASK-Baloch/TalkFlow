# ruff: noqa
import re
from typing import Any


class SemanticExtractor:
    @staticmethod
    def extract(text: str) -> dict[str, Any]:
        """
        Deterministically extracts domain entities from the transcript.
        """
        text = text.lower().replace(".", "").replace(",", "").replace("-", " ")
        
        result = {
            "medicare": False,
            "medicaid": False,
            "part_a": "unknown",
            "part_b": "unknown",
            "negation": False,
            "zip": None,
            "age": None,
            "carrier": None,
            "talkflow": False
        }
        
        # Medicare vs Medicaid
        if "medicare" in text:
            result["medicare"] = True
        if "medicaid" in text:
            result["medicaid"] = True
            
        # Part A / B
        if "part a" in text:
            result["part_a"] = "yes"
        if "part b" in text:
            result["part_b"] = "yes"
            
        # Negation
        if "no " in text or "don't" in text or "dont" in text or "not " in text:
            result["negation"] = True
            
        # TalkFlow
        if "talkflow" in text or "talk flow" in text:
            result["talkflow"] = True
            
        # Carriers
        carriers = ["humana", "aetna", "united", "blue cross"]
        for c in carriers:
            if c in text:
                result["carrier"] = c
                break
                
        # Zip (5 consecutive digits)
        # We also need to map words to numbers for zip code if it's spoken out loud
        # But Whisper usually returns digits.
        digits = re.sub(r'[^0-9]', '', text)
        if len(digits) == 5 and "zip" in text:
            result["zip"] = digits
        elif "zip" in text:
            # Maybe the number isn't 5 digits or something else
            pass
            
        # Age
        age_match = re.search(r'\b(\d{2})\b(?=.*(years old|age))', text)
        if age_match:
            result["age"] = age_match.group(1)
        elif "years old" in text or "i am" in text:
            # Fallback if digits were matched
            digit_match = re.search(r'\b(\d{2})\b', text)
            if digit_match and "zip" not in text:
                result["age"] = digit_match.group(1)
                
        return result

