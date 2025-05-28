from dataclasses import dataclass, field
from typing import Dict, List
import json
from datetime import datetime

@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0

@dataclass
class TokenTracker:
    """
    Tracks token usage and costs across multiple API calls.
    """
    # Current pricing as of 2024 (adjust as needed)
    PRICING = {
        "computer-use-preview": {"input": 0.003, "output": 0.012},
    }
    
    current_usage: TokenUsage = field(default_factory=TokenUsage)
    history: List[Dict] = field(default_factory=list)
    
    def add_usage(self, model: str, usage: Dict) -> None:
        """Add a new usage record."""
        # Handle different response formats
        if isinstance(usage, dict):
            # If usage is a dict with total_tokens, estimate prompt/completion split
            if "total_tokens" in usage and usage["total_tokens"] > 0:
                total_tokens = usage["total_tokens"]
                # Estimate 10% prompt, 90% completion as a rough approximation
                prompt_tokens = int(total_tokens * 0.1)
                completion_tokens = total_tokens - prompt_tokens
            else:
                # Use actual values if available
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", 0)
                total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)
        else:
            # If usage is just a number, treat it as total_tokens
            total_tokens = int(usage)
            prompt_tokens = int(total_tokens * 0.1)
            completion_tokens = total_tokens - prompt_tokens
        
        # Calculate cost
        pricing = self.PRICING.get(model, self.PRICING["computer-use-preview"])
        cost = (
            (prompt_tokens / 1000 * pricing["input"]) +
            (completion_tokens / 1000 * pricing["output"])
        )
        
        # Update current usage
        self.current_usage.prompt_tokens += prompt_tokens
        self.current_usage.completion_tokens += completion_tokens
        self.current_usage.total_tokens += total_tokens
        self.current_usage.cost += cost
        
        # Add to history
        self.history.append({
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost": cost
        })
    
    def get_current_usage(self) -> Dict:
        """Get current usage statistics."""
        return {
            "prompt_tokens": self.current_usage.prompt_tokens,
            "completion_tokens": self.current_usage.completion_tokens,
            "total_tokens": self.current_usage.total_tokens,
            "cost": self.current_usage.cost
        }
    
    def save_history(self, filename: str) -> None:
        """Save usage history to a JSON file."""
        with open(filename, 'w') as f:
            json.dump({
                "history": self.history,
                "total_usage": self.get_current_usage()
            }, f, indent=2)
    
    def load_history(self, filename: str) -> None:
        """Load usage history from a JSON file."""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                self.history = data["history"]
                total = data["total_usage"]
                self.current_usage = TokenUsage(
                    prompt_tokens=total["prompt_tokens"],
                    completion_tokens=total["completion_tokens"],
                    total_tokens=total["total_tokens"],
                    cost=total["cost"]
                )
        except FileNotFoundError:
            pass  # Start fresh if no history file exists 