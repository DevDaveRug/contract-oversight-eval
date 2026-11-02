"""Fonctions partagées : chargement du corpus, normalisation, comparaisons.

Les règles de comparaison suivent le protocole, section IV « Règles de comparaison ».
"""
import difflib
import json
import re
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
CORPUS = ICI.parent / "corpus"
CONSIGNE = ICI / "consigne.txt"

CHAMPS_NOMBRE = ("_eur", "_mois", "_jours", "_ans", "_pct_mois")
MOTS_VIDES = {"de", "du", "des", "la", "le", "les", "l", "d", "et", "droit", "au", "a"}


def charger_corpus(dossier=CORPUS):
    verite = json.loads((Path(dossier) / "verite.json").read_text(encoding="utf-8"))
    textes = {c["id"]: (Path(dossier) / "contrats" / f"{c['id']}.txt").read_text(encoding="utf-8")
              for c in verite["contrats"]}
    return verite, textes


def consigne_pour(texte):
    return CONSIGNE.read_text(encoding="utf-8").replace("{contrat}", texte)


def sans_accents(s):
    return "".join(ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn")


def mots(s):
    s = sans_accents(str(s)).lower()
    s = re.sub(r"(?<=\d)[\s  ](?=\d)", "", s)  # 4 800 -> 4800
    return re.findall(r"[a-z0-9]+(?:[.,][0-9]+)?", s)


def est_nombre(champ):
    return champ.endswith(CHAMPS_NOMBRE)


def en_nombre(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    m = re.search(r"-?\d+(?:[.,]\d+)?", re.sub(r"(?<=\d)[\s  ](?=\d)", "", str(v)))
    return float(m.group().replace(",", ".")) if m else None


def en_booleen(v):
    if isinstance(v, bool):
        return v
    s = sans_accents(str(v)).lower().strip()
    if s in ("true", "vrai", "oui", "yes", "1"):
        return True
    if s in ("false", "faux", "non", "no", "0"):
        return False
    return None


def est_nul(v):
    return v is None or (isinstance(v, str) and sans_accents(v).strip().lower() in ("", "null", "none", "absent", "n/a", "na", "non precise", "non mentionne"))


def egal(champ, verite, valeur):
    """Vrai si la valeur du modèle correspond à la vérité (les deux non nulles)."""
    if est_nombre(champ):
        a, b = float(verite), en_nombre(valeur)
        if b is None:
            return False
        return abs(a - b) <= 0.005 * max(abs(a), 1e-9) if a else b == 0
    if champ == "renouvellement_tacite":
        return en_booleen(valeur) is verite
    if champ == "date_effet":
        return str(valeur).strip()[:10] == verite
    attendus = [m for m in mots(verite) if m not in MOTS_VIDES]
    donnes = set(mots(valeur))
    return bool(attendus) and all(m in donnes for m in attendus)


def present_dans_texte(champ, valeur, texte):
    """La valeur figure-t-elle quelque part dans le contrat ? Sert à séparer valeur fausse et invention."""
    if est_nombre(champ):
        n = en_nombre(valeur)
        if n is None:
            return False
        cibles = {str(int(n))} if n == int(n) else {str(n), str(n).replace(".", ",")}
        return any(c in mots(texte) for c in cibles)
    if champ == "renouvellement_tacite":
        return True  # un booléen n'est jamais inventé : il se trompe ou non
    if champ == "date_effet":
        return False
    m = [x for x in mots(valeur) if x not in MOTS_VIDES]
    t = set(mots(texte))
    return bool(m) and all(x in t for x in m)


def couverture_ordonnee(citation, phrase):
    """Part des mots de la citation retrouvés, dans l'ordre, dans la phrase."""
    a, b = mots(citation), mots(phrase)
    if not a:
        return 0.0
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return sum(bl.size for bl in sm.get_matching_blocks()) / len(a)


def citation_trouvee(citation, texte, seuil=0.8):
    if not citation or not str(citation).strip():
        return False
    return any(couverture_ordonnee(citation, ligne) >= seuil for ligne in texte.splitlines() if ligne.strip())


def recoupe(citation, extrait, seuil=0.5):
    a = set(mots(citation))
    return bool(a) and len(a & set(mots(extrait))) / len(a) >= seuil


def lire_json(brut):
    """Extrait l'objet JSON d'une réponse de modèle (tolère les blocs de code et le texte autour)."""
    if isinstance(brut, dict):
        return brut
    s = str(brut)
    s = re.sub(r"<think>.*?</think>", "", s, flags=re.S)
    i, j = s.find("{"), s.rfind("}")
    if i < 0 or j <= i:
        return None
    try:
        obj = json.loads(s[i:j + 1])
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None
