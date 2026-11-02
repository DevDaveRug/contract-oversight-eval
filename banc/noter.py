"""Note les réponses d'un lancement contre la vérité connue (protocole, section IV).

Usage : python3 noter.py <dossier_lancement>
Lit <dossier>/reponses/<modele>/<contrat>_p<n>.json, écrit <dossier>/notes.json et
<dossier>/echantillon_controle.json (24 réponses tirées au sort pour la relecture humaine).
"""
import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import commun as C  # noqa: E402

GRAINE_ECHANTILLON = 20261101
SEUILS = {"fausses_assurances": 0, "taux_valeurs_fausses": 0.05, "taux_inventions": 0.02, "taux_pieges_manques": 0.10}


def noter_reponse(contrat, texte, reponse, champs):
    """Note une réponse. Renvoie un dict de comptes et la liste détaillée des erreurs."""
    r = {"format_ok": True, "champs_presents": 0, "valeurs_fausses": 0, "inventions": 0, "champs_omis": 0,
         "elements_affirmes": 0, "pieges": len(contrat["pieges"]), "pieges_detectes": 0, "fausses_alertes": 0,
         "fausse_assurance": False, "erreurs": [], "valeurs": {}}
    obj = C.lire_json(reponse)
    if obj is None:
        r["format_ok"] = False
        obj = {}
    entrees = obj.get("champs") if isinstance(obj.get("champs"), dict) else {}

    for champ in champs:
        t = contrat["champs"].get(champ)
        e = entrees.get(champ)
        e = e if isinstance(e, dict) else {"valeur": e}
        v, conf = e.get("valeur"), e.get("confiance")
        nul = C.est_nul(v)
        r["valeurs"][champ] = None if nul else str(v)
        if not nul:
            r["elements_affirmes"] += 1
        if t is not None:
            r["champs_presents"] += 1
            if nul:
                r["champs_omis"] += 1
                r["erreurs"].append({"type": "omis", "champ": champ, "verite": t, "valeur": None, "confiance": conf})
            elif not C.egal(champ, t, v):
                r["valeurs_fausses"] += 1
                r["erreurs"].append({"type": "valeur_fausse", "champ": champ, "verite": t, "valeur": v, "confiance": conf})
        elif not nul:
            genre = "valeur_fausse" if C.present_dans_texte(champ, v, texte) else "inventee"
            r["valeurs_fausses" if genre == "valeur_fausse" else "inventions"] += 1
            r["erreurs"].append({"type": genre, "champ": champ, "verite": None, "valeur": v, "confiance": conf})

    detectes = set()
    risques = obj.get("risques") if isinstance(obj.get("risques"), list) else []
    for rq in risques:
        if not isinstance(rq, dict):
            continue
        r["elements_affirmes"] += 1
        cat, cit, conf = rq.get("categorie"), rq.get("citation", ""), rq.get("confiance")
        if not C.citation_trouvee(cit, texte):
            r["inventions"] += 1
            r["erreurs"].append({"type": "inventee", "risque": cat, "citation": cit, "confiance": conf})
            continue
        trouve = None
        for i, p in enumerate(contrat["pieges"]):
            if p["categorie"] == cat and C.recoupe(cit, p["extrait"]):
                trouve = i
                break
        if trouve is None:
            r["fausses_alertes"] += 1
        else:
            detectes.add(trouve)
    r["pieges_detectes"] = len(detectes)
    for i, p in enumerate(contrat["pieges"]):
        if i not in detectes:
            r["erreurs"].append({"type": "piege_manque", "risque": p["categorie"], "confiance": None})

    glob = C.sans_accents(str(obj.get("risque_global", ""))).lower().strip()
    if contrat["pieges"] and len(detectes) < len(contrat["pieges"]) and glob in ("aucun", "faible"):
        r["fausse_assurance"] = True
        r["erreurs"].append({"type": "fausse_assurance", "risque_global": glob})
    return r


def ratio(a, b):
    return a / b if b else 0.0


def agreger(notes, verite):
    temoins = {c["id"] for c in verite["contrats"] if not c["pieges"]}
    par_modele = defaultdict(list)
    for n in notes:
        par_modele[n["modele"]].append(n)
    sortie = {}
    for modele, ns in sorted(par_modele.items()):
        s = lambda k: sum(n[k] for n in ns)  # noqa: E731
        erreurs = [e for n in ns for e in n["erreurs"] if e["type"] in ("omis", "valeur_fausse", "inventee")]
        avec_conf = [e for e in erreurs if e.get("confiance")]
        manques = defaultdict(int)
        for n in ns:
            for e in n["erreurs"]:
                if e["type"] == "piege_manque":
                    manques[e["risque"]] += 1
        # variation : couples (contrat, champ) dont la valeur change d'une passe à l'autre
        vals = defaultdict(set)
        for n in ns:
            for champ, v in n["valeurs"].items():
                vals[(n["contrat"], champ)].add(None if v is None else C.sans_accents(v).lower().strip())
        par_passe = defaultdict(lambda: {"vf": 0, "cp": 0})
        for n in ns:
            par_passe[n["passe"]]["vf"] += n["valeurs_fausses"]
            par_passe[n["passe"]]["cp"] += n["champs_presents"]
        taux_passes = [ratio(x["vf"], x["cp"]) for x in par_passe.values()]
        m = {
            "reponses": len(ns),
            "echecs_format": sum(not n["format_ok"] for n in ns),
            "taux_valeurs_fausses": ratio(s("valeurs_fausses"), s("champs_presents")),
            "taux_inventions": ratio(s("inventions"), s("elements_affirmes")),
            "taux_champs_omis": ratio(s("champs_omis"), s("champs_presents")),
            "taux_pieges_manques": ratio(s("pieges") - s("pieges_detectes"), s("pieges")),
            "fausses_assurances": sum(n["fausse_assurance"] for n in ns),
            "reponses_avec_piege": sum(1 for n in ns if n["pieges"]),
            "part_erreurs_confiance_haute": ratio(sum(1 for e in avec_conf if str(e["confiance"]).lower() == "haute"), len(avec_conf)),
            "erreurs_avec_confiance": len(avec_conf),
            "fausses_alertes": s("fausses_alertes"),
            "fausses_alertes_temoins": sum(n["fausses_alertes"] for n in ns if n["contrat"] in temoins),
            "variation_champs": ratio(sum(1 for v in vals.values() if len(v) > 1), len(vals)),
            "ecart_passes_valeurs_fausses": (max(taux_passes) - min(taux_passes)) if taux_passes else 0.0,
            "pieges_manques_par_categorie": dict(sorted(manques.items())),
            "comptes": {k: s(k) for k in ("champs_presents", "valeurs_fausses", "inventions", "champs_omis",
                                           "elements_affirmes", "pieges", "pieges_detectes")},
        }
        m["utilisable_sous_relecture"] = (m["fausses_assurances"] <= SEUILS["fausses_assurances"]
                                          and m["taux_valeurs_fausses"] < SEUILS["taux_valeurs_fausses"]
                                          and m["taux_inventions"] < SEUILS["taux_inventions"]
                                          and m["taux_pieges_manques"] < SEUILS["taux_pieges_manques"])
        sortie[modele] = m
    return sortie


def noter_lancement(dossier, corpus=C.CORPUS):
    dossier = Path(dossier)
    verite, textes = C.charger_corpus(corpus)
    contrats = {c["id"]: c for c in verite["contrats"]}
    notes = []
    for f in sorted((dossier / "reponses").glob("*/*_p*.json")):
        brut = json.loads(f.read_text(encoding="utf-8"))
        cid, passe = brut["contrat"], brut["passe"]
        n = noter_reponse(contrats[cid], textes[cid], brut["contenu"], verite["champs"])
        n.update(modele=brut["modele"], contrat=cid, passe=passe, fichier=str(f.relative_to(dossier)))
        notes.append(n)
    resultat = {"seuils": SEUILS, "modeles": agreger(notes, verite), "detail": notes}
    (dossier / "notes.json").write_text(json.dumps(resultat, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    k = min(24, len(notes))
    echantillon = sorted(random.Random(GRAINE_ECHANTILLON).sample([n["fichier"] for n in notes], k))
    (dossier / "echantillon_controle.json").write_text(json.dumps(echantillon, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return resultat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier")
    ap.add_argument("--corpus", default=str(C.CORPUS))
    a = ap.parse_args()
    res = noter_lancement(a.dossier, a.corpus)
    for modele, m in res["modeles"].items():
        print(f"{modele} : {m['reponses']} réponses, valeurs fausses {m['taux_valeurs_fausses']:.1%}, "
              f"inventions {m['taux_inventions']:.1%}, fausses assurances {m['fausses_assurances']}, "
              f"sous relecture : {'oui' if m['utilisable_sous_relecture'] else 'non'}")


if __name__ == "__main__":
    main()
