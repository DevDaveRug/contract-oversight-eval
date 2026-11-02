"""Produit le rapport (Markdown) et les tableaux (CSV) d'un lancement noté.

Usage : python3 rapport.py <dossier_lancement>
Écrit <dossier>/rapport.md et <dossier>/tableau_modeles.csv.
"""
import argparse
import csv
import json
from pathlib import Path

COLONNES = [
    ("reponses", "Réponses", "{}"),
    ("echecs_format", "Échecs de format", "{}"),
    ("taux_valeurs_fausses", "Valeurs fausses", "{:.1%}"),
    ("taux_inventions", "Clauses inventées", "{:.1%}"),
    ("taux_champs_omis", "Champs omis", "{:.1%}"),
    ("taux_pieges_manques", "Pièges manqués", "{:.1%}"),
    ("fausses_assurances", "Fausses assurances", "{}"),
    ("part_erreurs_confiance_haute", "Erreurs en confiance haute", "{:.0%}"),
    ("fausses_alertes_temoins", "Fausses alertes (témoins)", "{}"),
    ("variation_champs", "Variation entre passes", "{:.1%}"),
]


def rapport(dossier):
    dossier = Path(dossier)
    notes = json.loads((dossier / "notes.json").read_text(encoding="utf-8"))
    lancement = dossier / "lancement.json"
    meta = json.loads(lancement.read_text(encoding="utf-8")) if lancement.exists() else {}
    modeles, seuils = notes["modeles"], notes["seuils"]

    with (dossier / "tableau_modeles.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["modele"] + [c[0] for c in COLONNES] + ["utilisable_sous_relecture"])
        for m, v in modeles.items():
            w.writerow([m] + [v[c[0]] for c in COLONNES] + [v["utilisable_sous_relecture"]])

    l = ["# Rapport : erreurs des modèles ouverts sur des contrats à vérité connue", ""]
    if meta:
        l += [f"Lancement du {meta.get('debut', '?')[:10]}, {meta.get('passes')} passes, température {meta.get('temperature')}, "
              f"corpus de graine {meta.get('graine_corpus')}, {len(meta.get('contrats', []))} contrats.", ""]
    l += ["Seuils fixés avant les tests : zéro fausse assurance, moins de "
          f"{seuils['taux_valeurs_fausses']:.0%} de valeurs fausses, moins de {seuils['taux_inventions']:.0%} de clauses inventées, "
          f"moins de {seuils['taux_pieges_manques']:.0%} de pièges manqués.", "",
          "## I- Vue d'ensemble", "",
          "| Modèle | " + " | ".join(c[1] for c in COLONNES) + " | Sous relecture |",
          "|---" * (len(COLONNES) + 2) + "|"]
    for m, v in modeles.items():
        l.append(f"| {m} | " + " | ".join(c[2].format(v[c[0]]) for c in COLONNES)
                 + f" | {'oui' if v['utilisable_sous_relecture'] else 'non'} |")
    l += ["", "## II- Pièges manqués, par catégorie", ""]
    cats = sorted({k for v in modeles.values() for k in v["pieges_manques_par_categorie"]})
    if cats:
        l += ["| Modèle | " + " | ".join(cats) + " |", "|---" * (len(cats) + 1) + "|"]
        for m, v in modeles.items():
            l.append(f"| {m} | " + " | ".join(str(v["pieges_manques_par_categorie"].get(k, 0)) for k in cats) + " |")
    else:
        l.append("Aucun piège manqué.")
    l += ["", "## III- Ce qu'un humain doit vérifier", "",
          "-> Les erreurs marquées en confiance haute sont celles qui passent sans relecture : leur part par modèle est dans la colonne « Erreurs en confiance haute ».",
          "-> Les catégories de pièges les plus manquées (section II) sont celles à relire en priorité.",
          "-> Les réponses de l'échantillon de contrôle (`echantillon_controle.json`) sont à relire à la main avant publication (protocole, section VI).", "",
          "## IV- Limites", "",
          "-> Corpus fictif et liste fermée de catégories : voir le protocole, section VIII.", ""]
    (dossier / "rapport.md").write_text("\n".join(l), encoding="utf-8")
    return dossier / "rapport.md"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dossier")
    print(rapport(ap.parse_args().dossier))


if __name__ == "__main__":
    main()
