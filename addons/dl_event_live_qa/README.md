# Q&A en Direct (Évènements) — `dl_event_live_qa`

Module Odoo 19 qui ajoute des sessions de **Q&A en temps réel** (style Slido /
Slack AMA) sur les sessions d'évènement (`event.track`). Les participants
soumettent et votent leurs questions depuis une page publique ; les modérateurs
les traitent depuis le backend ; le présentateur affiche en plein écran les
questions les plus votées sur le vidéoprojecteur.

- **Auteur** : deltalog
- **Site** : <https://www.deltalog.dz/>
- **Version** : 19.0.1.0.0
- **Licence** : LGPL-3
- **Dépendances** : `base`, `website_event_track`

---

## 1. Vue d'ensemble

```
                           ┌─────────────────────────┐
                           │  Backend (modérateur)   │
                           │  event.track > onglet   │
                           │  Q&A en direct          │
                           └─────────────┬───────────┘
                                         │ approuve / rejette
                                         ▼
┌──────────────┐  POST /event/qa/<token>/submit   ┌──────────────────┐
│ Participants │ ───────────────────────────────► │  event.qa.question│
│ (navigateur) │ ◄─── POST /event/qa/<token>/    │   (PostgreSQL)   │
└──────────────┘      questions  (poll 10s)       └─────────┬────────┘
                                                            │
                                                            ▼
                                                 ┌──────────────────┐
                                                 │ Vue présentateur │
                                                 │ (plein écran)    │
                                                 └──────────────────┘
```

Trois publics, trois interfaces :

| Rôle           | Où                                          | Ce qu'il fait                                          |
|----------------|---------------------------------------------|--------------------------------------------------------|
| Participant    | `/event/qa/<token>` (public)                | Pose une question, vote pour celles des autres         |
| Modérateur     | Backend → Évènements → fiche `event.track`  | Active le Q&A, approuve / rejette / marque répondue    |
| Présentateur   | `/event/qa/<token>/presenter` (plein écran) | Projette les questions triées par votes décroissants   |

---

## 2. Installation

1. Copier le dossier `dl_event_live_qa/` dans votre `addons_path`.
2. Redémarrer Odoo.
3. Activer le mode développeur, puis **Apps → Mettre à jour la liste des modules**.
4. Rechercher *« Q&A en Direct (Évènements) »* et cliquer sur **Installer**.

Le module installe automatiquement `website_event_track` (donc tous les
modules d'évènement standard).

---

## 3. Modèle de données

### `event.qa.question` (nouveau modèle)

| Champ           | Type        | Description                                       |
|-----------------|-------------|---------------------------------------------------|
| `track_id`      | M2o         | Session concernée (`event.track`) — cascade       |
| `event_id`      | M2o related | Évènement parent (stocké, pour filtrage)          |
| `author_name`   | Char        | Nom de l'auteur (`"Anonyme"` par défaut)          |
| `question_text` | Text        | Texte de la question (max 1000 car.)              |
| `state`         | Selection   | `pending` / `approved` / `answered` / `rejected`  |
| `vote_count`    | Integer     | Compteur dénormalisé, incrémenté côté contrôleur  |

Tri par défaut : `vote_count desc, create_date desc`.

### `event.track` (étendu)

Champs ajoutés :

- `qa_enabled` — case à cocher pour activer la fonctionnalité.
- `qa_state` — `draft` / `active` / `done`.
- `qa_access_token` — UUID secret généré au premier démarrage ; sert de clé
  d'accès aux URLs publiques.
- `qa_question_ids` — One2many vers les questions.
- `qa_question_count`, `qa_pending_count`, `qa_approved_count` — compteurs
  calculés.
- `qa_public_url`, `qa_presenter_url` — URLs absolues calculées à partir de
  `web.base.url` et du jeton.
- `qa_public_qr_url` — URL `/report/barcode/?barcode_type=QR&value=...`
  pointant sur le générateur de QR code standard d'Odoo, affichée en image
  dans le formulaire (widget `image_url`, 220×220).

---

## 4. Workflow modérateur (backend)

1. Ouvrir une session de conférence (**Évènements → un évènement → Sessions**).
2. Aller dans l'onglet **« Q&A en direct »**.
3. Cocher **« Activer le Q&A en direct »** et sauvegarder.
4. Cliquer sur **« Démarrer le Q&A »** : un jeton UUID est généré, les liens
   publics et présentateur deviennent visibles (widget *Copy to clipboard*),
   accompagnés d'un **QR code** prêt à être projeté ou imprimé.
5. Partager le lien public avec les participants : copier l'URL ou faire un
   clic droit sur le QR code pour l'enregistrer / l'imprimer.
6. Au fil de l'eau, traiter les questions entrantes :
   - **Approuver** → la question apparaît sur la page publique et la vue
     présentateur.
   - **Marquer répondue** → la question reste visible mais étiquetée comme
     traitée.
   - **Rejeter** → la question disparaît des vues publiques.
7. En fin de session, **« Clôturer le Q&A »** : les soumissions sont bloquées,
   les questions restent consultables.
8. Bouton **« Régénérer le lien »** disponible à tout moment pour invalider
   les anciens liens publics (avec confirmation).

Un **smart button « Q&A »** sur la fiche session ouvre directement la liste
filtrée des questions de cette session.

Une **vue Kanban** dédiée par statut est aussi accessible via le menu
**Évènements → Q&A en direct** (toutes sessions confondues).

---

## 5. Page publique participants

URL : `/event/qa/<token>`

- En-tête avec dégradé : nom de l'évènement, titre de la session, pastille
  d'état (EN DIRECT / Pas commencé / Clôturé).
- Carte de soumission (visible uniquement si `qa_state == 'active'`) :
  - Nom optionnel (défaut « Anonyme »).
  - Champ question (max 1000 caractères).
- Liste des questions approuvées, triée par votes décroissants.
- Bouton **vote** par question — déduplication côté client via
  `sessionStorage` (une session de navigateur = un vote par question).
- **Poll JSON toutes les 10 secondes** (`/event/qa/<token>/questions`) pour
  rafraîchir la liste sans recharger la page.

---

## 6. Vue présentateur

URL : `/event/qa/<token>/presenter`

- Layout sans navbar ni footer (masqués via CSS sur la classe
  `.o_qa_presenter`) → quasi plein écran, prêt pour la projection.
- En-tête : nom de la session, nom de l'évènement, badge d'état.
- Liste des questions approuvées triées par votes (les boutons de vote sont
  désactivés via l'attribut `data-presenter="1"` lu par le JS).
- Pied de page rappelant l'URL publique pour que les participants la scannent.

---

## 7. Endpoints HTTP

Tous publics (`auth='public'`), authentifiés via le jeton dans l'URL.

| Méthode | Route                                  | Type | Rôle                                          |
|---------|----------------------------------------|------|-----------------------------------------------|
| GET     | `/event/qa/<token>`                    | HTTP | Page publique participants                    |
| GET     | `/event/qa/<token>/presenter`          | HTTP | Vue présentateur plein écran                  |
| POST    | `/event/qa/<token>/questions`          | JSON | Liste des questions visibles + état du Q&A    |
| POST    | `/event/qa/<token>/submit`             | JSON | Soumission d'une nouvelle question            |
| POST    | `/event/qa/<token>/vote`               | JSON | Incrément du compteur de votes                |

Validations côté serveur :
- `question_text` non vide, tronqué à 1000 caractères.
- `author_name` tronqué à 100 caractères ; défaut `"Anonymous"`.
- Soumission refusée si `qa_state != 'active'`.
- Vote refusé si la question n'est pas en `approved` ou `answered`, ou si elle
  n'appartient pas à la session ciblée par le jeton.

---

## 8. Sécurité

- Modèle `event.qa.question` :
  - `event.group_event_user` → read / write / create (pas de delete).
  - `event.group_event_manager` → tous droits.
- **Aucun droit ORM** pour les utilisateurs publics — tous les writes
  publics passent par `sudo()` côté contrôleur, avec le `qa_access_token` de
  la session comme unique secret d'autorisation.
- Le jeton est un UUID v4 ; il peut être régénéré à tout moment depuis le
  formulaire de la session (bouton **Régénérer le lien**), ce qui invalide
  les URLs précédentes.
- La déduplication de votes est **purement côté client** (sessionStorage).
  Pour des contraintes strictes (anti-bot, vote par IP), prévoir une table
  `(question_id, visitor_id)` en complément.

---

## 9. Assets front-end

| Bundle              | Fichier                                          |
|---------------------|--------------------------------------------------|
| `web.assets_frontend` | `static/src/css/qa_style.css`                  |
| `web.assets_frontend` | `static/src/js/qa_live.js` — poll + vote + submit |
| `web.assets_backend`  | `static/src/xml/qa_auto_refresh.xml`           |
| `web.assets_backend`  | `static/src/js/qa_auto_refresh.js` — widget Owl d'auto-refresh de l'onglet |

Le widget backend `qa_auto_refresh` recharge automatiquement l'onglet Q&A
toutes les 10 s tant que le Q&A est actif, avec bouton pause / reprise.

---

## 10. Limitations connues

- **Déduplication de vote** non persistée côté serveur (cf. section 8).
- Pas de **notification temps réel** (websocket / bus) — le rafraîchissement
  se fait par polling 10 s.
- Pas de **pièces jointes** ni de **markdown** dans le texte des questions.
- Pas de **règles ir.rule** multi-société ; toutes les questions sont
  visibles par tout utilisateur du groupe Évènements.
- Le module dépend de `website_event_track` (vue formulaire `event.track`
  héritée) ; il ne fonctionnera pas sur une instance qui n'a pas le module
  Site Web installé.

---

## 11. Pistes d'évolution

- Persistance de la déduplication de vote `(question_id, visitor_id)`.
- Notifications temps réel via le bus Odoo (`bus.bus`) pour remplacer le
  polling.
- Export des questions (CSV) après l'évènement.
- Modération assistée par IA (tri spam / langage inapproprié).
