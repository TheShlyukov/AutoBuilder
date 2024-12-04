import os
import subprocess
import sys
import shutil

class AutoBuilder:
    def __init__(self):
        self.package_managers = {
            "apt": "sudo apt-get install -y",
            "brew": "brew install",
            "choco": "choco install -y",
            "vcpkg": "vcpkg install"
        }
        self.languages = {
            "python": {
                "setup": self.setup_python,
                "compile": self.compile_python
            },
            "cpp": {
                "setup": self.setup_cpp,
                "compile": self.compile_cpp
            },
            "java": {
                "setup": self.setup_java,
                "compile": self.compile_java
            }
        }

    def run_command(self, command, cwd=None):
        try:
            result = subprocess.run(command, shell=True, cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(result.stdout.decode("utf-8"))
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stderr.decode('utf-8')}")
            sys.exit(1)

    def detect_package_manager(self):
        for pm in self.package_managers:
            if shutil.which(pm):
                print(f"Detected package manager: {pm}")
                return pm
        print("No supported package manager detected.")
        sys.exit(1)

    def install_packages(self, packages):
        pm = self.detect_package_manager()
        install_command = self.package_managers[pm]
        for package in packages:
            print(f"Installing {package}...")
            self.run_command(f"{install_command} {package}")

    def setup_python(self):
        print("Setting up Python environment...")
        self.install_packages(["python3", "pip"])
        self.run_command("pip install -r requirements.txt")

    def compile_python(self, project_path):
        print("Running Python project...")
        self.run_command(f"python3 {project_path}")

    def setup_cpp(self):
        print("Setting up C++ environment...")
        self.install_packages(["g++", "cmake"])

    def compile_cpp(self, project_path):
        print("Compiling C++ project...")
        build_dir = os.path.join(project_path, "build")
        os.makedirs(build_dir, exist_ok=True)
        self.run_command("cmake ..", cwd=build_dir)
        self.run_command("make", cwd=build_dir)

    def setup_java(self):
        print("Setting up Java environment...")
        self.install_packages(["openjdk"])

    def compile_java(self, project_path):
        print("Compiling Java project...")
        self.run_command(f"javac {project_path}/*.java")
        print("Running Java project...")
        self.run_command(f"java -cp {project_path} Main")

    def auto_build(self, language, project_path):
        if language not in self.languages:
            print(f"Unsupported language: {language}")
            sys.exit(1)

        setup = self.languages[language]["setup"]
        compile = self.languages[language]["compile"]

        setup()
        compile(project_path)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AutoBuilder: автоматическая сборка и настройка проектов.")
    parser.add_argument("language", help="Язык программирования (python, cpp, java и др.)")
    parser.add_argument("project_path", help="Путь к папке проекта")
    
    args = parser.parse_args()

    builder = AutoBuilder()
    builder.auto_build(args.language, args.project_path)