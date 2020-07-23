"""Reusable utilities for the Bond component."""

from typing import List, Optional

from bond_api import Action, Bond


class BondDevice:
    """Helper device class to hold ID and attributes together."""

    def __init__(self, device_id: str, attrs: dict, props: dict):
        """Create a helper device from ID and attributes returned by API."""
        self.device_id = device_id
        self.props = props
        self._attrs = attrs

    @property
    def name(self) -> str:
        """Get the name of this device."""
        return self._attrs["name"]

    @property
    def type(self) -> str:
        """Get the type of this device."""
        return self._attrs["type"]

    @property
    def trust_state(self) -> bool:
        """Check if Trust State is turned on."""
        return self.props.get("trust_state", False)

    def supports_speed(self) -> bool:
        """Return True if this device supports any of the speed related commands."""
        actions: List[str] = self._attrs["actions"]
        return bool([action for action in actions if action in [Action.SET_SPEED]])

    def supports_direction(self) -> bool:
        """Return True if this device supports any of the direction related commands."""
        actions: List[str] = self._attrs["actions"]
        return bool([action for action in actions if action in [Action.SET_DIRECTION]])

    def supports_light(self) -> bool:
        """Return True if this device supports any of the light related commands."""
        actions: List[str] = self._attrs["actions"]
        return bool(
            [
                action
                for action in actions
                if action in [Action.TURN_LIGHT_ON, Action.TURN_LIGHT_OFF]
            ]
        )


class BondHub:
    """Hub device representing Bond Bridge."""

    def __init__(self, bond: Bond):
        """Initialize Bond Hub."""
        self.bond: Bond = bond
        self._version: Optional[dict] = None
        self._devices: Optional[List[BondDevice]] = None

    async def setup(self):
        """Read hub version information."""
        self._version = await self.bond.version()

        # Fetch all available devices using Bond API.
        device_ids = await self.bond.devices()
        self._devices = [
            BondDevice(
                device_id,
                await self.bond.device(device_id),
                await self.bond.device_properties(device_id),
            )
            for device_id in device_ids
        ]

    @property
    def bond_id(self) -> str:
        """Return unique Bond ID for this hub."""
        return self._version["bondid"]

    @property
    def target(self) -> str:
        """Return this hub model."""
        return self._version.get("target")

    @property
    def fw_ver(self) -> str:
        """Return this hub firmware version."""
        return self._version.get("fw_ver")

    @property
    def devices(self) -> List[BondDevice]:
        """Return a list of all devices controlled by this hub."""
        return self._devices

    @property
    def is_bridge(self) -> bool:
        """Return if the Bond is a Bond Bridge. If False, it means that it is a Smart by Bond product."""
        return self._version.get("model").startswith("BD-")
