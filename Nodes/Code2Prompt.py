import os
import git
import glob
from typing import Dict, Any, List, Tuple
from pathlib import Path
import json
from .code_gen_base import CodeGenNodeBase

class Code2PromptNode(CodeGenNodeBase):
    """Node for converting repository code to comprehensive prompts"""
    
    # File extensions to process
    SUPPORTED_EXTENSIONS = {
        # Web Development
        '.js', '.jsx', '.ts', '.tsx', '.html', '.css', '.scss', '.sass',
        # Backend
        '.py', '.java', '.go', '.rb', '.php', '.cs',
        # Configuration
        '.json', '.yml', '.yaml', '.toml', '.ini',
        # Documentation
        '.md', '.rst',
        # Shell Scripts
        '.sh', '.bash',
        # Other
        '.sql', '.graphql'
    }
    
    # Files to ignore
    IGNORE_PATTERNS = [
        'node_modules/**',
        'venv/**',
        '.git/**',
        '**/*.min.js',
        '**/*.min.css',
        '**/dist/**',
        '**/build/**',
        '**/__pycache__/**',
        '.env*',
        '*.pyc',
        '*.pyo',
        '*.pyd'
    ]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "repository_url": ("STRING", {"default": ""}),
                "max_files": ("INT", {"default": 100, "min": 1, "max": 1000}),
                "max_file_size_kb": ("INT", {"default": 500, "min": 1, "max": 5000}),
                "output_format": (["detailed", "summary", "architecture"], {"default": "detailed"})
            },
            "optional": {
                "branch": ("STRING", {"default": "main"}),
                "include_patterns": ("STRING", {"multiline": True, "default": ""}),
                "exclude_patterns": ("STRING", {"multiline": True, "default": ""}),
                "context_notes": ("STRING", {"multiline": True, "default": ""})
            }
        }

    def clone_repository(self, repo_url: str, branch: str) -> str:
        """Clone repository to temporary directory"""
        temp_dir = os.path.join(os.getcwd(), 'temp_repos', Path(repo_url).stem)
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
        
        os.makedirs(temp_dir, exist_ok=True)
        git.Repo.clone_from(repo_url, temp_dir, branch=branch)
        return temp_dir

    def should_process_file(self, filepath: str, include_patterns: List[str], exclude_patterns: List[str]) -> bool:
        """Determine if file should be processed based on patterns"""
        from fnmatch import fnmatch
        
        # Check if file should be excluded
        for pattern in self.IGNORE_PATTERNS + exclude_patterns:
            if fnmatch(filepath, pattern):
                return False
        
        # Check if file matches include patterns
        if include_patterns:
            return any(fnmatch(filepath, pattern) for pattern in include_patterns)
        
        # Check file extension
        return Path(filepath).suffix in self.SUPPORTED_EXTENSIONS

    def analyze_file(self, filepath: str, max_size_kb: int) -> Dict[str, Any]:
        """Analyze single file and return its details"""
        file_size = os.path.getsize(filepath) / 1024  # Convert to KB
        if file_size > max_size_kb:
            return None
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'path': filepath,
                'size': file_size,
                'content': content,
                'lines': len(content.splitlines()),
                'extension': Path(filepath).suffix
            }
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            return None

    def generate_architecture_summary(self, files: List[Dict[str, Any]]) -> str:
        """Generate high-level architecture summary"""
        file_types = {}
        dir_structure = set()
        
        for file in files:
            ext = file['extension']
            file_types[ext] = file_types.get(ext, 0) + 1
            dir_structure.add(str(Path(file['path']).parent))
        
        summary = ["# Repository Architecture Summary\n"]
        
        # Directory structure
        summary.append("## Directory Structure\n```")
        for directory in sorted(dir_structure):
            summary.append(directory)
        summary.append("```\n")
        
        # File type distribution
        summary.append("## File Distribution\n")
        for ext, count in file_types.items():
            summary.append(f"- {ext}: {count} files")
        
        return "\n".join(summary)

    def generate_detailed_prompt(self, files: List[Dict[str, Any]]) -> str:
        """Generate detailed prompt including file contents"""
        prompt = ["# Repository Code Analysis\n"]
        
        for file in files:
            prompt.extend([
                f"\n## File: {file['path']}",
                f"Size: {file['size']:.2f}KB | Lines: {file['lines']}\n",
                "```" + file['extension'][1:],
                file['content'],
                "```\n"
            ])
        
        return "\n".join(prompt)

    def generate_summary_prompt(self, files: List[Dict[str, Any]]) -> str:
        """Generate summary prompt without full file contents"""
        summary = ["# Repository Summary\n"]
        
        for file in files:
            content_preview = file['content'][:200] + "..." if len(file['content']) > 200 else file['content']
            summary.extend([
                f"\n## {file['path']}",
                f"- Size: {file['size']:.2f}KB",
                f"- Lines: {file['lines']}",
                "- Preview:",
                "```" + file['extension'][1:],
                content_preview,
                "```\n"
            ])
        
        return "\n".join(summary)

    def execute(
        self,
        repository_url: str,
        max_files: int,
        max_file_size_kb: int,
        output_format: str,
        branch: str = "main",
        include_patterns: str = "",
        exclude_patterns: str = "",
        context_notes: str = ""
    ) -> tuple:
        try:
            # Process include/exclude patterns
            include_list = [p.strip() for p in include_patterns.split('\n') if p.strip()]
            exclude_list = [p.strip() for p in exclude_patterns.split('\n') if p.strip()]
            
            # Clone repository
            repo_dir = self.clone_repository(repository_url, branch)
            
            # Collect and analyze files
            analyzed_files = []
            for filepath in glob.glob(os.path.join(repo_dir, '**/*'), recursive=True):
                if len(analyzed_files) >= max_files:
                    break
                    
                rel_path = os.path.relpath(filepath, repo_dir)
                if os.path.isfile(filepath) and self.should_process_file(rel_path, include_list, exclude_list):
                    result = self.analyze_file(filepath, max_file_size_kb)
                    if result:
                        analyzed_files.append(result)
            
            # Generate prompt based on output format
            if output_format == "architecture":
                output = self.generate_architecture_summary(analyzed_files)
            elif output_format == "summary":
                output = self.generate_summary_prompt(analyzed_files)
            else:  # detailed
                output = self.generate_detailed_prompt(analyzed_files)
            
            # Add context notes if provided
            if context_notes:
                output = f"# Context Notes\n{context_notes}\n\n{output}"
            
            # Cleanup
            import shutil
            shutil.rmtree(repo_dir)
            
            return (output,)
            
        except Exception as e:
            return (f"Error processing repository: {str(e)}",)

# Add to existing node mappings
NODE_CLASS_MAPPINGS["Code2Prompt"] = Code2PromptNode
NODE_DISPLAY_NAME_MAPPINGS["Code2Prompt"] = "Code to Prompt Converter"
