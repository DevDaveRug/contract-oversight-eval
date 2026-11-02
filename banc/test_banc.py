"""Tests du banc d'essai, sans GPU ni réseau : python3 -m unittest test_banc.py (depuis banc/)."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import commun as C  # noqa: E402
import interroger  # noqa: E402
import noter  # noqa: E402
import rapport  # noqa: E402
import simuler  # noqa: E402


class Comparaisons(unittest.TestCase):
    def test_nombres(self):
        self.assertTrue(C.egal("montant_eur", 4800, "4 800 euros HT"))
        self.assertTrue(C.egal("penalite_retard_pct_mois", 15, "15 %"))
        self.assertFalse(C.egal("montant_eur", 4800, 6300))

    def test_textes(self):
        self.assertTrue(C.egal("juridiction", "Reims", "Tribunaux de Reims"))
        self.assertTrue(C.egal("loi_applicable", "droit français", "Droit Francais"))
        self.assertFalse(C.egal("loi_applicable", "droit luxembourgeois", "droit français"))

    def test_booleen_et_date(self):
        self.assertTrue(C.egal("renouvellement_tacite", True, "oui"))
        self.assertFalse(C.egal("renouvellement_tacite", False, True))
        self.assertTrue(C.egal("date_effet", "2026-04-24", "2026-04-24"))

    def test_lecture_json_tolerante(self):
        self.assertEqual(C.lire_json('<think>bla { </think>```json\n{"a": 1}\n```'), {"a": 1})
        self.assertIsNone(C.lire_json("pas de json"))

    def test_citation(self):
        texte = "Article 1 - Prix\nLe prix forfaitaire retenu est de 4 800 euros HT pour la durée du contrat.\n"
        self.assertTrue(C.citation_trouvee("Le prix forfaitaire retenu est de 4800 euros HT", texte))
        self.assertFalse(C.citation_trouvee("Le client cède son fonds de commerce.", texte))


class Notation(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dossier = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_parfait_sans_erreur(self):
        simuler.simuler(self.dossier, profils={"p": simuler.PROFILS["simule-parfait"]})
        m = noter.noter_lancement(self.dossier)["modeles"]["p"]
        self.assertEqual(m["reponses"], 60)
        for k in ("taux_valeurs_fausses", "taux_inventions", "taux_champs_omis", "taux_pieges_manques"):
            self.assertEqual(m[k], 0, k)
        self.assertEqual(m["fausses_assurances"], 0)
        self.assertEqual(m["fausses_alertes"], 0)
        self.assertTrue(m["utilisable_sous_relecture"])

    def test_erreurs_injectees_retrouvees_exactement(self):
        profil = dict(simuler.PROFILS["simule-bavard"], format=0)
        inj = simuler.simuler(self.dossier, graine=11, profils={"b": profil})["b"]
        m = noter.noter_lancement(self.dossier)["modeles"]["b"]
        c = m["comptes"]
        self.assertGreater(inj["faux"] + inj["invente"] + inj["manque"], 0)
        self.assertEqual(c["valeurs_fausses"], inj["faux"])
        self.assertEqual(c["inventions"], inj["invente"])
        self.assertEqual(c["champs_omis"], inj["omis"])
        self.assertEqual(c["pieges"] - c["pieges_detectes"], inj["manque"])
        self.assertEqual(m["fausses_alertes"], inj["alerte"])
        self.assertEqual(m["fausses_assurances"], inj["assurance"])
        self.assertFalse(m["utilisable_sous_relecture"])

    def test_echec_de_format(self):
        inj = simuler.simuler(self.dossier, graine=3, profils={"f": dict(simuler.PROFILS["simule-parfait"], format=1)})["f"]
        m = noter.noter_lancement(self.dossier)["modeles"]["f"]
        self.assertEqual(m["echecs_format"], inj["format"])
        self.assertEqual(m["taux_champs_omis"], 1)
        self.assertEqual(m["taux_pieges_manques"], 1)

    def test_valeur_leurre_comptee_fausse_pas_inventee(self):
        verite, textes = C.charger_corpus()
        nda = next(c for c in verite["contrats"] if c["type"] == "nda" and c["champs"]["montant_eur"] is None
                   and any(p["categorie"] == "penalite_excessive" for p in c["pieges"]))
        rep = {"champs": {"montant_eur": {"valeur": 500000, "confiance": "haute"}}, "risques": [], "risque_global": "eleve"}
        n = noter.noter_reponse(nda, textes[nda["id"]], json.dumps(rep), verite["champs"])
        self.assertEqual(n["valeurs_fausses"], 1)
        self.assertEqual(n["inventions"], 0)

    def test_rapport_et_echantillon(self):
        simuler.simuler(self.dossier)
        noter.noter_lancement(self.dossier)
        txt = rapport.rapport(self.dossier).read_text(encoding="utf-8")
        self.assertIn("simule-parfait", txt)
        self.assertEqual(len(json.loads((self.dossier / "echantillon_controle.json").read_text())), 24)
        self.assertTrue((self.dossier / "tableau_modeles.csv").exists())


class Interrogation(unittest.TestCase):
    def test_enregistre_et_reprend(self):
        appels = []

        def faux_serveur(base_url, modele, consigne, temperature, graine, delai, cle=None):
            appels.append((modele, graine))
            self.assertIn("CONTRAT :", consigne)
            return {"choices": [{"message": {"content": '{"champs": {}, "risques": [], "risque_global": "moyen"}'}}],
                    "model": modele}, 0.01

        with tempfile.TemporaryDirectory() as d:
            argv = ["--sortie", d, "--modeles", "m:1", "--passes", "2", "--contrats", "nda-01", "cgv-02"]
            self.assertEqual(interroger.main(argv, faux_serveur), 0)
            self.assertEqual(len(appels), 4)
            self.assertEqual(len(list(Path(d, "reponses", "m_1").glob("*.json"))), 4)
            interroger.main(argv, faux_serveur)  # reprise : rien n'est redemandé
            self.assertEqual(len(appels), 4)
            res = noter.noter_lancement(d)["modeles"]["m:1"]
            self.assertEqual(res["reponses"], 4)


if __name__ == "__main__":
    unittest.main()
