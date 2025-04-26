//SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "../lib/openzeppelin-contracts/contracts/utils/Counters.sol";
import "../lib/openzeppelin-contracts/contracts/token/ERC721/ERC721.sol";
import "../lib/openzeppelin-contracts/contracts/access/Ownable.sol";

contract EncryptedDroneNFT is ERC721, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    struct DroneRecord {
        string ipfsCID;
        uint256 timestamp;
    }

    mapping(address => bool) private _approvedManufacturers;
    mapping(address => bool) public viewWhitelist;
    mapping(address => bool) public viewBlacklist;

    mapping(uint256 => string) private _tokenURIs; 
    string private customBaseURI;

    mapping(uint256 => DroneRecord) private _droneData;

    event AccessCheck(
        address indexed caller,
        uint256 indexed tokenId,
        bool isContractOwner,
        bool isNFTHolder,
        bool isWhitelisted,
        bool isBlacklisted
    );
    event DroneMinted(uint indexed tokenId, address indexed owner, string tokenURI);
    event ManufacturerUpdated(address indexed manufacturer, bool status);
    event ViewListUpdated(address indexed target, bool whitelisted, bool blacklisted);

    constructor(string memory baseURI) ERC721("DroneFlightData", "DFD") {
        _transferOwnership(msg.sender);
        _approvedManufacturers[msg.sender] = true;
        viewWhitelist[msg.sender] = true; 
        customBaseURI = baseURI;
    }

    function mintDroneNFT(
        string memory ipfsCID,
        uint256 timestamp
    ) public returns (uint256) {
        require(
            _isApprovedManufacturer(msg.sender),
            "Access denied: Only approved manufacturers or Owner"
        );
        require(bytes(ipfsCID).length <= 1024, "Data too large");

        _tokenIds.increment();
        uint256 newTokenId = _tokenIds.current();
        
        _mint(msg.sender, newTokenId);

        _tokenURIs[newTokenId] = string(abi.encodePacked(customBaseURI, ipfsCID));
        _droneData[newTokenId] = DroneRecord(
            ipfsCID,
            timestamp
        );

        emit DroneMinted(newTokenId, msg.sender, _tokenURIs[newTokenId]);

        return newTokenId;
    }

    function getDroneRecord(uint256 tokenId) public view returns (
        string memory ipfsCID,
        uint256 timestamp
    ) {
        require(_exists(tokenId), "Token does not exist");
        address caller = _msgSender();
        bool isNFTHolder = (ownerOf(tokenId) == caller);
        bool isWhitelisted = viewWhitelist[caller];
        bool isBlacklisted = viewBlacklist[caller];

        require(
            caller == owner() || 
            isNFTHolder || 
            (isWhitelisted && !isBlacklisted),
            "Access denied"
        );

        return (_droneData[tokenId].ipfsCID, _droneData[tokenId].timestamp);
    }

    function addManufacturer(address manufacturer) public onlyOwner {
        _approvedManufacturers[manufacturer] = true;
        emit ManufacturerUpdated(manufacturer, true);
    }

    function removeManufacturer(address _manufacturer) public onlyOwner {
    
        _approvedManufacturers[_manufacturer] = false;
        emit ManufacturerUpdated(_manufacturer, false);
    }

    function updateViewList(
        address target,
        bool whitelistStatus,
        bool blacklistStatus
    ) public onlyOwner {
        viewWhitelist[target] = whitelistStatus;
        viewBlacklist[target] = blacklistStatus;
        emit ViewListUpdated(target, whitelistStatus, blacklistStatus);
    }

    function _isApprovedManufacturer(address account) internal view returns (bool) {
        return account == owner() || _approvedManufacturers[account];
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_exists(tokenId), "ERC721: URI query for nonexistent token");
        return _tokenURIs[tokenId]; 
    }

    function setBaseURI(string memory newBaseURI) public onlyOwner {
        customBaseURI= newBaseURI;
    }
}