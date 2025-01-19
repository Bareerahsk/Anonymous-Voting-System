// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract AnonymousVoting {
    address public owner;

    struct Candidate {
        string name;
        uint256 voteCount;
    }

    Candidate[] public candidates;
    mapping(bytes32 => bool) public usedSignatures;
    mapping(address => bool) public hasVoted;
    uint256 public totalVotes;

    event CandidateAdded(string name);
    event VoteCast(uint256 candidateIndex);

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can add candidates");
        _;
    }

    function addCandidate(string memory _name) public onlyOwner {
        candidates.push(Candidate(_name, 0));
        emit CandidateAdded(_name);
    }

    function vote(uint256 _candidateIndex, bytes32 _signature) public {
        require(_candidateIndex < candidates.length, "Invalid candidate index");
        require(!usedSignatures[_signature], "Signature already used");
        require(!hasVoted[msg.sender], "You have already voted");

        usedSignatures[_signature] = true;
        hasVoted[msg.sender] = true;
        candidates[_candidateIndex].voteCount++;
        totalVotes++;

        emit VoteCast(_candidateIndex);
    }

    function getCandidateCount() public view returns (uint256) {
        return candidates.length;
    }

    function getCandidate(uint256 _index) public view returns (string memory, uint256) {
        require(_index < candidates.length, "Invalid candidate index");
        return (candidates[_index].name, candidates[_index].voteCount);
    }
}