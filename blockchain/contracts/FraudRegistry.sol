// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract FraudRegistry {
    struct FraudReport {
        string vpa;
        bytes32 urlHash;
        uint256 reporterCount;
        uint256 firstReported;
        uint256 lastReported;
    }

    mapping(string => FraudReport) public fraudVPAs;
    mapping(bytes32 => FraudReport) public fraudURLs;
    mapping(address => mapping(string => bool)) public hasReported;

    event FraudReported(string indexed identifier, string fraudType, uint256 reportCount, address reporter);

    // simple helper to check for '@'
    function containsAtSymbol(string memory _str) private pure returns (bool) {
        bytes memory strBytes = bytes(_str);
        for(uint i = 0; i < strBytes.length; i++) {
            if (strBytes[i] == '@') {
                return true;
            }
        }
        return false;
    }

    function reportFraudVPA(string memory vpa) public {
        require(containsAtSymbol(vpa), "Invalid VPA format: Must contain '@'");
        require(!hasReported[msg.sender][vpa], "Address has already reported this VPA");

        hasReported[msg.sender][vpa] = true;

        FraudReport storage report = fraudVPAs[vpa];
        
        if (report.reporterCount == 0) {
            report.vpa = vpa;
            report.firstReported = block.timestamp;
        }

        report.reporterCount += 1;
        report.lastReported = block.timestamp;

        emit FraudReported(vpa, "VPA", report.reporterCount, msg.sender);
    }

    function reportFraudURL(string memory url) public {
        bytes32 urlHash = keccak256(abi.encodePacked(url));
        // Use string conversion of url hash for mapping check
        string memory hashStr = string(abi.encodePacked(urlHash));
        
        require(!hasReported[msg.sender][hashStr], "Address has already reported this URL");

        hasReported[msg.sender][hashStr] = true;

        FraudReport storage report = fraudURLs[urlHash];
        
        if (report.reporterCount == 0) {
            report.urlHash = urlHash;
            report.firstReported = block.timestamp;
        }

        report.reporterCount += 1;
        report.lastReported = block.timestamp;

        emit FraudReported(url, "URL", report.reporterCount, msg.sender);
    }

    function getFraudScore(string memory vpa) public view returns (uint256) {
        return fraudVPAs[vpa].reporterCount;
    }

    function isHighRisk(string memory vpa) public view returns (bool) {
        return fraudVPAs[vpa].reporterCount >= 3;
    }
}
