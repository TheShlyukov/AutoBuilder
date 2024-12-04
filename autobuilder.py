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
        response = input(f"{tool} не найден. Установить? (y/n): ").strip().lower()
        if response == "y":
            print(f"Устанавливаю {tool}...\")\n")
            self.run_command(install_command)
        else:
            print(f"{tool} необходим для продолжения. Завершаю работу.")
            sys.exit(1)

    def detect_or_install_package_manager(self, chosen_pm=None):
        if chosen_pm:
            if shutil.which(chosen_pm):
                print(f"Используем указанный менеджер пакетов: {chosen_pm}")
                return chosen_pm
            else:
                self.prompt_install(chosen_pm, self.get_install_command(chosen_pm))
        else:
            for pm in self.package_managers:
                if shutil.which(pm):
                    print(f"Обнаружен менеджер пакетов: {pm}")
                    return pm
            print("Менеджер пакетов не обнаружен.")
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
            print(f"Менеджер пакетов {package_manager} не поддерживается.")
            sys.exit(1)

        for package in packages:
            print(f"Устанавливаю {package} через {package_manager}...")
            self.run_command(f"{install_command} {package}")

    def setup_python(self):
        print("Настройка Python окружения...")
        self.install_packages(["python3", "pip"], package_manager="brew")
        response = input("Хотите установить pyinstaller для компиляции в бинарный файл? (y/n): ").strip().lower()
        if response == "y":
            self.run_command("pip install pyinstaller")

    def compile_python(self, project_path):
        response = input("Скомпилировать Python проект в бинарный файл? (y/n): ").strip().lower()
        if response == "y":
            print("Компиляция Python в бинарный файл...")
            self.run_command(f"pyinstaller --onefile {project_path}")
        else:
            print("Запуск Python проекта...")
            self.run_command(f"python3 {project_path}")

    def setup_cpp(self):
        print("Настройка C++ окружения...")
        self.install_packages(["g++", "cmake"], package_manager="brew")

    def compile_cpp(self, project_path):
        print("Компиляция C++ проекта...")
        build_dir = os.path.join(project_path, "build")
        os.makedirs(build_dir, exist_ok=True)
        self.run_command("cmake ..", cwd=build_dir)
        self.run_command("make", cwd=build_dir)

    def setup_java(self):
        print("Настройка Java окружения...")
        self.install_packages(["openjdk"], package_manager="brew")

    def compile_java(self, project_path):
        print("Компиляция Java проекта...")
        self.run_command(f"javac {project_path}/*.java")
        print("Запуск Java проекта...")
        self.run_command(f"java -cp {project_path} Main")

    def auto_build(self, language, project_path, package_manager=None):
        if language not in self.languages:
            print(f"Неподдерживаемый язык: {language}")
            sys.exit(1)

        pm = self.detect_or_install_package_manager(package_manager)

        setup = self.languages[language]["setup"]
        compile = self.languages[language]["compile"]

        setup()
        compile(project_path)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AutoBuilder: автоматическая сборка и настройка проектов.")
    parser.add_argument("language", help="Язык программирования (python, cpp, java и др.)")
    parser.add_argument("project_path", help="Путь к папке проекта")
    parser.add_argument("--package-manager", help="Менеджер пакетов для установки зависимостей (например, brew, apt, choco)")

    args = parser.parse_args()

    builder = AutoBuilder()
    builder.auto_build(args.language, args.project_path, args.package_manager)
