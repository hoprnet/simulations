# Simulations

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

- Declare a bunch of environment variables (can be through a .env file):
  - `API_HOST`: HOPRd node running on <2.1.0
  - `API_KEY`: API token 
  - `SUBGRAPH_DEPLOYER_KEY`: Subgraph deployer key
  - `SUBGRAPH_SAFES_BALANCES_QUERY_ID`: Query ID to the safe subgraph 

### Generate `requirements.txt`
- Install `pipreqsnb` via pip:
```
pip install pipreqsnb
```

- Generate requirement file based on notebook imports:
```bash
pipreqsnb . --ignore ".venv" --force
```