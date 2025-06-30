// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract BasicVoting {
    address public admin;
    uint256 public proposalCount;
    
    struct Proposal {
        uint256 id;
        string description;
        uint256 votesFor;
        uint256 votesAgainst;
        uint256 startTime;
        uint256 endTime;
        bool active;
        mapping(address => bool) hasVoted;
    }
    
    mapping(uint256 => Proposal) public proposals;
    
    event ProposalCreated(uint256 indexed proposalId, string description, uint256 endTime);
    event VoteCast(uint256 indexed proposalId, address indexed voter, bool support);
    event ProposalEnded(uint256 indexed proposalId, uint256 votesFor, uint256 votesAgainst);
    
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin can perform this action");
        _;
    }
    
    modifier validProposal(uint256 _proposalId) {
        require(_proposalId > 0 && _proposalId <= proposalCount, "Invalid proposal ID");
        _;
    }
    
    constructor() {
        admin = msg.sender;
    }
    
    function createProposal(string memory _description, uint256 _votingDurationInSeconds) 
        external 
        onlyAdmin 
    {
        require(bytes(_description).length > 0, "Description cannot be empty");
        require(_votingDurationInSeconds > 0, "Voting duration must be positive");
        
        proposalCount++;
        uint256 endTime = block.timestamp + _votingDurationInSeconds;
        
        Proposal storage newProposal = proposals[proposalCount];
        newProposal.id = proposalCount;
        newProposal.description = _description;
        newProposal.votesFor = 0;
        newProposal.votesAgainst = 0;
        newProposal.startTime = block.timestamp;
        newProposal.endTime = endTime;
        newProposal.active = true;
        
        emit ProposalCreated(proposalCount, _description, endTime);
    }
    
    function vote(uint256 _proposalId, bool _support) 
        external 
        validProposal(_proposalId) 
    {
        Proposal storage proposal = proposals[_proposalId];
        
        require(proposal.active, "Proposal is not active");
        require(block.timestamp <= proposal.endTime, "Voting period has ended");
        require(!proposal.hasVoted[msg.sender], "You have already voted on this proposal");
        
        proposal.hasVoted[msg.sender] = true;
        
        if (_support) {
            proposal.votesFor++;
        } else {
            proposal.votesAgainst++;
        }
        
        emit VoteCast(_proposalId, msg.sender, _support);
    }
    
    function endProposal(uint256 _proposalId) 
        external 
        onlyAdmin 
        validProposal(_proposalId) 
    {
        Proposal storage proposal = proposals[_proposalId];
        require(proposal.active, "Proposal is already ended");
        require(block.timestamp > proposal.endTime, "Voting period has not ended yet");
        
        proposal.active = false;
        emit ProposalEnded(_proposalId, proposal.votesFor, proposal.votesAgainst);
    }
    
    function getProposalInfo(uint256 _proposalId) 
        external 
        view 
        validProposal(_proposalId) 
        returns (
            string memory description,
            uint256 votesFor,
            uint256 votesAgainst,
            uint256 startTime,
            uint256 endTime,
            bool active
        ) 
    {
        Proposal storage proposal = proposals[_proposalId];
        return (
            proposal.description,
            proposal.votesFor,
            proposal.votesAgainst,
            proposal.startTime,
            proposal.endTime,
            proposal.active
        );
    }
    
    function hasVoted(uint256 _proposalId, address _voter) 
        external 
        view 
        validProposal(_proposalId) 
        returns (bool) 
    {
        return proposals[_proposalId].hasVoted[_voter];
    }
    
    function transferAdmin(address _newAdmin) external {
        require(_newAdmin != address(0), "New admin cannot be zero address");
        admin = _newAdmin;
    }
}
