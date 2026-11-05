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
  Dès que vous créez une nouvelle web-app ou déployez une mise à jour d'application pour Thomas, vous **DEVEZ systématiquement** créer un vrai logo illustré dans `assets/`, le copier dans `/Users/thomaslefevre/.t3/projects/allinone/assets/`, mettre à jour `index.html` (incrémenter `CACHE_KEY`), `scripts/sync_projects.py`, `projects.json`, et faire `git commit` + `git push` sur les deux dépôts (`https://mrthomaslef.github.io/allinone/`).
- **💖 Mapp Store (`/Users/thomaslefevre/.t3/projects/mapp-store`)** :
  Dès qu'une application créée ou mise à jour **concerne son épouse Marie** (Pédiatrie/Infectiologie comme `BiblioMarie`, Vie de famille & couple comme `Agenda Famille`, `Resto en Amoureux`, `Voyages-Voyages`, `Photo Famille`, `Film & Série`, Émile & `AssMat`/Mabrouka, ou Jeux familiaux), vous **DEVEZ systématiquement l'ajouter et la mettre à jour AUSSI sur le Mapp Store** (`index.html`, `scripts/sync_projects.py`, `projects.json` dans `/Users/thomaslefevre/.t3/projects/mapp-store`) et pousser sur GitHub (`https://mrthomaslef.github.io/mapp-store/`).

### 3. Coffre-Fort d'Identifiants & Mots de Passe (`t3-vault` — Trousseau macOS) :
- Tous les identifiants et mots de passe de Thomas sont stockés dans le **Trousseau macOS** via `/Users/thomaslefevre/.t3/bin/t3-vault`.
- Avant de demander un identifiant à l'utilisateur, vérifiez s'il est déjà dans le coffre-fort : `/Users/thomaslefevre/.t3/bin/t3-vault list`.
- Pour récupérer un identifiant ou mot de passe : `/Users/thomaslefevre/.t3/bin/t3-vault get <service> --field user` et `/Users/thomaslefevre/.t3/bin/t3-vault get <service> --field password`.
- Pour enregistrer un nouveau mot de passe : appelez l'outil `request_secret` (`delivery: "file"`) puis exécutez `/Users/thomaslefevre/.t3/bin/t3-vault set <service> --user "<login>" --password-file "<fichier>"`.

### 4. Instincts Atomiques Appris des Inputs de Thomas (`t3-instincts` — Ne jamais répéter ces erreurs) :
Ces règles sont extraites chaque nuit des inputs et corrections de Thomas. **Appliquez-les systématiquement sans qu'il ait besoin de le redemander** :
```text
# Active Instincts (9/13 | project=projet-regroup)
- [0.98][GLOBAL][ui-pwa] fullscreen-launch-and-controller-verify: WHEN Lors de la création ou configuration d'un lanceur de jeu (Recomp, Pegasus, Moonlight), d'un lecteur vidéo (Stremio/Film) ou d'un bouton 'Jouer direct' -> Toujours forcer l'ouverture en plein écran d'emblée (sans modale ni pop-up bloquante), vérifier le mapping manette (8BitDo) et la présence des sauvegardes avant d'annoncer que c'est terminé.
- [0.98][GLOBAL][ui-pwa] mobile-first-no-overflow-no-zoom: WHEN Lors de la création d'interfaces web, de tableaux cliniques ou de boutons interactifs consultés sur iPhone / mobile -> Empêcher le zoom au double-clic (touch-action: manipulation), garantir zéro débordement horizontal des tableaux sur mobile et privilégier des interfaces épurées orientées action directe.
- [0.95][GLOBAL][ui-pwa] pull-to-refresh-systematic: WHEN Lors de la création ou modification d'une application web ou PWA mobile/desktop -> Implanter systématiquement le Pull-to-Refresh tactile (touch) et souris (mouse) avec overscroll-behavior-y: contain et vibration haptique.
- [0.95][GLOBAL][security] t3-vault-keychain-only: WHEN Lorsqu'un identifiant, secret, token API ou mot de passe est requis ou fourni -> Ne jamais demander ni afficher de mot de passe en clair dans le chat. Toujours interroger /Users/thomaslefevre/.t3/bin/t3-vault ou utiliser request_secret (delivery: file) puis t3-vault set.
- [0.95][GLOBAL][git-deploy] tapp-mapp-store-dual-publish: WHEN Après toute création, mise à jour ou déploiement d'une web-app -> Mettre à jour et pousser systématiquement sur Tapp Store (allinone) ET sur Mapp Store (mapp-store) si l'app concerne Marie, Émile ou la famille.
- [0.92][GLOBAL][architecture] offline-embedded-bundle-pwa: WHEN Lors de la construction d'une PWA statique hébergée sur GitHub Pages avec données JSON -> Générer un fichier data/embedded_data.js (window.*_DATA) en plus des fichiers .json afin que l'application fonctionne à 100 % hors-ligne et en file:// sans erreur CORS.
- [0.92][GLOBAL][workflow] superpowers-verify-before-completion: WHEN Avant d'affirmer qu'une tâche, un script ou un déploiement est terminé -> Exécuter une vérification réelle (test, build_data.py, sync_projects.py, git status/diff) et citer le résultat observé. Pas de sous-agent par micro-tâche pour les petits correctifs afin de préserver les quotas 5h.
- [0.85][GLOBAL][git-deploy] git-push-systematic-verification: WHEN À la fin de toute modification de code, d'application web ou de configuration -> Vérifier systématiquement avec git status et git push que tous les dépôts modifiés (ainsi que Tapp Store / Mapp Store) sont poussés et à jour sur GitHub.
- [0.85][GLOBAL][git-deploy] tapp-store-custom-logo-and-cache-bust: WHEN À chaque création ou modification d'une application web ou PWA référencée sur le Tapp Store (allinone) ou Mapp Store -> Créer systématiquement un vrai logo SVG/PNG illustré dans assets/, le copier dans allinone/assets/, incrémenter CACHE_KEY dans index.html, purger les Service Workers pour que les modifications soient visibles immédiatement sans cache, et faire git commit + git push sur le projet ET sur le store.
```
- Dès que Thomas exprime une préférence récurrente ou corrige un comportement en session, enregistrez l'instinct immédiatement :
  `/Users/thomaslefevre/.t3/bin/t3-instincts learn --id "<slug>" --trigger "<quand>" --action "<action>" --project "$PWD"`
<!-- SUPER_AGENT_ROUTER_END -->








