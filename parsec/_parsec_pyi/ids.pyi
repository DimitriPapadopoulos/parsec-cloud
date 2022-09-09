from uuid import UUID

class OrganizationID:
    def __init__(self, data: str) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: OrganizationID) -> bool: ...
    def __ne__(self, other: OrganizationID) -> bool: ...
    def __lt__(self, other: OrganizationID) -> bool: ...
    def __gt__(self, other: OrganizationID) -> bool: ...
    def __le__(self, other: OrganizationID) -> bool: ...
    def __ge__(self, other: OrganizationID) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def str(self) -> str: ...

class UserID:
    def __init__(self, data: str) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: UserID) -> bool: ...
    def __ne__(self, other: UserID) -> bool: ...
    def __lt__(self, other: UserID) -> bool: ...
    def __gt__(self, other: UserID) -> bool: ...
    def __le__(self, other: UserID) -> bool: ...
    def __ge__(self, other: UserID) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def str(self) -> str: ...

class DeviceName:
    def __init__(self, data: str) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: DeviceName) -> bool: ...
    def __ne__(self, other: DeviceName) -> bool: ...
    def __lt__(self, other: DeviceName) -> bool: ...
    def __gt__(self, other: DeviceName) -> bool: ...
    def __le__(self, other: DeviceName) -> bool: ...
    def __ge__(self, other: DeviceName) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def str(self) -> str: ...

class DeviceID:
    def __init__(self, data: str) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: DeviceID | None) -> bool: ...
    def __ne__(self, other: DeviceID | None) -> bool: ...
    def __lt__(self, other: DeviceID | None) -> bool: ...
    def __gt__(self, other: DeviceID | None) -> bool: ...
    def __le__(self, other: DeviceID | None) -> bool: ...
    def __ge__(self, other: DeviceID | None) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def str(self) -> str: ...
    @property
    def user_id(self) -> UserID: ...
    @property
    def device_name(self) -> DeviceName: ...

class DeviceLabel:
    def __init__(self, data: str) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: DeviceLabel) -> bool: ...
    def __ne__(self, other: DeviceLabel) -> bool: ...
    def __lt__(self, other: DeviceLabel) -> bool: ...
    def __gt__(self, other: DeviceLabel) -> bool: ...
    def __le__(self, other: DeviceLabel) -> bool: ...
    def __ge__(self, other: DeviceLabel) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def str(self) -> str: ...

class HumanHandle:
    def __init__(self, email: str, label: str) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: HumanHandle | None) -> bool: ...
    def __ne__(self, other: HumanHandle | None) -> bool: ...
    def __lt__(self, other: HumanHandle | None) -> bool: ...
    def __gt__(self, other: HumanHandle | None) -> bool: ...
    def __le__(self, other: HumanHandle | None) -> bool: ...
    def __ge__(self, other: HumanHandle | None) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def email(self) -> str: ...
    @property
    def label(self) -> str: ...
    @property
    def str(self) -> str: ...

class RealmID:
    def __init__(self, uuid: UUID) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: RealmID) -> bool: ...
    def __ne__(self, other: RealmID) -> bool: ...
    def __lt__(self, other: RealmID) -> bool: ...
    def __gt__(self, other: RealmID) -> bool: ...
    def __le__(self, other: RealmID) -> bool: ...
    def __ge__(self, other: RealmID) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def uuid(self) -> UUID: ...
    @property
    def bytes(self) -> bytes: ...
    @property
    def hex(self) -> str: ...
    def from_bytes(bytes: bytes) -> RealmID: ...
    def from_hex(hex: str) -> RealmID: ...
    @classmethod
    def new() -> RealmID: ...
    @property
    def str(self) -> str: ...

class BlockID:
    def __init__(self, uuid: UUID) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: BlockID) -> bool: ...
    def __ne__(self, other: BlockID) -> bool: ...
    def __lt__(self, other: BlockID) -> bool: ...
    def __gt__(self, other: BlockID) -> bool: ...
    def __le__(self, other: BlockID) -> bool: ...
    def __ge__(self, other: BlockID) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def uuid(self) -> UUID: ...
    @property
    def bytes(self) -> bytes: ...
    @property
    def hex(self) -> str: ...
    def from_bytes(bytes: bytes) -> BlockID: ...
    def from_hex(hex: str) -> BlockID: ...
    @classmethod
    def new() -> BlockID: ...
    @property
    def str(self) -> str: ...

class VlobID:
    def __init__(self, uuid: UUID) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: VlobID) -> bool: ...
    def __ne__(self, other: VlobID) -> bool: ...
    def __lt__(self, other: VlobID) -> bool: ...
    def __gt__(self, other: VlobID) -> bool: ...
    def __le__(self, other: VlobID) -> bool: ...
    def __ge__(self, other: VlobID) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def uuid(self) -> UUID: ...
    @property
    def bytes(self) -> bytes: ...
    @property
    def hex(self) -> str: ...
    def from_bytes(bytes: bytes) -> VlobID: ...
    def from_hex(hex: str) -> VlobID: ...
    @classmethod
    def new() -> VlobID: ...
    @property
    def str(self) -> str: ...

class EntryID:
    def __init__(self, uuid: UUID) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: EntryID) -> bool: ...
    def __ne__(self, other: EntryID) -> bool: ...
    def __lt__(self, other: EntryID) -> bool: ...
    def __gt__(self, other: EntryID) -> bool: ...
    def __le__(self, other: EntryID) -> bool: ...
    def __ge__(self, other: EntryID) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def uuid(self) -> UUID: ...
    @property
    def bytes(self) -> bytes: ...
    @property
    def hex(self) -> str: ...
    def from_bytes(bytes: bytes) -> EntryID: ...
    def from_hex(hex: str) -> EntryID: ...
    @classmethod
    def new() -> EntryID: ...
    @property
    def str(self) -> str: ...

class ChunkID:
    def __init__(self, uuid: UUID) -> None: ...
    def __repr__(self) -> str: ...
    def __eq__(self, other: ChunkID | EntryID) -> bool: ...
    def __ne__(self, other: ChunkID | EntryID) -> bool: ...
    def __lt__(self, other: ChunkID | EntryID) -> bool: ...
    def __gt__(self, other: ChunkID | EntryID) -> bool: ...
    def __le__(self, other: ChunkID | EntryID) -> bool: ...
    def __ge__(self, other: ChunkID | EntryID) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def uuid(self) -> UUID: ...
    @property
    def bytes(self) -> bytes: ...
    @property
    def hex(self) -> str: ...
    def from_bytes(bytes: bytes) -> ChunkID: ...
    def from_hex(hex: str) -> ChunkID: ...
    @classmethod
    def new() -> ChunkID: ...
    @property
    def str(self) -> str: ...

class SequesterServiceID:
    def __init__(self, uuid: UUID) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    def __eq__(self, other: SequesterServiceID) -> bool: ...
    def __ne__(self, other: SequesterServiceID) -> bool: ...
    def __lt__(self, other: SequesterServiceID) -> bool: ...
    def __gt__(self, other: SequesterServiceID) -> bool: ...
    def __le__(self, other: SequesterServiceID) -> bool: ...
    def __ge__(self, other: SequesterServiceID) -> bool: ...
    def __hash__(self) -> int: ...
    @property
    def uuid(self) -> UUID: ...
    @property
    def bytes(self) -> bytes: ...
    @property
    def hex(self) -> str: ...
    def from_bytes(bytes: bytes) -> SequesterServiceID: ...
    def from_hex(hex: str) -> SequesterServiceID: ...
    @classmethod
    def new() -> SequesterServiceID: ...
