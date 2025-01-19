import hashlib
import random
import ecdsa
from web3 import Web3

def hash_function(data):
    return int(hashlib.sha256(data.encode()).hexdigest(), 16)

def generate_key_pair(seed=None):
    if seed is not None:
        random.seed(seed)
    private_key = random.randint(1, ecdsa.SECP256k1.order - 1)
    public_key = private_key * ecdsa.SECP256k1.generator
    return private_key, public_key

def point_to_string(point):
    return f"{point.x()}|{point.y()}"

def sign(message, private_key, public_keys, signer_index):
    n = len(public_keys)
    message_hash = hash_function(message)
    k = random.randint(1, ecdsa.SECP256k1.order - 1)
    e = hash_function(point_to_string(k * ecdsa.SECP256k1.generator) + message)
    s = [random.randint(1, ecdsa.SECP256k1.order - 1) for _ in range(n)]
    c = [0] * n
    c[(signer_index + 1) % n] = e
    for i in range(n - 1):
        idx = (signer_index + 1 + i) % n
        next_idx = (idx + 1) % n
        point = s[idx] * ecdsa.SECP256k1.generator + c[idx] * public_keys[idx]
        c[next_idx] = hash_function(point_to_string(point) + message)
    s[signer_index] = (k - private_key * c[signer_index]) % ecdsa.SECP256k1.order
    return c[0], s

def verify(message, signature, public_keys):
    n = len(public_keys)
    c, s = signature
    message_hash = hash_function(message)
    for i in range(n):
        point = s[i] * ecdsa.SECP256k1.generator + c * public_keys[i]
        c = hash_function(point_to_string(point) + message)
    return c == signature[0]

def connect_to_ganache():
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
    return w3

def deploy_contract(w3, abi, bytecode):
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    accounts = w3.eth.accounts
    if not accounts:
        raise ValueError("No accounts found. Make sure Ganache is running and has accounts.")
    from_address = accounts[0]
    tx_hash = contract.constructor().transact({'from': from_address, 'gas': 6000000})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    return w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

def vote(w3, contract, candidate_index, signature):
    accounts = w3.eth.accounts
    if not accounts:
        raise ValueError("No accounts found. Make sure Ganache is running and has accounts.")
    from_address = accounts[0]
    tx_hash = contract.functions.vote(candidate_index, Web3.keccak(text=str(signature))).transact({'from': from_address})
    w3.eth.wait_for_transaction_receipt(tx_hash)

def main():
    w3 = connect_to_ganache()
    
    # Check if connected to Ganache
    if not w3.is_connected():
        print("Not connected to Ganache. Make sure Ganache is running.")
        return

    # Check if accounts are available
    accounts = w3.eth.accounts
    if not accounts:
        print("No accounts found. Make sure Ganache is running and has accounts.")
        return

    print(f"Connected to Ganache. Available accounts: {accounts}")

    # Deploy the contract (you need to provide ABI and bytecode)
    abi = [
	{
		"inputs": [
			{
				"internalType": "string",
				"name": "_name",
				"type": "string"
			}
		],
		"name": "addCandidate",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"stateMutability": "nonpayable",
		"type": "constructor"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "string",
				"name": "name",
				"type": "string"
			}
		],
		"name": "CandidateAdded",
		"type": "event"
	},
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "candidateIndex",
				"type": "uint256"
			}
		],
		"name": "VoteCast",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_candidateIndex",
				"type": "uint256"
			},
			{
				"internalType": "bytes32",
				"name": "_signature",
				"type": "bytes32"
			}
		],
		"name": "voteNormal",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_candidateIndex",
				"type": "uint256"
			},
			{
				"internalType": "bytes32",
				"name": "_signature",
				"type": "bytes32"
			}
		],
		"name": "voteRing",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "candidates",
		"outputs": [
			{
				"internalType": "string",
				"name": "name",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "voteCount",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_index",
				"type": "uint256"
			}
		],
		"name": "getCandidate",
		"outputs": [
			{
				"internalType": "string",
				"name": "",
				"type": "string"
			},
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "getCandidateCount",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "_voter",
				"type": "address"
			}
		],
		"name": "getVotingStatus",
		"outputs": [
			{
				"internalType": "bool",
				"name": "normalVote",
				"type": "bool"
			},
			{
				"internalType": "bool",
				"name": "ringVote",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "hasNormalVoted",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"name": "hasRingVoted",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "owner",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "totalVotes",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "bytes32",
				"name": "",
				"type": "bytes32"
			}
		],
		"name": "usedSignatures",
		"outputs": [
			{
				"internalType": "bool",
				"name": "",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
] # Add the ABI of your compiled contract here
    bytecode = "608060405234801561001057600080fd5b50610c16806100206000396000f3fe608060405234801561001057600080fd5b506004361061007d5760003560e01c806335b8e8201161005b57806335b8e820146100ef578063462e91ec1461012057806368bb8bb61461013c578063f978fd61146101585761007d565b80630d15fd771461008257806330a56347146100a05780633477ee2e146100be575b600080fd5b61008a610188565b604051610097919061099f565b60405180910390f35b6100a861018e565b6040516100b5919061099f565b60405180910390f35b6100d860048036038101906100d391906107b6565b61019a565b6040516100e692919061092f565b60405180910390f35b610109600480360381019061010491906107b6565b610256565b60405161011792919061092f565b60405180910390f35b61013a60048036038101906101359190610775565b6103cc565b005b610156600480360381019061015191906107df565b610470565b005b610172600480360381019061016d919061074c565b6105f7565b60405161017f91906108f2565b60405180910390f35b60025481565b60008080549050905090565b600081815481106101aa57600080fd5b90600052602060002090600202016000915090508060000180546101cd90610a99565b80601f01602080910402602001604051908101604052809291908181526020018280546101f990610a99565b80156102465780601f1061021b57610100808354040283529160200191610246565b820191906000526020600020905b81548152906001019060200180831161022957829003601f168201915b5050505050908060010154905082565b60606000808054905083106102a0576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004016102979061097f565b60405180910390fd5b600083815481106102da577f4e487b7100000000000000000000000000000000000000000000000000000000600052603260045260246000fd5b906000526020600020906002020160000160008481548110610325577f4e487b7100000000000000000000000000000000000000000000000000000000600052603260045260246000fd5b90600052602060002090600202016001015481805461034390610a99565b80601f016020809104026020016040519081016040528092919081815260200182805461036f90610a99565b80156103bc5780601f10610391576101008083540402835291602001916103bc565b820191906000526020600020905b81548152906001019060200180831161039f57829003601f168201915b5050505050915091509150915091565b60006040518060400160405280838152602001600081525090806001815401808255809150506001900390600052602060002090600202016000909190919091506000820151816000019080519060200190610429929190610617565b506020820151816001015550507ff29562dad1599aea0ebb142466120aab326d5efa8f839df82a9c064bf78e893881604051610465919061090d565b60405180910390a150565b60008054905082106104b7576040517f08c379a00000000000000000000000000000000000000000000000000000000081526004016104ae9061097f565b60405180910390fd5b6001600082815260200190815260200160002060009054906101000a900460ff1615610518576040517f08c379a000000000000000000000000000000000000000000000000000000000815260040161050f9061095f565b60405180910390fd5b600180600083815260200190815260200160002060006101000a81548160ff0219169083151502179055506000828154811061057d577f4e487b7100000000000000000000000000000000000000000000000000000000600052603260045260246000fd5b9060005260206000209060020201600101600081548092919061059f90610acb565b9190505550600260008154809291906105b790610acb565b91905055507f9593d9bd30eff4872ec3bab10360ad82eaac80651801e68f47f0674c38415c3d826040516105eb919061099f565b60405180910390a15050565b60016020528060005260406000206000915054906101000a900460ff1681565b82805461062390610a99565b90600052602060002090601f016020900481019282610645576000855561068c565b82601f1061065e57805160ff191683800117855561068c565b8280016001018555821561068c579182015b8281111561068b578251825591602001919060010190610670565b5b509050610699919061069d565b5090565b5b808211156106b657600081600090555060010161069e565b5090565b60006106cd6106c8846109eb565b6109ba565b9050828152602081018484840111156106e557600080fd5b6106f0848285610a57565b509392505050565b60008135905061070781610bb2565b92915050565b600082601f83011261071e57600080fd5b813561072e8482602086016106ba565b91505092915050565b60008135905061074681610bc9565b92915050565b60006020828403121561075e57600080fd5b600061076c848285016106f8565b91505092915050565b60006020828403121561078757600080fd5b600082013567ffffffffffffffff8111156107a157600080fd5b6107ad8482850161070d565b91505092915050565b6000602082840312156107c857600080fd5b60006107d684828501610737565b91505092915050565b600080604083850312156107f257600080fd5b600061080085828601610737565b9250506020610811858286016106f8565b9150509250929050565b61082481610a37565b82525050565b600061083582610a1b565b61083f8185610a26565b935061084f818560208601610a66565b61085881610ba1565b840191505092915050565b6000610870601683610a26565b91507f5369676e617475726520616c72656164792075736564000000000000000000006000830152602082019050919050565b60006108b0601783610a26565b91507f496e76616c69642063616e64696461746520696e6465780000000000000000006000830152602082019050919050565b6108ec81610a4d565b82525050565b6000602082019050610907600083018461081b565b92915050565b60006020820190508181036000830152610927818461082a565b905092915050565b60006040820190508181036000830152610949818561082a565b905061095860208301846108e3565b9392505050565b6000602082019050818103600083015261097881610863565b9050919050565b60006020820190508181036000830152610998816108a3565b9050919050565b60006020820190506109b460008301846108e3565b92915050565b6000604051905081810181811067ffffffffffffffff821117156109e1576109e0610b72565b5b8060405250919050565b600067ffffffffffffffff821115610a0657610a05610b72565b5b601f19601f8301169050602081019050919050565b600081519050919050565b600082825260208201905092915050565b60008115159050919050565b6000819050919050565b6000819050919050565b82818337600083830152505050565b60005b83811015610a84578082015181840152602081019050610a69565b83811115610a93576000848401525b50505050565b60006002820490506001821680610ab157607f821691505b60208210811415610ac557610ac4610b43565b5b50919050565b6000610ad682610a4d565b91507fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff821415610b0957610b08610b14565b5b600182019050919050565b7f4e487b7100000000000000000000000000000000000000000000000000000000600052601160045260246000fd5b7f4e487b7100000000000000000000000000000000000000000000000000000000600052602260045260246000fd5b7f4e487b7100000000000000000000000000000000000000000000000000000000600052604160045260246000fd5b6000601f19601f8301169050919050565b610bbb81610a43565b8114610bc657600080fd5b50565b610bd281610a4d565b8114610bdd57600080fd5b5056fea2646970667358221220c875e60c41047b271e09ad77bf32d09fcefea18e2ad0e9c1b2d62cc0cd01450c64736f6c63430008000033"  # Add the bytecode of your compiled contract here
    
    try:
        contract = deploy_contract(w3, abi, bytecode)
        print(f"Contract deployed at address: {contract.address}")
    except Exception as e:
        print(f"Error deploying contract: {e}")
        return

    # Get user input
    message = input("Enter the message to sign (vote data): ")
    num_keys = int(input("Enter the number of keys in the ring (minimum 2): "))
    
    while num_keys < 2:
        num_keys = int(input("Number of keys must be at least 2. Please enter again: "))
    
    signer_index = int(input(f"Enter the signer's index (0 to {num_keys - 1}): "))
    
    while signer_index < 0 or signer_index >= num_keys:
        signer_index = int(input(f"Invalid index. Please enter a number between 0 and {num_keys - 1}: "))

    print(f"\nGenerating {num_keys} key pairs...")
    private_keys = []
    public_keys = []

    # Generate key pairs for the ring members
    for i in range(num_keys):
        private_key, public_key = generate_key_pair(seed=i)  # Use deterministic seeds
        private_keys.append(private_key)
        public_keys.append(public_key)

    print(f"Key pairs generated. Signer index: {signer_index}")

    print("\nSigning process:")
    signature = sign(message, private_keys[signer_index], public_keys, signer_index)
    print("Message signature:", signature)

    print("\nVerification process:")
    is_valid = verify(message, signature, public_keys)
    print("Signature valid:", is_valid)

    if is_valid:
        try:
            # Extract candidate index from the message (assuming it's the first character)
            candidate_index = int(message[0])
            vote(w3, contract, candidate_index, str(signature))
            print("Vote cast successfully!")
        except Exception as e:
            print(f"Error casting vote: {e}")
    else:
        print("Invalid signature. Vote not cast.")

if __name__ == "__main__":
    main()