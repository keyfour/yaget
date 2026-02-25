#!/usr/bin/env python3
"""
yaget - CLI Entry Point

A tool that converts requirements documents written in Markdown into programming code using locally installed small Large Language Models (LLMs).
"""

import argparse
import logging
import os
from pathlib import Path

from . import config, parser, splitter, llm_client, writer


def main() -> None:
    """Main entry point for the yaget CLI."""
    parser = argparse.ArgumentParser(
        description="Convert requirements documents to code using local LLMs"
    )
    parser.add_argument(
        "requirements_file",
        help="Path to the requirements Markdown file",
    )
    parser.add_argument(
        "--model",
        help="LLM model name (overrides environment variable)",
        default=None,
    )
    parser.add_argument(
        "--context-size",
        help="Context window size in tokens (overrides environment variable)",
        type=int,
        default=None,
    )
    parser.add_argument(
        "--temperature",
        help="Sampling temperature (overrides environment variable)",
        type=float,
        default=None,
    )
    parser.add_argument(
        "--verbose",
        help="Enable verbose logging",
        action="store_true",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Load configuration
    config.load_config(
        model_name=args.model,
        context_size=args.context_size,
        temperature=args.temperature,
    )

    try:
        # Parse requirements file
        sections = parser.parse_requirements_file(args.requirements_file)
        if not sections:
            logging.warning("No sections found in requirements file")
            return

        # Process each section
        for file_path, content in sections:
            # Split content if needed
            prompts = splitter.split_content(content, config.get_context_size())
            
            # Generate code for each prompt
            generated_code = []
            for prompt in prompts:
                code = llm_client.generate_code(prompt)
                if code:
                    generated_code.append(code)
            
            # Write the combined code to file
            if generated_code:
                final_code = "\n\n".join(generated_code)
                writer.write_code_to_file(file_path, final_code)
                logging.info(f"Successfully generated: {file_path}")

    except Exception as e:
        logging.error(f"Error processing requirements: {e}")
        raise


if __name__ == "__main__":
    main()