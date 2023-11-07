from typing import Optional
from netmiko.nec_base_connection import NecBaseConnection


class NecIosBase(NecBaseConnection):
    """Common Methods for IOS (both SSH and telnet)."""

    def session_preparation(self) -> None:
        """Prepare the session after the connection has been established."""
        self.set_base_prompt()

    def set_base_prompt(
        self,
        pri_prompt_terminator: str = "#",
        alt_prompt_terminator: str = "(config)#",
        delay_factor: float = 1.0,
        pattern: Optional[str] = None,
    ) -> str:
        """
        Cisco IOS/IOS-XE abbreviates the prompt at 20-chars in config mode.

        Consequently, abbreviate the base_prompt
        """
        base_prompt = super().set_base_prompt(
            pri_prompt_terminator=pri_prompt_terminator,
            alt_prompt_terminator=alt_prompt_terminator,
            delay_factor=delay_factor,
            pattern=pattern,
        )
        self.base_prompt = base_prompt[:16]
        return self.base_prompt

    def check_config_mode(
        self,
        check_string: str = ")#",
        pattern: str = r"[>#]",
        force_regex: bool = False,
    ) -> bool:
        """
        Checks if the device is in configuration mode or not.

        Cisco IOS devices abbreviate the prompt at 20 chars in config mode
        """
        return super().check_config_mode(check_string=check_string, pattern=pattern)

    def save_config(
        self, cmd: str = "write mem", confirm: bool = False, confirm_response: str = ""
    ) -> str:
        """Saves Config Using Copy Run Start"""
        return super().save_config(
            cmd=cmd, confirm=confirm, confirm_response=confirm_response
        )


class NecIosSSH(NecIosBase):
    """Cisco IOS SSH driver."""

    pass
