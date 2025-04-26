// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/eVTOken.sol";

contract EncryptedDroneNFTGasSnapshots is Test {
    EncryptedDroneNFT droneNFT;
    address owner = vm.addr(1);
    address manufacturer = vm.addr(2);
    address user = vm.addr(3);

    string constant BASE_URI ="ipfs://QmYourMetadata";
    string public MAX_CID;

    constructor() {
        bytes memory cidBytes = new bytes(1024);
        for (uint i=0; i < cidBytes.length; i++) {
            cidBytes[i] ='a';
        }

        MAX_CID =string(cidBytes);
    }

    function setUp() public {
        vm.startPrank(owner);
        droneNFT = new EncryptedDroneNFT(BASE_URI);
        droneNFT.addManufacturer(manufacturer);
        vm.stopPrank();
    }

    function test_1_ContractDeployment() public {
        vm.pauseGasMetering();
        EncryptedDroneNFT target;
        vm.resumeGasMetering();

        target = new EncryptedDroneNFT(BASE_URI);

        vm.pauseGasMetering();
        target;
        vm.resumeGasMetering();
    }

    function test_2_MintDroneNFT() public {
        vm.prank(manufacturer);
        droneNFT.mintDroneNFT("QmNdvFyhQBntkdjuNmv9Bd2ztDdyGWcNqZUjTVC28D2dmU", block.timestamp);    
    }

    function test_3_AddManufacturer() public{
        vm.prank(owner);
        droneNFT.addManufacturer(address(0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266));
        
    }

    function test_4_RemoveManufacturer() public{
        vm.prank(owner);
        droneNFT.removeManufacturer(manufacturer);

    }

    function test_5_UpdateViewList_Whitelist() public {
        vm.prank(owner);
        droneNFT.updateViewList(user, true, false);
    }

    function test_6_UpdateViewList_Blacklist() public {
        vm.prank(owner);
        droneNFT.updateViewList(user, false, true);
    }


    function test_7_SetBaseURI() public{
        vm.prank(owner);
        droneNFT.setBaseURI("ipfs://QmYourMetadataCID/");
    }

    function test_8_GetDroneRecord() public {
        vm.prank(manufacturer);
        droneNFT.mintDroneNFT("QmNdvFyhQBntkdjuNmv9Bd2ztDdyGWcNqZUjTVC28D2dmU", block.timestamp);

        vm.prank(owner);
        droneNFT.getDroneRecord(1);
    
        vm.prank(manufacturer);
        droneNFT.getDroneRecord(1);
    }


    function test_9_TokenURI_Access() public {
        vm.prank(manufacturer);
        droneNFT.mintDroneNFT("QmNdvFyhQBntkdjuNmv9Bd2ztDdyGWcNqZUjTVC28D2dmU", block.timestamp);
        droneNFT.tokenURI(1);
    }

    function test_10_MaxLengthCID() public {
        vm.prank(manufacturer);
        droneNFT.mintDroneNFT(MAX_CID, block.timestamp);
    }
}
