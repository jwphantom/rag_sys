# save_requirements.py
import pkg_resources
import re
from pathlib import Path


def get_imports(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    imports = re.findall(r"^import\s+(\w+)|^from\s+(\w+)", content, re.MULTILINE)
    return set(imp[0] or imp[1] for imp in imports)


def get_project_imports(project_path):
    all_imports = set()
    for py_file in Path(project_path).rglob("*.py"):
        all_imports.update(get_imports(py_file))
    return all_imports


def get_installed_packages():
    return {pkg.key for pkg in pkg_resources.working_set}


def save_requirements(project_path, output_file="requirement.txt"):
    project_imports = get_project_imports(project_path)
    installed_packages = get_installed_packages()

    with open(output_file, "w") as f:
        for package in sorted(project_imports.intersection(installed_packages)):
            version = pkg_resources.get_distribution(package).version
            f.write(f"{package}=={version}\n")

    print(f"Requirements saved to {output_file}")


if __name__ == "__main__":
    project_path = "."  # Chemin vers votre projet
    save_requirements(project_path)
