import subprocess

def run_workflow():
    print("Starting filling...")
    # This waits for script1 to finish before moving to the next line
    subprocess.run(["python", "fill_contract.py"], check=True)
    
    print("Filling finished. Starting merging...")
    subprocess.run(["python", "merge_words.py"], check=True)
    
    print("Workflow complete!")

if __name__ == "__main__":
    run_workflow()
