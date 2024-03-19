
#!/bin/bash

# Input and output files
CSV_FILE="$1"
NO_SAFE_OUTPUT="no_safes_addresses.csv"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# RPC parameters
RPC_PAYLOAD_STRUCT='{
    "jsonrpc": "2.0", "id": 1, "method": "eth_call",
    "params": [
        {
            "from": "0x0000000000000000000000000000000000000000",
            "data": "0xc7ecab8f000000000000000000000000NODE_ADDRESS",
            "to": "0x582b4b586168621daf83beb2aeadb5fb20f8d50d"
        },
        "latest"
    ]
}'
RPC_ENDPOINT="https://rpc.ankr.com/gnosis"

echo "NODE_ADDRESS" > $NO_SAFE_OUTPUT
start=`date +%s`

# Progress parameters
((lines=$(wc -l < $CSV_FILE)-1))
progress=1

# Counters
fails=0
oks=0
skips=0

while IFS="," read -r chain_addr multi_addr
do
  if [ -n "$multi_addr" ]; then
        PAYLOAD=$(echo $RPC_PAYLOAD_STRUCT | sed "s/NODE_ADDRESS/$(echo $chain_addr | sed "s/0x//g")/g")
        address=$(curl -s -X POST -H "Content-Type: application/json" -d "$PAYLOAD" $RPC_ENDPOINT | jq -r .result)
        if [[ "$address" == "0x0000000000000000000000000000000000000000000000000000000000000000" ]]; then
            echo "$chain_addr" >> $NO_SAFE_OUTPUT
            echo -e "($(printf "%03d" $progress)/$lines) $chain_addr: ${RED}FAILED${NC}"
            ((fails=fails+1))
        else            
            echo -e "($(printf "%03d" $progress)/$lines) $chain_addr: ${GREEN}OK${NC}"
            ((oks=oks+1))
        fi
    else
        echo -e "($(printf "%03d" $progress)/$lines) $chain_addr: ${YELLOW}SKIPPED${NC}"
        ((skips=skips+1))
    fi

    ((progress=progress+1))
done < <(tail -n +2 $CSV_FILE)

end=`date +%s`
runtime=$((end-start))


echo "---"
echo -e "Completed in ${runtime}s:  ${GREEN}${oks} ok${NC}, ${RED}${fails} failed${NC}, ${YELLOW}${skips} skipped${NC}"