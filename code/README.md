# SMARTGIFT

We have improved and are improving the use of SmartGift. The following is an implement of the method in the paper, and the code is an example.

## HOW TO USE

Step 1: Get the training data from Etherscan, you can get the data by using the API provided by Etherscan.

For example using the `get_transaction` under `crawl` directory, you can get all the transactions by using `eth_getBlockByNumber` API.

And then using `get_input_with_contract` under `crawl` directory, you can get the raw transactions inputs and crawl bytecode and abi from Etherscan. The data will be saved as:

```
{
    bytecode: xxxx,
    abi: xxx.
    inputs: xxx
}
```
Step 2: Use the project [ethereum-input-decoder](https://github.com/miguelmota/ethereum-input-data-decoder) to decode the input. For example like the code in `metadata.js`, finally use the `getSample.py` to get the final processed function data and input data.

you can find the sample data like the following:

```
[
    {
        "inputs": [
            [
                "bbe4781f4bc38bb622f9b37c77d9317987a601fe",
                "592000000000"
            ],
            [
                "8aeabc1ea5205b84877ba61df7b745d6ab0d5cd6",
                "26039214"
            ],
            [
                "67655e8fcd903f75aceb82bb3f782687ce985d35",
                "46319000000000000000000"
            ]
        ],
        "function": {
            "types": [
                "address",
                "uint256"
            ],
            "method": "transfer"
        }
    },
    {
        "inputs": [
            [
                "2a0c0dbecc7e4d658f48e01e3fa353f44050c208",
                "17743000000"
            ]
        ],
        "function": {
            "types": [
                "address",
                "uint256"
            ],
            "method": "approve"
        }
    },
    {
        "inputs": [
            [
                "e5caef4af8780e59df925470b050fb23c43ca68c",
                "17743000000"
            ]
        ],
        "function": {
            "types": [
                "address",
                "uint256"
            ],
            "method": "depositToken"
        }
    }
]
```

Step 3: Now we get the sample data with all the functions and inputs we crawled. Then use the main program `SmartGift.py`. Before this you need to download the BERT model and use `bert-serving-start` to run the server, and then use `pip` download the relative library.

use the instruction like the following:

```
python3 SmartGift.py target_abi_path sample_path output_path k
```