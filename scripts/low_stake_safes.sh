#!/bin/bash

: ${THRESHOLD:=10000}

# Input and output files
LOW_STAKE_OUTPUT="low_stake_addresses.csv"

# Subgraph parameters
THEGRAPH_QUERY="{safes(first: 1000, skip: 0) { registeredNodesInNetworkRegistry { node { id } safe { id balance { wxHoprBalance } } } } }"
SUBGRAPH_QUERY="{\"query\": \"$THEGRAPH_QUERY\"}"

SUBGRAPH_ENDPOINT="https://api.studio.thegraph.com/query/40439/hopr-nodes-dufour/version/latest"

echo "Fetching nodes with less than $THRESHOLD wxHOPR in their safes (modify threshold by setting THRESHOLD env var)"

safes=$(curl -s -X POST -H "Content-Type: application/json" -d "$SUBGRAPH_QUERY" $SUBGRAPH_ENDPOINT | jq -r .data.safes[].registeredNodesInNetworkRegistry[])

addresses=($(echo $safes | jq -r .node.id))
balances=($(echo $safes | jq -r .safe.balance.wxHoprBalance))

echo "NODE_ADDRESS, BALANCE" > $LOW_STAKE_OUTPUT

for i in "${!addresses[@]}"; do
    if (( $(echo "${balances[i]} < $THRESHOLD" | bc -l) )); then
        echo -e "${addresses[i]}: ${balances[i]}wxHOPR"
        echo "${addresses[i]}, ${balances[i]}" >> $LOW_STAKE_OUTPUT
    fi
done