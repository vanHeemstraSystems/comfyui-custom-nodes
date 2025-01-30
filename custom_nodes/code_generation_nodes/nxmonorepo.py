import os
from typing import Dict, Any
from .code_gen_base import CodeGenNodeBase  # Import from previous artifact

class NXMonorepoNode(CodeGenNodeBase):
    """Node for generating NX Monorepo prompts for Cursor.io git integration"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_name": ("STRING", {"default": "my-nx-project"}),
                "positive_prompt": ("STRING", {"multiline": True, "default": ""}),
                "negative_prompt": ("STRING", {"multiline": True, "default": ""}),
                "repository_url": ("STRING", {"default": ""}),
                "base_branch": ("STRING", {"default": "main"}),
                "pr_title": ("STRING", {"default": "feat: Initialize NX monorepo structure"})
            },
            "optional": {
                "additional_apps": ("STRING", {"multiline": True, "default": ""}),
                "additional_libs": ("STRING", {"multiline": True, "default": ""}),
                "custom_dependencies": ("STRING", {"multiline": True, "default": ""}),
                "pr_description": ("STRING", {"multiline": True, "default": ""})
            }
        }

    def generate_base_prompt(self, project_name: str) -> str:
        """Generate the base prompt template for NX monorepo"""
        return f'''
Task: Initialize an NX monorepo and create a pull request with the complete implementation.

Project Requirements:

Project name: {project_name}

1. Initialize a new NX workspace with:
   - Integrated monorepo style
   - Apps directory structure
   - Package-based scope (@{project_name})
   - TypeScript configuration
   - ESLint setup
   - Jest for testing

2. Create the following applications:
   - Frontend app using React + TypeScript
   - Backend API using NestJS
   - Admin dashboard using React + TypeScript

3. Create shared libraries:
   - @{project_name}/shared/types (TypeScript interfaces and types)
   - @{project_name}/shared/ui (React components)
   - @{project_name}/shared/utils (Helper functions)
   - @{project_name}/shared/api-interfaces (API DTOs and interfaces)

4. Set up the following configuration files:
   - nx.json with cache and affected configuration
   - .prettierrc with standard rules
   - .eslintrc.json with TypeScript and React rules
   - jest.config.js for each app and lib
   - tsconfig.base.json with path aliases
   - .gitignore with standard exclusions

5. Include basic CI setup:
   - GitHub Actions workflow for build and test
   - Workspace lint configuration
   - Build targets for all apps and libs

6. Dependencies to include:
   - @nx/react
   - @nx/nest
   - @nx/js
   - @types/node
   - typescript
   - @testing-library/react
   - jest
   - eslint
   - prettier

7. Set up scripts in root package.json:
   - build:all
   - test:all
   - lint:all
   - serve:frontend
   - serve:backend
   - serve:admin

Implementation Guidelines:
- Follow NX best practices for module boundaries
- Implement library categories (feature, ui, util, data-access)
- Set up proper import restrictions
- Configure dependency management
'''

    def format_git_instructions(
        self,
        repository_url: str,
        base_branch: str,
        pr_title: str,
        pr_description: str
    ) -> str:
        """Format git and PR creation instructions"""
        return f'''
Git Operations:
1. Clone the repository: {repository_url}
2. Create a new branch from {base_branch}
3. Implement all required files and configurations
4. Stage all changes
5. Create a pull request with:
   - Title: {pr_title}
   - Base branch: {base_branch}
   - Description: {pr_description if pr_description else "Initialize NX monorepo structure with standard configuration and best practices"}

Please include in the PR description:
1. Development server startup instructions
2. Test execution commands
3. Build process instructions
4. Component/module generation commands
'''

    def execute(
        self,
        project_name: str,
        positive_prompt: str,
        negative_prompt: str,
        repository_url: str,
        base_branch: str,
        pr_title: str,
        additional_apps: str = "",
        additional_libs: str = "",
        custom_dependencies: str = "",
        pr_description: str = ""
    ) -> tuple:
        # Generate base prompt
        prompt_parts = [
            "# NX Monorepo Generation and PR Creation\n",
            self.generate_base_prompt(project_name)
        ]
        
        # Add additional requirements if specified
        if any([additional_apps, additional_libs, custom_dependencies]):
            prompt_parts.append("\nCustom Requirements:")
            if additional_apps:
                prompt_parts.append("\nAdditional Applications:\n" + additional_apps)
            if additional_libs:
                prompt_parts.append("\nAdditional Libraries:\n" + additional_libs)
            if custom_dependencies:
                prompt_parts.append("\nAdditional Dependencies:\n" + custom_dependencies)

        # Add positive/negative prompts
        if positive_prompt:
            prompt_parts.append("\nAdditional Requirements to Include:\n" + positive_prompt)
        if negative_prompt:
            prompt_parts.append("\nRequirements to Avoid:\n" + negative_prompt)

        # Add git instructions
        prompt_parts.append(self.format_git_instructions(
            repository_url,
            base_branch,
            pr_title,
            pr_description
        ))
        
        # Combine all parts into final prompt
        final_prompt = "\n".join(prompt_parts)
        
        # Send to Cursor.io for implementation
        response = self.send_to_cursor(final_prompt)
        
        return (response,)

# Add to existing node mappings
NODE_CLASS_MAPPINGS["NXMonorepo"] = NXMonorepoNode
NODE_DISPLAY_NAME_MAPPINGS["NXMonorepo"] = "NX Monorepo Generator"
