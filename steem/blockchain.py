import time
from .block import Block
from . import steem as stm
from .utils import parse_time

virtual_operations = [
    "fill_convert_request",
    "author_reward",
    "curation_reward",
    "comment_reward",
    "liquidity_reward",
    "interest",
    "fill_vesting_withdraw",
    "fill_order",
    "shutdown_witness",
    "fill_transfer_from_savings",
    "hardfork",
    "comment_payout_update"
]


class Blockchain(object):
    def __init__(
        self,
        steem_instance=None,
        mode="irreversible"
    ):
        """ This class allows to access the blockchain and read data
            from it

            :param Steem steem: Steem() instance to use when accesing a RPC
            :param str mode: (default) Irreversible block
                    (``irreversible``) or actual head block (``head``)
        """
        if not steem_instance:
            steem_instance = stm.Steem()
        self.steem = steem_instance

        if mode == "irreversible":
            self.mode = 'last_irreversible_block_num'
        elif mode == "head":
            self.mode = "head_block_number"
        else:
            raise ValueError("invalid value for 'mode'!")

    def info(self):
        """ This call returns the *dynamic global properties*
        """
        return self.steem.rpc.get_dynamic_global_properties()

    def config(self):
        return self.steem.rpc.get_config()

    def get_current_block_num(self):
        """ This call returns the current block
        """
        return self.info().get(self.mode)

    def get_current_block(self):
        """ This call returns the current block
        """
        return Block(self.get_current_block_num())

    def blocks(self, start, stop):
        """ Yields blocks starting from ``start``.

            :param int start: Starting block
            :param int stop: Stop at this block
            :param str mode: We here have the choice between
                 * "head": the last block
                 * "irreversible": the block that is confirmed by 2/3 of all block producers and is thus irreversible!
        """
        # Let's find out how often blocks are generated!
        block_interval = self.config().get("STEEMIT_BLOCK_INTERVAL")

        if not start:
            start = self.get_current_block_num()

        # We are going to loop indefinitely
        while True:

            # Get chain properies to identify the
            head_block = self.get_current_block_num()

            # Blocks from start until head block
            for blocknum in range(start, head_block + 1):
                # Get full block
                block = self.steem.rpc.get_block(blocknum)
                block.update({"block_num": blocknum})
                yield block

            # Set new start
            start = head_block + 1

            if stop and start > stop:
                break

            # Sleep for one block
            time.sleep(block_interval)

    def ops(self, start=None, stop=None, only_virtual_ops=False, **kwargs):
        """ Yields all operations (including virtual operations) starting from ``start``.

            :param int start: Starting block
            :param int stop: Stop at this block
            :param str mode: We here have the choice between
                 * "head": the last block
                 * "irreversible": the block that is confirmed by 2/3 of all block producers and is thus irreversible!
            :param bool only_virtual_ops: Only yield virtual operations

            This call returns a list with elements that look like
            this and carries only one operation each:::

                {'block': 8411453,
                 'op': ['vote',
                        {'author': 'dana-edwards',
                         'permlink': 'church-encoding-numbers-defined-as-functions',
                         'voter': 'juanmiguelsalas',
                         'weight': 6000}],
                 'op_in_trx': 0,
                 'timestamp': '2017-01-12T12:26:03',
                 'trx_id': 'e897886e8b7560f37da31eb1a42177c6f236c985',
                 'trx_in_block': 1,
                 'virtual_op': 0}

        """

        # Let's find out how often blocks are generated!
        block_interval = self.config().get("STEEMIT_BLOCK_INTERVAL")

        if not start:
            start = self.get_current_block_num()

        # We are going to loop indefinitely
        while True:

            # Get chain properies to identify the
            head_block = self.get_current_block_num()

            # Blocks from start until head block
            for blocknum in range(start, head_block + 1):
                # Get full block
                yield from self.steem.rpc.get_ops_in_block(blocknum, only_virtual_ops)

            # Set new start
            start = head_block + 1

            if stop and start > stop:
                break

            # Sleep for one block
            time.sleep(block_interval)

    def stream(self, opNames=None, *args, **kwargs):
        """ Yield specific operations (e.g. comments) only

            :param array opNames: List of operations to filter for, e.g.
                vote, comment, transfer, transfer_to_vesting,
                withdraw_vesting, limit_order_create, limit_order_cancel,
                feed_publish, convert, account_create, account_update,
                witness_update, account_witness_vote, account_witness_proxy,
                pow, custom, report_over_production, fill_convert_request,
                comment_reward, curate_reward, liquidity_reward, interest,
                fill_vesting_withdraw, fill_order,
            :param int start: Start at this block
            :param int stop: Stop at this block
            :param str mode: We here have the choice between
                 * "head": the last block
                 * "irreversible": the block that is confirmed by 2/3 of all block producers and is thus irreversible!
        """
        if isinstance(opNames, str):
            opNames = [opNames]
        kwargs["only_virtual_ops"] = not bool(set(opNames).difference(virtual_operations))
        for op in self.ops(*args, **kwargs):
            if not opNames or op["op"][0] in opNames:
                yield {
                    **op["op"][1],
                    "type": op["op"][0],
                    "timestamp": op.get("timestamp"),
                    "block_num": op.get("block_num")
                }

    def replay(self, start_block=1, end_block=None, filter_by=list(), **kwargs):
        """ Same as ``stream`` with different prototyp
        """
        return self.stream(
            opNames=filter_by,
            start=start_block,
            stop=end_block,
            mode=self.mode,
            **kwargs
        )

    def block_time(self, block_num):
        """ Returns a datetime of the block with the given block
            number.

            :param int block_num: Block number
        """
        return Block(block_num).time()

    def block_timestamp(self, block_num):
        """ Returns the timestamp of the block with the given block
            number.

            :param int block_num: Block number
        """
        return int(Block(block_num).time().timestamp())

    def get_block_from_time(self, timestring, error_margin=10):
        """ Estimate block number from given time

            :param str timestring: String representing time
            :param int error_margin: Estimate block number within this interval (in seconds)

        """
        known_block = self.get_current_block()
        known_block_timestamp = self.block_timestamp(known_block)
        timestring_timestamp = parse_time(timestring).timestamp()
        delta = known_block_timestamp - timestring_timestamp
        block_delta = delta / 3
        guess_block = known_block - block_delta
        guess_block_timestamp = self.block_timestamp(guess_block)
        error = timestring_timestamp - guess_block_timestamp
        while abs(error) > error_margin:
            guess_block += error / 3
            guess_block_timestamp = self.block_timestamp(guess_block)
            error = timestring_timestamp - guess_block_timestamp
        return int(guess_block)

    def get_all_accounts(self, start='', stop='', steps=1e6, **kwargs):
        """ Yields account names between start and stop.

            :param str start: Start at this account name
            :param str stop: Stop at this account name
            :param int steps: Obtain ``steps`` names with a single call from RPC
        """
        lastname = start
        while True:
            names = self.steem.rpc.lookup_accounts(lastname, steps)
            for name in names:
                yield name
                if name == stop:
                    break
            if lastname == names[-1]:
                break
            lastname = names[-1]
            if len(names) < steps:
                break
