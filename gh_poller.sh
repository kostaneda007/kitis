#!/bin/bash
set -u
SCRATCH="$HOME/.hermes/cache/scratch"
DC_FILE="$SCRATCH/device_code.json"

# читаем device_code.json (если есть), иначе генерируем
if [ -f "$DC_FILE" ]; then
  DC=$(python3 -c "import json;print(json.load(open('$DC_FILE'))['device_code'])")
  INTERVAL=$(python3 -c "import json;print(json.load(open('$DC_FILE'))['interval'])")
else
  DI=$(curl -s -X POST "https://github.com/login/device/code" -H "Accept: application/json" -d "client_id=178c6fc778ccc68e1d6a" -d "scope=repo,read:org,workflow,gist" | python3 -c "import json,sys;print(json.load(sys.stdin)['interval'])")
  INTERVAL=${DI:-5}
fi

echo "Poller: polling device code (interval=$INTERVAL)..."
while true; do
  sleep "$INTERVAL"
  OUT=$(curl -s -X POST "https://github.com/login/oauth/access_token" -H "Accept: application/json" -d "client_id=178c6fc778ccc68e1d6a" -d "device_code=$DC" -d "grant_type=urn:ietf:params:oauth:grant-type:device_code")
  RC=$?
  if [ $RC -ne 0 ]; then echo "curl error $RC"; sleep $((INTERVAL+2)); continue; fi
  AUTH=$(echo "$OUT" | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    if 'access_token' in d:
        print('TOKEN_OK'); open('$SCRATCH/gh_token.txt','w').write(d['access_token'])
        print('TOKEN_SAVED')
        raise SystemExit(0)
    print('ERR:', d.get('error','-'))
" 2>/dev/null)
  echo "$AUTH"
  if echo "$AUTH" | grep -q "TOKEN_OK"; then
    echo "TOKEN_RECEIVED — configuring gh..."
    TOK=$(cat "$SCRATCH/gh_token.txt")
    git config --global github.token "$TOK"
    git config --global credential.helper 'store --file='
    # save minimal hosts config
    printf 'github.com:\n    host: github.com\n    oauth_token: %s\n' "$TOK" > "$HOME/.config/gh/hosts.yml"
    chmod 600 "$HOME/.config/gh/hosts.yml"
    echo "GH_TOKEN_SAVED"
    gh auth status 2>&1 | head -3
    break
  fi
done
