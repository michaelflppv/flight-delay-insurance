<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

</head>
<body>

<h1>Block Flight Smart Contracts</h1>

<h2>Introduction</h2>
<p>Block Flight is a decentralized application (DApp) designed to manage and facilitate the purchase of flight insurance policies using a custom ERC20 token called FIT. This document provides a detailed explanation of the smart contracts deployed on the Ethereum blockchain.</p>

<h2>FIT Token Contract</h2>
<p>The FIT token is an ERC20 token used within the Block Flight ecosystem. It serves as the currency for purchasing insurance policies.</p>

<pre>
<code>
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract MyToken is ERC20 {
    constructor(uint256 initialSupply) ERC20("FlightInsuranceToken", "FIT") {
        _mint(msg.sender, initialSupply);
    }
}
</code>
</pre>

<h3>Contract Details</h3>
<ul>
    <li><strong>Type:</strong> ERC20 Token</li>
    <li><strong>Token Name:</strong> FlightInsuranceToken (FIT)</li>
    <li><strong>Token Address:</strong> <code>0xb800B43C4C2fA585eD6c57C0b221a7B2E32489B8</code></li>
    <li><strong>Supply:</strong> The initial supply is set during deployment</li>
    <li><strong>Supply Policy:</strong> Fixed supply, minted once to deployer</li>
    <li><strong>Pricing:</strong> Determined by market dynamics</li>
    <li><strong>Design Choices:</strong> Uses OpenZeppelin’s ERC20 implementation for security and compliance</li>
</ul>

<h2>Insurance Engine Contract</h2>
<p>The InsuranceEngine contract manages insurance policies and facilitates their purchase using FIT tokens. It leverages the ERC20 token standard for transactions.</p>

<pre>
<code>
  
    function addInsurancePolicy(uint256 _price) external onlyOwner 
  
    function purchaseInsurance(uint256 _policyId) external 

    function updateInsurancePrice(uint256 _policyId, uint256 _newPrice)

    function getInsurancePolicies() external view returns (uint256[] memory, uint256[] memory) 

    function isInsured(address _user, uint256 _policyId) external view returns (bool) 

    function withdrawTokens(uint256 _amount) external onlyOwner 
          
</code>
</pre>

<h3>Contract Details</h3>
<ul>
    <li><strong>Token Integration:</strong> Initialized with an ERC20 token interface (IERC20), facilitating transactions using FIT tokens.</li>
    <li><strong>Policy Management:</strong> Policies are structured entities with unique IDs and prices. Managed using mappings for efficiency and scalability.</li>
    <li><strong>Owner Privileges:</strong> The contract employs the Ownable pattern. The owner can add new insurance policies and update existing policy prices.</li>
    <li><strong>Insurance Purchase Process:</strong> Users can purchase insurance by invoking the <code>purchaseInsurance</code> function, which verifies policy validity, checks existing coverage, and facilitates token transfer.</li>
    <li><strong>Transparency and Accessibility:</strong> The <code>getInsurancePolicies</code> function allows querying available policies and their prices. The <code>isInsured</code> function enables users to verify their insurance status.</li>
    <li><strong>Events:</strong> Emits events such as <code>InsurancePurchased</code>, <code>InsurancePriceUpdated</code>, and <code>InsurancePolicyAdded</code> to log contract interactions.</li>
</ul>

<h2>Beta Version Deployment</h2>
<p>The beta version of the InsuranceEngine contract is deployed on the Sepolia ERC network at the following address: <code>0x7F0b6c053DeF457ebbaCcBed66d688d5636C67ae</code>. This deployment enables users to explore and utilize decentralized insurance solutions powered by Ethereum and FIT tokens.</p>

</body>
</html>
