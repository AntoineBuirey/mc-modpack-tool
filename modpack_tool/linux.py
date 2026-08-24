import sys
from pathlib import Path
import subprocess

SERVICE_TEMPLATE = """[Unit]
Description={service_name}
After=network.target

[Service]
User={user}
Group={group}
WorkingDirectory={working_directory}
ExecStart={exec_start}
Restart=always
RestartSec=10
StandardOutput=append:/var/log/minecraft/{service_name}/server.log
StandardError=append:/var/log/minecraft/{service_name}/error.log

[Install]
WantedBy=multi-user.target
"""

log_path = Path("/var/log/modpack-tool/linux.log")
log_path.parent.mkdir(parents=True, exist_ok=True)

def is_valid_filename(filename: str) -> bool:
    """
    Validates if the provided filename is valid for a systemd service file.
    """
    # A valid filename should not contain any of the following characters: / \ : * ? " < > | and spaces
    # It should also not be empty.
    invalid_chars = set('/\\:*?"<>| ')
    return not any(char in invalid_chars for char in filename) and len(filename) > 0

def create_systemd_service(service_name: str, working_directory: str, exec_start: str, user: str = "minecraft", group: str = "minecraft") -> None:
    """
    Creates a systemd service file for the Minecraft server.
    """
    if not sys.platform == "linux":
        raise EnvironmentError("This function is only supported on Linux systems.")
    
    if not is_valid_filename(service_name):
        raise ValueError(f"Invalid service name '{service_name}'. It must not contain spaces or any of the following characters: / \\ : * ? \" < > |")
    service_content = SERVICE_TEMPLATE.format(
        service_name=service_name,
        user=user,
        group=group,
        working_directory=working_directory,
        exec_start=exec_start
    )
    
    service_file_path = f"/etc/systemd/system/{service_name}.service"
    
    with open(service_file_path, "w", encoding="utf-8") as service_file:
        service_file.write(service_content)
    
    # Reload systemd to recognize the new service
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"Created systemd service file at {service_file_path}\n")
        subprocess.run(["systemctl", "daemon-reload"], check=True, stdout=log_file, stderr=log_file)
    

def create_user(user: str, group: str) -> None:
    """
    Creates a system user and group for running the Minecraft server.
    """
    if not sys.platform == "linux":
        raise EnvironmentError("This function is only supported on Linux systems.")
    
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"Creating user '{user}' and group '{group}' if they do not exist.\n")
        # Create group if it doesn't exist
        subprocess.run(["getent", "group", group], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if subprocess.run(["getent", "group", group]).returncode != 0:
            subprocess.run(["groupadd", group], check=True, stdout=log_file, stderr=log_file)
        
        # Create user if it doesn't exist
        subprocess.run(["id", "-u", user], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if subprocess.run(["id", "-u", user]).returncode != 0:
            subprocess.run(["useradd", "-r", "-g", group, "-d", f"/home/{user}", "-s", "/bin/false", user], check=True, stdout=log_file, stderr=log_file)

def change_folder_ownership(path: str, user: str, group: str) -> None:
    """
    if not sys.platform == "linux":
        raise EnvironmentError("This function is only supported on Linux systems.")
        
    Changes the ownership of the specified folder to the given user and group.
    """
    if not sys.platform == "linux":
        raise EnvironmentError("This function is only supported on Linux systems.")

    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"Changing ownership of {path} to {user}:{group}\n")
        subprocess.run(["chown", "-R", f"{user}:{group}", path], check=True, stdout=log_file, stderr=log_file)
        
def change_folder_permissions(path: str, mode : str) -> None:
    """
    Changes the permissions of the specified folder to the given mode.
    """
    if not sys.platform == "linux":
        raise EnvironmentError("This function is only supported on Linux systems.")
    
    if not isinstance(mode, str) or not mode.isdigit() or len(mode) not in [3, 4]:
        raise ValueError(f"Invalid mode '{mode}'. It must be a string representing octal permissions (e.g., '755' or '0755').")
    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"Changing permissions of {path} to {mode}\n")
        subprocess.run(["chmod", "-R", mode, path], check=True, stdout=log_file, stderr=log_file)
