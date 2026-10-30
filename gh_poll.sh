#!/bin/bash
set -u
cd "$HOME/.hermes/cache/scratch"
# прочитаем device_code.json (или сгенерируем новый)
if [ -f device_code.json ]; then
  dc=$(python3 -c "import json;print(json.load(open('device_code.json'))['dc'])")
  INTERVAL=$(python3 -c "import json;print(json.load(open('device_code.json'))['interval'])")
else
  dc=$(curl -s -X POST "https://github.com/login/device/code" -H "Accept: application/json" -d "client_id=178c6fc778ccc68e1d6a" -d "scope=repo,read:org,workflow,gist" | python3 -c "import json,sys;print(json.load(sys.stdin)['device_code'])")
  INTERVAL=5
fi
echo "device_code=$dc interval=$INTERVAL"
echo "POLLER STARTED"
while true; do
  sleep $INTERVAL
  OUT=$(curl -s -X POST "https://github.com/login/oauth/access_token" \
    -H "Accept: application/json" \
    -d "client_id=178c6fc778ccc68e1d6a" \
    -d "device_code=$dc" \
    -d "grant_type=urn:ietf:params:oauth:grant-type:device_code")
  RC=$?
  if [ $RC -ne 0 ]; then echo "poll: $OUT"; sleep $((INTERVAL+3)); continue; fi
  ACCESS=$(echo "$OUT" | python3 -c "
import sys,json
d=json.loads(sys.stdin.read())
if 'access_token' in d:
    print('TOKEN_OK')
    open('gh_token.txt','w').write(d['access_token'])
    # save basic auth config
    import pathlib
    p=pathlib.Path.home()/'.config/gh'; p.mkdir(parents=True, exist_ok=True)
    p.joinpath('hosts.yml').write_text('github.com:\n    git_protocol: https\n    user: ' && echo ok)
    print('TOKEN_SAVE')
    exit(0)
  )
  echo "$OUT"
  e=$(echo "$OUT" | python3 -c "import sys,json;print(json.load(sys.stdin).get('error','-'))")
  if [ "$e" = "slow_down" ]; then INTERVAL=$((INTERVAL+5)); fi
done
