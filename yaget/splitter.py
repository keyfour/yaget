"""
Content splitting for yaget.

This module splits long content into manageable prompts based on the LLM's context window.
"""

import math
from typing import List


def split_content(content: str, context_size: int) -> List[str]:
    """
    Split content into prompts that fit within the LLM's context window.
    
    Args:
        content: The content to split
        context_size: The context window size in tokens
        
    Returns:
        List of prompt strings
    """
    # Simple token estimation: 1 token per 4 characters (rough approximation)
    def estimate_tokens(text: str) -> int:
        return max(1, math.ceil(len(text) / 4))

    # If content fits in one prompt, return it as-is
    if estimate_tokens(content) <= context_size:
        return [content]

    # Split by paragraphs
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    prompts = []
    current_prompt = []
    current_token_count = 0

    for paragraph in paragraphs:
        paragraph_token_count = estimate_tokens(paragraph)
        
        # If adding this paragraph would exceed context, start a new prompt
        if current_token_count + paragraph_token_count > context_size:
            if current_prompt:
                prompts.append('\n\n'.join(current_prompt))
                current_prompt = []
                current_token_count = 0
            
            # If single paragraph is too long, split it further
            if paragraph_token_count > context_size:
                words = paragraph.split()
                current_words = []
                current_word_token_count = 0
                
                for word in words:
                    word_token_count = estimate_tokens(word + ' ')
                    if current_word_token_count + word_token_count > context_size:
                        if current_words:
                            prompts.append(' '.join(current_words))
                            current_words = []
                            current_word_token_count = 0
                    current_words.append(word)
                    current_word_token_count += word_token_count
                
                if current_words:
                    prompts.append(' '.join(current_words))
            else:
                current_prompt.append(paragraph)
                current_token_count += paragraph_token_count
        else:
            current_prompt.append(paragraph)
            current_token_count += paragraph_token_count

    if current_prompt:
        prompts.append('\n\n'.join(current_prompt))

    return prompts