import os
import zipfile

def create_submission_zip(zip_filename="Source Code.zip"):
    print(f"Building submission zip: {zip_filename}")
    
    # Files and directories to include
    includes = [
        "state.py",
        "nodes.py",
        "graph.py",
        "demo.py",
        "tools.py",
        "rag_setup.py",
        "requirements.txt",
        ".env.example",
        "README.md",
        "memory.db"
    ]
    
    dirs_to_include = [
        "documents"
        # We purposely exclude 'venv', '.git', '__pycache__', 'chroma_db' 
        # as chroma_db can be large and can be regenerated.
    ]
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in includes:
            if os.path.exists(file):
                zipf.write(file)
                print(f"Added {file}")
            else:
                print(f"Warning: {file} not found. Skipping.")
                
        for d in dirs_to_include:
            if os.path.exists(d):
                for root, _, files in os.walk(d):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path)
                        print(f"Added {file_path}")
            else:
                print(f"Warning: Directory {d} not found. Skipping.")
                
    print("\nSubmission zip created successfully!")
    print("Please make sure you have generated the 'workflow_diagram.png' and taken your screenshots for the final submission.")

if __name__ == "__main__":
    create_submission_zip()
