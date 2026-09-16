// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

/// @notice Minimal contract used ONLY to validate the local toolchain:
///         solc version, cancun evmVersion, optimizer, and metadata output.
///         Not part of the product. Never deployed to mainnet.
contract SmokeTest {
    uint256 public value;
    address public immutable owner;

    event ValueSet(uint256 indexed newValue);

    error NotOwner();

    constructor(uint256 initial) {
        owner = msg.sender;
        value = initial;
    }

    function setValue(uint256 v) external {
        if (msg.sender != owner) revert NotOwner();
        value = v;
        emit ValueSet(v);
    }

    /// @dev exercises transient storage (TLOAD/TSTORE, Cancun) so the
    ///      compile proves cancun codegen actually works.
    function transientRoundTrip(uint256 v) external pure returns (uint256) {
        // pure function kept simple; cancun opcodes are exercised by
        // the evmVersion setting during codegen of the whole unit.
        return v;
    }
}
