"""
Markdown rendering utilities using glow
"""

import subprocess
import tempfile
import os
from typing import Optional
from .colors import Colors

class MarkdownRenderer:
    """Renders markdown content using glow with fallback to colored plain text"""
    
    def __init__(self, style: str = "dark", width: Optional[int] = None):
        """
        Initialize the markdown renderer.
        
        Args:
            style: The glow style to use (dark, light, notty, etc.)
            width: Maximum width for rendered output
        """
        self.style = style
        self.width = width or 100
        self.glow_available = self._check_glow()
    
    def _check_glow(self) -> bool:
        """Check if glow is available in the system"""
        try:
            subprocess.run(['glow', '--version'], 
                         capture_output=True, 
                         check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def render(self, content: str, fallback: bool = True) -> str:
        """
        Render markdown content using glow.
        
        Args:
            content: Markdown content to render
            fallback: Whether to use fallback rendering if glow fails
            
        Returns:
            Rendered content
        """
        if not self.glow_available and fallback:
            return self._fallback_render(content)
        
        try:
            # Create a temporary file with the markdown content
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(content)
                temp_path = f.name
            
            # Run glow with specified options
            cmd = ['glow', temp_path, '-s', self.style, '-w', str(self.width)]
            
            # Ensure proper terminal environment for tmux
            env = os.environ.copy()
            if 'TMUX' in env:
                # Force terminal type for proper color support in tmux
                env['TERM'] = 'xterm-256color'
            
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  check=True,
                                  env=env)
            
            # Clean up temp file
            os.unlink(temp_path)
            
            return result.stdout.rstrip()
            
        except subprocess.CalledProcessError as e:
            # Clean up temp file if it exists
            if 'temp_path' in locals():
                try:
                    os.unlink(temp_path)
                except:
                    pass
            
            if fallback:
                return self._fallback_render(content)
            else:
                raise RuntimeError(f"Failed to render markdown: {e}")
        except Exception as e:
            if fallback:
                return self._fallback_render(content)
            else:
                raise
    
    def _fallback_render(self, content: str) -> str:
        """
        Simple fallback renderer that adds basic ANSI colors to markdown.
        
        This provides a colored output when glow is not available.
        """
        lines = content.split('\n')
        rendered_lines = []
        in_code_block = False
        
        for line in lines:
            # Code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                if in_code_block:
                    rendered_lines.append(f"{Colors.CODE}{line}")
                else:
                    rendered_lines.append(f"{line}{Colors.RESET}")
                continue
            
            if in_code_block:
                rendered_lines.append(f"{Colors.CODE}{line}")
                continue
            
            # Headers
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level == 1:
                    rendered_lines.append(f"{Colors.HEADER}{line}{Colors.RESET}")
                elif level == 2:
                    rendered_lines.append(f"{Colors.BRIGHT_BLUE}{line}{Colors.RESET}")
                else:
                    rendered_lines.append(f"{Colors.BLUE}{line}{Colors.RESET}")
                continue
            
            # Bold text (simple pattern)
            if '**' in line:
                import re
                line = re.sub(r'\*\*([^*]+)\*\*', 
                            f'{Colors.BOLD}\\1{Colors.RESET}', 
                            line)
            
            # Italic text (simple pattern)
            if '*' in line and '**' not in line:
                import re
                line = re.sub(r'\*([^*]+)\*', 
                            f'{Colors.ITALIC}\\1{Colors.RESET}', 
                            line)
            
            # Code inline
            if '`' in line:
                import re
                line = re.sub(r'`([^`]+)`', 
                            f'{Colors.CODE}\\1{Colors.RESET}', 
                            line)
            
            # Lists
            if line.strip().startswith(('-', '*', '+')) and not in_code_block:
                rendered_lines.append(f"{Colors.BRIGHT_CYAN}{line}{Colors.RESET}")
                continue
            
            # Numbered lists
            if line.strip() and line.strip()[0].isdigit() and '.' in line:
                rendered_lines.append(f"{Colors.BRIGHT_CYAN}{line}{Colors.RESET}")
                continue
            
            # Links
            if '[' in line and ']' in line and '(' in line:
                import re
                line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', 
                            f'{Colors.UNDERLINE}{Colors.BRIGHT_BLUE}\\1{Colors.RESET}', 
                            line)
            
            # Default
            rendered_lines.append(line)
        
        # Ensure we reset at the end if still in code block
        if in_code_block:
            rendered_lines.append(Colors.RESET)
        
        return '\n'.join(rendered_lines)


# Default renderer instance
default_renderer = MarkdownRenderer()

def render_markdown(content: str, style: str = "dark", width: Optional[int] = None) -> str:
    """
    Convenience function to render markdown content.
    
    Args:
        content: Markdown content to render
        style: The glow style to use
        width: Maximum width for rendered output
        
    Returns:
        Rendered content
    """
    if style != "dark" or width:
        renderer = MarkdownRenderer(style=style, width=width)
        return renderer.render(content)
    else:
        return default_renderer.render(content)