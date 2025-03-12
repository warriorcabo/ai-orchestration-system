# src/utils/feedback_loop_manager.py

import os
import logging
import time
from typing import Dict, Any, List, Optional, Tuple

from src.utils.error_handler import log_error

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class FeedbackLoopManager:
    """Manager for implementing AI feedback loops and quality control"""

    def __init__(self):
        """Initialize the feedback loop manager"""
        # Maximum number of revision cycles
        self.max_revision_cycles = int(os.environ.get("MAX_REVISION_CYCLES", "2"))

        # Minimum improvement threshold (as percentage)
        self.min_improvement_threshold = float(os.environ.get("MIN_IMPROVEMENT_THRESHOLD", "10.0"))

        # Quality thresholds
        self.quality_thresholds = {
            "min_acceptable": float(os.environ.get("MIN_QUALITY_THRESHOLD", "70.0")),
            "good": float(os.environ.get("GOOD_QUALITY_THRESHOLD", "85.0")),
            "excellent": float(os.environ.get("EXCELLENT_QUALITY_THRESHOLD", "95.0"))
        }

        # Response history store (for temporary storage during active loops)
        self.response_history = {}

    def process_feedback_loop(self, conversation_id: str, user_query: str,
                             initial_response: str, review_function, 
                             revision_function) -> Tuple[str, Dict[str, Any]]:
        """Process a complete feedback loop for an AI response"""
        try:
            # Initialize response tracking
            current_response = initial_response
            revision_count = 0
            improvement_history = []

            # Store initial quality
            improvement_history.append({
                "revision": revision_count,
                "timestamp": time.time()
            })

            # Store in history
            self.response_history[conversation_id] = {
                "user_query": user_query,
                "initial_response": initial_response,
                "current_response": current_response,
                "revisions": [],
                "quality_metrics": improvement_history
            }

            # Start revision loop - limited to max_revision_cycles
            while revision_count < self.max_revision_cycles:
                # Get review feedback
                review_feedback = review_function(current_response, user_query)

                # Check if review says no changes needed or if we've reached max cycles
                if "APPROVED" in review_feedback.upper():
                    logger.info(f"Response approved by reviewer after {revision_count} revisions.")
                    break

                # Apply revision
                revised_response = revision_function(current_response, review_feedback, user_query)
                
                # Check if the revision made any meaningful changes
                if self._is_similar(current_response, revised_response):
                    logger.info("Revision did not produce meaningful changes. Stopping feedback loop.")
                    break

                # Store revision data
                self.response_history[conversation_id]["revisions"].append({
                    "revision_number": revision_count + 1,
                    "review_feedback": review_feedback,
                    "revised_response": revised_response,
                    "timestamp": time.time()
                })

                # Update current response
                current_response = revised_response

                # Increment revision count
                revision_count += 1

            # Format the final response to remove any instruction artifacts
            final_response = self._format_final_response(current_response)

            # Update final response in history
            self.response_history[conversation_id]["current_response"] = final_response

            # Return final response and history
            return final_response, self.response_history[conversation_id]

        except Exception as e:
            logger.error(f"Error in feedback loop: {str(e)}")
            log_error("feedback_loop_manager", f"Feedback loop error: {str(e)}")
            # Return initial response in case of error
            return self._format_final_response(initial_response), {"error": str(e)}
    
    def _is_similar(self, response1: str, response2: str, threshold: float = 0.9) -> bool:
        """Check if two responses are very similar (to prevent endless minor edits)"""
        # Simple length comparison first
        len1, len2 = len(response1), len(response2)
        if abs(len1 - len2) < 10:  # Almost identical length
            # Count character differences
            shorter, longer = (response1, response2) if len1 <= len2 else (response2, response1)
            
            # Simple character-level similarity
            same_chars = sum(1 for a, b in zip(shorter, longer) if a == b)
            similarity = same_chars / len(longer)
            
            return similarity > threshold
        
        return False
    
    def _format_final_response(self, response: str) -> str:
        """Clean up the response to remove any instruction artifacts"""
        # Check if the response contains typical instruction patterns
        instruction_patterns = [
            "ORIGINAL OUTPUT:",
            "FEEDBACK:",
            "ORIGINAL QUERY:",
            "Provide a complete revised version",
            "Please revise the following"
        ]
        
        # If it looks like it contains instruction artifacts
        if any(pattern in response for pattern in instruction_patterns):
            # Try to extract just the core response
            try:
                # Simplistic approach - take the first paragraph that doesn't look like instructions
                lines = response.split('\n')
                for line in lines:
                    line = line.strip()
                    if line and not any(pattern in line for pattern in instruction_patterns):
                        # Found a likely "real" content line
                        return line
            except Exception:
                # If parsing fails, just return a simplified version
                pass
        
        return response

    def cleanup_old_histories(self, max_age_hours: int = 24) -> int:
        """Remove old conversation histories to free memory"""
        cutoff_time = time.time() - (max_age_hours * 3600)
        keys_to_remove = []

        for conv_id, history in self.response_history.items():
            # Check the timestamp of the last revision
            quality_metrics = history.get("quality_metrics", [])
            if quality_metrics and quality_metrics[-1].get("timestamp", 0) < cutoff_time:
                keys_to_remove.append(conv_id)

        # Remove old histories
        for key in keys_to_remove:
            del self.response_history[key]

        return len(keys_to_remove)
