// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract InsuranceEngine is Ownable {
    IERC20 public token;

    struct InsurancePolicy {
        uint256 id;
        uint256 price;
        mapping(address => bool) insured;
    }

    mapping(uint256 => InsurancePolicy) public policies;
    uint256 public policyCount;

    event InsurancePurchased(address indexed user, uint256 policyId);
    event InsurancePriceUpdated(uint256 policyId, uint256 newPrice);
    event InsurancePolicyAdded(uint256 policyId, uint256 price);


    constructor(IERC20 _token) Ownable(msg.sender) {
        token = _token;
    }

    function addInsurancePolicy(uint256 _price) external onlyOwner {
        policyCount++;
        InsurancePolicy storage policy = policies[policyCount];
        policy.id = policyCount;
        policy.price = _price;
        emit InsurancePolicyAdded(policyCount, _price);
    }

    function purchaseInsurance(uint256 _policyId) external {
        require(_policyId > 0 && _policyId <= policyCount, "Invalid policy ID");
        require(!policies[_policyId].insured[msg.sender], "Already insured for this policy");
        require(token.transferFrom(msg.sender, address(this), policies[_policyId].price), "Token transfer failed");

        policies[_policyId].insured[msg.sender] = true;
        emit InsurancePurchased(msg.sender, _policyId);
    }

    function updateInsurancePrice(uint256 _policyId, uint256 _newPrice) external onlyOwner {
        require(_policyId > 0 && _policyId <= policyCount, "Invalid policy ID");
        policies[_policyId].price = _newPrice;
        emit InsurancePriceUpdated(_policyId, _newPrice);
    }

    function getInsurancePolicies() external view returns (uint256[] memory, uint256[] memory) {
        uint256[] memory ids = new uint256[](policyCount);
        uint256[] memory prices = new uint256[](policyCount);

        for (uint256 i = 1; i <= policyCount; i++) {
            ids[i - 1] = policies[i].id;
            prices[i - 1] = policies[i].price;
        }

        return (ids, prices);
    }

    function isInsured(address _user, uint256 _policyId) external view returns (bool) {
        require(_policyId > 0 && _policyId <= policyCount, "Invalid policy ID");
        return policies[_policyId].insured[_user];
    }
}
