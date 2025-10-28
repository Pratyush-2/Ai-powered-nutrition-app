"""Security input validation for AI components."""

import re


class InputValidator:
    """Validates input for AI components."""

    def __init__(self):
        """Initialize the validator."""
        self.max_query_length = 1000
        self.max_input_length = 5000

    def validate_query(self, query: str) -> bool:
        """Validate a search query."""
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")
        
        if len(query) > self.max_query_length:
            raise ValueError(f"Query exceeds maximum length of {self.max_query_length}")
        
        # Check for malicious patterns
        malicious_patterns = [
            r'^\s*$',  # Empty or whitespace only
            r'[<>]',   # HTML tags
            r'\{\{.*\}\}',  # Template injection
            r'\$\{.*\}'  # Command injection
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, query):
                raise ValueError("Invalid characters in query")
        
        return True

    def validate_input(self, data: str) -> bool:
        """Validate general input data."""
        if not data or not isinstance(data, str):
            raise ValueError("Input must be a non-empty string")
        
        if len(data) > self.max_input_length:
            raise ValueError(f"Input exceeds maximum length of {self.max_input_length}")
        
        return True


input_validator = InputValidator()