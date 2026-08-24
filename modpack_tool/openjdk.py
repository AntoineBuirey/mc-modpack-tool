import subprocess
import sys
import os
from pathlib import Path

from .progressBar import ProgressBar
from .classes import Version


def check_java_installed() -> bool:
    try:
        subprocess.run(['java', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error checking Java version: {e}")
        return False
    return True

def get_java_version(minecraft_version: Version) -> int:
    """
    Returns the requied Java version for the given Minecraft version.
    """
    mapping ={
        Version(1,7,0): 8,
        Version(1,17,0) : 16,
        Version(1,18,0) : 17,
        Version(1,20,5) : 21
    }
    for version, java_version in sorted(mapping.items(), reverse=True):
        if minecraft_version >= version:
            return java_version
    raise ValueError(f"No Java version mapping found for Minecraft version {minecraft_version}. Please update the mapping in the code.")
    
def is_java_installed(required_version: int) -> bool:
    """
    Checks if the required Java version is installed.
    """
    try:
        result = subprocess.run(['java', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stderr
        if f'openjdk version "{required_version}' in output or f'java version "{required_version}' in output:
            return True
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error checking Java version: {e}")
        return False
    return False

def install_openjdk(version: int, progressbar : ProgressBar|None = None) -> None:
    """
    Installe automatiquement une version spécifique d'OpenJDK (Temurin Headless)
    sur Debian 12 (Bookworm) et Debian 13 (Trixie).
    """
    if not sys.platform == "linux":
        raise EnvironmentError("This function is only supported on Linux systems.")
    
    if is_java_installed(version):
        print(f"Java {version} is already installed.")
        return
    
    # 1. Vérification des privilèges Root / Sudo
    if os.geteuid() != 0:
        raise PermissionError("This function requires root privileges. Please run the script as root or with sudo.")

    pb = progressbar.set_subbar(5, f"Installing OpenJDK {version}", use_percentage=False) if progressbar else None
    log_path = Path("/var/log/modpack-tool/openjdk.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with log_path.open("a", encoding="utf-8") as log_file:
        try:
            subprocess.run(["apt-get", "update"], check=True, stdout=log_file, stderr=log_file)
            subprocess.run(["apt-get", "install", "-y", "wget", "apt-transport-https", "gnupg"], check=True, stdout=log_file, stderr=log_file)
            if pb:
                pb.update(1)

            os.makedirs("/etc/apt/keyrings", exist_ok=True)
            key_url = "https://packages.adoptium.net/artifactory/api/gpg/key/public"
            keyring_path = "/etc/apt/keyrings/adoptium.gpg"

            # Download the official Adoptium GPG key and convert it to a proper apt keyring.
            key_proc = subprocess.run(["wget", "-qO-", key_url], check=True, stdout=subprocess.PIPE, stderr=log_file)
            subprocess.run(["gpg", "--dearmor", "--yes", "--output", keyring_path], input=key_proc.stdout, check=True, stdout=log_file, stderr=log_file)
            if pb:
                pb.update(1)

            # Récupère le nom de code de la distribution (ex: bookworm, trixie)
            codename = ""
            try:
                codename_proc = subprocess.run(["lsb_release", "-cs"], stdout=subprocess.PIPE, text=True, check=False, stderr=log_file)
                codename = codename_proc.stdout.strip()
            except Exception:
                codename = ""

            if not codename:
                try:
                    with open("/etc/os-release", "r") as f:
                        for line in f:
                            if line.startswith("VERSION_CODENAME="):
                                codename = line.split("=", 1)[1].strip().strip('"')
                                break
                except Exception:
                    codename = ""

            if not codename:
                raise ValueError("Could not determine the distribution codename. Please ensure lsb_release is installed or check /etc/os-release.")

            repo_line = f"deb [signed-by={keyring_path}] https://packages.adoptium.net/artifactory/deb {codename} main\n"
            with open("/etc/apt/sources.list.d/adoptium.list", "w") as repo_file:
                repo_file.write(repo_line)
            if pb:
                pb.update(1)

            subprocess.run(["apt-get", "update"], check=True, stdout=log_file, stderr=log_file)
            if pb:
                pb.update(1)

            package_name = f"temurin-{version}-jdk"

            # Vérification si le paquet existe dans les dépôts mis à jour
            check_pkg = subprocess.run(["apt-cache", "show", package_name], stdout=subprocess.PIPE, stderr=log_file)
            if check_pkg.returncode != 0:
                raise ValueError(f"Package {package_name} not found in the repositories. Please check the version or the repository configuration.")

            subprocess.run(["apt-get", "install", "-y", package_name], check=True, stdout=log_file, stderr=log_file)
            if pb:
                pb.update(1)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"An error occurred while executing a command: {e}")
        except Exception as e:
            raise RuntimeError(f"An error occurred during the installation of OpenJDK {version}: {e}")
    
    if progressbar:
        progressbar.remove_subbar()
