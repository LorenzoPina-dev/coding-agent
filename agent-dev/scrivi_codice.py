import os
import fnmatch

def read_gitignore(root_dir):
    patterns = []
    gitignore_path = os.path.join(root_dir, '.gitignore')
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    
    return patterns

def should_ignore(path, patterns, root_dir):
    rel_path = os.path.relpath(path, root_dir)
    
    for pattern in patterns:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(path), pattern):
            return True
    
    return False

def is_venv_directory(path):
    """Controlla se è una directory virtualenv"""
    dir_name = os.path.basename(path)
    venv_names = ['venv', '.venv', 'env', '.env', 'virtualenv']
    
    if dir_name in venv_names:
        return True
    
    # Controlla se contiene file tipici di venv
    if os.path.isdir(path):
        venv_files = ['pyvenv.cfg', 'activate', 'pip-selfcheck.json']
        for venv_file in venv_files:
            if os.path.exists(os.path.join(path, venv_file)):
                return True
    
    return False

def export_py_json():
    root_dir = os.path.abspath('.')
    
    patterns = read_gitignore(root_dir)
    patterns.extend(['.git', '__pycache__', '*.pyc'])
    
    with open('output.txt', 'w', encoding='utf-8') as out:
        for root, dirs, files in os.walk(root_dir):
            # Rimuovi directory venv
            dirs[:] = [d for d in dirs if not is_venv_directory(os.path.join(root, d))]
            # Rimuovi altre directory da ignorare
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__']]
            
            for file in files:
                if not (file.endswith('.py') or file.endswith('.json')):
                    continue
                
                file_path = os.path.join(root, file)
                
                if should_ignore(file_path, patterns, root_dir):
                    continue
                
                # Controlla se il file è dentro una venv
                path_parts = os.path.normpath(file_path).split(os.sep)
                if any(is_venv_directory(part) for part in path_parts if os.path.isdir(os.path.join(root_dir, part))):
                    continue
                
                rel_path = os.path.relpath(file_path, root_dir)
                out.write(f"=== {rel_path} ===\n\n")
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        out.write(f.read())
                except:
                    out.write("[Errore lettura file]\n")
                
                out.write("\n\n")

if __name__ == "__main__":
    export_py_json()