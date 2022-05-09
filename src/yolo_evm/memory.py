from .constants import MAX_UINT256, MAX_UINT8

ZERO_WORD = [0] * 32

# thanks, https://stackoverflow.com/questions/14822184/is-there-a-ceiling-equivalent-of-operator-in-python
def ceildiv(a, b):
    return -(a // -b)


class Memory:
    def __init__(self) -> None:
        # TODO: use https://docs.python.org/3/library/functions.html#func-bytearray
        self.memory = []

    def store(self, offset: int, value: int) -> None:
        if offset < 0 or offset > MAX_UINT256:
            raise InvalidMemoryAccess({"offset": offset, "value": value})

        if value < 0 or value > MAX_UINT8:
            raise InvalidMemoryValue({"offset": offset, "value": value})

        self._expand_if_needed(offset)
        self.memory[offset] = value

    def load(self, offset: int) -> int:
        if offset < 0:
            raise InvalidMemoryAccess({"offset": offset})

        self._expand_if_needed(offset)
        return self.memory[offset]

    def load_range(self, offset: int, length: int) -> bytes:
        if offset < 0:
            raise InvalidMemoryAccess({"offset": offset, "length": length})

        self._expand_if_needed(offset + length - 1)

        return bytes(self.memory[offset : offset + length])

    def active_words(self) -> int:
        return len(self.memory) // 32

    # per the definition of MSTORE8 and MLOAD in the yellow paper, the number of active words is
    # expanded when both reading and writing a previously untouched memory location
    # MLOAD:
    #   μ′i ≡ max(μi,⌈(μs[0]+32)÷32⌉)
    # MSTORE8:
    #   μ′i ≡ max(μi, ⌈(μs[0]+1)÷32⌉)
    #
    # human-readable Solidity docs:
    # https://docs.soliditylang.org/en/latest/introduction-to-smart-contracts.html#storage-memory-and-the-stack
    def _expand_if_needed(self, offset: int) -> None:
        if offset < len(self.memory):
            return

        active_words_after = max(self.active_words(), ceildiv(offset + 1, 32))

        self.memory.extend(ZERO_WORD * (active_words_after - self.active_words()))

        assert len(self.memory) % 32 == 0

    def __len__(self) -> int:
        return len(self.memory)

    def __str__(self) -> str:
        return str(self.memory)

    def __repr__(self) -> str:
        return str(self)


class InvalidMemoryAccess(Exception):
    ...


class InvalidMemoryValue(Exception):
    ...
