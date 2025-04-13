import json  
import argparse  
import os  
import importlib.metadata  
import subprocess  
import hashlib  
import platform  
import psutil  
from datetime import datetime  
import sys  

sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------- ARGPARSE ----------------------------
parser = argparse.ArgumentParser()
parser.add_argument("--model-path", required=True, help="Path to the model directory")
parser.add_argument("--output-dir", required=True, help="Path to save the generated reports")
args = parser.parse_args()

model_path = args.model_path
output_dir = args.output_dir

if not os.path.exists(model_path):
    print(f"❌ Error: Model path does not exist: {model_path}")
    exit(1)

# ---------------------------- UTILS ----------------------------

def calculate_file_hash(file_path):  
    if not os.path.exists(file_path):  
        return "N/A"  
    hasher = hashlib.sha256()  
    with open(file_path, "rb") as f:  
        hasher.update(f.read())  
    return hasher.hexdigest()  

def read_requirements(file_path):  
    if os.path.exists(file_path):  
        with open(file_path, "r") as f:  
            packages = [line.strip() for line in f.readlines() if line.strip()]  
        installed = {d.metadata["Name"].lower(): d.version for d in importlib.metadata.distributions()}  
        return {pkg: installed.get(pkg.lower(), "Not Installed") for pkg in packages}  
    return {}  

def read_json(file_path):  
    if os.path.exists(file_path):  
        with open(file_path, "r", encoding="utf-8") as f:  
            return json.load(f)  
    return {}  

def extract_model_metadata(model_file):  
    return {  
        "File Path": model_file,  
        "Size (KB)": os.path.getsize(model_file) / 1024 if os.path.exists(model_file) else "N/A",  
        "SHA-256 Hash": calculate_file_hash(model_file)  
    }  

def extract_dataset_metadata(dataset_path):  
    try:  
        import pandas as pd  
        df = pd.read_csv(dataset_path)  
        return {  
            "Shape": df.shape,  
            "Columns": list(df.columns),  
            "Missing Values": df.isnull().sum().to_dict(),  
            "Types": df.dtypes.astype(str).to_dict(),  
        }  
    except Exception as e:  
        print(f"⚠️ Dataset metadata extraction failed: {e}")  
        return {}  

def extract_model_architecture(model_file):  
    try:  
        with open(model_file, "r", encoding="utf-8") as f:  
            code = f.read()  
        return {  
            "Preview": code[:500] + "..." if len(code) > 500 else code,  
            "File Size": os.path.getsize(model_file)  
        }  
    except Exception as e:  
        print(f"⚠️ Model architecture preview failed: {e}")  
        return {}  

def extract_hardware_info():  
    return {  
        "OS": platform.platform(),  
        "CPU": platform.processor(),  
        "RAM (GB)": round(psutil.virtual_memory().total / (1024 ** 3), 2),  
        "Python Version": platform.python_version()  
    }  

def detect_basic_ai_risks(model_info):  
    risks = []  
    if "explainability" not in model_info:  
        risks.append("⚠️ Explainability not defined.")  
    if "bias_mitigation" not in model_info:  
        risks.append("⚠️ Bias mitigation not mentioned.")  
    return risks  

# ---------------------------- MAIN GEN ----------------------------

def generate_aibom(input_folder, reports_folder):  
    requirements_file = os.path.join(input_folder, "requirements.txt")  
    model_info_file = os.path.join(input_folder, "model_info.json")  
    dataset_file = os.path.join(input_folder, "dataset.json")  
    model_file = os.path.join(input_folder, "model.py")  

    aibom = {
        "AIBOM Version": "1.0.0",
        "Generated On": datetime.utcnow().isoformat() + "Z",
        "Model Information": read_json(model_info_file),
        "Dataset Information": read_json(dataset_file),
        "Dataset Metadata": extract_dataset_metadata(dataset_file),
        "Model Metadata": extract_model_metadata(model_file),
        "Model Architecture": extract_model_architecture(model_file),
        "Dependencies": read_requirements(requirements_file),
        "Hardware Environment": extract_hardware_info(),
        "AI Specific Warnings": detect_basic_ai_risks(read_json(model_info_file)),
    }

    os.makedirs(reports_folder, exist_ok=True)

    aibom_file = os.path.join(reports_folder, "aibom.json")  
    with open(aibom_file, "w", encoding="utf-8") as f:  
        json.dump(aibom, f, indent=2)  

    print(f"✅ AIBOM saved to {aibom_file}")  
    return aibom_file  

def generate_sbom(input_folder, reports_folder):  
    sbom_file = os.path.join(reports_folder, "sbom.json")  
    try:  
        subprocess.run(["syft", f"dir:{input_folder}", "-o", "json", "-q"], check=True, stdout=open(sbom_file, "w"))  
        print(f"✅ SBOM saved to {sbom_file}")  
        return sbom_file  
    except subprocess.CalledProcessError as e:  
        print(f"❌ Error generating SBOM: {e}")  
        return None  

def generate_vulnerability_report(input_folder, reports_folder):  
    vulnerability_file = os.path.join(reports_folder, "vulnerability.json")  
    try:  
        TRIVY_PATH = r"C:\Users\HP\scoop\shims\trivy.exe"  
        result = subprocess.run(
            [TRIVY_PATH, "fs", input_folder, "--include-dev-deps", "-f", "json", "-o", vulnerability_file], 
            check=True, capture_output=True, text=True
        )
        print(f"✅ Vulnerability report saved to {vulnerability_file}")  
        return vulnerability_file  
    except subprocess.CalledProcessError as e:  
        print(f"❌ Error generating vulnerability report: {e}")
        print("🐛 Trivy stderr:", e.stderr)
        return None  

def generate_audit_log(output_dir):  
    log = {
        "event": "AIBOM + SBOM + Vulnerability Report Generated",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user": os.getenv("USERNAME", "unknown"),
        "reports": os.listdir(output_dir)
    }
    with open(os.path.join(output_dir, "audit_log.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    print("🧾 Audit log created.")

# ---------------------------- MAIN ----------------------------

def main():
    print(f"✅ Using model path: {model_path}")
    print(f"✅ Output will be saved to: {output_dir}")

    generate_aibom(model_path, output_dir)
    generate_sbom(model_path, output_dir)
    generate_vulnerability_report(model_path, output_dir)
    generate_audit_log(output_dir)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"🔥 Script crashed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
