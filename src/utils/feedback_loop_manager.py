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
        self.max_revision_cycles = int(os.environ.get("MAX_REVISION_CYCLES", "3"))

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

            # Start revision loop
            while revision_count < self.max_revision_cycles:
                # Get review feedback
                review_feedback = review_function(current_response, user_query)

                # Check if review says no changes needed
                if "APPROVED" in review_feedback.upper():
                    logger.info(f"Response approved by reviewer after {revision_count} revisions.")
                    break

                # Apply revision
                revised_response = revision_function(current_response, review_feedback, user_query)

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

            # Update final response in history
            self.response_history[conversation_id]["current_response"] = current_response

            # Return final response and history
            return current_response, self.response_history[conversation_id]

        except Exception as e:
            logger.error(f"Error in feedback loop: {str(e)}")
            log_error("feedback_loop_manager", f"Feedback loop error: {str(e)}")
            # Return initial response in case of error
            return initial_response, {"error": str(e)}

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
