# Simulations

## Table of contents
- [Table of contents](#table-of-contents)
- [Modules](#modules)
  - [APR simulations](#apr-simulations)
  - [Outside safe's balance](#outside-safe-balance)
  - [Checksum baseline](#checksum-baseline)
  - [Waitlist update](#waitlist-update)
- [Scripts](#scripts)

## Modules
### `apr-simulations`
First, head into the `apr_simulations` folder:
```
cd apr_simulations
```

Install all required dependancies:

```sh
pip install -r requirements.txt
```

If you want to an updated version with the current running nodes in the network: declare a bunch of environment variables (can be through a .env file):
  - `API_HOST`: HOPRd node running on <2.1.0
  - `API_KEY`: API token 
  - `SUBGRAPH_DEPLOYER_KEY`: Subgraph deployer key
  - `SUBGRAPH_SAFES_BALANCES_QUERY_ID`: Query ID to the safe subgraph 

If not set, a snapshot of data from the past will be used (see snapshot dates in the `snapshot` folder).


### `outside-safe-balance`
This module allows you to sum up all the funds in outgoing channels for nodes linked to a safe.

The modules requires environment variables:
- `NODE_ADDRESS`: Full address of a running HOPRd node (format: `https://host:port`)
- `NODE_KEY`: Its corresponding API token
- `SUBGRAPH_SAFES_URL`: The URL to the `hopr-nodes-dufour` subgraph (decentralized or decentralized endpoint). This info can be found in subgraph-dedicated Notion page


To run the module, you can specify either a node or a safe address. If you specify:
- a safe address, the module will look for nodes associated with this safe.
- a node address, the module will first look for the associated safe, before finding all the other nodes associated to this safe. 

An extra parameter can be provided, an output file. If provided, a json file listing funds per node will be generated.

Either way, the command is the same:

```sh
python -m outside-safe-balance --address <ADDRESS> [--output <JSON_OUTPUT_PATH>]
```

Some environment files needs to be set beforehead. You can either set them by your own, or copy/paste/rename the `.env.example` file to `.env` and specify the desired values for the following parameters:
- The `<SAFE_ADDRESS>` parameter is required (either safe or node address)
- The `<JSON_OUTPUT_PATH>` parameter is optional

### `checksum-baseline`
This module generate the baseline checksum for every block containing HOPRd logs.

Multiple parameter can be set:
- `--minblock` (optional): The block number to start gettings logs from. Should not be changed, unless you know what you are doing. Default is `29706814`
- `--startblock`: The block you want the checksum from. Can be a lower-bound block, if `endblock` is set.
- `--endblock` (optional): The upper-bound block you want the checksum from.
- `--blocksfile` (optional): A .json file to store the gathered blocks, events, and checksums in. Default is `blocks.json`. If provided and the file already exist, the module will try to load data from this file to save some execution and subgraph query time.
- `--folder` (optional): A temp folder to store temporary subgraph query data. Once subgraph queries are done, content will be converted into a single file store at `blocksfile`. Default is `./_temp_results`.

Workflow is as follow: is `blocksfile` file exist, will load data from it. Else, if data is available in `folder`, will load data from there and generate `blocksfile`. Else, logs will be gathered from subgraph, saved temporarly to `folder` and then converted to `blocksfile`.

Here are some ways to run the module:

```sh
python -m checksum-baseline --startblock 31000000
```
this will print checksum for block `31000000` and some blocks around it.

```sh
python -m checksum-baseline --startblock 31000000 --endblock 31000010
```
this will print checksum for blocks `31000000` to `31000010`.

### `waitlist-update`

The module generates the list of eligible nodes to join the HOPR network. It requires a `registry` file, which is the results (.xlsx format) from the form that community members fill in when asking to join. It generates an .xlsx file that list the elgibles nodes.

The module relies solely on subgraph calls to get relevant data, and filter out non-eligible nodes. This comes with some mandatory environment variables:
- `SUBGRAPH_SAFES_URL`: url of the `hopr-nodes-dufour` subgraph
- `SUBGRAPH_NFT_URL`: url of the `hopr-stake-all-seasons` subgraph

Those values can be found in the notion page dedicated to subgraphs.

To run the module, use the following command:
```sh
python -m waitlist-update --registry <PATH_TO_REGISTRY_FILE> [--output <PATH_TO_OUTPUT_FILE>]
```
- `--registry` (optional): Path to the registry file (.xslx). Default is `registy.xlsx`
- `--output`(optional): Path to the output file (.xslx). Default is `output.xslx`

## Scripts

- `low_stake_safes.sh`: list all safes that have stake lower than 10000wxHOPR (or value from THRESHOLD env var). Stores results to `low_stake_addresses.csv`
- `safe_probe.sh`: check all nodes from csv input file (specified as CLI's first argument) if they have an associated safe. Format of input file should be two column csv (node address and multi-address), see `scripts/new_node_multiaddr.csv`. Stores results to `no_safes_addresses.csv`