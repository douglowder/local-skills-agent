"""
Code Quality Analyzer Script

Provides comprehensive code quality metrics for Python files including:
- Cyclomatic complexity
- Maintainability index
- Documentation coverage
- Code organization metrics
"""

import ast
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any


class CodeAnalyzer:
    """Analyzes Python code for quality metrics."""

    def __init__(self, code: str, filename: str = "unknown.py"):
        self.code = code
        self.filename = filename
        self.lines = code.split('\n')
        try:
            self.tree = ast.parse(code)
        except SyntaxError as e:
            self.tree = None
            self.parse_error = str(e)

    def calculate_cyclomatic_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity for a function or method.

        Cyclomatic complexity is a measure of code complexity that counts
        the number of linearly independent paths through the code.
        """
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            # Decision points add to complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, (ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Each additional condition in boolean expression
                complexity += len(child.values) - 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1

        return complexity

    def analyze_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Analyze a single function for various metrics."""
        complexity = self.calculate_cyclomatic_complexity(node)
        lines = node.end_lineno - node.lineno + 1 if node.end_lineno else 0
        docstring = ast.get_docstring(node)

        # Count parameters
        num_params = len(node.args.args)

        # Check for type hints
        has_return_type = node.returns is not None
        param_type_hints = sum(1 for arg in node.args.args if arg.annotation)

        # Count nested functions
        nested_functions = sum(
            1 for child in ast.walk(node)
            if isinstance(child, ast.FunctionDef) and child != node
        )

        return {
            'name': node.name,
            'lineno': node.lineno,
            'complexity': complexity,
            'lines': lines,
            'has_docstring': docstring is not None,
            'docstring_length': len(docstring) if docstring else 0,
            'num_params': num_params,
            'has_return_type': has_return_type,
            'type_hint_coverage': param_type_hints / num_params if num_params > 0 else 1.0,
            'nested_functions': nested_functions,
        }

    def analyze_class(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Analyze a class for various metrics."""
        docstring = ast.get_docstring(node)

        # Count methods
        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
        num_methods = len(methods)

        # Count attributes (simplified - only __init__ assignments)
        attributes = set()
        for method in methods:
            if method.name == '__init__':
                for child in ast.walk(method):
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Attribute):
                                if isinstance(target.value, ast.Name) and target.value.id == 'self':
                                    attributes.add(target.attr)

        return {
            'name': node.name,
            'lineno': node.lineno,
            'has_docstring': docstring is not None,
            'num_methods': num_methods,
            'num_attributes': len(attributes),
            'methods': [self.analyze_function(m) for m in methods],
        }

    def analyze_imports(self) -> Dict[str, Any]:
        """Analyze import organization."""
        if not self.tree:
            return {'error': 'Unable to parse'}

        stdlib_imports = []
        third_party_imports = []
        local_imports = []

        # Common stdlib modules (partial list)
        stdlib_modules = {
            'os', 'sys', 're', 'json', 'ast', 'pathlib', 'typing',
            'collections', 'itertools', 'functools', 'datetime', 'time',
            'math', 'random', 'io', 'csv', 'pickle', 'subprocess'
        }

        for node in ast.walk(self.tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if module in stdlib_modules:
                        stdlib_imports.append(alias.name)
                    else:
                        third_party_imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    if module in stdlib_modules:
                        stdlib_imports.append(node.module)
                    elif node.level == 0:  # Absolute import
                        third_party_imports.append(node.module)
                    else:  # Relative import
                        local_imports.append(node.module or '')

        return {
            'stdlib_count': len(stdlib_imports),
            'third_party_count': len(third_party_imports),
            'local_count': len(local_imports),
            'total_imports': len(stdlib_imports) + len(third_party_imports) + len(local_imports),
        }

    def count_comments(self) -> Dict[str, int]:
        """Count comments in the code."""
        comment_lines = sum(1 for line in self.lines if line.strip().startswith('#'))
        code_lines = len([l for l in self.lines if l.strip() and not l.strip().startswith('#')])

        return {
            'comment_lines': comment_lines,
            'code_lines': code_lines,
            'comment_ratio': comment_lines / code_lines if code_lines > 0 else 0,
        }

    def calculate_maintainability_index(self, functions: List[Dict]) -> float:
        """
        Calculate a simplified maintainability index.

        This is a simplified version of the industry-standard MI formula.
        Higher scores (closer to 100) indicate better maintainability.
        """
        if not functions:
            return 100.0

        avg_complexity = sum(f['complexity'] for f in functions) / len(functions)
        total_lines = len(self.lines)

        # Simplified MI calculation
        complexity_penalty = avg_complexity * 8
        length_penalty = total_lines / 100
        doc_bonus = sum(1 for f in functions if f['has_docstring']) / len(functions) * 10

        mi = 100 - complexity_penalty - length_penalty + doc_bonus
        return max(0.0, min(100.0, mi))

    def get_full_analysis(self) -> Dict[str, Any]:
        """Perform complete code analysis and return all metrics."""
        if not self.tree:
            return {
                'filename': self.filename,
                'error': getattr(self, 'parse_error', 'Unable to parse file'),
            }

        # Analyze all top-level functions
        functions = []
        classes = []

        for node in self.tree.body:
            if isinstance(node, ast.FunctionDef):
                functions.append(self.analyze_function(node))
            elif isinstance(node, ast.ClassDef):
                class_analysis = self.analyze_class(node)
                classes.append(class_analysis)
                functions.extend(class_analysis['methods'])

        # Calculate aggregate metrics
        comments = self.count_comments()
        imports = self.analyze_imports()

        analysis = {
            'filename': self.filename,
            'total_lines': len(self.lines),
            'code_lines': comments['code_lines'],
            'comment_lines': comments['comment_lines'],
            'comment_ratio': round(comments['comment_ratio'] * 100, 2),

            'total_functions': len(functions),
            'total_classes': len(classes),

            'avg_complexity': round(sum(f['complexity'] for f in functions) / len(functions), 2) if functions else 0,
            'max_complexity': max((f['complexity'] for f in functions), default=0),
            'min_complexity': min((f['complexity'] for f in functions), default=0),

            'avg_function_length': round(sum(f['lines'] for f in functions) / len(functions), 2) if functions else 0,
            'max_function_length': max((f['lines'] for f in functions), default=0),

            'docstring_coverage': round(sum(1 for f in functions if f['has_docstring']) / len(functions) * 100, 2) if functions else 0,

            'maintainability_index': round(self.calculate_maintainability_index(functions), 2),

            'imports': imports,

            'high_complexity_functions': sorted(
                [{'name': f['name'], 'complexity': f['complexity'], 'line': f['lineno']}
                 for f in functions if f['complexity'] > 10],
                key=lambda x: x['complexity'],
                reverse=True
            ),

            'long_functions': sorted(
                [{'name': f['name'], 'lines': f['lines'], 'line': f['lineno']}
                 for f in functions if f['lines'] > 50],
                key=lambda x: x['lines'],
                reverse=True
            ),

            'undocumented_functions': [
                {'name': f['name'], 'line': f['lineno']}
                for f in functions if not f['has_docstring']
            ],

            'functions': functions[:10],  # Limit for output size
            'classes': classes[:10],
        }

        return analysis


def analyze_file(filepath: str) -> Dict[str, Any]:
    """Analyze a Python file and return metrics."""
    try:
        path = Path(filepath)
        code = path.read_text(encoding='utf-8')
        analyzer = CodeAnalyzer(code, filename=path.name)
        return analyzer.get_full_analysis()
    except Exception as e:
        return {
            'filename': filepath,
            'error': f'Failed to analyze file: {str(e)}'
        }


def main():
    """Command-line interface for the analyzer."""
    if len(sys.argv) < 2:
        print("Usage: python analyzer.py <python_file>")
        sys.exit(1)

    filepath = sys.argv[1]
    result = analyze_file(filepath)

    # Pretty print JSON
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
