#!/usr/bin/env bash
# Pilot run: measures answer time and GPU memory fit for the 4 tier-1 models,
# on ONE contract from a separate pilot corpus (seed 1), so the 20 evaluation
# contracts are never shown to a model before the official run.
# Usage, as root on a fresh Ubuntu GPU instance:
#   curl -fsSL https://raw.githubusercontent.com/DevDaveRug/contract-oversight-eval/main/pilote.sh | bash
set -euo pipefail
MODELES="qwen3.8:27b qwen3.6:35b phi4:14b gpt-oss:20b"

echo "== GPU"; nvidia-smi --query-gpu=name,memory.total --format=csv

echo "== Ollama"
command -v ollama >/dev/null || curl -fsSL https://ollama.com/install.sh | sh
mkdir -p /etc/systemd/system/ollama.service.d
printf '[Service]\nEnvironment="OLLAMA_CONTEXT_LENGTH=8192"\n' > /etc/systemd/system/ollama.service.d/contexte.conf
systemctl daemon-reload && systemctl restart ollama && sleep 5

echo "== Models (about 64 GB to download)"
for m in $MODELES; do ollama pull "$m"; done
ollama list

echo "== Bench"
[ -d contract-oversight-eval ] || git clone --depth 1 https://github.com/DevDaveRug/contract-oversight-eval
cd contract-oversight-eval
python3 banc/generer_corpus.py --graine 1 --sortie pilote/corpus
for m in $MODELES; do
  python3 banc/interroger.py --sortie pilote/reponses --modeles "$m" --passes 1 \
    --contrats prestation-01 --corpus pilote/corpus
  echo "-- memory placement for $m (100% GPU expected):"; ollama ps
done

echo "== RESULT: copy everything below and paste it to Claude"
python3 - <<'EOF'
import json, glob
for f in sorted(glob.glob("pilote/reponses/reponses/*/*.json")):
    r = json.load(open(f))
    print(f'{r["modele"]}: {r["duree_s"]} s, tokens {r.get("usage")}')
EOF
ollama list
