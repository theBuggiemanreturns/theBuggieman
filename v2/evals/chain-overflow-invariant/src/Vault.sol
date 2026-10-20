// SPDX-License-Identifier: MIT
// DELIBERATELY VULNERABLE — eval target only. Do not deploy.
pragma solidity ^0.8.0;

contract Vault {
    uint64 public constant CAP = type(uint64).max; // supply cap guard target
    mapping(address => uint256) public balances;
    address[] public holders;

    // P-A: aggregates into uint256 but mints on a uint64 cast of the aggregate.
    function batchCredit(address[] calldata who, uint256[] calldata amounts) external {
        require(who.length == amounts.length, "len");
        uint256 total;
        for (uint256 i; i < amounts.length; ++i) {
            // each holder credited its FULL amount
            if (balances[who[i]] == 0) holders.push(who[i]);
            balances[who[i]] += amounts[i];
            unchecked { total += amounts[i]; }
        }
        // aggregate cast to uint64 — wraps if total > 2^64
        uint64 minted = uint64(total);
        require(supplyInvariant(), "supply");
        emit Credited(minted);
    }

    // P-B: guard accumulates balances into a uint64 — wraps on the same 2^64.
    function supplyInvariant() public view returns (bool) {
        uint64 acc;
        for (uint256 i; i < holders.length; ++i) {
            unchecked { acc += uint64(balances[holders[i]]); }
        }
        return acc <= CAP;
    }

    function sumOfBalances() external view returns (uint256 s) {
        for (uint256 i; i < holders.length; ++i) s += balances[holders[i]];
    }

    event Credited(uint64 minted);
}
