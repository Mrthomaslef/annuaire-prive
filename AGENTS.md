# Instructions Agent — projet-regroup

<!-- SUPER_AGENT_ROUTER_START -->
## 🧠 Super-Agent, Aiguillage Inter-Projets & Publication Stores (Dr Thomas Lefèvre)

Vous êtes connecté à l'**Écosystème Global & Second Brain** de Thomas Lefèvre.
Avant de répondre à une demande transversale ou touchant un autre projet, consultez :
- **La cartographie complète en temps réel** : `/Users/thomaslefevre/2nd brain/06 - Cartographie Globale des Projets.md`
- **Le Second Brain médical Cochin** : `/Users/thomaslefevre/2nd brain/AGENTS.md`

### 1. Règle d'Aiguillage Proactive :
- Si l'utilisateur pose une question ou demande une action qui concerne un autre projet que le dossier courant (ex: billets SNCF/vacances, restaurant avec Marie, document notarié/impôt, protocole RI Cochin, planning des internes, nounou Mabrouka, finances, photos de famille ou article BiblioOstéo/BiblioMarie), **ne dites jamais que vous n'avez pas l'information**.
- Consultez directement les fichiers du projet cible via son chemin local répertorié dans `/Users/thomaslefevre/2nd brain/06 - Cartographie Globale des Projets.md` et aiguillez l'utilisateur.

### 2. Règle Obligatoire : Publication Systématique sur Tapp Store & Mapp Store :
- **🛍️ Tapp Store (`/Users/thomaslefevre/.t3/projects/allinone`)** :
  Dès que vous créez une nouvelle web-app ou déployez une mise à jour d'application pour Thomas, vous **DEVEZ systématiquement** vérifier qu'elle est référencée et à jour dans le **Tapp Store** (`index.html`, `scripts/sync_projects.py`, `projects.json` dans `/Users/thomaslefevre/.t3/projects/allinone`) et pousser la mise à jour sur GitHub (`https://mrthomaslef.github.io/allinone/`).
- **💖 Mapp Store (`/Users/thomaslefevre/.t3/projects/mapp-store`)** :
  Dès qu'une application créée ou mise à jour **concerne son épouse Marie** (Pédiatrie/Infectiologie comme `BiblioMarie`, Vie de famille & couple comme `Agenda Famille`, `Resto en Amoureux`, `Voyages-Voyages`, `Photo Famille`, Émile & `AssMat`/Mabrouka, ou Jeux familiaux comme `DinoCiel`, `milTCG`, `QUIZ du 7TER`, `Monopoly`, `PokéQuiz`), vous **DEVEZ systématiquement l'ajouter et la mettre à jour AUSSI sur le Mapp Store** (`index.html`, `scripts/sync_projects.py`, `projects.json` dans `/Users/thomaslefevre/.t3/projects/mapp-store`) et pousser sur GitHub (`https://mrthomaslef.github.io/mapp-store/`).

### 3. Coffre-Fort d'Identifiants & Mots de Passe (`t3-vault` — Trousseau macOS) :
- Tous les identifiants et mots de passe de Thomas sont stockés dans le **Trousseau macOS** via `/Users/thomaslefevre/.t3/bin/t3-vault`.
- Avant de demander un identifiant à l'utilisateur, vérifiez s'il est déjà dans le coffre-fort : `/Users/thomaslefevre/.t3/bin/t3-vault list`.
- Pour récupérer un identifiant ou mot de passe : `/Users/thomaslefevre/.t3/bin/t3-vault get <service> --field user` et `/Users/thomaslefevre/.t3/bin/t3-vault get <service> --field password`.
- Pour enregistrer un nouveau mot de passe : appelez l'outil `request_secret` (`delivery: "file"`) puis exécutez `/Users/thomaslefevre/.t3/bin/t3-vault set <service> --user "<login>" --password-file "<fichier>"`.

### 4. Workflow `superpowers` & Instincts Atomiques Locaux (`t3-instincts`) :
- Au début d'une tâche d'ingénierie, chargez les instincts actifs du projet : `/Users/thomaslefevre/.t3/bin/t3-instincts context --project "$PWD"`.
- Suivez la méthodologie `superpowers` : Spec concise → Micro-Plan YAGNI (exécution inline par défaut pour préserver les quotas 5h) → Root-Cause Debugging → Preuve réelle avant complétion (`Verification Before Completion`).
- Dès que Thomas exprime une préférence récurrente ou corrige un comportement, enregistrez l'instinct en local : `/Users/thomaslefevre/.t3/bin/t3-instincts learn --id "<slug>" --trigger "<quand>" --action "<action>" --project "$PWD"`.
<!-- SUPER_AGENT_ROUTER_END -->






