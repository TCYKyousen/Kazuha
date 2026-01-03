import os
import subprocess
import sys
from pathlib import Path

def compile_ts_files():
    translations_dir = Path(__file__).parent / "translations"
    if not translations_dir.exists():
        print(f"Error: {translations_dir} not found.")
        return

    lrelease = "lrelease"
    
    in_path = False
    try:
        subprocess.run([lrelease, "-version"], capture_output=True, check=True)
        in_path = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    if not in_path:
        print("lrelease not in PATH, searching in site-packages...")
        import PyQt6
        pyqt_path = Path(PyQt6.__file__).parent
        lrelease_paths = list(pyqt_path.glob("**/lrelease.exe"))
        
        if not lrelease_paths:
             base_prefix = Path(sys.base_prefix)
             site_packages = base_prefix / "Lib" / "site-packages"
             if not site_packages.exists():
                 site_packages = Path(sys.prefix) / "Lib" / "site-packages"
             
             lrelease_paths.extend(list(site_packages.glob("**/lrelease.exe")))
             lrelease_paths.extend(list(site_packages.glob("**/bin/lrelease.exe")))
             
        if lrelease_paths:
            lrelease = str(lrelease_paths[0])
            print(f"Found lrelease: {lrelease}")
        else:
            print("Error: lrelease.exe not found. Please install pyqt6-tools or add lrelease to PATH.")
            return

    ts_files = list(translations_dir.glob("*.ts"))
    if not ts_files:
        print("No .ts files found in translations directory.")
        return

    for ts_file in ts_files:
        qm_file = ts_file.with_suffix(".qm")
        print(f"Compiling {ts_file.name} -> {qm_file.name}...")
        try:
            subprocess.run([lrelease, str(ts_file), "-qm", str(qm_file)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to compile {ts_file.name}: {e}")

if __name__ == "__main__":
    compile_ts_files()
