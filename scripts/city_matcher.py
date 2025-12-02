from thefuzz import process, fuzz
import pandas as pd

class CityMatcher:
    def __init__(self, reference_cities, threshold=85):
        """
        reference_cities: List of valid cities (from BLS/Numbeo)
        threshold: Score (0-100) required to consider it a match
        """
        # Convert all references to lowercase for consistent matching
        self.reference_map = {city.lower(): city for city in reference_cities}
        self.valid_cities = list(self.reference_map.keys())
        self.threshold = threshold
        self.cache = {} # Product-grade optimization: Remember previous answers

    def match(self, input_city):
        """
        Returns the best matching VALID city, or None if no match found.
        """
        if pd.isna(input_city): return None
        
        # 1. Cleaning
        clean_input = str(input_city).lower().split(',')[0].strip()
        clean_input = clean_input.replace("st.", "saint").replace("metropolitan statistical area", "")
        
        # 2. Check Cache (Optimization)
        if clean_input in self.cache:
            return self.cache[clean_input]
        
        # 3. Exact Match (Fastest)
        if clean_input in self.valid_cities:
            self.cache[clean_input] = self.reference_map[clean_input]
            return self.reference_map[clean_input]
            
        # 4. Fuzzy Match (The "Smart" part)
        # extracting the single best match
        best_match, score = process.extractOne(clean_input, self.valid_cities, scorer=fuzz.token_sort_ratio)
        
        if score >= self.threshold:
            # We found a match! Return the capitalized version from reference
            matched_name = self.reference_map[best_match]
            self.cache[clean_input] = matched_name
            return matched_name
        
        # 5. No Match
        self.cache[clean_input] = None
        return None