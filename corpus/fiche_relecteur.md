# Fiche du relecteur : pièges et vérité connue

Corpus généré par `banc/generer_corpus.py`, graine 20261101. Fichier produit par le générateur : toute correction se fait dans le générateur, puis le corpus est régénéré.

Pour chaque contrat (texte dans `contrats/<id>.txt`), trois questions :

-> 1- Chaque piège listé est-il un vrai risque pour un dirigeant qui signe ?
-> 2- Le contrat porte-t-il un risque qui n'est PAS listé ? (pour les témoins : la liste doit être vide)
-> 3- Les valeurs de la vérité sont-elles celles qu'un juriste lirait ?

## prestation-01 (prestation)

-> **penalite_excessive** : « Tout retard de paiement entraîne de plein droit une pénalité de 15 % du montant dû par mois de retard. »
   Pourquoi : 15 % par mois, soit 180 % par an, sans commune mesure avec le taux légal.
-> **renouvellement_tacite_piege** : « À défaut de dénonciation par lettre recommandée au moins 180 jours avant son terme, le contrat est reconduit tacitement pour une durée de 12 mois. »
   Pourquoi : Préavis de six mois et reconduction pour une durée double, dans un article séparé de la durée.
-> **responsabilite_desequilibree** : « La responsabilité du Prestataire est limitée, toutes causes confondues, à la somme de 100 euros. »
   Pourquoi : Plafond de 100 euros pour une mission de 4800 euros.

Vérité : partie_a = Boréal Conseil SAS ; partie_b = Moulin Neuf SARL ; montant_eur = 4800 ; date_effet = 2026-04-24 ; duree_mois = 6 ; preavis_jours = 180 ; renouvellement_tacite = True ; penalite_retard_pct_mois = 15 ; loi_applicable = droit français ; juridiction = Reims ; plafond_responsabilite_eur = 100
Leurres : montant_eur 6300 (devis initial révisé) ; date_effet 2026-04-09 (date de signature, pas date d'effet)

Avis du relecteur : 

## prestation-02 (prestation)

-> **responsabilite_desequilibree** : « La responsabilité du Prestataire est limitée, toutes causes confondues, à la somme de 100 euros. »
   Pourquoi : Plafond de 100 euros pour une mission de 7200 euros.

Vérité : partie_a = Atelier Verrand SARL ; partie_b = Pierre-Feuille Éditions ; montant_eur = 7200 ; date_effet = 2026-03-08 ; duree_mois = 6 ; preavis_jours = 30 ; renouvellement_tacite = False ; penalite_retard_pct_mois = 1 ; loi_applicable = droit français ; juridiction = Dijon ; plafond_responsabilite_eur = 100
Leurres : montant_eur 10200 (devis initial révisé) ; date_effet 2026-02-21 (date de signature, pas date d'effet)

Avis du relecteur : 

## prestation-03 (prestation)

-> **responsabilite_desequilibree** : « La responsabilité du Prestataire est limitée, toutes causes confondues, à la somme de 100 euros. »
   Pourquoi : Plafond de 100 euros pour une mission de 4800 euros.

Vérité : partie_a = Oriel Patrimoine SCI ; partie_b = Jardins Marceau SCOP ; montant_eur = 4800 ; date_effet = 2026-01-30 ; duree_mois = 6 ; preavis_jours = 60 ; renouvellement_tacite = False ; penalite_retard_pct_mois = 1 ; loi_applicable = droit français ; juridiction = Reims ; plafond_responsabilite_eur = 100
Leurres : montant_eur 7800 (devis initial révisé) ; date_effet 2026-01-15 (date de signature, pas date d'effet)

Avis du relecteur : 

## prestation-04 (prestation)

-> **penalite_excessive** : « Tout retard de paiement entraîne de plein droit une pénalité de 15 % du montant dû par mois de retard. »
   Pourquoi : 15 % par mois, soit 180 % par an, sans commune mesure avec le taux légal.
-> **renouvellement_tacite_piege** : « À défaut de dénonciation par lettre recommandée au moins 180 jours avant son terme, le contrat est reconduit tacitement pour une durée de 24 mois. »
   Pourquoi : Préavis de six mois et reconduction pour une durée double, dans un article séparé de la durée.
-> **responsabilite_desequilibree** : « La responsabilité du Prestataire est limitée, toutes causes confondues, à la somme de 100 euros. »
   Pourquoi : Plafond de 100 euros pour une mission de 7200 euros.

Vérité : partie_a = Dunemont Formation SAS ; partie_b = Lumière Blanche SAS ; montant_eur = 7200 ; date_effet = 2026-04-28 ; duree_mois = 12 ; preavis_jours = 180 ; renouvellement_tacite = True ; penalite_retard_pct_mois = 15 ; loi_applicable = droit français ; juridiction = Reims ; plafond_responsabilite_eur = 100
Leurres : montant_eur 10200 (devis initial révisé) ; date_effet 2026-03-28 (date de signature, pas date d'effet)

Avis du relecteur : 

## prestation-05 (prestation)

-> Témoin : aucun piège.

Vérité : partie_a = Nord-Est Numérique SAS ; partie_b = Jardins Marceau SCOP ; montant_eur = 12500 ; date_effet = 2026-06-12 ; duree_mois = 6 ; preavis_jours = 60 ; renouvellement_tacite = False ; penalite_retard_pct_mois = 1 ; loi_applicable = droit français ; juridiction = Dijon ; plafond_responsabilite_eur = 12500
Leurres : montant_eur 15500 (devis initial révisé) ; date_effet 2026-06-02 (date de signature, pas date d'effet)

Avis du relecteur : 

## bail-01 (bail)

-> **juridiction_eloignee** : « Le présent contrat est régi par le droit singapourien. Tout litige sera porté devant les tribunaux de Singapour. »
   Pourquoi : Contrat entre deux parties françaises, exécuté en France, renvoyé vers un droit et un tribunal étrangers.

Vérité : partie_a = SCI Rue Haute ; partie_b = Moulin Neuf SARL ; montant_eur = 1200 ; date_effet = 2026-10-03 ; duree_mois = 36 ; preavis_jours = 90 ; renouvellement_tacite = False ; loi_applicable = droit singapourien ; juridiction = Singapour ; depot_garantie_eur = 2400
Leurres : montant_eur 14400 (loyer annuel, le champ attend le loyer mensuel) ; date_effet 2026-09-18 (date de signature, pas date d'effet)

Avis du relecteur : 

## bail-02 (bail)

-> **revision_prix_unilaterale** : « Le Bailleur pourra réviser le loyer à tout moment, par simple notification, en fonction de l'évolution du marché local qu'il apprécie seul. »
   Pourquoi : Révision à la discrétion du bailleur, sans indice ni plafond.
-> **penalite_excessive** : « Le Preneur verse un dépôt de garantie de 19 800 euros, qui reste acquis au Bailleur en cas de départ avant le terme, quel qu'en soit le motif. »
   Pourquoi : Douze mois de loyer, perdus en totalité en cas de départ anticipé.
-> **resiliation_unilaterale** : « Le Bailleur peut résilier le bail à tout moment, sans motif, moyennant un préavis de 90 jours. Le Preneur ne peut résilier avant le terme. »
   Pourquoi : Faculté de sortie réservée au seul bailleur.

Vérité : partie_a = SCI Rue Haute ; partie_b = Kervella Logistique SARL ; montant_eur = 1650 ; date_effet = 2026-06-19 ; duree_mois = 36 ; preavis_jours = 90 ; renouvellement_tacite = False ; loi_applicable = droit français ; juridiction = Strasbourg ; depot_garantie_eur = 19800
Leurres : montant_eur 19800 (loyer annuel, le champ attend le loyer mensuel) ; date_effet 2026-06-04 (date de signature, pas date d'effet)

Avis du relecteur : 

## bail-03 (bail)

-> **penalite_excessive** : « Le Preneur verse un dépôt de garantie de 14 400 euros, qui reste acquis au Bailleur en cas de départ avant le terme, quel qu'en soit le motif. »
   Pourquoi : Douze mois de loyer, perdus en totalité en cas de départ anticipé.
-> **juridiction_eloignee** : « Le présent contrat est régi par le droit luxembourgeois. Tout litige sera porté devant les tribunaux de Luxembourg. »
   Pourquoi : Contrat entre deux parties françaises, exécuté en France, renvoyé vers un droit et un tribunal étrangers.

Vérité : partie_a = SCI Rue Haute ; partie_b = Éclats de Lune EURL ; montant_eur = 1200 ; date_effet = 2026-02-22 ; duree_mois = 36 ; preavis_jours = 90 ; renouvellement_tacite = False ; loi_applicable = droit luxembourgeois ; juridiction = Luxembourg ; depot_garantie_eur = 14400
Leurres : montant_eur 14400 (loyer annuel, le champ attend le loyer mensuel) ; date_effet 2026-02-21 (date de signature, pas date d'effet)

Avis du relecteur : 

## bail-04 (bail)

-> **juridiction_eloignee** : « Le présent contrat est régi par le droit luxembourgeois. Tout litige sera porté devant les tribunaux de Luxembourg. »
   Pourquoi : Contrat entre deux parties françaises, exécuté en France, renvoyé vers un droit et un tribunal étrangers.

Vérité : partie_a = SCI Rue Haute ; partie_b = Moulin Neuf SARL ; montant_eur = 1650 ; date_effet = 2026-02-19 ; duree_mois = 36 ; preavis_jours = 90 ; renouvellement_tacite = False ; loi_applicable = droit luxembourgeois ; juridiction = Luxembourg ; depot_garantie_eur = 3300
Leurres : montant_eur 19800 (loyer annuel, le champ attend le loyer mensuel) ; date_effet 2026-02-18 (date de signature, pas date d'effet)

Avis du relecteur : 

## bail-05 (bail)

-> Témoin : aucun piège.

Vérité : partie_a = Oriel Patrimoine SCI ; partie_b = Boréal Conseil SAS ; montant_eur = 1200 ; date_effet = 2026-01-31 ; duree_mois = 36 ; preavis_jours = 90 ; renouvellement_tacite = False ; loi_applicable = droit français ; juridiction = Besançon ; depot_garantie_eur = 2400
Leurres : montant_eur 14400 (loyer annuel, le champ attend le loyer mensuel) ; date_effet 2026-01-16 (date de signature, pas date d'effet)

Avis du relecteur : 

## nda-01 (nda)

-> **non_concurrence_large** : « L'obligation de confidentialité survit 99 ans à l'expiration de l'accord et interdit à la Partie réceptrice toute activité concurrente pendant cette période. »
   Pourquoi : Une non-concurrence de fait, sans limite raisonnable ni contrepartie, cachée dans la clause de confidentialité.
-> **cession_propriete_intellectuelle** : « Toute idée, amélioration ou invention conçue par la Partie réceptrice pendant la durée de l'accord appartient à la Partie divulgatrice, sans contrepartie. »
   Pourquoi : Un accord de confidentialité qui transfère les inventions de la partie réceptrice.

Vérité : partie_a = Lumière Blanche SAS ; partie_b = Éclats de Lune EURL ; date_effet = 2026-01-06 ; duree_mois = 24 ; renouvellement_tacite = False ; loi_applicable = droit français ; juridiction = Strasbourg ; duree_confidentialite_ans = 99 ; non_concurrence_mois = 1188
Leurres : date_effet 2026-01-06 (date de signature, pas date d'effet)

Avis du relecteur : 

## nda-02 (nda)

-> **non_concurrence_large** : « L'obligation de confidentialité survit 99 ans à l'expiration de l'accord et interdit à la Partie réceptrice toute activité concurrente pendant cette période. »
   Pourquoi : Une non-concurrence de fait, sans limite raisonnable ni contrepartie, cachée dans la clause de confidentialité.
-> **penalite_excessive** : « Toute divulgation, même involontaire, entraîne le paiement d'une indemnité forfaitaire de 500 000 euros, sans préjudice de dommages et intérêts complémentaires. »
   Pourquoi : Montant forfaitaire sans lien avec un préjudice, même pour une faute involontaire.
-> **cession_propriete_intellectuelle** : « Toute idée, amélioration ou invention conçue par la Partie réceptrice pendant la durée de l'accord appartient à la Partie divulgatrice, sans contrepartie. »
   Pourquoi : Un accord de confidentialité qui transfère les inventions de la partie réceptrice.

Vérité : partie_a = Pierre-Feuille Éditions ; partie_b = Lumière Blanche SAS ; date_effet = 2026-08-25 ; duree_mois = 24 ; renouvellement_tacite = False ; loi_applicable = droit français ; juridiction = Metz ; duree_confidentialite_ans = 99 ; non_concurrence_mois = 1188
Leurres : date_effet 2026-08-25 (date de signature, pas date d'effet)

Avis du relecteur : 

## nda-03 (nda)

-> **penalite_excessive** : « Toute divulgation, même involontaire, entraîne le paiement d'une indemnité forfaitaire de 500 000 euros, sans préjudice de dommages et intérêts complémentaires. »
   Pourquoi : Montant forfaitaire sans lien avec un préjudice, même pour une faute involontaire.
-> **cession_propriete_intellectuelle** : « Toute idée, amélioration ou invention conçue par la Partie réceptrice pendant la durée de l'accord appartient à la Partie divulgatrice, sans contrepartie. »
   Pourquoi : Un accord de confidentialité qui transfère les inventions de la partie réceptrice.

Vérité : partie_a = Oriel Patrimoine SCI ; partie_b = Quai Ouest SAS ; date_effet = 2026-06-11 ; duree_mois = 12 ; renouvellement_tacite = False ; loi_applicable = droit français ; juridiction = Mulhouse ; duree_confidentialite_ans = 3
Leurres : date_effet 2026-06-11 (date de signature, pas date d'effet)

Avis du relecteur : 

## nda-04 (nda)

-> **non_concurrence_large** : « L'obligation de confidentialité survit 99 ans à l'expiration de l'accord et interdit à la Partie réceptrice toute activité concurrente pendant cette période. »
   Pourquoi : Une non-concurrence de fait, sans limite raisonnable ni contrepartie, cachée dans la clause de confidentialité.
-> **cession_propriete_intellectuelle** : « Toute idée, amélioration ou invention conçue par la Partie réceptrice pendant la durée de l'accord appartient à la Partie divulgatrice, sans contrepartie. »
   Pourquoi : Un accord de confidentialité qui transfère les inventions de la partie réceptrice.

Vérité : partie_a = Lumière Blanche SAS ; partie_b = Atelier Verrand SARL ; date_effet = 2026-04-26 ; duree_mois = 24 ; renouvellement_tacite = False ; loi_applicable = droit français ; juridiction = Strasbourg ; duree_confidentialite_ans = 99 ; non_concurrence_mois = 1188
Leurres : date_effet 2026-04-26 (date de signature, pas date d'effet)

Avis du relecteur : 

## nda-05 (nda)

-> Témoin : aucun piège.

Vérité : partie_a = Lumière Blanche SAS ; partie_b = Groupe Hallier SAS ; date_effet = 2026-05-27 ; duree_mois = 24 ; renouvellement_tacite = False ; loi_applicable = droit français ; juridiction = Metz ; duree_confidentialite_ans = 3
Leurres : date_effet 2026-05-27 (date de signature, pas date d'effet)

Avis du relecteur : 

## cgv-01 (cgv)

-> **revision_prix_unilaterale** : « L'Éditeur peut modifier ses tarifs à tout moment ; le nouveau prix s'applique dès sa publication sur le site, sans autre information du Client. »
   Pourquoi : Hausse sans préavis ni faculté de résiliation.
-> **responsabilite_desequilibree** : « L'Éditeur n'est responsable d'aucun dommage, direct ou indirect, y compris la perte des données du Client. »
   Pourquoi : Exclusion totale, y compris de la perte de données, pour un service qui les héberge.

Vérité : partie_a = Ibis Rouge Studio ; partie_b = Sophie Vellard, entrepreneur individuel ; montant_eur = 49 ; date_effet = 2026-07-10 ; duree_mois = 12 ; preavis_jours = 30 ; renouvellement_tacite = True ; loi_applicable = droit français ; juridiction = Besançon ; plafond_responsabilite_eur = 0
Leurres : montant_eur 588 (total annuel, le champ attend le prix mensuel) ; date_effet 2026-07-10 (date de signature, pas date d'effet)

Avis du relecteur : 

## cgv-02 (cgv)

-> **responsabilite_desequilibree** : « L'Éditeur n'est responsable d'aucun dommage, direct ou indirect, y compris la perte des données du Client. »
   Pourquoi : Exclusion totale, y compris de la perte de données, pour un service qui les héberge.

Vérité : partie_a = Moulin Neuf SARL ; partie_b = Hélène Gasquet, entrepreneur individuel ; montant_eur = 290 ; date_effet = 2026-04-11 ; duree_mois = 12 ; preavis_jours = 30 ; renouvellement_tacite = True ; loi_applicable = droit français ; juridiction = Mulhouse ; plafond_responsabilite_eur = 0
Leurres : montant_eur 3480 (total annuel, le champ attend le prix mensuel) ; date_effet 2026-04-11 (date de signature, pas date d'effet)

Avis du relecteur : 

## cgv-03 (cgv)

-> **revision_prix_unilaterale** : « L'Éditeur peut modifier ses tarifs à tout moment ; le nouveau prix s'applique dès sa publication sur le site, sans autre information du Client. »
   Pourquoi : Hausse sans préavis ni faculté de résiliation.

Vérité : partie_a = Éclats de Lune EURL ; partie_b = Marc Aubrac, entrepreneur individuel ; montant_eur = 149 ; date_effet = 2026-08-06 ; duree_mois = 12 ; preavis_jours = 30 ; renouvellement_tacite = True ; loi_applicable = droit français ; juridiction = Colmar ; plafond_responsabilite_eur = 1788
Leurres : montant_eur 1788 (total annuel, le champ attend le prix mensuel) ; date_effet 2026-08-06 (date de signature, pas date d'effet)

Avis du relecteur : 

## cgv-04 (cgv)

-> **responsabilite_desequilibree** : « L'Éditeur n'est responsable d'aucun dommage, direct ou indirect, y compris la perte des données du Client. »
   Pourquoi : Exclusion totale, y compris de la perte de données, pour un service qui les héberge.
-> **juridiction_eloignee** : « Le présent contrat est régi par le droit luxembourgeois. Tout litige sera porté devant les tribunaux de Luxembourg. »
   Pourquoi : Contrat entre deux parties françaises, exécuté en France, renvoyé vers un droit et un tribunal étrangers.

Vérité : partie_a = Groupe Hallier SAS ; partie_b = Hélène Gasquet, entrepreneur individuel ; montant_eur = 290 ; date_effet = 2026-07-20 ; duree_mois = 12 ; preavis_jours = 30 ; renouvellement_tacite = True ; loi_applicable = droit luxembourgeois ; juridiction = Luxembourg ; plafond_responsabilite_eur = 0
Leurres : montant_eur 3480 (total annuel, le champ attend le prix mensuel) ; date_effet 2026-07-20 (date de signature, pas date d'effet)

Avis du relecteur : 

## cgv-05 (cgv)

-> Témoin : aucun piège.

Vérité : partie_a = Dunemont Formation SAS ; partie_b = Thomas Rieuvert, entrepreneur individuel ; montant_eur = 149 ; date_effet = 2026-03-25 ; duree_mois = 12 ; preavis_jours = 30 ; renouvellement_tacite = True ; loi_applicable = droit français ; juridiction = Reims ; plafond_responsabilite_eur = 1788
Leurres : montant_eur 1788 (total annuel, le champ attend le prix mensuel) ; date_effet 2026-03-25 (date de signature, pas date d'effet)

Avis du relecteur : 

