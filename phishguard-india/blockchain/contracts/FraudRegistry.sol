// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract FraudRegistry {
    mapping(string => bool) private flagged;

    event VpaFlagged(string vpa, address reporter);

    function flagVpa(string calldata vpa) external {
        flagged[vpa] = true;
        emit VpaFlagged(vpa, msg.sender);
    }

    function isFlagged(string calldata vpa) external view returns (bool) {
        return flagged[vpa];
    }
}
