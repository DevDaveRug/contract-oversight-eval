"""Fabrique des réponses simulées à partir de la vérité, avec des erreurs injectées et comptées.

Sert à tester le banc sans GPU : la notation doit retrouver exactement les erreurs injectées.
Usage : python3 simuler.py --sortie ../resultats/simulation [--graine 7]
"""
import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import commun as C  # noqa: E402

PROFILS = {
    # nom du modèle simulé : probabilités par champ ou par piège
    "simule-parfait": dict(faux=0, invente=0, omis=0, manque=0, assurance=0, format=0, alerte=0),
    "simule-prudent": dict(faux=0.02, invente=0, omis=0.05, manque=0.1, assurance=0, format=0, alerte=0.1),
    "simule-bavard": dict(faux=0.08, invente=0.1, omis=0.02, manque=0.3, assurance=0.5, format=0.03, alerte=0.3),
}


def reponse(contrat, texte, profil, r, journal):
    if r.random() < profil["format"]:
        journal["format"] += 1
        return "Voici mon analyse du contrat : il semble équilibré."
    champs = {}
    for champ, t in contrat["champs"].items():
        conf = r.choice(["haute", "haute", "moyenne", "basse"])
        if t is not None and r.random() < profil["omis"]:
            champs[champ] = {"valeur": None, "confiance": conf, "citation": ""}
            journal["omis"] += 1
        elif t is not None and r.random() < profil["faux"]:
            if C.est_nombre(champ):
                v = t * 2 + 1
            elif champ == "renouvellement_tacite":
                v = not t
            elif champ == "date_effet":
                v = "1999-01-01"
            else:
                v = "Zorglub Industries"
            champs[champ] = {"valeur": v, "confiance": conf, "citation": ""}
            journal["faux"] += 1
        elif t is None and r.random() < profil["invente"]:
            champs[champ] = {"valeur": 987654 if C.est_nombre(champ) else "Clause Fantôme", "confiance": conf, "citation": ""}
            journal["invente"] += 1
        else:
            champs[champ] = {"valeur": t, "confiance": conf, "citation": ""}
    risques, manque = [], 0
    for p in contrat["pieges"]:
        if r.random() < profil["manque"]:
            manque += 1
            continue
        risques.append({"categorie": p["categorie"], "citation": p["extrait"], "confiance": "haute", "explication": "simulé"})
    journal["manque"] += manque
    if r.random() < profil["alerte"]:
        # fausse alerte : une phrase neutre réellement présente, sous une catégorie qui n'y correspond pas
        ligne = next(l for l in texte.splitlines() if l.startswith("Fait en deux"))
        risques.append({"categorie": "penalite_excessive", "citation": ligne, "confiance": "moyenne", "explication": "simulé"})
        journal["alerte"] += 1
    if r.random() < profil["invente"]:
        risques.append({"categorie": "cession_propriete_intellectuelle", "citation": "Le client cède son fonds de commerce au prestataire.",
                        "confiance": "haute", "explication": "simulé"})
        journal["invente"] += 1
    glob = "eleve" if contrat["pieges"] else "aucun"
    if contrat["pieges"] and manque and r.random() < profil["assurance"]:
        glob = "faible"
        journal["assurance"] += 1
    obj = {"resume": "Réponse simulée.", "champs": champs, "risques": risques, "risque_global": glob}
    return "```json\n" + json.dumps(obj, ensure_ascii=False) + "\n```"


def simuler(sortie, graine=7, passes=3, profils=PROFILS):
    verite, textes = C.charger_corpus()
    r = random.Random(graine)
    journaux = {}
    for nom, profil in profils.items():
        j = journaux[nom] = dict(format=0, omis=0, faux=0, invente=0, manque=0, alerte=0, assurance=0)
        d = Path(sortie) / "reponses" / nom
        d.mkdir(parents=True, exist_ok=True)
        for c in verite["contrats"]:
            for passe in range(1, passes + 1):
                contenu = reponse(c, textes[c["id"]], profil, r, j)
                (d / f"{c['id']}_p{passe}.json").write_text(json.dumps(
                    {"modele": nom, "contrat": c["id"], "passe": passe, "duree_s": 0, "contenu": contenu},
                    ensure_ascii=False) + "\n", encoding="utf-8")
    (Path(sortie) / "injections.json").write_text(json.dumps(journaux, indent=1) + "\n", encoding="utf-8")
    return journaux


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sortie", required=True)
    ap.add_argument("--graine", type=int, default=7)
    a = ap.parse_args()
    print(json.dumps(simuler(a.sortie, a.graine), indent=1))


if __name__ == "__main__":
    main()
