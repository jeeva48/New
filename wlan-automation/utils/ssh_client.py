"""Thin SSH wrapper (paramiko) for running commands on an AP or Linux test client."""
import paramiko

from utils.logger import get_logger

log = get_logger("ssh")


class SSHClient:
    def __init__(self, host: str, username: str, password: str, port: int = 22):
        self.host, self.port = host, port
        self.username, self.password = username, password
        self._client = None

    def __enter__(self):
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._client.connect(
            self.host, port=self.port,
            username=self.username, password=self.password, timeout=10,
        )
        return self

    def __exit__(self, *exc):
        if self._client:
            self._client.close()

    def run(self, command: str, timeout: int = 30) -> str:
        log.info("SSH %s: %s", self.host, command)
        _, stdout, stderr = self._client.exec_command(command, timeout=timeout)
        out, err = stdout.read().decode(), stderr.read().decode()
        if stdout.channel.recv_exit_status() != 0:
            raise RuntimeError(f"Command failed: {command}\n{err}")
        return out
