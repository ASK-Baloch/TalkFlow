import logging
import re
from functools import lru_cache

logger = logging.getLogger("talkflow.asr.normalization")


class DomainNormalizer:
    def __init__(self):
        from app.core.config import get_asr_vocabulary
        self.vocab = get_asr_vocabulary()
        
        # Parse terms
        self.terms = self.vocab.get("terms", {})
        
        # Compile patterns for each term
        self._compiled_patterns = {}
        for term_key, term_data in self.terms.items():
            canonical = term_data.get("canonical", term_key)
            variants = term_data.get("variants", [])
            
            # Escape strings to be safe for regex
            match_strings = [re.escape(canonical)] + [re.escape(v) for v in variants]
            
            # Sort by length descending to match longest phrases first (e.g., 'Medicare Part A' before 'Medicare')
            match_strings.sort(key=len, reverse=True)
            
            # Create regex boundary pattern
            pattern_str = r'\b(?:' + '|'.join(match_strings) + r')\b'
            
            self._compiled_patterns[term_key] = {
                "pattern": re.compile(pattern_str, flags=re.IGNORECASE),
                "canonical": canonical
            }
            
        # Extract globals
        self.global_terms = self.vocab.get("global", [])
        
        # States
        self.state_terms = self.vocab.get("states", {})

    def normalize(self, text: str, context_hints: list[str] | None = None) -> tuple[str, list[dict[str, str]]]:
        if not text:
            return text, []
            
        original_text = text
        corrections = []

        # 1. Normalize numbers
        text = self._normalize_numbers(text)

        # 2. Determine active terms based on context
        active_term_keys = set(self.global_terms)
        
        if context_hints:
            for hint in context_hints:
                if hint in self.state_terms:
                    active_term_keys.update(self.state_terms[hint])
                elif hint in self.terms:
                    # Also allow directly passing a term key as a hint
                    active_term_keys.add(hint)

        # 3. Apply compiled regex patterns
        # To avoid partial overlapping replacements (like 'Medicare Part A' vs 'Medicare'),
        # we ideally replace longer canonical matches first, but since they are processed independently
        # we'll sort active keys by canonical length descending.
        sorted_keys = sorted(
            active_term_keys, 
            key=lambda k: len(self._compiled_patterns[k]["canonical"]) if k in self._compiled_patterns else 0, 
            reverse=True
        )

        for term_key in sorted_keys:
            if term_key not in self._compiled_patterns:
                continue
                
            entry = self._compiled_patterns[term_key]
            pattern = entry["pattern"]
            canonical = entry["canonical"]
            
            # Keep track of matches to log them
            def replace_and_log(match, canonical_inner=canonical):
                matched_str = match.group(0)
                # Only log if it's an actual correction (case or text differs)
                if matched_str != canonical_inner:
                    corrections.append({
                        "original": matched_str,
                        "corrected": canonical_inner,
                        "method": "domain_alias"
                    })
                return canonical_inner
                
            text = pattern.sub(replace_and_log, text)
            
        # Basic cleanup
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Log corrections
        if corrections:
            import json
            for corr in corrections:
                log_data = {
                    "event": "asr_domain_normalization",
                    "original_phrase": corr["original"],
                    "canonical": corr["corrected"],
                    "raw_text": original_text,
                    "normalized_text": text
                }
                logger.debug(json.dumps(log_data))
            
        return text, corrections

    def _normalize_numbers(self, text: str) -> str:
        number_words = {
            'zero': '0', 'oh': '0',
            'one': '1', 'two': '2', 'three': '3', 
            'four': '4', 'five': '5', 'six': '6', 
            'seven': '7', 'eight': '8', 'nine': '9'
        }
        
        words_pattern = r'\b(?:' + '|'.join(number_words.keys()) + r')\b'
        five_digit_pattern = r'((?:' + words_pattern + r'\s+){4}' + words_pattern + r')'
        
        def replace_zip(match):
            spoken = match.group(1).lower()
            for word, digit in number_words.items():
                spoken = re.sub(r'\b' + word + r'\b', digit, spoken)
            return spoken.replace(' ', '')
            
        return re.sub(five_digit_pattern, replace_zip, text, flags=re.IGNORECASE)


@lru_cache
def get_domain_normalizer() -> DomainNormalizer:
    return DomainNormalizer()


def normalize_transcript(text: str, context_hints: list[str] | None = None) -> str:
    """
    Backwards compatibility for tests and callers that don't need the correction list.
    """
    normalizer = get_domain_normalizer()
    text, _ = normalizer.normalize(text, context_hints)
    return text
