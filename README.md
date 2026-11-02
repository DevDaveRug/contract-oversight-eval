# contract-oversight-eval

Pre-registered public evaluation: where open-weight LLMs confidently get contracts wrong, and what a human reviewer must check before trusting them.

**Status (1 November 2026)**: protocol in draft, pending an independent legal reviewer. No model has been run yet. The protocol will be frozen and tagged before the first run, and all results will be published here, including bad ones.

## Why

Small firms are starting to run open-weight models on their own machines to read confidential documents, contracts first. The usual safeguard is "a human checks the output". This evaluation measures where that human should look: which errors the models make, how often, and above all how often they state an error with high confidence.

## What is here

- `PROTOCOL.md`: the question, corpus, models, exact error definitions and pass thresholds, fixed before the tests.
- `corpus/contrats/`: 20 fictional French contracts (services, commercial lease, NDA, terms of sale) with 30 planted traps across 8 risk categories, plus 4 trap-free controls.
- `corpus/verite.json`: the ground truth, never shown to the models. `corpus/fiche_relecteur.md`: the same, readable, for the reviewer.
- `banc/`: the test bench, Python 3.9+ standard library only.
  - `generer_corpus.py` rebuilds the corpus (fixed seed, byte-identical output).
  - `consigne.txt` is the prompt sent to every model.
  - `interroger.py` queries models through any OpenAI-compatible API (Ollama by default) and saves raw answers, resumable.
  - `noter.py` scores answers against the ground truth; `rapport.py` writes the report and a CSV table.
  - `simuler.py` and `test_banc.py`: simulated answers with known injected errors; the 11 tests check that scoring finds them exactly.

File and folder names are in French, like the contracts.

## Run it

```
cd banc && python3 -m unittest test_banc.py      # no GPU, no network
python3 banc/interroger.py --sortie resultats/tier1 --modeles qwen3.8:27b qwen3.6:35b phi4:14b gpt-oss:20b
python3 banc/noter.py resultats/tier1
python3 banc/rapport.py resultats/tier1
```

With Ollama, start the server with `OLLAMA_CONTEXT_LENGTH=8192` so every model gets the same context size.

## Author

David Ruggieri, France. The code, the fictional contracts and parts of this text were written with an AI assistant (Claude); every decision in the protocol is the author's.

## License

Code (`banc/`): MIT, see `LICENSE`. Corpus, ground truth, results and reports: CC BY 4.0, see `corpus/LICENSE.md`.
