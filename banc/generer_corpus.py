"""Génère le corpus de contrats fictifs et sa vérité connue.

Reproductible : même graine, même corpus, octet pour octet.
Usage : python3 generer_corpus.py [--graine 20261101] [--sortie ../corpus]

Chaque contrat porte :
-> des champs (montant, durée, préavis...) présents ou absents, notés dans la vérité ;
-> des leurres (un montant de devis initial, une date de signature) qui ne sont pas la bonne valeur ;
-> zéro à trois pièges, chacun rattaché à une catégorie de risque de la liste fermée.
Quatre contrats sur vingt sont des témoins sans piège, pour mesurer les fausses alertes.
Trois à cinq articles neutres (force majeure, assurances, données personnelles...) noient les pièges.
"""
import argparse
import json
import random
from datetime import date, timedelta
from pathlib import Path

CHAMPS = [
    "partie_a", "partie_b", "montant_eur", "date_effet", "duree_mois", "preavis_jours",
    "renouvellement_tacite", "penalite_retard_pct_mois", "loi_applicable", "juridiction",
    "plafond_responsabilite_eur", "depot_garantie_eur", "duree_confidentialite_ans",
    "non_concurrence_mois",
]

CATEGORIES_RISQUE = [
    "renouvellement_tacite_piege",      # reconduction longue ou préavis très long, noyée
    "penalite_excessive",               # pénalité disproportionnée
    "resiliation_unilaterale",          # une seule partie peut résilier sans motif
    "non_concurrence_large",            # non-concurrence longue ou sans contrepartie
    "responsabilite_desequilibree",     # plafond dérisoire ou exclusion totale au profit d'une partie
    "juridiction_eloignee",             # juridiction ou loi étrangère pour un contrat local
    "cession_propriete_intellectuelle", # cession totale et gratuite des créations
    "revision_prix_unilaterale",        # le prix peut monter sans accord
]

SOCIETES = [
    "Atelier Verrand SARL", "Boréal Conseil SAS", "Cabinet Lhermite", "Dunemont Formation SAS",
    "Éclats de Lune EURL", "Forges de Saint-Aubin SA", "Groupe Hallier SAS", "Ibis Rouge Studio",
    "Jardins Marceau SCOP", "Kervella Logistique SARL", "Lumière Blanche SAS", "Moulin Neuf SARL",
    "Nord-Est Numérique SAS", "Oriel Patrimoine SCI", "Pierre-Feuille Éditions", "Quai Ouest SAS",
]
PERSONNES = [
    "Claire Dumontel", "Marc Aubrac", "Sophie Vellard", "Julien Carrère", "Inès Maraval",
    "Thomas Rieuvert", "Hélène Gasquet", "Pierre Sandral",
]
VILLES = ["Colmar", "Mulhouse", "Strasbourg", "Nancy", "Dijon", "Besançon", "Metz", "Reims"]
ETRANGER = [("droit luxembourgeois", "Luxembourg"), ("droit de l'État du Delaware", "Wilmington"),
            ("droit singapourien", "Singapour")]


def fr_montant(x):
    return f"{x:,}".replace(",", " ") + " euros"


def fr_date(d):
    mois = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
            "septembre", "octobre", "novembre", "décembre"][d.month - 1]
    return f"{d.day} {mois} {d.year}"


class Contrat:
    def __init__(self, ident, type_):
        self.id = ident
        self.type = type_
        self.articles = []
        self.verite = {c: None for c in CHAMPS}
        self.pieges = []
        self.leurres = []

    def art(self, titre, texte):
        self.articles.append((titre, texte))

    def piege(self, categorie, extrait, explication):
        assert categorie in CATEGORIES_RISQUE
        self.pieges.append({"categorie": categorie, "extrait": extrait, "explication": explication})
        return extrait

    def texte(self, titre):
        lignes = [titre.upper(), ""]
        for i, (t, corps) in enumerate(self.articles, 1):
            lignes += [f"Article {i} - {t}", corps, ""]
        lignes.append("Fait en deux exemplaires originaux.")
        return "\n".join(lignes) + "\n"


def commun(c, r, a, b, montant, effet, signature, duree, preavis, ville, loi_etrangere):
    c.verite.update(partie_a=a, partie_b=b, date_effet=effet.isoformat(), duree_mois=duree)
    c.leurres.append({"champ": "date_effet", "valeur": signature.isoformat(),
                      "pourquoi": "date de signature, pas date d'effet"})
    if loi_etrangere:
        loi, juri = loi_etrangere
        c.verite.update(loi_applicable=loi, juridiction=juri)
        clause = c.piege("juridiction_eloignee",
                         f"Le présent contrat est régi par le {loi}. Tout litige sera porté devant les tribunaux de {juri}.",
                         "Contrat entre deux parties françaises, exécuté en France, renvoyé vers un droit et un tribunal étrangers.")
    else:
        c.verite.update(loi_applicable="droit français", juridiction=ville)
        clause = (f"Le présent contrat est régi par le droit français. Tout litige relève de la compétence "
                  f"exclusive des tribunaux de {ville}.")
    return clause


def options_pieges(r, n):
    return r.sample(range(4), n)


def prestation(c, r, pieges):
    a, b = r.sample(SOCIETES, 2)
    montant = r.choice([4800, 7200, 9600, 12500, 18000])
    initial = montant + r.choice([1500, 2400, 3000])
    signature = date(2026, r.randint(1, 9), r.randint(1, 28))
    effet = signature + timedelta(days=r.choice([10, 15, 31]))
    duree = r.choice([6, 12, 24])
    preavis = r.choice([30, 60])
    ville = r.choice(VILLES)
    c.verite["montant_eur"] = montant
    c.leurres.append({"champ": "montant_eur", "valeur": initial, "pourquoi": "devis initial révisé"})
    c.art("Parties", f"Entre {a}, ci-après le Client, et {b}, ci-après le Prestataire. "
          f"Le présent contrat est signé le {fr_date(signature)}.")
    c.art("Objet", "Le Prestataire réalise pour le Client une mission d'accompagnement commercial : "
          "audit du processus de vente, formation de l'équipe et suivi mensuel des indicateurs.")
    c.art("Prix", f"Le devis initial n° D-{r.randint(100, 999)} d'un montant de {fr_montant(initial)} HT a été révisé "
          f"d'un commun accord. Le prix forfaitaire retenu est de {fr_montant(montant)} HT pour la durée du contrat, "
          "payable en mensualités égales à trente jours fin de mois.")
    if 0 in pieges:
        c.verite["penalite_retard_pct_mois"] = 15
        c.art("Retard de paiement", c.piege("penalite_excessive",
              "Tout retard de paiement entraîne de plein droit une pénalité de 15 % du montant dû par mois de retard.",
              "15 % par mois, soit 180 % par an, sans commune mesure avec le taux légal."))
    else:
        c.verite["penalite_retard_pct_mois"] = 1
        c.art("Retard de paiement", "Tout retard de paiement entraîne une pénalité de 1 % du montant dû par mois de retard, "
              "outre l'indemnité forfaitaire légale de recouvrement.")
    c.art("Durée", f"Le contrat prend effet le {fr_date(effet)} pour une durée de {duree} mois.")
    if 1 in pieges:
        c.verite.update(renouvellement_tacite=True, preavis_jours=180)
        c.art("Reconduction", c.piege("renouvellement_tacite_piege",
              f"À défaut de dénonciation par lettre recommandée au moins 180 jours avant son terme, le contrat est reconduit tacitement pour une durée de {duree * 2} mois.",
              "Préavis de six mois et reconduction pour une durée double, dans un article séparé de la durée."))
    else:
        c.verite.update(renouvellement_tacite=False, preavis_jours=preavis)
        c.art("Fin du contrat", f"Le contrat prend fin à son terme sans reconduction. Chaque partie peut y mettre fin "
              f"de manière anticipée moyennant un préavis de {preavis} jours.")
    if 2 in pieges:
        c.art("Propriété intellectuelle", c.piege("cession_propriete_intellectuelle",
              "Le Prestataire cède au Client, à titre exclusif et sans contrepartie supplémentaire, l'ensemble des droits sur ses méthodes, outils et supports, y compris ceux antérieurs au présent contrat.",
              "Cession gratuite incluant le savoir-faire antérieur du prestataire."))
    else:
        c.art("Propriété intellectuelle", "Les supports créés pour la mission sont remis au Client pour son usage interne. "
              "Le Prestataire conserve ses méthodes et outils antérieurs.")
    if 3 in pieges:
        c.verite["plafond_responsabilite_eur"] = 100
        c.art("Responsabilité", c.piege("responsabilite_desequilibree",
              "La responsabilité du Prestataire est limitée, toutes causes confondues, à la somme de 100 euros.",
              f"Plafond de 100 euros pour une mission de {montant} euros."))
    else:
        c.verite["plafond_responsabilite_eur"] = montant
        c.art("Responsabilité", "La responsabilité de chaque partie est limitée au montant total du prix du contrat.")
    c.art("Droit applicable", commun(c, r, a, b, montant, effet, signature, duree, preavis, ville, None))
    return "Contrat de prestation de services"


def bail(c, r, pieges):
    bailleur = r.choice([s for s in SOCIETES if "SCI" in s] + ["SCI Les Tilleuls", "SCI Rue Haute"])
    preneur = r.choice(SOCIETES)
    loyer = r.choice([850, 1200, 1650, 2300])
    signature = date(2026, r.randint(1, 9), r.randint(1, 28))
    effet = signature + timedelta(days=r.choice([1, 15, 30]))
    duree = 36
    ville = r.choice(VILLES)
    c.verite["montant_eur"] = loyer
    c.leurres.append({"champ": "montant_eur", "valeur": loyer * 12, "pourquoi": "loyer annuel, le champ attend le loyer mensuel"})
    c.art("Parties", f"Entre {bailleur}, ci-après le Bailleur, et {preneur}, ci-après le Preneur. "
          f"Signé le {fr_date(signature)}.")
    c.art("Désignation", f"Le Bailleur loue au Preneur un local à usage de bureau de {r.choice([45, 60, 85, 120])} m², situé à {ville}.")
    c.art("Durée", f"Le bail est consenti pour une durée de {duree} mois à compter du {fr_date(effet)}, "
          "soit un bail dérogatoire au statut des baux commerciaux.")
    c.art("Loyer", f"Le loyer est fixé à {fr_montant(loyer)} hors charges par mois, soit {fr_montant(loyer * 12)} par an, "
          "payable d'avance le premier de chaque mois.")
    if 0 in pieges:
        c.art("Révision", c.piege("revision_prix_unilaterale",
              "Le Bailleur pourra réviser le loyer à tout moment, par simple notification, en fonction de l'évolution du marché local qu'il apprécie seul.",
              "Révision à la discrétion du bailleur, sans indice ni plafond."))
    else:
        c.art("Révision", "Le loyer est révisé chaque année à la date anniversaire selon l'indice des loyers des activités tertiaires.")
    if 1 in pieges:
        c.verite["depot_garantie_eur"] = loyer * 12
        c.art("Dépôt de garantie", c.piege("penalite_excessive",
              f"Le Preneur verse un dépôt de garantie de {fr_montant(loyer * 12)}, qui reste acquis au Bailleur en cas de départ avant le terme, quel qu'en soit le motif.",
              "Douze mois de loyer, perdus en totalité en cas de départ anticipé."))
    else:
        c.verite["depot_garantie_eur"] = loyer * 2
        c.art("Dépôt de garantie", f"Le Preneur verse un dépôt de garantie de {fr_montant(loyer * 2)}, restitué dans les deux mois suivant la remise des clés.")
    if 2 in pieges:
        c.verite["preavis_jours"] = 90
        c.art("Résiliation", c.piege("resiliation_unilaterale",
              "Le Bailleur peut résilier le bail à tout moment, sans motif, moyennant un préavis de 90 jours. Le Preneur ne peut résilier avant le terme.",
              "Faculté de sortie réservée au seul bailleur."))
    else:
        c.verite["preavis_jours"] = 90
        c.art("Résiliation", "Chaque partie peut résilier le bail moyennant un préavis de 90 jours par lettre recommandée.")
    c.verite["renouvellement_tacite"] = False
    loi = r.choice(ETRANGER) if 3 in pieges else None
    c.art("Litiges", commun(c, r, bailleur, preneur, loyer, effet, signature, duree, 90, ville, loi))
    return "Bail de local professionnel"


def nda(c, r, pieges):
    a, b = r.sample(SOCIETES, 2)
    signature = date(2026, r.randint(1, 9), r.randint(1, 28))
    effet = signature
    ville = r.choice(VILLES)
    c.art("Parties", f"Entre {a}, ci-après la Partie divulgatrice, et {b}, ci-après la Partie réceptrice. "
          f"Signé et applicable à compter du {fr_date(signature)}.")
    c.art("Objet", "Les parties étudient un projet de partenariat commercial et échangent à ce titre des informations confidentielles.")
    c.art("Informations confidentielles", "Sont confidentielles toutes les informations transmises par écrit et marquées comme telles.")
    duree = r.choice([12, 24])
    c.art("Durée", f"Le présent accord est conclu pour une durée de {duree} mois.")
    if 0 in pieges:
        c.verite["duree_confidentialite_ans"] = 99
        c.art("Durée de l'obligation", c.piege("non_concurrence_large",
              "L'obligation de confidentialité survit 99 ans à l'expiration de l'accord et interdit à la Partie réceptrice toute activité concurrente pendant cette période.",
              "Une non-concurrence de fait, sans limite raisonnable ni contrepartie, cachée dans la clause de confidentialité."))
        c.verite["non_concurrence_mois"] = 99 * 12
    else:
        ans = r.choice([3, 5])
        c.verite["duree_confidentialite_ans"] = ans
        c.art("Durée de l'obligation", f"L'obligation de confidentialité survit {ans} ans à l'expiration de l'accord.")
    if 1 in pieges:
        c.art("Sanction", c.piege("penalite_excessive",
              "Toute divulgation, même involontaire, entraîne le paiement d'une indemnité forfaitaire de 500 000 euros, sans préjudice de dommages et intérêts complémentaires.",
              "Montant forfaitaire sans lien avec un préjudice, même pour une faute involontaire."))
        # montant_eur reste absent : une indemnité forfaitaire n'est pas un prix (définition dans la consigne)
    if 2 in pieges:
        c.art("Résultats", c.piege("cession_propriete_intellectuelle",
              "Toute idée, amélioration ou invention conçue par la Partie réceptrice pendant la durée de l'accord appartient à la Partie divulgatrice, sans contrepartie.",
              "Un accord de confidentialité qui transfère les inventions de la partie réceptrice."))
    c.verite["renouvellement_tacite"] = False
    loi = r.choice(ETRANGER) if 3 in pieges else None
    c.art("Litiges", commun(c, r, a, b, None, effet, signature, duree, None, ville, loi))
    return "Accord de confidentialité"


def cgv(c, r, pieges):
    a = r.choice([s for s in SOCIETES if "SCI" not in s])
    b = r.choice(PERSONNES) + ", entrepreneur individuel"
    prix = r.choice([49, 89, 149, 290])
    signature = date(2026, r.randint(1, 9), r.randint(1, 28))
    effet = signature
    ville = r.choice(VILLES)
    c.verite["montant_eur"] = prix
    c.leurres.append({"champ": "montant_eur", "valeur": prix * 12, "pourquoi": "total annuel, le champ attend le prix mensuel"})
    c.art("Parties", f"Conditions générales de vente du service en ligne édité par {a}, ci-après l'Éditeur, acceptées par {b}, "
          f"ci-après le Client, le {fr_date(signature)}.")
    c.art("Service", "L'Éditeur fournit un logiciel de gestion de rendez-vous accessible en ligne.")
    c.art("Prix", f"L'abonnement est facturé {fr_montant(prix)} HT par mois, soit {fr_montant(prix * 12)} HT par an, payable d'avance.")
    duree = 12
    if 0 in pieges:
        c.verite.update(renouvellement_tacite=True, preavis_jours=90)
        c.art("Durée", f"L'abonnement est souscrit pour {duree} mois à compter de son acceptation.")
        c.art("Dispositions diverses", "Les présentes conditions peuvent être consultées à tout moment sur le site de l'Éditeur. "
              + c.piege("renouvellement_tacite_piege",
                        "Sauf résiliation notifiée au moins 90 jours avant l'échéance, l'abonnement est renouvelé pour 36 mois, le prix de la période étant exigible en totalité.",
                        "Renouvellement de trois ans, payable d'avance, glissé dans les dispositions diverses."))
    else:
        c.verite.update(renouvellement_tacite=True, preavis_jours=30)
        c.art("Durée", f"L'abonnement est souscrit pour {duree} mois à compter de son acceptation et se renouvelle par période d'un mois, "
              "résiliable à tout moment avec un préavis de 30 jours.")
    if 1 in pieges:
        c.art("Évolution du prix", c.piege("revision_prix_unilaterale",
              "L'Éditeur peut modifier ses tarifs à tout moment ; le nouveau prix s'applique dès sa publication sur le site, sans autre information du Client.",
              "Hausse sans préavis ni faculté de résiliation."))
    if 2 in pieges:
        c.verite["plafond_responsabilite_eur"] = 0
        c.art("Responsabilité", c.piege("responsabilite_desequilibree",
              "L'Éditeur n'est responsable d'aucun dommage, direct ou indirect, y compris la perte des données du Client.",
              "Exclusion totale, y compris de la perte de données, pour un service qui les héberge."))
    else:
        c.verite["plafond_responsabilite_eur"] = prix * 12
        c.art("Responsabilité", "La responsabilité de l'Éditeur est limitée aux sommes versées par le Client au cours des douze derniers mois.")
    loi = r.choice(ETRANGER) if 3 in pieges else None
    c.art("Litiges", commun(c, r, a, b, prix, effet, signature, duree, None, ville, loi))
    return "Conditions générales de vente"


NEUTRES = [
    ("Force majeure", "Aucune des parties ne pourra être tenue pour responsable d'un manquement résultant d'un cas de force majeure "
     "au sens de l'article 1218 du Code civil. La partie empêchée en informe l'autre sans délai ; si l'empêchement dure plus "
     "de trente jours, chaque partie peut mettre fin au contrat sans indemnité."),
    ("Assurances", "Chaque partie déclare être titulaire d'une police d'assurance de responsabilité civile professionnelle "
     "couvrant les conséquences de son activité, et s'engage à en justifier à première demande."),
    ("Données personnelles", "Les parties s'engagent à traiter les données personnelles éventuellement échangées dans le respect "
     "du règlement (UE) 2016/679. Chaque partie reste responsable des traitements qu'elle met en œuvre pour son propre compte."),
    ("Notifications", "Toute notification au titre du présent contrat est faite par écrit, par lettre recommandée avec accusé de "
     "réception ou par courrier électronique avec accusé de lecture, aux adresses communiquées par chaque partie."),
    ("Intégralité", "Le présent contrat exprime l'intégralité de l'accord des parties et remplace tout échange antérieur portant "
     "sur le même objet. Toute modification fait l'objet d'un avenant signé des deux parties."),
    ("Indépendance des parties", "Les parties agissent en toute indépendance. Aucune d'elles ne peut prendre d'engagement au nom "
     "et pour le compte de l'autre."),
    ("Non-renonciation", "Le fait pour une partie de ne pas se prévaloir d'un manquement de l'autre partie ne vaut pas renonciation "
     "à s'en prévaloir ultérieurement."),
    ("Divisibilité", "Si une stipulation du présent contrat est déclarée nulle, les autres stipulations conservent leur plein effet."),
]


def remplir(c, r):
    """Insère trois à cinq articles neutres à des places tirées au sort, jamais avant les parties ni après les litiges."""
    for art in r.sample(NEUTRES, r.randint(3, 5)):
        c.articles.insert(r.randint(1, len(c.articles) - 1), art)


TYPES = [("prestation", prestation), ("bail", bail), ("nda", nda), ("cgv", cgv)]


def generer(graine):
    r = random.Random(graine)
    contrats = []
    for type_, fonction in TYPES:
        for k in range(1, 6):
            c = Contrat(f"{type_}-{k:02d}", type_)
            n = 0 if k == 5 else r.choice([1, 2, 3])  # le cinquième de chaque type est un témoin sans piège
            titre = fonction(c, r, options_pieges(r, n))
            remplir(c, r)
            contrats.append((c, c.texte(titre)))
    return contrats


def fiche_relecteur(verite):
    """Fiche lisible pour le relecteur : ce qu'il doit valider, contrat par contrat."""
    l = ["# Fiche du relecteur : pièges et vérité connue", "",
         f"Corpus généré par `banc/generer_corpus.py`, graine {verite['graine']}. Fichier produit par le générateur : "
         "toute correction se fait dans le générateur, puis le corpus est régénéré.", "",
         "Pour chaque contrat (texte dans `contrats/<id>.txt`), trois questions :", "",
         "-> 1- Chaque piège listé est-il un vrai risque pour un dirigeant qui signe ?",
         "-> 2- Le contrat porte-t-il un risque qui n'est PAS listé ? (pour les témoins : la liste doit être vide)",
         "-> 3- Les valeurs de la vérité sont-elles celles qu'un juriste lirait ?", ""]
    for c in verite["contrats"]:
        l += [f"## {c['id']} ({c['type']})", ""]
        if c["pieges"]:
            for p in c["pieges"]:
                l += [f"-> **{p['categorie']}** : « {p['extrait']} »", f"   Pourquoi : {p['explication']}"]
        else:
            l.append("-> Témoin : aucun piège.")
        presents = {k: v for k, v in c["champs"].items() if v is not None}
        l += ["", "Vérité : " + " ; ".join(f"{k} = {v}" for k, v in presents.items())]
        if c["leurres"]:
            l.append("Leurres : " + " ; ".join(f"{x['champ']} {x['valeur']} ({x['pourquoi']})" for x in c["leurres"]))
        l += ["", "Avis du relecteur : ", ""]
    return "\n".join(l) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--graine", type=int, default=20261101)
    ap.add_argument("--sortie", default=str(Path(__file__).resolve().parent.parent / "corpus"))
    a = ap.parse_args()
    sortie = Path(a.sortie)
    (sortie / "contrats").mkdir(parents=True, exist_ok=True)
    verite = {"graine": a.graine, "champs": CHAMPS, "categories_risque": CATEGORIES_RISQUE, "contrats": []}
    for c, texte in generer(a.graine):
        (sortie / "contrats" / f"{c.id}.txt").write_text(texte, encoding="utf-8")
        for p in c.pieges:
            assert p["extrait"] in texte, (c.id, p["extrait"][:40])
        verite["contrats"].append({"id": c.id, "type": c.type, "champs": c.verite,
                                   "pieges": c.pieges, "leurres": c.leurres})
    (sortie / "verite.json").write_text(json.dumps(verite, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (sortie / "fiche_relecteur.md").write_text(fiche_relecteur(verite), encoding="utf-8")
    n_pieges = sum(len(x["pieges"]) for x in verite["contrats"])
    print(f"{len(verite['contrats'])} contrats, {n_pieges} pièges, sortie : {sortie}")


if __name__ == "__main__":
    main()
