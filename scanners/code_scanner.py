"""
Code scanner for analyzing code structure and patterns in projects
"""

import os
import re
from rich.progress import track
from rich.syntax import Syntax
from rich.table import Table
from .base import BaseScanner
from utils.console import console


class CodeScanner(BaseScanner):
    """Scanner for analyzing code structures in source files"""

    def __init__(self, extensions=None):
        """
        Initialize the Code Scanner

        Args:
            extensions (list): List of file extensions to scan
        """
        super().__init__()
        self.extensions = (
            extensions
            if extensions
            else [".py", ".cpp", ".h", ".java", ".js", ".html", ".sh"]
        )

    def scan(self, directory):
        """
        Scan a directory for code structure analysis

        Args:
            directory (str): The directory to scan

        Returns:
            dict: Code analysis results
        """
        console.print(
            f"🔍 Scanning files in [bold]{directory}[/bold] for code structure...",
            style="bold cyan",
        )

        # Load ignore list
        ignore_list = self.load_ignore_list(directory)

        # List files to scan
        files = self.list_files(directory, ignore_list, self.extensions)

        # Analysis results
        results = {
            "files": [],
            "stats": {
                "total_files": len(files),
                "total_lines": 0,
                "code_lines": 0,
                "comment_lines": 0,
                "blank_lines": 0,
                "functions": 0,
                "classes": 0,
            },
            "dependencies": [],
            "language_distribution": {},
        }

        # Scan files for code metrics
        for file_path in track(files, description="Analyzing code structure..."):
            file_analysis = self._analyze_file(file_path)
            results["files"].append(file_analysis)

            # Update overall stats
            results["stats"]["total_lines"] += file_analysis["stats"]["total_lines"]
            results["stats"]["code_lines"] += file_analysis["stats"]["code_lines"]
            results["stats"]["comment_lines"] += file_analysis["stats"]["comment_lines"]
            results["stats"]["blank_lines"] += file_analysis["stats"]["blank_lines"]
            results["stats"]["functions"] += file_analysis["stats"]["functions"]
            results["stats"]["classes"] += file_analysis["stats"]["classes"]

            # Update language distribution
            extension = os.path.splitext(file_path)[1]
            if extension in results["language_distribution"]:
                results["language_distribution"][extension] += 1
            else:
                results["language_distribution"][extension] = 1

        console.print(
            f"[bold green]✔[/bold green] Analyzed [bold]{len(files)}[/bold] files."
        )
        return results

    def process_with_model(self, scan_results, model):
        """
        Process code scan results with a model

        Args:
            scan_results (dict): The results from the scan
            model (BaseModel): The model to use for processing

        Returns:
            dict: The processed results with insights
        """
        console.print(
            "⚙️ [bold cyan]Generating insights for code structure...[/bold cyan]"
        )

        # Create a summary of the codebase
        summary = (
            f"Project contains {scan_results['stats']['total_files']} files with "
            f"{scan_results['stats']['total_lines']} lines of code.\n\n"
            f"Language distribution: {scan_results['language_distribution']}\n\n"
            f"Code metrics:\n"
            f"- Code lines: {scan_results['stats']['code_lines']}\n"
            f"- Comment lines: {scan_results['stats']['comment_lines']}\n"
            f"- Blank lines: {scan_results['stats']['blank_lines']}\n"
            f"- Functions: {scan_results['stats']['functions']}\n"
            f"- Classes: {scan_results['stats']['classes']}\n\n"
        )

        # Add information about the largest files
        largest_files = sorted(
            scan_results["files"], key=lambda x: x["stats"]["total_lines"], reverse=True
        )[:5]

        summary += "Top 5 largest files:\n"
        for file in largest_files:
            summary += f"- {file['file_path']}: {file['stats']['total_lines']} lines\n"

        # Ask the model for insights
        prompt = (
            f"Based on the following code structure analysis, provide insights about the codebase, "
            f"potential code smells, and suggestions for improvement:\n\n{summary}"
        )

        insights = model.generate(prompt)

        # Return the processed results
        return {"scan_results": scan_results, "summary": summary, "insights": insights}

    def display_results(self, processed_results):
        """
        Display the processed code analysis results

        Args:
            processed_results (dict): The processed results
        """
        scan_results = processed_results["scan_results"]

        # Display overall stats
        console.print("[bold yellow]Code Analysis Summary:[/bold yellow]")

        # Create a table for the statistics
        stats_table = Table(title="Project Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")

        stats = scan_results["stats"]
        stats_table.add_row("Total Files", str(stats["total_files"]))
        stats_table.add_row("Total Lines", str(stats["total_lines"]))
        stats_table.add_row("Code Lines", str(stats["code_lines"]))
        stats_table.add_row("Comment Lines", str(stats["comment_lines"]))
        stats_table.add_row("Blank Lines", str(stats["blank_lines"]))
        stats_table.add_row("Functions", str(stats["functions"]))
        stats_table.add_row("Classes", str(stats["classes"]))

        console.print(stats_table)

        # Display language distribution
        lang_table = Table(title="Language Distribution")
        lang_table.add_column("Extension", style="cyan")
        lang_table.add_column("Files", style="green")

        for ext, count in scan_results["language_distribution"].items():
            lang_table.add_row(ext, str(count))

        console.print(lang_table)

        # Display model insights
        console.print("[bold yellow]Model Insights:[/bold yellow]")
        console.print(processed_results["insights"])

    def _analyze_file(self, file_path):
        """
        Analyze a single file for code metrics

        Args:
            file_path (str): Path to the file

        Returns:
            dict: Analysis results for the file
        """
        extension = os.path.splitext(file_path)[1]

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.readlines()
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    content = f.readlines()
            except Exception as e:
                console.print(
                    f"[bold red]Error:[/bold red] Could not read file {file_path}: {e}"
                )
                return self._empty_file_analysis(file_path)
        except Exception as e:
            console.print(
                f"[bold red]Error:[/bold red] Could not read file {file_path}: {e}"
            )
            return self._empty_file_analysis(file_path)

        # Initialize file analysis
        analysis = {
            "file_path": file_path,
            "stats": {
                "total_lines": len(content),
                "code_lines": 0,
                "comment_lines": 0,
                "blank_lines": 0,
                "functions": 0,
                "classes": 0,
            },
            "imports": [],
            "functions": [],
            "classes": [],
        }

        # Analyze based on file type
        if extension == ".py":
            self._analyze_python_file(content, analysis)
        elif extension in [".js", ".ts"]:
            self._analyze_javascript_file(content, analysis)
        elif extension in [".java"]:
            self._analyze_java_file(content, analysis)
        elif extension in [".cpp", ".c", ".h", ".hpp"]:
            self._analyze_cpp_file(content, analysis)
        else:
            # Generic analysis for other file types
            self._analyze_generic_file(content, analysis)

        return analysis

    def _empty_file_analysis(self, file_path):
        """Create an empty analysis for files that couldn't be read"""
        return {
            "file_path": file_path,
            "stats": {
                "total_lines": 0,
                "code_lines": 0,
                "comment_lines": 0,
                "blank_lines": 0,
                "functions": 0,
                "classes": 0,
            },
            "imports": [],
            "functions": [],
            "classes": [],
        }

    def _analyze_python_file(self, content, analysis):
        """Analyze a Python file"""
        in_multiline_comment = False

        # Regular expressions for Python
        import_pattern = re.compile(r"^import\s+(\w+)|^from\s+(\w+)")
        function_pattern = re.compile(r"^\s*def\s+(\w+)\s*\(")
        class_pattern = re.compile(r"^\s*class\s+(\w+)")

        for line in content:
            line = line.strip()

            # Check for blank lines
            if not line:
                analysis["stats"]["blank_lines"] += 1
                continue

            # Check for multiline comments (docstrings)
            if '"""' in line or "'''" in line:
                if in_multiline_comment:
                    in_multiline_comment = False
                    analysis["stats"]["comment_lines"] += 1
                    continue
                elif line.count('"""') == 2 or line.count("'''") == 2:
                    # Single line docstring
                    analysis["stats"]["comment_lines"] += 1
                    continue
                else:
                    in_multiline_comment = True
                    analysis["stats"]["comment_lines"] += 1
                    continue

            if in_multiline_comment:
                analysis["stats"]["comment_lines"] += 1
                continue

            # Check for single line comments
            if line.startswith("#"):
                analysis["stats"]["comment_lines"] += 1
                continue

            # Count code lines
            analysis["stats"]["code_lines"] += 1

            # Check for imports
            import_match = import_pattern.match(line)
            if import_match:
                module = import_match.group(1) or import_match.group(2)
                if module not in analysis["imports"]:
                    analysis["imports"].append(module)

            # Check for functions
            function_match = function_pattern.match(line)
            if function_match:
                analysis["stats"]["functions"] += 1
                analysis["functions"].append(function_match.group(1))

            # Check for classes
            class_match = class_pattern.match(line)
            if class_match:
                analysis["stats"]["classes"] += 1
                analysis["classes"].append(class_match.group(1))

    def _analyze_javascript_file(self, content, analysis):
        """Analyze a JavaScript file"""
        in_multiline_comment = False

        # Regular expressions for JavaScript
        import_pattern = re.compile(r'(import|require)\s+.*?[\'"](.+?)[\'"]')
        function_pattern = re.compile(
            r"function\s+(\w+)|(\w+)\s*=\s*function|(\w+)\s*:\s*function"
        )
        class_pattern = re.compile(r"class\s+(\w+)")

        for line in content:
            line = line.strip()

            # Check for blank lines
            if not line:
                analysis["stats"]["blank_lines"] += 1
                continue

            # Check for multiline comments
            if "/*" in line and "*/" not in line:
                in_multiline_comment = True
                analysis["stats"]["comment_lines"] += 1
                continue

            if "*/" in line and in_multiline_comment:
                in_multiline_comment = False
                analysis["stats"]["comment_lines"] += 1
                continue

            if in_multiline_comment:
                analysis["stats"]["comment_lines"] += 1
                continue

            # Check for single line comments
            if line.startswith("//"):
                analysis["stats"]["comment_lines"] += 1
                continue

            # Count code lines
            analysis["stats"]["code_lines"] += 1

            # Check for imports
            import_match = import_pattern.search(line)
            if import_match:
                module = import_match.group(2)
                if module not in analysis["imports"]:
                    analysis["imports"].append(module)

            # Check for functions
            function_match = function_pattern.search(line)
            if function_match:
                func_name = (
                    function_match.group(1)
                    or function_match.group(2)
                    or function_match.group(3)
                )
                if func_name:
                    analysis["stats"]["functions"] += 1
                    analysis["functions"].append(func_name)

            # Check for classes
            class_match = class_pattern.search(line)
            if class_match:
                analysis["stats"]["classes"] += 1
                analysis["classes"].append(class_match.group(1))

    def _analyze_java_file(self, content, analysis):
        """Analyze a Java file"""
        # Simplified Java analysis
        in_multiline_comment = False

        for line in content:
            line = line.strip()

            # Check for blank lines
            if not line:
                analysis["stats"]["blank_lines"] += 1
                continue

            # Check for multiline comments
            if "/*" in line and "*/" not in line:
                in_multiline_comment = True
                analysis["stats"]["comment_lines"] += 1
                continue

            if "*/" in line and in_multiline_comment:
                in_multiline_comment = False
                analysis["stats"]["comment_lines"] += 1
                continue

            if in_multiline_comment:
                analysis["stats"]["comment_lines"] += 1
                continue

            # Check for single line comments
            if line.startswith("//"):
                analysis["stats"]["comment_lines"] += 1
                continue

            # Count code lines
            analysis["stats"]["code_lines"] += 1

            # Very basic function and class detection
            if "class " in line and "{" in line:
                analysis["stats"]["classes"] += 1
            if (
                ("public " in line or "private " in line or "protected " in line)
                and "(" in line
                and ")" in line
            ):
                analysis["stats"]["functions"] += 1

    def _analyze_cpp_file(self, content, analysis):
        """Analyze a C++ file"""
        # Simplified C++ analysis
        in_multiline_comment = False

        for line in content:
            line = line.strip()

            # Check for blank lines
            if not line:
                analysis["stats"]["blank_lines"] += 1
                continue

            # Check for multiline comments
            if "/*" in line and "*/" not in line:
                in_multiline_comment = True
                analysis["stats"]["comment_lines"] += 1
                continue

            if "*/" in line and in_multiline_comment:
                in_multiline_comment = False
                analysis["stats"]["comment_lines"] += 1
                continue

            if in_multiline_comment:
                analysis["stats"]["comment_lines"] += 1
                continue

            # Check for single line comments
            if line.startswith("//"):
                analysis["stats"]["comment_lines"] += 1
                continue

            # Count code lines
            analysis["stats"]["code_lines"] += 1

            # Very basic function and class detection
            if "class " in line and ("{" in line or ";" in line):
                analysis["stats"]["classes"] += 1
            if (
                ("void " in line or "int " in line or "bool " in line)
                and "(" in line
                and ")" in line
            ):
                analysis["stats"]["functions"] += 1

    def _analyze_generic_file(self, content, analysis):
        """Generic analysis for other file types"""
        for line in content:
            line = line.strip()

            # Check for blank lines
            if not line:
                analysis["stats"]["blank_lines"] += 1
                continue

            # Simple guess at comment lines
            if line.startswith("#") or line.startswith("//") or line.startswith("<!--"):
                analysis["stats"]["comment_lines"] += 1
                continue

            # Count code lines
            analysis["stats"]["code_lines"] += 1
