# Simulations

## APR simulations
First, head into the `apr_simulations` folder:
```
cd apr_simulations
```

### Run simulation
- Install all required dependancies:
```
pip install -r requirements.txt
```

If you want to an updated version with the current running nodes in the network: declare a bunch of environment variables (can be through a .env file):
  - `API_HOST`: HOPRd node running on <2.1.0
  - `API_KEY`: API token 
  - `SUBGRAPH_DEPLOYER_KEY`: Subgraph deployer key
  - `SUBGRAPH_SAFES_BALANCES_QUERY_ID`: Query ID to the safe subgraph 

If not set, a snapshot of data from the past will be used (see snapshot dates in the `snapshot` folder).
### Generate `requirements.txt`
- Install `pipreqsnb` via pip:
```
pip install pipreqsnb
```

- Generate requirement file based on notebook imports:
```bash
pipreqsnb . --ignore ".venv" --force
```


## List outgoing channels
This module allows you to, from a safe address, get all the connected nodes, for each node get all the outgoing channels, and sum up their balances.
The modules requires two environment variables:
- `NODE_ADDRESS`: Full address of a running HOPRd node (format: `https://host:port`)
- `NODE_KEY`: Its corresponding API token

### Run the module
To run the module, use the following command:

```
python -m list_outgoing_balances --address <SAFE_ADDRESS> [--output <JSON_OUTPUT_PATH>]
```

- The `<SAFE_ADDRESS>` parameter is required
- The `<JSON_OUTPUT_PATH>` parameter is optional. By default it is set to `results.json`