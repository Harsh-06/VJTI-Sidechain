from dataclasses import replace
from core import Block, BlockHeader, Chain
from vjti_chain_relayer import VJTIChainRelayer
import utils.constants as consts

class ChainSupport:
    def __init__(self, relayer: VJTIChainRelayer) -> None:
        self.relayer = relayer

    def block_header_exists(self, block_header: BlockHeader) -> bool:
        return self.relayer.exists(block_header)

    def chain_is_ok(self, chain: Chain) -> bool:
        header_list = chain.header_list
        for header in reversed(header_list):
            if ChainSupport._should_exist(header):
                return self.block_header_exists(header)
        return False

    def new_block(self, block: Block) -> bool:
        if ChainSupport._should_exist(block.header):
            self._write_to_main_chain(block)

    @staticmethod
    def _should_exist(block_header: BlockHeader) -> bool:
        return block_header.height % consts.SIDE_CHAIN_TO_MAIN_CHAIN_RATIO == 0
    
    def _write_to_main_chain(self, block: Block) -> None:
        return self.relayer.write(block.header)
