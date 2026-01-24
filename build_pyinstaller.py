import os
import sys
import shutil
import subprocess


def run():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(root_dir, "dist")
    build_dir = os.path.join(root_dir, "build")

    python_exe = sys.executable

    icons_dir = os.path.join(root_dir, "icons")
    logo_ico = os.path.join(icons_dir, "logo.ico")

    cmd = [
        python_exe,
        "-m",
        "nuitka",
        "--onefile",
        "--windows-console-mode=disable",
        "--output-dir=dist",
        "--output-filename=Kazuha",
        "--enable-plugin=pyside6",
        "--include-module=PySide6.QtXml",
        "--nofollow-import-to=PyQt5,setuptools,pkg_resources",
        "--include-data-file=version.json=version.json",
        "--include-data-dir=config=config",
        "--include-data-dir=plugins=plugins",
        "--include-data-dir=icons=icons",
        "--include-data-dir=ppt_assistant=ppt_assistant",
        "--include-data-dir=fonts=fonts",
        "main.py",
    ]

    if os.path.exists(logo_ico):
        cmd.insert(-1, f"--windows-icon-from-ico={logo_ico}")

    if os.path.isdir(dist_dir):
        shutil.rmtree(dist_dir, ignore_errors=True)
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir, ignore_errors=True)
    for extra in [
        "main.build",
        "main.dist",
        "main.onefile-build",
        "Kazuha.build",
        "Kazuha.dist",
        "Kazuha.onefile-build",
    ]:
        extra_path = os.path.join(root_dir, extra)
        if os.path.isdir(extra_path):
            shutil.rmtree(extra_path, ignore_errors=True)

    subprocess.check_call(cmd, cwd=root_dir)

    exe_name = "Kazuha.exe"
    src_exe = os.path.join(dist_dir, exe_name)
    dst_exe = os.path.join(root_dir, exe_name)

    if os.path.exists(src_exe):
        if os.path.exists(dst_exe):
            os.remove(dst_exe)
        shutil.move(src_exe, dst_exe)

    if os.path.isdir(dist_dir):
        shutil.rmtree(dist_dir, ignore_errors=True)
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir, ignore_errors=True)
    for extra in [
        "main.build",
        "main.dist",
        "main.onefile-build",
        "Kazuha.build",
        "Kazuha.dist",
        "Kazuha.onefile-build",
    ]:
        extra_path = os.path.join(root_dir, extra)
        if os.path.isdir(extra_path):
            shutil.rmtree(extra_path, ignore_errors=True)


if __name__ == "__main__":
    run()
