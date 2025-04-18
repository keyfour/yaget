"""
Text scanner for extracting and analyzing content from text files with embeddings
"""

import os
import re
from rich.progress import track
from rich.table import Table
from .base import BaseScanner
from utils.console import console
from utils.file_utils import read_file_safely


class TextScanner(BaseScanner):
    """Scanner for extracting and analyzing text file content with embeddings"""

    def __init__(self, extensions=None):
        """
        Initialize the text scanner

        Args:
            extensions (list): List of text file extensions to scan
        """
        super().__init__()
        self.extensions = (
            extensions
            if extensions
            else [
                ".txt",
                ".md",
                ".rst",
                ".json",
                ".yaml",
                ".yml",
                ".ini",
                ".conf",
                ".config",
            ]
        )

        # Try to import required libraries for text splitting
        try:
            from langchain.text_splitter import RecursiveCharacterTextSplitter

            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200, length_function=len
            )
        except ImportError:
            console.print(
                "[bold red]Error:[/bold red] langchain is not installed. Please install it with 'pip install langchain'"
            )
            self.text_splitter = None

    def scan(self, directory):
        """
        Scan a directory for text files and extract content

        Args:
            directory (str): The directory to scan

        Returns:
            dict: Text analysis results with content chunks
        """
        if not self.text_splitter:
            console.print(
                "[bold red]Error:[/bold red] Required dependencies not installed."
            )
            return {"error": "Missing dependencies"}

        console.print(
            f"🔍 Scanning files in [bold]{directory}[/bold] for text content...",
            style="bold cyan",
        )

        # Load ignore list
        ignore_list = self.load_ignore_list(directory)

        # Collect all text files
        text_files = []
        for root, dirs, files in os.walk(directory):
            # Remove directories from the scan if they are in the ignore list
            dirs[:] = [
                d
                for d in dirs
                if not self.should_ignore(os.path.join(root, d), ignore_list, directory)
            ]
            for filename in files:
                extension = os.path.splitext(filename)[1].lower()
                if extension in self.extensions:
                    file_path = os.path.join(root, filename)
                    if not self.should_ignore(file_path, ignore_list, directory):
                        text_files.append(file_path)

        console.print(f"Found [bold]{len(text_files)}[/bold] text files.")

        # Analyze each text file
        text_analysis = []
        all_chunks = []

        for file_path in track(text_files, description="Extracting text content..."):
            analysis = self._analyze_text_file(file_path)
            text_analysis.append(analysis)

            # Add the chunks to the global list
            if "chunks" in analysis and analysis["chunks"]:
                for chunk in analysis["chunks"]:
                    all_chunks.append(
                        {
                            "content": chunk,
                            "metadata": {
                                "filename": analysis["filename"],
                                "path": analysis["path"],
                                "type": analysis["file_type"],
                            },
                        }
                    )

        # Generate embeddings for all chunks
        embeddings = self._create_embeddings(all_chunks)

        # Compile overall stats
        stats = {
            "total_files": len(text_files),
            "total_lines": sum(text["line_count"] for text in text_analysis),
            "total_words": sum(text["word_count"] for text in text_analysis),
            "total_chunks": len(all_chunks),
            "file_types": self._count_file_types(text_analysis),
        }

        results = {
            "stats": stats,
            "text_files": text_analysis,
            "chunks": all_chunks,
            "embeddings": embeddings,
        }

        console.print(
            f"[bold green]✔[/bold green] Extracted content from [bold]{len(text_files)}[/bold] text files with [bold]{len(all_chunks)}[/bold] chunks."
        )
        return results

    def process_with_model(self, scan_results, model):
        """
        Process text scan results with a model

        Args:
            scan_results (dict): The results from the scan
            model (BaseModel): The model to use for processing

        Returns:
            dict: The processed results with insights
        """
        if "error" in scan_results:
            return {"error": scan_results["error"]}

        console.print(
            "⚙️ [bold cyan]Generating insights for text content...[/bold cyan]"
        )

        # Summary of text files
        summary = (
            f"Analyzed {scan_results['stats']['total_files']} text files with "
            f"{scan_results['stats']['total_lines']} total lines and "
            f"{scan_results['stats']['total_chunks']} content chunks.\n\n"
        )

        # Add information about file types
        summary += "File types:\n"
        for file_type, count in scan_results["stats"]["file_types"].items():
            summary += f"- {file_type}: {count} files\n"

        # Add information about each file
        summary += "\nLargest text files in the project:\n"
        largest_files = sorted(
            scan_results["text_files"], key=lambda x: x["word_count"], reverse=True
        )[:5]

        for text_file in largest_files:
            summary += f"- {text_file['filename']} ({text_file['file_type']}): {text_file['line_count']} lines, {text_file['word_count']} words\n"

        # Add sample content from a few chunks
        sample_chunks = scan_results["chunks"][:5]  # Take first 5 chunks

        summary += "\nSample content chunks:\n"
        for i, chunk in enumerate(sample_chunks):
            summary += f"--- Chunk {i+1} from {chunk['metadata']['filename']} ---\n"
            content_sample = (
                chunk["content"][:500] + "..."
                if len(chunk["content"]) > 500
                else chunk["content"]
            )
            summary += f"{content_sample}\n\n"

        # Ask the model for insights about the text content
        prompt = (
            f"Based on the following text analysis from a project, provide insights about the content, "
            f"potential themes, and how these documents might relate to the project:\n\n{summary}"
        )

        insights = model.generate(prompt)

        # Return the processed results
        return {"scan_results": scan_results, "summary": summary, "insights": insights}

    def display_results(self, processed_results):
        """
        Display the processed text analysis results

        Args:
            processed_results (dict): The processed results
        """
        if "error" in processed_results:
            console.print(f"[bold red]Error:[/bold red] {processed_results['error']}")
            return

        scan_results = processed_results["scan_results"]

        # Display overall stats
        console.print("[bold yellow]Text Analysis Summary:[/bold yellow]")

        # Create a table for the statistics
        stats_table = Table(title="Text File Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")

        stats = scan_results["stats"]
        stats_table.add_row("Total Files", str(stats["total_files"]))
        stats_table.add_row("Total Lines", str(stats["total_lines"]))
        stats_table.add_row("Total Words", str(stats["total_words"]))
        stats_table.add_row("Total Content Chunks", str(stats["total_chunks"]))

        console.print(stats_table)

        # Display information about file types
        file_types_table = Table(title="File Types")
        file_types_table.add_column("Extension", style="cyan")
        file_types_table.add_column("Count", style="green")

        for ext, count in stats["file_types"].items():
            file_types_table.add_row(ext, str(count))

        console.print(file_types_table)

        # Display information about the largest files
        largest_files = sorted(
            scan_results["text_files"], key=lambda x: x["word_count"], reverse=True
        )[:10]

        files_table = Table(title="Largest Text Files")
        files_table.add_column("Filename", style="cyan")
        files_table.add_column("Type", style="blue")
        files_table.add_column("Lines", style="green")
        files_table.add_column("Words", style="green")

        for text_file in largest_files:
            files_table.add_row(
                text_file["filename"],
                text_file["file_type"],
                str(text_file["line_count"]),
                str(text_file["word_count"]),
            )

        console.print(files_table)

        # Display model insights
        console.print("[bold yellow]Model Insights:[/bold yellow]")
        console.print(processed_results["insights"])

    def _analyze_text_file(self, file_path):
        """
        Analyze a single text file and create content chunks

        Args:
            file_path (str): Path to the text file

        Returns:
            dict: Analysis results for the text file
        """
        filename = os.path.basename(file_path)
        file_type = os.path.splitext(filename)[1].lower()

        try:
            # Read the file content
            content = read_file_safely(file_path)

            if content is None:
                raise ValueError(f"Could not read file: {file_path}")

            # Count lines and words
            lines = content.splitlines()
            line_count = len(lines)
            word_count = len(re.findall(r"\w+", content))

            # Create chunks from the text
            chunks = []
            if content.strip() and self.text_splitter:
                chunks = self.text_splitter.split_text(content)

            return {
                "filename": filename,
                "path": file_path,
                "file_type": file_type,
                "line_count": line_count,
                "word_count": word_count,
                "content": content,
                "chunks": chunks,
            }

        except Exception as e:
            console.print(
                f"[bold red]Error:[/bold red] Could not process text file {filename}: {e}"
            )
            return {
                "filename": filename,
                "path": file_path,
                "file_type": file_type,
                "line_count": 0,
                "word_count": 0,
                "content": f"Error reading file: {str(e)}",
                "chunks": [],
                "error": str(e),
            }

    def _count_file_types(self, text_analysis):
        """Count the occurrence of each file type"""
        file_types = {}
        for file_info in text_analysis:
            file_type = file_info["file_type"]
            if file_type in file_types:
                file_types[file_type] += 1
            else:
                file_types[file_type] = 1
        return file_types

    def _create_embeddings(self, chunks):
        """
        Create embeddings for text chunks

        Args:
            chunks (list): List of text chunks with metadata

        Returns:
            dict: Embeddings data structure or None if embedding fails
        """
        try:
            # Try to import necessary libraries
            from langchain.embeddings import OllamaEmbeddings, OpenAIEmbeddings
            from langchain.vectorstores import FAISS
            import os

            # Choose embedding model based on available environment
            embedding_model = None

            if os.getenv("PROVIDER", "openai").lower() == "ollama":
                ollama_server = os.getenv("OLLAMA_SERVER", "http://localhost:11434")
                embedding_model = OllamaEmbeddings(
                    base_url=ollama_server, model=os.getenv("EMBEDDING_MODEL", "llama3")
                )
                console.print("[bold green]✔[/bold green] Using Ollama for embeddings")
            else:  # Default to OpenAI
                if os.getenv("OPENAI_API_KEY"):
                    embedding_model = OpenAIEmbeddings()
                    console.print(
                        "[bold green]✔[/bold green] Using OpenAI for embeddings"
                    )

            if embedding_model:
                # Format documents for vector storage
                documents = []
                for chunk in chunks:
                    documents.append(
                        {
                            "page_content": chunk["content"],
                            "metadata": chunk["metadata"],
                        }
                    )

                # Create vector store
                vector_store = FAISS.from_documents(documents, embedding_model)

                console.print(
                    "[bold green]✔[/bold green] Created embeddings for text content"
                )

                # Return serialized vector store
                return {"vector_store": vector_store, "status": "success"}
            else:
                console.print(
                    "[bold yellow]Warning:[/bold yellow] No embedding model available"
                )
                return {"status": "no_model", "message": "No embedding model available"}

        except ImportError as e:
            console.print(
                f"[bold yellow]Warning:[/bold yellow] Could not create embeddings: {e}"
            )
            console.print(
                "Install required packages with 'pip install langchain faiss-cpu'"
            )
            return {"status": "error", "message": f"Missing dependencies: {str(e)}"}
        except Exception as e:
            console.print(
                f"[bold red]Error:[/bold red] Failed to create embeddings: {e}"
            )
            return {"status": "error", "message": str(e)}

    def query_text_content(self, query, embeddings_data, top_k=3):
        """
        Query the text content using semantic search

        Args:
            query (str): The query string
            embeddings_data (dict): The embeddings data from scan
            top_k (int): Number of results to return

        Returns:
            list: List of relevant content chunks
        """
        if not embeddings_data or embeddings_data.get("status") != "success":
            console.print(
                "[bold yellow]Warning:[/bold yellow] No valid embeddings available"
            )
            return []

        vector_store = embeddings_data.get("vector_store")
        if not vector_store:
            return []

        try:
            results = vector_store.similarity_search(query, k=top_k)
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": i,  # Just using position as proxy for score
                }
                for i, doc in enumerate(results)
            ]
        except Exception as e:
            console.print(
                f"[bold red]Error:[/bold red] Failed to query embeddings: {e}"
            )
            return []
