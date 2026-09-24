// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

/// @title CertificateRegistry
/// @notice Stores tamper-evident fingerprints of academic certificates.
/// @dev No personally identifiable data is stored on-chain.

contract CertificateRegistry {
    struct Certificate {
        bytes32 studentRef;
        string ipfsCid;
        address issuer;
        uint64 issuedAt;
        uint64 revokedAt;
        uint8 aiRiskScore;
    }

    address public admin;

    mapping(address => bool) public isInstitution;
    mapping(address => string) public institutionName;

    // docHash => certificate record
    mapping(bytes32 => Certificate) private _certs;

    event InstitutionRegistered(
        address indexed inst,
        string name
    );

    event InstitutionRevoked(
        address indexed inst
    );

    event CertificateIssued(
        bytes32 indexed docHash,
        address indexed issuer,
        bytes32 studentRef
    );

    event CertificateRevoked(
        bytes32 indexed docHash,
        string reason
    );

    error NotAdmin();
    error NotInstitution();
    error AlreadyIssued();
    error UnknownCertificate();
    error AlreadyRevoked();

    modifier onlyAdmin() {
        if (msg.sender != admin) revert NotAdmin();
        _;
    }

    modifier onlyInstitution() {
        if (!isInstitution[msg.sender]) revert NotInstitution();
        _;
    }

    constructor() {
        admin = msg.sender;
    }

    // ---------- Governance ----------

    function registerInstitution(
        address inst,
        string calldata name
    ) external onlyAdmin {
        isInstitution[inst] = true;
        institutionName[inst] = name;

        emit InstitutionRegistered(inst, name);
    }

    function revokeInstitution(
        address inst
    ) external onlyAdmin {
        isInstitution[inst] = false;

        emit InstitutionRevoked(inst);
    }

    // ---------- Issuance ----------

    function issueCertificate(
        bytes32 docHash,
        bytes32 studentRef,
        string calldata ipfsCid,
        uint8 aiRiskScore
    ) public onlyInstitution {
        
        if (_certs[docHash].issuedAt != 0) {
            revert AlreadyIssued();
        }

        _certs[docHash] = Certificate({
            studentRef: studentRef,
            ipfsCid: ipfsCid,
            issuer: msg.sender,
            issuedAt: uint64(block.timestamp),
            revokedAt: 0,
            aiRiskScore: aiRiskScore
        });

        emit CertificateIssued(
            docHash,
            msg.sender,
            studentRef
        );
    }

    /// @notice Gas-efficient batch issuance
    function issueBatch(
        bytes32[] calldata docHashes,
        bytes32[] calldata studentRefs,
        string[] calldata cids,
        uint8[] calldata risks
    ) external onlyInstitution {
        
        uint256 n = docHashes.length;

        require(
            studentRefs.length == n &&
            cids.length == n &&
            risks.length == n,
            "length mismatch"
        );

        for (uint256 i; i < n; ++i) {
            issueCertificate(
                docHashes[i],
                studentRefs[i],
                cids[i],
                risks[i]
            );
        }
    }

    function revokeCertificate(
        bytes32 docHash,
        string calldata reason
    ) external {
        
        Certificate storage c = _certs[docHash];

        if (c.issuedAt == 0) {
            revert UnknownCertificate();
        }

        if (c.issuer != msg.sender && msg.sender != admin) {
            revert NotInstitution();
        }

        if (c.revokedAt != 0) {
            revert AlreadyRevoked();
        }

        c.revokedAt = uint64(block.timestamp);

        emit CertificateRevoked(
            docHash,
            reason
        );
    }

    // ---------- Verification ----------

    function verify(
        bytes32 docHash
    )
        external
        view
        returns (
            bool exists,
            bool valid,
            address issuer,
            string memory issuerName,
            uint64 issuedAt,
            uint64 revokedAt,
            string memory ipfsCid,
            uint8 aiRiskScore
        )
    {
        Certificate memory c = _certs[docHash];

        exists = c.issuedAt != 0;

        valid =
            exists &&
            c.revokedAt == 0 &&
            isInstitution[c.issuer];

        return (
            exists,
            valid,
            c.issuer,
            institutionName[c.issuer],
            c.issuedAt,
            c.revokedAt,
            c.ipfsCid,
            c.aiRiskScore
        );
    }
}