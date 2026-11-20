# 📚 Système Pro de Gestion de Bibliothèque & Dashboard Moderne

Une application moderne, dynamique et élégante pour la gestion complète d'une bibliothèque, développée conformément au **Document de Référence : Organisation, Fonds Documentaire et Règlement des Prêts**.

---

## 🌟 Expérience Visuelle & Fonctionnalités

### 1. 📊 Tableau de Bord (Dashboard) Dynamique & Agréable
- **Cartes KPI avec micro-animations** :
  - Nombre total d'ouvrages et pourcentage de disponibilité
  - Prêts actifs sous contrôle du délai réglementaire de **2 semaines (14 jours)**
  - **Badge d'alerte rouge clignotant** dès qu'un retard est détecté
  - Total des cotisations annuelles perçues en F CFA
- **Graphiques interactifs Chart.js** :
  - *Graphique Donut* : Répartition du fonds entre les 2 sections officielles (*Fonds Général & Littérature* vs *Jeunesse, Sciences & Documentaires*).
  - *Graphique en barres* : Volumes d'ouvrages par rayon majeur (*Romans, Bandes dessinées, Informatique, Atlas...*).
- **Tableau des alertes & relances** : identification immédiate des lecteurs à contacter par téléphone pour les retards.

### 2. 📖 Fonds Documentaire (2 Sections, 21 Catégories)
- Menus déroulants en cascade respectant fidèlement le document officiel.
- Recherche instantanée en temps réel (au fur et à mesure de la frappe).
- Filtres rapides par section (*Tous*, *Fonds Général*, *Jeunesse & Sciences*).
- Gestion du mode d'acquisition (*Dons en nature* ou *Partenariats maisons d'édition*) et état (*Neuf, Bon, Moyen, Dégradé*).

### 3. 👥 Usagers & Tarifs d'Abonnement
- Enregistrement des lecteurs avec tarification annuelle officielle :
  - **Écoliers** : 1 000 F / an
  - **Élèves (1er cycle)** : 2 000 F / an
  - **Étudiants** : 3 000 F / an
  - **Personnes avec source de revenus** : 5 000 F / an

### 4. 📝 Fiche de Suivi des Emprunts (Registre Lecteurs - Section 4)
- Conforme au tableau du document officiel (*Nom et prénom, Sexe, Niveau, Titre de livre, Contact*).
- Contrôle obligatoire de l'état au départ et au retour.
- Validation des retours en un clic avec notification toast.
- Bouton d'impression du registre.

---

## 🚀 Comment Lancer l'Application

### Méthode 1 : Double-clic direct
Double-cliquez simplement sur :
👉 `LANCER_APPLICATION.bat`

### Méthode 2 : Ligne de commande
```powershell
python app_web.py
```
L'interface s'ouvre automatiquement dans votre navigateur à l'adresse [http://127.0.0.1:5000](http://127.0.0.1:5000).
