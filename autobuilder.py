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

    def prompt_install(self, tool, install_command):
        response = input(f"{tool} not found. Do you want to install it? (y/n): ").strip().lower()
        if response == "y":
            print(f"Installing {tool}...\")\n")
            self.run_command(install_command)
        else:
            print(f"{tool} is needed to continue. Shuting down.")
            sys.exit(1)

    def detect_or_install_package_manager(self, chosen_pm=None):
        if chosen_pm:
            if shutil.which(chosen_pm):
                print(f"Using selected Package Manager: {chosen_pm}")
                return chosen_pm
            else:
                self.prompt_install(chosen_pm, self.get_install_command(chosen_pm))
        else:
            for pm in self.package_managers:
                if shutil.which(pm):
                    print(f"Package Manager found: {pm}")
                    return pm
            print("Package Manager not found.")
        sys.exit(1)

    def get_install_command(self, manager):
        if manager == "brew":
            return "/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        elif manager == "vcpkg":
            return "git clone https://github.com/microsoft/vcpkg.git && ./vcpkg/bootstrap-vcpkg.sh"
        else:
            return ""

    def install_packages(self, packages, package_manager):
        install_command = self.package_managers.get(package_manager)
        if not install_command:
            print(f"Package Manager {package_manager} doesn't support on your system.")
            sys.exit(1)

        for package in packages:
            print(f"Installing {package} with {package_manager}...")
            self.run_command(f"{install_command} {package}")

    def setup_python(self):
        print("Setting up Python environment...")
        self.install_packages(["python3", "pip"], package_manager="brew")
        response = input("Do you wish to install pyinstaller for compiling to binary? (y/n): ").strip().lower()
        if response == "y":
            self.run_command("pip install pyinstaller")

    def compile_python(self, project_path):
        response = input("Do you want compile Python project to binary? (y/n): ").strip().lower()
        if response == "y":
            print("Compiling Python project to binary...")
            self.run_command(f"pyinstaller --onefile {project_path}")
        else:
            print("Running Python project...")
            self.run_command(f"python3 {project_path}")

    def setup_cpp(self):
        print("Setting up C++ environment...")
        self.install_packages(["g++", "cmake"], package_manager="brew")

    def compile_cpp(self, project_path):
        print("Compiling C++ project...")
        build_dir = os.path.join(project_path, "build")
        os.makedirs(build_dir, exist_ok=True)
        self.run_command("cmake ..", cwd=build_dir)
        self.run_command("make", cwd=build_dir)

    def setup_java(self):
        print("Setting up Java environment...")
        self.install_packages(["openjdk"], package_manager="brew")

    def compile_java(self, project_path):
        print("Compiling Java project...")
        self.run_command(f"javac {project_path}/*.java")
        print("Running Java project...")
        self.run_command(f"java -cp {project_path} Main")

    def auto_build(self, language, project_path, package_manager=None):
        if language not in self.languages:
            print(f"Unsupported language: {language}")
            sys.exit(1)

        pm = self.detect_or_install_package_manager(package_manager)

        setup = self.languages[language]["setup"]
        compile = self.languages[language]["compile"]

        setup()
        compile(project_path)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AutoBuilder: automatic build and setup for projects.")
    parser.add_argument("language", help="Programming language (python, cpp, java и др.)")
    parser.add_argument("project_path", help="Path to project")
    parser.add_argument("--package-manager", help="Package Manager to installing dependencies (e.g. brew, apt, choco, vcpkg)")

    args = parser.parse_args()

    builder = AutoBuilder()
    builder.auto_build(args.language, args.project_path, args.package_manager)
