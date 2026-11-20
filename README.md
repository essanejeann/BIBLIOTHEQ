# Gestion de Bibliothèque

Projet académique réalisé dans le cadre du cursus universitaire.

- **Étudiant :** ESSANE JEAN NOEL
- **Filière :** Génie Logiciel
- **Niveau :** Licence 2

---

## 1. Présentation du Projet

Application complète de gestion de bibliothèque développée selon les spécifications du document officiel d'organisation, du fonds documentaire et du règlement des prêts :

1. **Classification du fonds documentaire** :
   - Section Fonds Général & Littérature (10 catégories : Nouveautés, Romans, Théâtre, Informatique, etc.)
   - Section Jeunesse, Sciences & Documentaires (11 catégories : BD, Histoire, Médecine, Atlas, etc.)
2. **Gestion des usagers et tarification annuelle** :
   - Écoliers : 1 000 F CFA / an
   - Élèves (1er cycle) : 2 000 F CFA / an
   - Étudiants : 3 000 F CFA / an
   - Personnes avec source de revenus : 5 000 F CFA / an
3. **Registre des prêts (Fiche de suivi)** :
   - Délai réglementaire d'emprunt fixé à 2 semaines (14 jours).
   - Détection et calcul des jours de retard.
   - Contrôle systématique de l'état des ouvrages au départ et au retour.
4. **Persistance des données** :
   - Sauvegarde structurée au format JSON (`bibliotheque_data.json`).

---

## 2. Structure du Code

- `app_web.py` : Application principale avec interface web locale et tableau de bord.
- `app_gui.py` : Interface graphique de bureau (Tkinter).
- `bibliothe.py` : Version console (CLI) en ligne de commande.
- `bibliotheque_data.json` : Base de données locale partagée entre les interfaces.
- `LANCER_APPLICATION.bat` : Script de démarrage rapide pour Windows.

---

## 3. Prérequis et Installation

- **Python 3.10+**
- Bibliothèque requise : **Flask**

Pour installer Flask (si ce n'est pas déjà fait) :
```bash
pip install flask
```

---

## 4. Démarrage de l'Application

### Méthode 1 : Démarrage direct (Recommandé sous Windows)
Double-cliquez sur le fichier exécutable par lot :
```text
LANCER_APPLICATION.bat
```

### Méthode 2 : Lancement de l'interface Web & Dashboard
Ouvrez un terminal dans le dossier du projet et exécutez :
```bash
python app_web.py
```
Puis accédez à l'adresse suivante dans votre navigateur :
```text
http://127.0.0.1:5000
```

### Méthode 3 : Lancement de l'interface de bureau (Tkinter)
```bash
python app_gui.py
```

### Méthode 4 : Lancement en mode console
```bash
python bibliothe.py
```
