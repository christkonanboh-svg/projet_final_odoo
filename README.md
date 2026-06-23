# Module Odoo 18 : Gestion de Parc Informatique (it_parc)

Ce module personnalisé permet à **TECHPARK CI** de gérer l'intégralité de son parc informatique (équipements, affectations, interventions de maintenance, contrats fournisseurs, et alertes de garantie).

## Fonctionnalités principales

1. **Gestion des Équipements** : Suivi détaillé des serveurs, postes de travail, téléphones, imprimantes, etc., par catégorie, localisation et état.
2. **Historique des Affectations** : Enregistrement de chaque affectation d'équipement à un employé ou département.
3. **Suivi des Interventions de Maintenance** : Enregistrement des pannes et interventions avec calcul automatique de la durée et des coûts.
4. **Contrats Fournisseurs** : Gestion des contrats de maintenance/licence associés aux équipements avec calcul des jours restants avant expiration.
5. **Alertes de Garantie et de Contrat** : Détection automatique et manuelle des expirations proches pour générer des alertes de maintenance.
6. **Importation CSV** : Outil d'importation d'équipements avec détection automatique du délimiteur.
7. **Rapports PDF (QWeb)** :
   - Fiche d'équipement individuelle.
   - Inventaire filtrable par catégorie et département.
   - Historique des maintenances par période.
8. **Exports Excel (xlsxwriter)** :
   - Liste des équipements (Inventaire).
   - Synthèse mensuelle des coûts de maintenance.
   - Contrats expirant dans les 60 jours (avec mise en couleur conditionnelle : rouge si <30 jours, orange si 30-60 jours).
9. **Tableau de bord interactif (OWL 2)** :
   - Indicateurs clés (KPIs) : taux de disponibilité, équipements en panne, coûts cumulés, contrats en alerte.
   - Graphiques dynamiques (Chart.js) : évolution mensuelle des coûts et répartition par catégorie.

---

## Prérequis et Installation

### Dépendances requises
Le module dépend des modules Odoo standard suivants :
- `base`
- `hr`
- `stock`
- `purchase`
- `account`
- `maintenance`
- `mail`
- `contacts`
- `web`

Assurez-vous également que la bibliothèque Python `xlsxwriter` est installée dans votre environnement virtuel (déjà présente dans l'environnement virtuel actuel).

### Procédure d'installation

1. Copiez le dossier `it_parc` dans le répertoire des addons de votre instance Odoo 18.
2. Lancez le serveur Odoo en forçant l'installation/mise à jour du module :
   ```bash
   venv\Scripts\python odoo-bin -c odoo.conf -i it_parc
   ```
3. Ou si Odoo tourne déjà, activez le **Mode Développeur** dans la configuration, allez dans le menu **Applications**, cliquez sur **Mettre à jour la liste des applications**, puis recherchez `it_parc` (Gestion de Parc Informatique) et cliquez sur **Installer**.

> ⚠️ **Apres installation ou mise à jour** : Si le dashboard OWL n'affiche pas les graphiques (écran blanc ou pas de données), videz le cache navigateur (**Ctrl+F5** ou **Ctrl+Maj+R**) puis videz le cache des assets Odoo : **Paramètres > Technique > Effacer les assets** ou rendez-vous sur `http://localhost:8069/web?debug=assets`.

---

## Importation CSV

L'assistant d'importation est disponible sous **IT Parc > Outils > Importer des équipements (CSV)**.

### Format attendu (colonnes fixes) :
Le fichier CSV doit contenir les en-têtes exacts suivants :
`Nom, Numéro de Série, Catégorie, Valeur, Date Achat, Garantie, Localisation, État, Employé, Département`

- **Date Achat / Garantie** : Formats supportés : `AAAA-MM-JJ` (ex. `2026-01-15`), `DD/MM/AAAA` ou `DD-MM-AAAA`
- **État** : Une des valeurs suivantes : `Brouillon`, `Affecté`, `En maintenance`, `Retiré`
- **Catégories / Localisations / Employés / Départements** : S'ils n'existent pas dans la base de données, ils seront automatiquement créés à la volée.

---

## Droits de Sécurité

Le module implémente deux rôles d'accès :
1. **IT Technicien** : 
   - Peut lire et modifier les équipements.
   - A un accès complet aux interventions de maintenance.
   - Ne peut pas configurer les catégories, localisations, contrats fournisseurs ou utiliser les outils d'administration (Wizards d'importation, rapports de synthèse, etc.).
2. **IT Manager** : 
   - Accès complet (lecture, écriture, création, suppression) sur l'ensemble des fonctionnalités, menus, configurations et rapports du module.
