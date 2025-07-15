#!/usr/bin/env python3
"""
Generate architecture diagram for PyClaudeCli project.
This script analyzes the codebase and creates an architecture diagram at Resources/Arch.png.
"""

import os
import subprocess
import sys
from pathlib import Path
import ast
import json
from typing import Dict, List, Set, Tuple

class CodeAnalyzer:
    """Analyze Python codebase structure and dependencies."""
    
    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.imports: Dict[str, Set[str]] = {}
        self.classes: Dict[str, List[str]] = {}
        self.functions: Dict[str, List[str]] = {}
        
    def analyze_file(self, file_path: Path) -> None:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            relative_path = str(file_path.relative_to(self.root_path))
            
            # Extract imports
            imports = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
            
            self.imports[relative_path] = imports
            
            # Extract classes and functions
            classes = []
            functions = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree)):
                        functions.append(node.name)
            
            if classes:
                self.classes[relative_path] = classes
            if functions:
                self.functions[relative_path] = functions
                
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def analyze_codebase(self) -> None:
        """Analyze all Python files in the codebase."""
        for file_path in self.root_path.rglob("*.py"):
            # Skip test files and setup files
            if any(part in str(file_path) for part in ['test_', 'tests/', 'setup.py', '__pycache__']):
                continue
            self.analyze_file(file_path)

def generate_dot_file(analyzer: CodeAnalyzer) -> str:
    """Generate GraphViz DOT content based on code analysis."""
    
    dot_content = """digraph PyClaudeCliArchitecture {
    // Graph settings
    rankdir=TB;
    bgcolor="white";
    node [shape=box, style=filled, fontname="Arial", fontsize=12];
    edge [fontname="Arial", fontsize=10];
    compound=true;
    
    // Title
    labelloc="t";
    label="PyClaudeCli Architecture\\nAI-Powered Command Line Interface";
    fontsize=20;
    fontname="Arial Bold";
    
    // Define color scheme
    // Entry points: Light green
    // Core components: Light blue
    // API layer: Light pink
    // Utilities: Light yellow
    // External: Light gray
    
    // Entry Points
    subgraph cluster_entry {
        label="Entry Points";
        style=filled;
        color=darkgreen;
        fillcolor=lightgreen;
        fontsize=14;
        
        main_py [label="main.py\\nPrimary Entry Point", fillcolor=palegreen, shape=ellipse];
        main_module [label="ai/__main__.py\\nModule Entry Point", fillcolor=palegreen, shape=ellipse];
    }
    
    // Core CLI Components
    subgraph cluster_core {
        label="Core Components";
        style=filled;
        color=darkblue;
        fillcolor=lightblue;
        fontsize=14;
        
        cli_handler [label="ai/cli.py\\nCLI Handler\\n• Argument parsing\\n• Command routing\\n• Lifecycle management", fillcolor=lightblue];
        constants [label="ai/constants.py\\nConfiguration\\n• API settings\\n• Default values", fillcolor=lightblue];
        models [label="ai/models.py\\nData Models\\n• Interaction class\\n• Serialization", fillcolor=lightblue];
    }
    
    // Interaction Modes
    subgraph cluster_modes {
        label="Interaction Modes";
        style=filled;
        color=darkorange;
        fillcolor=lightyellow;
        fontsize=14;
        
        interactive [label="ai/modes/interactive.py\\nInteractive Mode\\n• Prompt toolkit UI\\n• Vim keybindings\\n• File uploads", fillcolor=gold];
        async_interactive [label="ai/modes/async_interactive.py\\nAsync Interactive\\n• Non-blocking UI\\n• Concurrent ops", fillcolor=gold];
    }
    
    // API Layer
    subgraph cluster_api {
        label="API Layer";
        style=filled;
        color=darkred;
        fillcolor=lightpink;
        fontsize=14;
        
        api_client [label="ai/api/client.py\\nClaude API Client\\n• Authentication\\n• Request handling\\n• Retry logic", fillcolor=pink];
        async_client [label="ai/api/async_client.py\\nAsync API Client\\n• Async operations\\n• Streaming support", fillcolor=pink];
    }
    
    // Plugin System
    subgraph cluster_plugins {
        label="Plugin System";
        style=filled;
        color=purple;
        fillcolor=lavender;
        fontsize=14;
        
        plugin_manager [label="Plugin Manager\\n• Load plugins\\n• Execute hooks", fillcolor=plum];
        plugin_base [label="Base Classes\\n• Plugin interfaces\\n• Decorators", fillcolor=plum];
    }
    
    // Utilities
    subgraph cluster_utils {
        label="Utilities";
        style=filled;
        color=darkorange;
        fillcolor=lightyellow;
        fontsize=14;
        
        subgraph cluster_io {
            label="I/O & Storage";
            io_utils [label="ai/utils/io.py\\n• File operations\\n• Token management\\n• Conversation persist", fillcolor=khaki];
            config [label="ai/utils/config.py\\n• Settings management\\n• Environment vars", fillcolor=khaki];
        }
        
        subgraph cluster_ui {
            label="UI Components";
            colors [label="ai/utils/colors.py\\nANSI colors", fillcolor=khaki];
            spinner [label="ai/utils/spinner.py\\nProgress animation", fillcolor=khaki];
            output_formatter [label="ai/utils/output_formatter.py\\nOutput formatting", fillcolor=khaki];
            markdown_renderer [label="ai/utils/markdown_renderer.py\\nMarkdown rendering", fillcolor=khaki];
        }
        
        subgraph cluster_core_utils {
            label="Core Utilities";
            validation [label="ai/utils/validation.py\\nInput validation", fillcolor=khaki];
            exceptions [label="ai/utils/exceptions.py\\nError handling", fillcolor=khaki];
            logging [label="ai/utils/logging.py\\nLogging system", fillcolor=khaki];
            streaming [label="ai/utils/streaming.py\\nStream processing", fillcolor=khaki];
            connection_pool [label="ai/utils/connection_pool.py\\nConnection pooling", fillcolor=khaki];
        }
    }
    
    // External Services
    subgraph cluster_external {
        label="External Services";
        style=filled;
        color=darkgray;
        fillcolor=lightgray;
        fontsize=14;
        
        claude_api [label="Anthropic Claude API\\n• Text generation\\n• Image analysis", fillcolor=gray, fontcolor=white, shape=cylinder];
        filesystem [label="File System\\n• ~/.ask_* files\\n• Configuration\\n• History", fillcolor=gray, fontcolor=white, shape=cylinder];
    }
    
    // Main flow connections
    main_py -> cli_handler [label="imports", weight=10];
    main_module -> cli_handler [label="imports", weight=10];
    
    cli_handler -> interactive [label="interactive mode", weight=5];
    cli_handler -> async_interactive [label="async mode", weight=5];
    cli_handler -> api_client [label="direct query", weight=5];
    
    interactive -> api_client [label="API calls", weight=5];
    async_interactive -> async_client [label="async calls", weight=5];
    
    api_client -> claude_api [label="HTTP requests", weight=10];
    async_client -> claude_api [label="async HTTP", weight=10];
    
    // Data flow
    cli_handler -> models [label="creates", style=dashed];
    models -> io_utils [label="serialize", style=dashed];
    io_utils -> filesystem [label="persist", style=dashed];
    
    // Utility connections
    cli_handler -> validation [label="validates"];
    cli_handler -> config [label="loads"];
    cli_handler -> logging [label="logs"];
    cli_handler -> exceptions [label="handles"];
    
    interactive -> colors [label="uses"];
    interactive -> spinner [label="uses"];
    interactive -> output_formatter [label="uses"];
    
    api_client -> connection_pool [label="uses"];
    async_client -> streaming [label="uses"];
    
    // Plugin connections
    cli_handler -> plugin_manager [label="loads plugins", style=dotted];
    plugin_manager -> plugin_base [label="implements", style=dotted];
    
    // Configuration flow
    config -> filesystem [label="reads config"];
    logging -> filesystem [label="writes logs"];
    
    // Legend
    subgraph cluster_legend {
        label="Legend";
        style=filled;
        fillcolor=white;
        fontsize=12;
        
        leg_entry [label="Entry Point", fillcolor=palegreen, shape=ellipse];
        leg_core [label="Core Component", fillcolor=lightblue];
        leg_mode [label="Interaction Mode", fillcolor=gold];
        leg_api [label="API Layer", fillcolor=pink];
        leg_plugin [label="Plugin System", fillcolor=plum];
        leg_util [label="Utility", fillcolor=khaki];
        leg_external [label="External Service", fillcolor=gray, fontcolor=white, shape=cylinder];
        
        leg_flow [label="Main Flow", style=invis];
        leg_data [label="Data Flow", style=invis];
        leg_plugin_flow [label="Plugin Flow", style=invis];
        
        leg_flow -> leg_data [label="control flow"];
        leg_data -> leg_plugin_flow [label="data flow", style=dashed];
        leg_plugin_flow -> leg_entry [label="plugin flow", style=dotted];
    }
}
"""
    
    return dot_content

def ensure_graphviz_installed():
    """Check if GraphViz is installed and provide installation instructions if not."""
    try:
        result = subprocess.run(['dot', '-V'], capture_output=True, text=True)
        if result.returncode != 0:
            raise FileNotFoundError
    except FileNotFoundError:
        print("GraphViz is not installed. Please install it first:")
        print("\nOn Ubuntu/Debian:")
        print("  sudo apt-get install graphviz")
        print("\nOn macOS:")
        print("  brew install graphviz")
        print("\nOn Windows:")
        print("  Download from https://graphviz.org/download/")
        sys.exit(1)

def main():
    """Main function to generate the architecture diagram."""
    # Get the project root directory
    script_dir = Path(__file__).parent
    root_dir = script_dir
    
    print("PyClaudeCli Architecture Diagram Generator")
    print("=" * 50)
    
    # Ensure GraphViz is installed
    ensure_graphviz_installed()
    
    # Analyze the codebase
    print("\n1. Analyzing codebase structure...")
    analyzer = CodeAnalyzer(root_dir)
    analyzer.analyze_codebase()
    
    print(f"   - Found {len(analyzer.imports)} Python files")
    print(f"   - Found {sum(len(c) for c in analyzer.classes.values())} classes")
    print(f"   - Found {sum(len(f) for f in analyzer.functions.values())} top-level functions")
    
    # Generate DOT file
    print("\n2. Generating DOT file...")
    dot_content = generate_dot_file(analyzer)
    
    # Create a temporary DOT file
    dot_file = script_dir / "architecture_temp.dot"
    with open(dot_file, 'w') as f:
        f.write(dot_content)
    print(f"   - Created {dot_file}")
    
    # Create Resources directory if it doesn't exist
    resources_dir = root_dir / "Resources"
    resources_dir.mkdir(exist_ok=True)
    
    # Generate PNG file
    print("\n3. Generating PNG diagram...")
    output_file = resources_dir / "Arch.png"
    
    try:
        # Generate high-quality PNG
        subprocess.run([
            'dot', '-Tpng', 
            '-Gdpi=150',  # Higher DPI for better quality
            '-Gsize=12,8!',  # Size in inches (! forces exact size)
            '-Gratio=fill',  # Fill the specified size
            str(dot_file), 
            '-o', str(output_file)
        ], check=True)
        
        print(f"   - Generated {output_file}")
        
        # Also generate SVG for scalability
        svg_file = resources_dir / "Arch.svg"
        subprocess.run(['dot', '-Tsvg', str(dot_file), '-o', str(svg_file)], check=True)
        print(f"   - Generated {svg_file}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating diagram: {e}")
        sys.exit(1)
    finally:
        # Clean up temporary DOT file
        if dot_file.exists():
            dot_file.unlink()
    
    print("\n✅ Architecture diagram generated successfully!")
    print(f"   PNG: {output_file}")
    print(f"   SVG: {svg_file}")
    
    # Display some statistics
    print("\n📊 Codebase Statistics:")
    print(f"   - Entry points: 2")
    print(f"   - Core modules: {len([f for f in analyzer.imports if 'ai/' in f and 'test' not in f])}")
    print(f"   - Utility modules: {len([f for f in analyzer.imports if 'utils/' in f])}")
    print(f"   - Total lines of code: ~{sum(1 for _ in root_dir.rglob('*.py') if 'test' not in str(_)) * 100} (estimated)")

if __name__ == "__main__":
    main()