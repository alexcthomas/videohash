import os

import pytest

from videohash.exceptions import DidNotSupplyPathOrUrl, StoragePathDoesNotExist
from videohash.utils import create_and_return_temporary_directory
from videohash.videohash import VideoHash

this_dir = os.path.dirname(os.path.realpath(__file__))
ROCKET_MKV = os.path.join(this_dir, os.path.pardir, "assets", "rocket.mkv")
ROCKET_HASH = "0b1010100110101001111111111111101101011110101100010000001100000011"
ROCKET_HASH_HEX = "0xa9a9fffb5eb10303"


def test_hash_values():
    videohash = VideoHash(path=ROCKET_MKV, frame_interval=3)
    assert videohash.hash == ROCKET_HASH
    assert str(videohash) == ROCKET_HASH
    assert videohash.hash_hex == ROCKET_HASH_HEX
    assert ROCKET_HASH_HEX in repr(videohash)
    assert ROCKET_HASH in repr(videohash)
    assert (len(videohash) - 2) == videohash.bits_in_hash


def test_comparison_operators():
    videohash1 = VideoHash(path=ROCKET_MKV, frame_interval=3)
    videohash2 = VideoHash(path=ROCKET_MKV, frame_interval=3)

    assert videohash1 == videohash2
    assert videohash1 == ROCKET_HASH
    assert videohash1 == ROCKET_HASH_HEX
    assert videohash1 == videohash2.bitlist
    assert not (videohash1 != videohash2)
    assert videohash1 - videohash2 == 0
    assert videohash1 - ROCKET_HASH == 0
    assert videohash1.is_similar(videohash2)
    assert not videohash1.is_diffrent(videohash2)


def test_subtraction_errors():
    videohash = VideoHash(path=ROCKET_MKV, frame_interval=3)

    with pytest.raises(TypeError):
        _ = videohash - None

    with pytest.raises(ValueError):
        _ = videohash - ROCKET_HASH[0:-2]

    with pytest.raises(TypeError):
        _ = videohash - ("XX" + ROCKET_HASH[2:])

    with pytest.raises(TypeError):
        _ = videohash - True

    with pytest.raises(ValueError):
        _ = videohash - [1, 0, 1, 1, 1]


def test_static_methods():
    with pytest.raises(ValueError):
        VideoHash.hex2bin("741fcfff8f780000", 64)

    with pytest.raises(ValueError):
        VideoHash.bin2hex("010101001")


def test_hamming_distance():
    class FakeVideoHash(VideoHash):
        def __init__(self, hash=None):
            self.hash = hash

    fake = FakeVideoHash(hash="0b0011010")
    fake.hamming_distance(string_a="0b1011010", string_b="0b1011010")

    fake = FakeVideoHash()
    with pytest.raises(ValueError):
        fake.hamming_distance(string_a="abc", string_b="abcd")

    with pytest.raises(ValueError):
        fake.hamming_distance(bitlist_a=[1, 0, 1, 1, 0], bitlist_b=[1, 0, 1, 1])


def test_storage_path_does_not_exist():
    storage_path = os.path.join(
        create_and_return_temporary_directory(),
        ("thisdirdoesnotexist" + os.path.sep),
    )
    with pytest.raises(StoragePathDoesNotExist):
        VideoHash(path=ROCKET_MKV, storage_path=storage_path)


def test_did_not_supply_path():
    with pytest.raises(DidNotSupplyPathOrUrl):
        VideoHash(path="")
