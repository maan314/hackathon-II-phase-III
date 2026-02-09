"""
Context window management for conversation history.

Manages conversation history to fit within token limits.
"""
import os
from typing import List, Dict


class ContextManager:
    """
    Manages conversation context window to prevent token overflow.

    Implements sliding window approach with configurable limits.
    """

    def __init__(self):
        """
        Initialize context manager with configuration from environment.

        Environment variables:
        - CONTEXT_WINDOW_SIZE: Maximum number of messages (default: 50)
        """
        self.max_messages = int(os.getenv("CONTEXT_WINDOW_SIZE", "50"))
        self.max_tokens_estimate = 4000  # Conservative estimate for context

    def prepare_context(
        self,
        messages: List[Dict[str, str]],
        include_system_prompt: bool = False
    ) -> List[Dict[str, str]]:
        """
        Prepare conversation context within token limits.

        Uses sliding window approach: keeps most recent messages.

        Args:
            messages: List of messages in format [{"role": "user/assistant", "content": "..."}]
            include_system_prompt: Whether to account for system prompt in token count

        Returns:
            Truncated list of messages that fit within context window
        """
        if not messages:
            return []

        # Simple approach: limit by message count
        # More sophisticated approach would estimate tokens per message
        if len(messages) <= self.max_messages:
            return messages

        # Keep most recent messages (sliding window)
        return messages[-self.max_messages:]

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Uses rough approximation: 4 characters ≈ 1 token.

        Args:
            text: Text to estimate

        Returns:
            Estimated token count
        """
        return len(text) // 4

    def estimate_context_tokens(self, messages: List[Dict[str, str]]) -> int:
        """
        Estimate total tokens for message list.

        Args:
            messages: List of messages

        Returns:
            Estimated total token count
        """
        total_chars = sum(len(msg.get("content", "")) for msg in messages)
        return self.estimate_tokens(total_chars)

    def should_truncate(self, messages: List[Dict[str, str]]) -> bool:
        """
        Check if messages should be truncated.

        Args:
            messages: List of messages

        Returns:
            True if truncation needed, False otherwise
        """
        if len(messages) > self.max_messages:
            return True

        estimated_tokens = self.estimate_context_tokens(messages)
        return estimated_tokens > self.max_tokens_estimate

    def get_context_summary(self, messages: List[Dict[str, str]]) -> Dict[str, int]:
        """
        Get summary statistics for context.

        Args:
            messages: List of messages

        Returns:
            Dict with message_count and estimated_tokens
        """
        return {
            "message_count": len(messages),
            "estimated_tokens": self.estimate_context_tokens(messages),
            "max_messages": self.max_messages,
            "max_tokens_estimate": self.max_tokens_estimate
        }
