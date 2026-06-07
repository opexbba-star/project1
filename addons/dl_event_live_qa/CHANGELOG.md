# Notes de version — `dl_event_live_qa`

Toutes les évolutions notables de ce module sont consignées ici.
Format inspiré de [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/),
versionnage [SemVer](https://semver.org/lang/fr/) appliqué au schéma
Odoo : `SERIE.MAJOR.MINOR.PATCH` (ex. `19.0.1.0.0`).

---

## [19.0.1.0.0] — 2026-05-18

Première version publique du module — refonte deltalog du prototype
interne `event_live_qa`.

### Ajouté
- **Modèle `event.qa.question`** : entité de question avec auteur, texte,
  état (`pending` / `approved` / `answered` / `rejected`) et compteur de
  votes dénormalisé.
- **Extension `event.track`** : champs `qa_enabled`, `qa_state`,
  `qa_access_token` (UUID), URLs publique et présentateur calculées,
  compteurs (total / en attente / approuvées).
- **Onglet « Q&A en direct »** sur la fiche session :
  - case Activer + statut (`draft` / `active` / `done`) en badge coloré ;
  - boutons Démarrer / Clôturer / Remettre en brouillon / Régénérer le
    lien / Ouvrir la page publique / Ouvrir la vue présentateur ;
  - liens publics avec widget *Copy to clipboard* + **QR code** (220×220)
    du lien public, généré via `/report/barcode/?barcode_type=QR&value=...`
    et affiché via le widget `image_url` ;
  - liste embarquée des questions de la session avec actions de
    modération en ligne (approuver / marquer répondue / rejeter).
- **Smart button « Q&A »** sur la fiche session affichant le nombre de
  questions et ouvrant la vue filtrée.
- **Menu Évènements → Q&A en direct** listant toutes les questions
  toutes sessions confondues (kanban + liste + form).
- **Page publique participants** (`/event/qa/<token>`) :
  - en-tête avec dégradé et pastille EN DIRECT animée ;
  - carte de soumission (nom optionnel + question, max 1000 car.) visible
    uniquement quand le Q&A est actif ;
  - liste des questions approuvées triée par votes décroissants ;
  - vote en un clic avec déduplication client (sessionStorage) ;
  - rafraîchissement automatique toutes les 10 s.
- **Vue présentateur plein écran** (`/event/qa/<token>/presenter`)
  utilisable pour la projection (navbar / footer masqués via CSS).
- **Endpoints JSON publics** :
  - `POST /event/qa/<token>/questions` — liste des questions visibles ;
  - `POST /event/qa/<token>/submit` — soumission de question ;
  - `POST /event/qa/<token>/vote` — incrément de vote.
- **Widget Owl backend `qa_auto_refresh`** : recharge l'onglet Q&A
  toutes les 10 s avec bouton pause / reprise et horodatage du dernier
  rafraîchissement.
- **Données de démo** (`data/demo_data.xml`) pour tester rapidement.

### Sécurité
- Accès ORM réservé aux groupes Évènements existants
  (`event.group_event_user` en read / write / create,
  `event.group_event_manager` pour le delete).
- Aucun droit ORM pour le public ; toutes les écritures publiques
  passent par `sudo()` avec le `qa_access_token` comme secret
  d'autorisation.
- Bouton **Régénérer le lien** pour invalider les URLs publiques
  compromises (avec confirmation).
- Limites dures côté contrôleur : 1000 caractères pour le texte, 100
  pour l'auteur ; soumission refusée si le Q&A n'est pas `active`.

### Changements vs prototype `event_live_qa`
- Renommage technique du module : `event_live_qa` → `dl_event_live_qa`
  (toutes les références XML / Owl / contrôleurs mises à jour).
- `author` du manifest : `Weasydoo` → `deltalog`.
- `website` du manifest : `https://www.weasydoo.com` →
  `https://www.deltalog.dz/`.
- Préfixage des chemins d'assets (`dl_event_live_qa/static/...`).

### Migration depuis `event_live_qa`
Le module est traité par Odoo comme un **nouveau module** (renommage
technique). Procédure recommandée :
1. **Désinstaller** `event_live_qa` (les questions seront supprimées en
   cascade — exporter au préalable si nécessaire).
2. Mettre à jour la liste des modules.
3. **Installer** `dl_event_live_qa`.
4. Réactiver le Q&A sur les sessions concernées (un nouveau jeton sera
   généré, les anciens liens publics ne fonctionneront plus).

### Limitations connues
- Déduplication de vote uniquement côté client (sessionStorage), non
  persistée côté serveur.
- Rafraîchissement par polling 10 s — pas de notifications temps réel
  via `bus.bus`.
- Pas de pièces jointes, ni de markdown dans les questions.
- Pas de règles `ir.rule` multi-société.

[19.0.1.0.0]: # "Version initiale deltalog"
