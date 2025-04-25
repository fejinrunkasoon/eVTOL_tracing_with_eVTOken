// SPDX-License-Identifier: CC-BY-NC-ND-4.0
pragma solidity ^0.8.18;

import "./SimpleApprover.sol";


contract AirspaceAuth is Approvable {

    struct AirspaceApplication {
        // 基础信息
        string reqNo;               // 外部申请流水号
        uint8 applicantType;  
        ZKProof proof_applicant_type;      // 申请者类型 (1: 组织机构, 2: 个人)
    
        UAS[] uasInfo;
        ZKProof[] proof_uas;

        // 申请主体
        Subject applicant;          // 组织机构或个人信息
        ZKProof proof_applicant;

        // 操作人员
        Person[] operators;         // 操作人列表
        ZKProof[] proof_operators;

        // 空域信息
        Airspace[] airspaces;       // 申请空域列表
        ZKProof[] proof_airspaces;

        // 文件资料
        File[] files;               // 相关文件
    
        // 任务信息
        uint32 missionType;         // 飞行任务性质 (1-33 对应不同任务类型)
        ZKProof proof_mission_type;       
        string emergencyProc;  // 应急处置程序
    
        // 空域类型
        uint8 spaceReqType;         // 空域类型 (3: 隔离空域, 4: 非隔离空域)
        ZKProof proof_space_req_type;

           // 时间信息
        TimeSlice[] flightTimes;
        ZKProof[] proof_flight_times;

        // 设备信息
        uint8 operationMode ;        // 操控模式 (1: 遥控, 2: 自主)
        ZKProof proof_operation_mode;
        uint8 flightMode ;     // 飞行模式 (0: 视距外, 1: 视距内)
        ZKProof proof_flight_mode;

        // 元数据
        string sourceSystem;        // 来源系统名称
        string memo;                // 备注

        bool approved;
    }

    // 嵌套结构体定义
    struct Subject {
        bool isOrganization;       // true: 组织机构, false: 个人
        Organization orgData;       // 组织机构信息
        Person personData;         // 个人信息
    }

    struct Organization {
        string name;               // 机构名称
        string unifiedSocialCode;  // 统一社会信用代码
    }

    struct Person {
        string name;               // 姓名
        uint8 idType;              // 证件类型 (1: 身份证, 2: 护照等)
        string encryptedIdNumber;  // 加密证件号
        string phone;              // 联系电话
    }

    struct Airspace {
        string code;               // 空域代号
        uint8 airspaceType;        // 空域类型 (1-13 对应标准定义)
        uint8 shapeType;           // 空域形状 (0: 网格, 1: 多边形等)
        uint24 minAltitude;        // 底高 (米)
        uint24 maxAltitude;        // 顶高 (米)
        string coordinates;        // 坐标数据 (Geohash/坐标串)
    }

    struct File {
        string name;               // 文件名称
        string fileType;           // 文件扩展名
        uint256 size;              // 文件大小 (字节)
        string md5Hash;            // 文件MD5
        string url;                // 文件存储地址
    }

    struct TimeSlice {
        uint64 startTime;          // UTC时间戳 (秒)
        uint64 endTime;            // UTC时间戳 (秒)
    }

    struct UAS {
        string manufacturerId;     // 制造商社会信用代码
        string model;              // 产品型号
        string serialNumber;       // 产品序列号
        string registrationNumber; // 实名登记号
    }
  

    // AirspaceAuth中的ZKProof结构
    struct ZKProof { 
        uint256[2] a;    // G1Point.X/Y
        uint256[2][2] b; // G2Point.X[0]/X[1], Y[0]/Y[1]
        uint256[2] c;    // G1Point.X/Y
        uint256[2] input;
    }

    event NewFlightRequest(
        uint createdAt,
        string reqNo,  // 对应原serial_number
        uint8 operationMode,        // 原op_mode
        uint8 applicantType,        // 新增申请类型
        bool isIsolated,            // 对应原flight_cat
        uint32 missionType,         // 新增任务类型
        uint8 connectMethod,        // 对应原ex_connect_meth
        uint256 endurance,
        string emergencyProc,
        uint256 indexed operatorCount, // 操作员数量
        bool indexed approved
    );

    event NewPrivateFlightRequest(
        uint createdAt,
        uint8 operationMode,
        uint8 applicantType,
        bool isIsolated,
        bool indexed approved
    );

    constructor() Approvable(msg.sender, "Owner") {}

    // 内部处理核心逻辑
    function _processApplication(
        AirspaceApplication memory app,
        string memory emergencyProc
    ) internal {
        app.approved = false;

        if (_validateApplication(app)) {
            app.approved = true;
        }

        if (app.applicantType == 2) { // 个人申请触发私有事件
            emit NewPrivateFlightRequest(
                block.timestamp,
                app.operationMode,
                app.applicantType,
                app.spaceReqType == 3, // 3表示隔离空域
                app.approved
            );
        } else { // 机构申请触发完整事件
            emit NewFlightRequest(
                block.timestamp,
                app.reqNo,
                app.operationMode,
                app.applicantType,
                app.spaceReqType == 3,
                app.missionType,
                _getConnectMethodCode(app), // 连接方式编码
                _calculateEndurance(app),   // 计算总续航
                emergencyProc,
                app.operators.length,      // 操作员数量
                app.approved
            );
        }
        
    }

    // 公开接口
    function submitApplication (
        AirspaceApplication memory app,
        string calldata emergencyProc
    ) public {
        _processApplication(app, emergencyProc);
    }

    // 验证逻辑
    function _validateApplication(
        AirspaceApplication memory app
    ) internal pure returns (bool) {
        bool baseVerification = _verifyZKProof(
            app.proof_applicant_type,
            abi.encodePacked(app.applicantType)
        ) && _verifyZKProof(
            app.proof_space_req_type,
            abi.encodePacked(app.spaceReqType)
        );

        // 根据申请类型增加验证
        if (app.applicantType == 1) { // 机构验证
            return baseVerification &&
                _verifyZKProof(
                    app.proof_applicant,
                    abi.encode(app.applicant.orgData)
                );
        } else { // 个人验证
            return baseVerification &&
                _verifyZKProof(
                    app.proof_applicant,
                    abi.encode(app.applicant.personData)
                ) &&
                _verifyZKProof(
                    app.proof_mission_type,
                    abi.encodePacked(app.missionType)
                );
        }
    }

    // ZK验证适配层
    function _verifyZKProof(
        ZKProof memory proof,
        bytes memory inputs
    ) private pure returns (bool) {
        // 保持原有验证结构
        return verifyProof(
            proof.a,
            proof.b,
            proof.c,
            inputs
        );
    }

    // 辅助函数（需实现具体逻辑）
    function _getConnectMethodCode(
        AirspaceApplication memory app
    ) private pure returns (uint8) {
        // 根据设备信息生成连接方式编码
        return app.operationMode == 1 ? 1 : 2; 
    }

    function _calculateEndurance(
        AirspaceApplication memory app
    ) private pure returns (uint256) {
        // 计算总续航时间（示例逻辑）
        uint256 total;
        for (uint i=0; i<app.flightTimes.length; i++) {
            total += app.flightTimes[i].endTime - app.flightTimes[i].startTime;
        }
        return total;
    }

    // 验证函数占位符
    function verifyProof(
        uint256[2] memory,
        uint256[2][2] memory,
        uint256[2] memory,
        bytes memory
    ) public pure returns (bool) {
        return true; // 实际应调用zk验证器
    }
}

//组织类型验证
    field[3] hash = keccak[unifiedSocialCode];
    field computedHash = hash[0] * (2**128) + hash[1];

    assert(computedHash == registeredHash);
 private field unifiedSocialCode,
  field registeredHash
  
  ["REQ-20231001-001",1, [ // UAS[] uasInfo (动态数组)
    [ // UAS 1
      "MANUFACTURER-001",  // manufacturerId
      "DJI-M300",          // model
      "SN-12345678",       // serialNumber
      "REG-CN-2023-001"    // registrationNumber
    ],
    [ // UAS 2
      "MANUFACTURER-002",
      "AUTEL-EVO2",
      "SN-87654321",
      "REG-CN-2023-002"
    ]
  ], 
  


  // ========== UAS信息 ==========
  [ // UAS[] uasInfo (动态数组)
    [ // UAS 1
      "MANUFACTURER-001",  // manufacturerId
      "DJI-M300",          // model
      "SN-12345678",       // serialNumber
      "REG-CN-2023-001"    // registrationNumber
    ],
    [ // UAS 2
      "MANUFACTURER-002",
      "AUTEL-EVO2",
      "SN-87654321",
      "REG-CN-2023-002"
    ]
  ],
  
  [ // ZKProof[] proof_uas
    [ /* 每个proof结构同proof_applicant_type */ ],
    [ /* 第二个proof */ ]
  ],

  // ========== 申请主体 ==========
  [ // Subject applicant
    true,  // isOrganization
    
    [ // Organization orgData (当isOrganization=true时)
      "大疆创新科技有限公司",
      "91440300MA5DKM1234"  // unifiedSocialCode
    ],
    
    []  // personData留空
  ],
  
  [ // ZKProof proof_applicant
    /* 结构同上 */
  ],

  // ========== 操作人员 ==========
  [ // Person[] operators
    [
      "张三",
      1,  // idType (1-身份证)
      "0xENCRYPTED_310123...",  // encryptedIdNumber
      "+86-13800138000"
    ],
    [
      "李四",
      2,  // idType (2-护照)
      "0xENCRYPTED_PASSPORT...",
      "+86-13912345678"
    ]
  ],
  
  [ // ZKProof[] proof_operators
    [ /* proof1 */ ],
    [ /* proof2 */ ]
  ],

  // ========== 空域信息 ==========
  [ // Airspace[] airspaces
    [
      "AS-ZS-001",   // code
      3,             // airspaceType (3类空域)
      1,             // shapeType (1-多边形)
      100,           // minAltitude (米)
      500,           // maxAltitude (米)
      "GEOHASH-1234" // coordinates
    ]
  ],
  
  [ // ZKProof[] proof_airspaces
    [ /* proof */ ]
  ],

  // ========== 文件资料 ==========
  [ // File[] files
    [
      "flight-plan.pdf",
      "pdf",
      "2048",       // size (bytes)
      "e4d909c290...", // md5Hash
      "ipfs://Qm..."
    ]
  ],

  // ========== 任务信息 ==========
  5,  // missionType (5-测绘任务)
  
  [ // ZKProof proof_mission_type
    /* 结构同上 */
  ],
  
  "紧急迫降程序说明",  // emergencyProc

  // ========== 空域类型 ==========
  3,  // spaceReqType (3-隔离空域)
  
  [ // ZKProof proof_space_req_type
    /* 结构同上 */
  ],

  // ========== 时间信息 ==========
  [ // TimeSlice[] flightTimes
    [
      1696147200,  // startTime (2023-10-01 00:00 UTC)
      1696233600   // endTime (2023-10-02 00:00 UTC)
    ]
  ],
  
  [ // ZKProof[] proof_flight_times
    [ /* proof */ ]
  ],

  // ========== 设备信息 ==========
  1,  // operationMode (1-遥控)
  
  [ // ZKProof proof_operation_mode
    /* 结构同上 */
  ],
  
  0,  // flightMode (0-视距外)
  
  [ // ZKProof proof_flight_mode
    /* 结构同上 */
  ],
  "UAS-Management-System",  
  "测试申请数据",            
  false  
]
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  [["0x1b0aefb0b64ced52fdeaeb46ac6805d0fd148bb7a99f0d6c667704887dfb283d","0x0eb821a36c8b4bbe282d47b7740b69292c8d2e583513d53345e535079b231daa"],[["0x057b3888e358d96f00d631861ec1e8454ff8ac1dcf9dc4b76b14fe7abb802d05","0x125b657d9fba89a60e8342b74d1ee9b7fc3c234fc23ee6aaa3750ddc7d8d19f0"],["0x25290f5252765521626c9e3334496dd1f8d4462c61c803b533470a4f5738f779","0x0f0bdb9b0c34efbb1e6c6d1d0c8414278729d61dc657d856a082f0aa1abe1ea4"]],["0x2e3af922d78c2f4cedf7d8f6f21c055969d7bbced88b6bbe532c3837e11bf5fb","0x2eeab6d8f4b1e1a45f9988a533d2636dd941c62697639124e21a03764dfa40fd"]],["0x0000000000000000000000000000000000000000000000000000000000000003","0x0000000000000000000000000000000000000000000000000000000000000001","0x0000000000000000000000000000000000000000000000000000000000000001"]