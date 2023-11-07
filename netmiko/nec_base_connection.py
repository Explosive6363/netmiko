"""CiscoBaseConnection is netmiko SSH class for Cisco and Cisco-like platforms."""
from typing import Optional
import re
from netmiko.base_connection import BaseConnection
from netmiko.scp_handler import BaseFileTransfer


class NecBaseConnection(BaseConnection):
    """Base Class for cisco-like behavior."""

    def check_enable_mode(self, check_string: str = "(config)#") -> bool:
        """Check if in enable mode. Return boolean."""
        return super().check_enable_mode(check_string=check_string)

    def enable(
        self,
        cmd: str = "svintr-config",
        pattern: str = "ssword",
        enable_pattern: Optional[str] = None,
        check_state: bool = True,
        re_flags: int = re.IGNORECASE,
    ) -> str:
        """Enter enable mode."""
        return super().enable(
            cmd=cmd,
            pattern=pattern,
            enable_pattern=enable_pattern,
            check_state=check_state,
            re_flags=re_flags,
        )

    def exit_enable_mode(self, exit_command: str = "exit") -> str:
        """Exits enable (privileged exec) mode."""
        return super().exit_enable_mode(exit_command=exit_command)

    def check_config_mode(
        self, check_string: str = ")#", pattern: str = "", force_regex: bool = False
    ) -> bool:
        """Checks if the device is in configuration mode or not."""
        return super().check_config_mode(
            check_string=check_string, pattern=pattern, force_regex=force_regex
        )

    def config_mode(
        self,
        config_command: str = "configure terminal",
        pattern: str = "",
        re_flags: int = 0,
    ) -> str:
        return super().config_mode(
            config_command=config_command, pattern=pattern, re_flags=re_flags
        )

    def exit_config_mode(self, exit_config: str = "exit", pattern: str = r"#.*") -> str:
        """Exit from configuration mode."""
        return super().exit_config_mode(exit_config=exit_config, pattern=pattern)


    def cleanup(self, command: str = "exit") -> None:
        """Gracefully exit the SSH session."""
        try:
            if self.check_config_mode():
                self.exit_config_mode()
        except Exception:
            pass
        # Always try to send final 'exit' (command)
        if self.session_log:
            self.session_log.fin = True
        self.write_channel(command + self.RETURN)

    def _autodetect_fs(
        self, cmd: str = "dir", pattern: str = r"Directory of (.*)/"
    ) -> str:
        """Autodetect the file system on the remote device. Used by SCP operations."""
        if not self.check_enable_mode():
            raise ValueError("Must be in enable mode to auto-detect the file-system.")
        output = self._send_command_str(cmd)
        match = re.search(pattern, output)
        if match:
            file_system = match.group(1)
            # Test file_system
            cmd = f"dir {file_system}"
            output = self._send_command_str(cmd)
            if "% Invalid" in output or "%Error:" in output:
                raise ValueError(
                    "An error occurred in dynamically determining remote file "
                    "system: {} {}".format(cmd, output)
                )
            else:
                return file_system

        raise ValueError(
            "An error occurred in dynamically determining remote file "
            "system: {} {}".format(cmd, output)
        )

    def save_config(
        self,
        cmd: str = "copy running-config startup-config",
        confirm: bool = False,
        confirm_response: str = "",
    ) -> str:
        """Saves Config."""
        self.enable()
        if confirm:
            output = self._send_command_timing_str(
                command_string=cmd, strip_prompt=False, strip_command=False
            )
            if confirm_response:
                output += self._send_command_timing_str(
                    confirm_response, strip_prompt=False, strip_command=False
                )
            else:
                # Send enter by default
                output += self._send_command_timing_str(
                    self.RETURN, strip_prompt=False, strip_command=False
                )
        else:
            # Some devices are slow so match on trailing-prompt if you can
            output = self._send_command_str(
                command_string=cmd,
                strip_prompt=False,
                strip_command=False,
                read_timeout=100.0,
            )
        return output


class NecSSHConnection(NecBaseConnection):
    pass


class NecFileTransfer(BaseFileTransfer):
    pass
