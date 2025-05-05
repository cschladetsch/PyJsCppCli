# File: create_zip.py
import zipfile
from datetime import datetime

def create_memory_system_zip():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"memory_system_{timestamp}.zip"

    files = {
        "__init__.py": '''from .context import ContextMemory
from .persistence import JsonPersistence

memory_system = ContextMemory(JsonPersistence())''',

        "context.py": '''class ContextMemory:
    def __init__(self, persistence):
        self.persistence = persistence''',

        "persistence.py": '''class JsonPersistence:
    def __init__(self):
        pass''',

        "README.md": '''# Memory System
Context-aware memory system'''
    }

    with zipfile.ZipFile(zip_name, 'w') as zf:
        for filename, content in files.items():
            zf.writestr(f"memory_system/{filename}", content)

    print(f"Created: {zip_name}")

if __name__ == "__main__":
    create_memory_system_zip()
