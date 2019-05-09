import pytest
from eth_utils import decode_hex

from raiden.constants import EMPTY_HASH, EMPTY_MERKLE_ROOT
from raiden.tests.utils import factories
from raiden.transfer.secret_registry import events_for_onchain_secretreveal
from raiden.transfer.state import TransactionExecutionStatus
from raiden.transfer.utils import hash_balance_data


@pytest.mark.parametrize(
    "values,expected",
    (
        ((0, 0, EMPTY_HASH), bytes(32)),
        (
            (1, 5, EMPTY_MERKLE_ROOT),
            decode_hex("0xc6b26a4554afa01fb3409b3bd6e7605a1c1af45b7e644282c6ebf34eddb6f893"),
        ),
    ),
)
def test_hash_balance_data(values, expected):
    assert hash_balance_data(values[0], values[1], values[2]) == expected


def test_events_for_onchain_secretreveal_with_unfit_channels():
    settle = factories.TransactionExecutionStatusProperties()
    settled = factories.create(factories.NettingChannelStateProperties(settle_transaction=settle))
    secret = factories.UNIT_SECRET
    block_hash = factories.make_block_hash()

    events = events_for_onchain_secretreveal(settled, secret, 10, block_hash)
    assert not events, "Secret reveal event should not be generated for settled channel"

    settle = factories.replace(settle, result=TransactionExecutionStatus.FAILURE)
    unusable = factories.create(factories.NettingChannelStateProperties(settle_transaction=settle))

    events = events_for_onchain_secretreveal(unusable, secret, 10, block_hash)
    assert not events, "Secret reveal event should not be generated for unusable channel."


def test_events_for_onchain_secretreveal_typechecks_secret():
    channel = factories.create(factories.NettingChannelStateProperties())
    block_hash = factories.make_block_hash()
    with pytest.raises(ValueError):
        events_for_onchain_secretreveal(channel, "This is an invalid secret", 10, block_hash)
