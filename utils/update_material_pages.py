
import os
import re
from pathlib import Path

def update_material_pages():
    """
    Updates all material pages to use the centralized CSS
    """
    # Get the root directory
    project_root = Path(__file__).parent.parent
    material_pages_dir = os.path.join(project_root, "pages", "pages_Material")
    
    # Get all Python files in the material pages directory
    python_files = [f for f in os.listdir(material_pages_dir) if f.endswith('.py') and f != 'material_utils.py']
    
    # Import statement for the utilities
    material_utils_import = "from pages.pages_Material.material_utils import load_material_css, create_header, create_section_header, create_info_box\n"
    
    # Function to add the import statement if it doesn't exist
    def add_import_if_needed(content):
        if "from pages.pages_Material.material_utils import" not in content:
            # Find the position after the last import
            import_match = re.search(r'^import.*$|^from.*import.*$', content, re.MULTILINE)
            if import_match:
                last_import_pos = 0
                for match in re.finditer(r'^import.*$|^from.*import.*$', content, re.MULTILINE):
                    last_import_pos = match.end()
                
                # Insert the import after the last import
                content = content[:last_import_pos] + "\n" + material_utils_import + content[last_import_pos:]
            else:
                # If no imports found, add at the beginning
                content = material_utils_import + content
        
        return content
    
    # Function to add load_material_css call if it doesn't exist
    def add_css_loader_if_needed(content):
        if "load_material_css()" not in content:
            # Find the render function
            render_match = re.search(r'def\s+render_\w+\(\):\s*', content)
            if render_match:
                # Find the first line after the function definition
                after_def_pos = render_match.end()
                # Look for the next non-whitespace and non-comment line
                next_line_match = re.search(r'^\s*[^#\s]', content[after_def_pos:], re.MULTILINE)
                if next_line_match:
                    insert_pos = after_def_pos + next_line_match.start()
                    # Insert the CSS loader call
                    content = content[:insert_pos] + "    # Load the unified CSS\n    load_material_css()\n\n" + content[insert_pos:]
        
        return content
    
    # Process each file
    for file in python_files:
        file_path = os.path.join(material_pages_dir, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Modify the content
            content = add_import_if_needed(content)
            content = add_css_loader_if_needed(content)
            
            # Write back to the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            print(f"Updated {file}")
        except Exception as e:
            print(f"Error updating {file}: {str(e)}")

if __name__ == "__main__":
    update_material_pages()
