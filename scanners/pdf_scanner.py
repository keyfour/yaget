"""
PDF scanner for extracting and analyzing content from PDF files
"""

import os
import re
from rich.progress import track
from rich.table import Table
from .base import BaseScanner
from utils.console import console


class PdfScanner(BaseScanner):
    """Scanner for extracting and analyzing PDF content"""

    def __init__(self):
        """Initialize the PDF scanner"""
        super().__init__()
        # Try to import PyPDF2, handle if it's not installed
        try:
            import PyPDF2

            self.PyPDF2 = PyPDF2
        except ImportError:
            console.print(
                "[bold red]Error:[/bold red] PyPDF2 is not installed. Please install it with 'pip install PyPDF2'"
            )
            self.PyPDF2 = None

    def scan(self, directory):
        """
        Scan a directory for PDF files and extract their content

        Args:
            directory (str): The directory to scan

        Returns:
            dict: PDF analysis results
        """
        if not self.PyPDF2:
            console.print(
                "[bold red]Error:[/bold red] PyPDF2 is not installed. Cannot scan PDF files."
            )
            return {"error": "PyPDF2 not installed"}

        console.print(
            f"🔍 Scanning files in [bold]{directory}[/bold] for PDFs...",
            style="bold cyan",
        )

        # Load ignore list
        ignore_list = self.load_ignore_list(directory)

        # Collect all PDF files
        pdf_files = []
        for root, dirs, files in os.walk(directory):
            # Remove directories from the scan if they are in the ignore list
            dirs[:] = [
                d
                for d in dirs
                if not self.should_ignore(os.path.join(root, d), ignore_list, directory)
            ]
            for filename in files:
                if filename.lower().endswith(".pdf"):
                    file_path = os.path.join(root, filename)
                    if not self.should_ignore(file_path, ignore_list, directory):
                        pdf_files.append(file_path)

        console.print(f"Found [bold]{len(pdf_files)}[/bold] PDF files.")

        # Analyze each PDF file
        pdf_analysis = []
        for pdf_path in track(pdf_files, description="Extracting PDF content..."):
            analysis = self._analyze_pdf(pdf_path)
            pdf_analysis.append(analysis)

        # Compile overall stats
        stats = {
            "total_pdfs": len(pdf_files),
            "total_pages": sum(pdf["page_count"] for pdf in pdf_analysis),
            "total_words": sum(pdf["word_count"] for pdf in pdf_analysis),
            "average_pages_per_pdf": round(
                sum(pdf["page_count"] for pdf in pdf_analysis) / max(len(pdf_files), 1),
                2,
            ),
        }

        results = {"stats": stats, "pdf_files": pdf_analysis}

        console.print(
            f"[bold green]✔[/bold green] Extracted content from [bold]{len(pdf_files)}[/bold] PDF files."
        )
        return results

    def process_with_model(self, scan_results, model):
        """
        Process PDF scan results with a model

        Args:
            scan_results (dict): The results from the scan
            model (BaseModel): The model to use for processing

        Returns:
            dict: The processed results with insights
        """
        if "error" in scan_results:
            return {"error": scan_results["error"]}

        console.print("⚙️ [bold cyan]Generating insights for PDF content...[/bold cyan]")

        # Summary of PDF files
        summary = (
            f"Analyzed {scan_results['stats']['total_pdfs']} PDF files with "
            f"{scan_results['stats']['total_pages']} total pages.\n\n"
        )

        # Add information about each PDF
        summary += "PDF files in the project:\n"
        for pdf in scan_results["pdf_files"]:
            summary += f"- {pdf['filename']}: {pdf['page_count']} pages, {pdf['word_count']} words\n"
            if pdf["metadata"]:
                summary += f"  Metadata: {pdf['metadata']}\n"

        # Add sample content from largest PDFs
        largest_pdfs = sorted(
            scan_results["pdf_files"], key=lambda x: x["page_count"], reverse=True
        )[:3]

        summary += "\nSample content from largest PDFs:\n"
        for pdf in largest_pdfs:
            # Truncate content to avoid overwhelming the model
            content_sample = (
                pdf["content"][:1000] + "..."
                if len(pdf["content"]) > 1000
                else pdf["content"]
            )
            summary += f"--- {pdf['filename']} ---\n{content_sample}\n\n"

        # Ask the model for insights about the PDFs
        prompt = (
            f"Based on the following PDF analysis from a project, provide insights about the content, "
            f"potential themes, and how these documents might relate to the project:\n\n{summary}"
        )

        insights = model.generate(prompt)

        # Return the processed results
        return {"scan_results": scan_results, "summary": summary, "insights": insights}

    def display_results(self, processed_results):
        """
        Display the processed PDF analysis results

        Args:
            processed_results (dict): The processed results
        """
        if "error" in processed_results:
            console.print(f"[bold red]Error:[/bold red] {processed_results['error']}")
            return

        scan_results = processed_results["scan_results"]

        # Display overall stats
        console.print("[bold yellow]PDF Analysis Summary:[/bold yellow]")

        # Create a table for the statistics
        stats_table = Table(title="PDF Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")

        stats = scan_results["stats"]
        stats_table.add_row("Total PDFs", str(stats["total_pdfs"]))
        stats_table.add_row("Total Pages", str(stats["total_pages"]))
        stats_table.add_row("Total Words", str(stats["total_words"]))
        stats_table.add_row(
            "Average Pages Per PDF", str(stats["average_pages_per_pdf"])
        )

        console.print(stats_table)

        # Display information about each PDF
        console.print("[bold yellow]PDF Files:[/bold yellow]")

        pdfs_table = Table(title="PDF Files")
        pdfs_table.add_column("Filename", style="cyan")
        pdfs_table.add_column("Pages", style="green")
        pdfs_table.add_column("Words", style="green")
        pdfs_table.add_column("Title", style="blue")

        for pdf in scan_results["pdf_files"]:
            title = pdf["metadata"].get("title", "") if pdf["metadata"] else ""
            pdfs_table.add_row(
                pdf["filename"], str(pdf["page_count"]), str(pdf["word_count"]), title
            )

        console.print(pdfs_table)

        # Display model insights
        console.print("[bold yellow]Model Insights:[/bold yellow]")
        console.print(processed_results["insights"])

    def _analyze_pdf(self, pdf_path):
        """
        Analyze a single PDF file

        Args:
            pdf_path (str): Path to the PDF file

        Returns:
            dict: Analysis results for the PDF
        """
        filename = os.path.basename(pdf_path)

        try:
            with open(pdf_path, "rb") as file:
                reader = self.PyPDF2.PdfReader(file)

                # Extract metadata
                metadata = {}
                if reader.metadata:
                    for key, value in reader.metadata.items():
                        if key.startswith("/"):
                            key = key[1:]  # Remove leading slash
                        metadata[key.lower()] = value

                # Extract text from all pages
                text = ""
                page_count = len(reader.pages)
                for page_num in range(page_count):
                    page = reader.pages[page_num]
                    text += page.extract_text() + "\n\n"

                # Count words
                word_count = len(re.findall(r"\w+", text))

                return {
                    "filename": filename,
                    "path": pdf_path,
                    "page_count": page_count,
                    "word_count": word_count,
                    "metadata": metadata,
                    "content": text,
                }

        except Exception as e:
            console.print(
                f"[bold red]Error:[/bold red] Could not read PDF {filename}: {e}"
            )
            return {
                "filename": filename,
                "path": pdf_path,
                "page_count": 0,
                "word_count": 0,
                "metadata": {},
                "content": f"Error reading file: {str(e)}",
                "error": str(e),
            }
