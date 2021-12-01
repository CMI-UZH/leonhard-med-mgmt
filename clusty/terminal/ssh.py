"""SSH configuration functions"""

from pathlib import Path

ssh_config_file_str = "~/.ssh/config"
ssh_config_file = Path(ssh_config_file_str).expanduser().resolve()
indent = "\n\t"
end = "\n\n"


def config_control_master() -> None:
    """The control master configuration in the ssh config file allows for multiple logins to the same SSH host
    without the need to reenter credentials"""

    config = f"ControlMaster auto{indent}ControlPath ~/.ssh/control-%r@%h:%p:{end}"

    with open(ssh_config_file, 'r+') as file:
        content = file.read()
        if config not in content:
            file.seek(0, 0)
            file.write(config + content)

    print(f"ssh-config: Added Control Master to {ssh_config_file_str}")


def config_host(ssh_alias: str, host_name: str, user: str, ssh_key: str = None, proxy_jump: str = None,
                proxy_host_name: str = None, forward_port: int = None) -> None:
    """Add host configuration to the SSH config file depending on options passed in"""

    header = f"Host {ssh_alias} {host_name}"
    config = f"{indent}User {user}"
    if ssh_key is not None:
        config += f"{indent}IdentityFile <~/.ssh/{ssh_key}"
    config += f"{indent}HostName {host_name}"
    if proxy_jump is not None:
        config += f"{indent}ProxyJump {proxy_jump}"
    if proxy_host_name is not None:
        config += f"{indent}ProxyCommand ssh -Y %r@{proxy_host_name} -W %h:%p"
    if forward_port is not None:
        config += f"{indent}ForwardAgent yes"
        config += f"{indent}LocalForward {forward_port} 127.0.0.1:{forward_port}"
    config += end

    # Append to SSH configuration file if it doesn't exist yet
    append_config = False
    with open(ssh_config_file, 'r') as file:
        content = file.read()
        if header not in content:
            append_config = True

    if append_config:
        with open(ssh_config_file, 'a') as file:
            file.write(header + config)
            print(f"ssh-config: Added host {ssh_alias} to {ssh_config_file_str}")
