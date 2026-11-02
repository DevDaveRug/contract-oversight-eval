"""Interroge des modèles par une API compatible OpenAI (Ollama, vLLM, llama.cpp...) et enregistre les réponses brutes.

Usage :
  python3 interroger.py --sortie ../resultats/palier1 --modeles qwen3.8:27b qwen3.6:35b phi4:14b gpt-oss:20b
Options : --base-url (défaut http://localhost:11434/v1, celui d'Ollama), --passes 3, --temperature 0.7,
          --contrats nda-01 cgv-02 (pour un essai court), --delai 600 (secondes par requête).
Clé d'API éventuelle : variable d'environnement BANC_API_KEY (jamais dans la ligne de commande).

Reprise : une réponse déjà enregistrée n'est pas redemandée. On peut donc relancer après une coupure.
Contexte : Ollama ne prend pas la taille de contexte par cette API ; démarrer le serveur avec
OLLAMA_CONTEXT_LENGTH=8192 (protocole, section III).
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import commun as C  # noqa: E402


def nom_fichier(modele):
    return modele.replace("/", "_").replace(":", "_")


def demander(base_url, modele, consigne, temperature, graine, delai, cle=None):
    corps = json.dumps({"model": modele, "temperature": temperature, "seed": graine,
                        "messages": [{"role": "user", "content": consigne}]}).encode("utf-8")
    entetes = {"Content-Type": "application/json"}
    if cle:
        entetes["Authorization"] = f"Bearer {cle}"
    req = urllib.request.Request(base_url.rstrip("/") + "/chat/completions", data=corps, headers=entetes)
    debut = time.monotonic()
    with urllib.request.urlopen(req, timeout=delai) as rep:
        donnees = json.loads(rep.read().decode("utf-8"))
    return donnees, time.monotonic() - debut


def main(argv=None, demander_fn=demander):
    ap = argparse.ArgumentParser()
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--modeles", nargs="+", required=True)
    ap.add_argument("--base-url", default="http://localhost:11434/v1")
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--contrats", nargs="*")
    ap.add_argument("--delai", type=int, default=600)
    ap.add_argument("--corpus", default=str(C.CORPUS), help="dossier du corpus ; un corpus de pilote hors évaluation évite d'exposer les vrais contrats")
    a = ap.parse_args(argv)

    verite, textes = C.charger_corpus(a.corpus)
    ids = a.contrats or [c["id"] for c in verite["contrats"]]
    sortie = Path(a.sortie)
    (sortie / "reponses").mkdir(parents=True, exist_ok=True)
    meta = {"debut": datetime.now(timezone.utc).isoformat(), "base_url": a.base_url, "modeles": a.modeles,
            "passes": a.passes, "temperature": a.temperature, "graine_corpus": verite["graine"], "corpus": a.corpus, "contrats": ids}
    (sortie / "lancement.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    cle = os.environ.get("BANC_API_KEY")
    total, faits, echecs = len(a.modeles) * len(ids) * a.passes, 0, 0
    for modele in a.modeles:
        d = sortie / "reponses" / nom_fichier(modele)
        d.mkdir(parents=True, exist_ok=True)
        for cid in ids:
            for passe in range(1, a.passes + 1):
                f = d / f"{cid}_p{passe}.json"
                faits += 1
                if f.exists():
                    continue
                for essai in range(3):
                    try:
                        donnees, duree = demander_fn(a.base_url, modele, C.consigne_pour(textes[cid]),
                                                     a.temperature, passe, a.delai, cle)
                        contenu = donnees["choices"][0]["message"].get("content") or ""
                        break
                    except (urllib.error.URLError, TimeoutError, KeyError, ValueError) as e:
                        erreur = f"{type(e).__name__}: {e}"
                        time.sleep(2 ** essai)
                else:
                    echecs += 1
                    print(f"[{faits}/{total}] {modele} {cid} p{passe} : échec ({erreur}), sera retenté au prochain lancement")
                    continue
                f.write_text(json.dumps({"modele": modele, "contrat": cid, "passe": passe, "duree_s": round(duree, 2),
                                         "usage": donnees.get("usage"), "modele_servi": donnees.get("model"),
                                         "contenu": contenu}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
                print(f"[{faits}/{total}] {modele} {cid} p{passe} : {duree:.1f} s")
    print(f"Terminé : {total - echecs} réponses enregistrées sur {total}, {echecs} échecs.")
    return echecs


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
