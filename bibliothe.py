"""
Application de Gestion de Bibliothèque (Mode Console)
Basée sur le Document de Référence :
- Classification du Fonds Documentaire (2 Sections, 21 Catégories)
- Conditions d'Emprunt (durée 2 semaines) et Tarifs d'Abonnement
- Registre Lecteurs / Fiche de Suivi des Emprunts
- Modalités d'acquisition et Contrôle de l'état des ouvrages
"""

import json
import os
import sys
from datetime import datetime, timedelta

DATA_FILE = "bibliotheque_data.json"

# --- RÉFÉRENTIELS BASÉS SUR LE DOCUMENT OFFICIEL ---

SECTIONS_CATEGORIES = {
    "Fonds Général & Littérature": [
        "Nouveautés",
        "Nouveaux horizons",
        "Usuels, encyclopédies",
        "Romans",
        "Théâtre",
        "Littérature négro-africaine",
        "Science sociale Afrique",
        "Littérature française",
        "Informatique et généralités / revues",
        "Philosophie / Religion"
    ],
    "Jeunesse, Sciences & Documentaires": [
        "Bande dessinée",
        "Album",
        "Littérature jeunesse, contes et légendes",
        "Histoire et Géographie",
        "Langue, SVT",
        "Sciences sociales",
        "Médecine",
        "Sciences techniques",
        "Art et loisirs",
        "Documentaire",
        "Atlas"
    ]
}

TARIFS_ABONNEMENT = {
    "1": ("Écoliers", 1000),
    "2": ("Élèves (1er cycle)", 2000),
    "3": ("Étudiants", 3000),
    "4": ("Personnes avec source de revenus", 5000)
}

DUREE_EMPRUNT_JOURS = 14  # 2 semaines


# --- GESTION DE LA PERSISTANCE (JSON) ---

def charger_donnees():
    """Charge les données du fichier JSON ou initialise une structure par défaut."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Erreur de lecture du fichier {DATA_FILE}: {e}")
            print("[*] Création d'une nouvelle base de données vierge.")

    donnees_initiales = {
        "livres": [],
        "usagers": [],
        "emprunts": []
    }
    sauvegarder_donnees(donnees_initiales)
    return donnees_initiales


def sauvegarder_donnees(donnees):
    """Sauvegarde les données dans le fichier JSON."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(donnees, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[!] Erreur de sauvegarde : {e}")


# --- UTILITAIRES D'AFFICHAGE ---

def effacer_ecran():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    input("\nAppuyez sur [Entrée] pour continuer...")


def titre(texte):
    print("=" * 70)
    print(f" {texte.upper()} ".center(70, "="))
    print("=" * 70)


def sous_titre(texte):
    print("\n" + "-" * 70)
    print(f"  {texte}")
    print("-" * 70)


# --- 1. GESTION DU FONDS DOCUMENTAIRE (LIVRES) ---

def choisir_section_et_categorie():
    """Permet de sélectionner une section et une catégorie conformes au document."""
    sections = list(SECTIONS_CATEGORIES.keys())
    print("\nSections disponibles :")
    for i, s in enumerate(sections, 1):
        print(f"  {i}. {s}")
    
    while True:
        choix_s = input(f"Choisissez la section (1-{len(sections)}) : ").strip()
        if choix_s.isdigit() and 1 <= int(choix_s) <= len(sections):
            section_choisie = sections[int(choix_s) - 1]
            break
        print("Choix invalide. Réessayez.")

    categories = SECTIONS_CATEGORIES[section_choisie]
    print(f"\nCatégories pour '{section_choisie}' :")
    for j, c in enumerate(categories, 1):
        print(f"  {j}. {c}")
    
    while True:
        choix_c = input(f"Choisissez la catégorie (1-{len(categories)}) : ").strip()
        if choix_c.isdigit() and 1 <= int(choix_c) <= len(categories):
            categorie_choisie = categories[int(choix_c) - 1]
            break
        print("Choix invalide. Réessayez.")

    return section_choisie, categorie_choisie


def ajouter_livre(donnees):
    titre("Ajout d'un nouvel ouvrage")
    
    titre_livre = input("Titre de l'ouvrage : ").strip()
    while not titre_livre:
        titre_livre = input("Le titre ne peut pas être vide : ").strip()
        
    auteur = input("Auteur(s) : ").strip() or "Inconnu"
    
    section, categorie = choisir_section_et_categorie()

    print("\nModalité d'acquisition :")
    print("  1. Don en nature")
    print("  2. Acquisition / Édition en partenariat avec les autorités régionales")
    choix_acq = input("Choix (1-2, défaut 1) : ").strip()
    acquisition = "Acquisition / Partenariat" if choix_acq == "2" else "Don en nature"

    print("\nÉtat initial de l'ouvrage (contrôle obligatoire) :")
    print("  1. Neuf")
    print("  2. Bon état")
    print("  3. État moyen")
    print("  4. Dégradé / Réparé")
    choix_etat = input("Choix (1-4, défaut 2) : ").strip()
    etats = {"1": "Neuf", "2": "Bon état", "3": "État moyen", "4": "Dégradé"}
    etat = etats.get(choix_etat, "Bon état")

    nouveau_id = max([l["id"] for l in donnees["livres"]], default=0) + 1
    
    nouveau_livre = {
        "id": nouveau_id,
        "titre": titre_livre,
        "auteur": auteur,
        "section": section,
        "categorie": categorie,
        "acquisition": acquisition,
        "etat": etat,
        "disponible": True
    }
    
    donnees["livres"].append(nouveau_livre)
    sauvegarder_donnees(donnees)
    print(f"\n[✓] Ouvrage '{titre_livre}' enregistré avec succès (ID: #{nouveau_id}).")
    pause()


def lister_livres(donnees):
    titre("Catalogue des Ouvrages (Fonds Documentaire)")
    if not donnees["livres"]:
        print("\nAucun livre enregistré pour le moment.")
        pause()
        return

    print(f"\nTotal : {len(donnees['livres'])} ouvrage(s)")
    print("-" * 90)
    print(f"{'ID':<4} | {'Titre':<30} | {'Auteur':<18} | {'Catégorie':<22} | {'Dispo':<8}")
    print("-" * 90)

    for l in donnees["livres"]:
        titre_court = l["titre"][:28] + ".." if len(l["titre"]) > 30 else l["titre"]
        auteur_court = l["auteur"][:16] + ".." if len(l["auteur"]) > 18 else l["auteur"]
        cat_courte = l["categorie"][:20] + ".." if len(l["categorie"]) > 22 else l["categorie"]
        dispo = "Oui" if l["disponible"] else "Emprunté"
        print(f"{l['id']:<4} | {titre_court:<30} | {auteur_court:<18} | {cat_courte:<22} | {dispo:<8}")
    print("-" * 90)
    pause()


def rechercher_livres(donnees):
    titre("Recherche d'Ouvrages")
    mot_cle = input("Entrez un titre, un auteur ou une catégorie : ").strip().lower()
    if not mot_cle:
        return

    resultats = [
        l for l in donnees["livres"]
        if mot_cle in l["titre"].lower()
        or mot_cle in l["auteur"].lower()
        or mot_cle in l["categorie"].lower()
        or mot_cle in l["section"].lower()
    ]

    print(f"\nRésultats trouvés : {len(resultats)}")
    if resultats:
        print("-" * 95)
        print(f"{'ID':<4} | {'Titre':<28} | {'Auteur':<18} | {'Section/Catégorie':<30} | {'État':<10}")
        print("-" * 95)
        for l in resultats:
            loc = f"{l['section'][:10]}.. / {l['categorie'][:15]}"
            print(f"{l['id']:<4} | {l['titre'][:26]:<28} | {l['auteur'][:16]:<18} | {loc:<30} | {l['etat']:<10}")
        print("-" * 95)
    pause()


# --- 2. GESTION DES USAGERS & ABONNEMENTS ---

def inscrire_usager(donnees):
    titre("Inscription d'un Usager / Abonnement")
    
    nom_prenom = input("Nom et prénom : ").strip()
    while not nom_prenom:
        nom_prenom = input("Le nom et prénom sont obligatoires : ").strip()

    print("\nSexe :")
    print("  1. Masculin (M)")
    print("  2. Féminin (F)")
    choix_sexe = input("Choix (1-2) : ").strip()
    sexe = "F" if choix_sexe == "2" else "M"

    print("\nCatégorie d'usager et Tarif d'abonnement (annuel) :")
    for cle, (libelle, montant) in TARIFS_ABONNEMENT.items():
        print(f"  {cle}. {libelle:<32} : {montant} F / an")
    
    while True:
        choix_cat = input("Sélectionnez la catégorie (1-4) : ").strip()
        if choix_cat in TARIFS_ABONNEMENT:
            niveau, tarif = TARIFS_ABONNEMENT[choix_cat]
            break
        print("Choix invalide.")

    contact = input("Contact (Téléphone / Adresse) : ").strip()
    while not contact:
        contact = input("Le contact est obligatoire pour la fiche de suivi : ").strip()

    nouveau_id = max([u["id"] for u in donnees["usagers"]], default=0) + 1
    date_inscription = datetime.now().strftime("%Y-%m-%d")

    nouvel_usager = {
        "id": nouveau_id,
        "nom_prenom": nom_prenom,
        "sexe": sexe,
        "niveau": niveau,
        "tarif_annuel": tarif,
        "contact": contact,
        "date_inscription": date_inscription,
        "actif": True
    }

    donnees["usagers"].append(nouvel_usager)
    sauvegarder_donnees(donnees)
    
    print("\n" + "=" * 50)
    print(f"[✓] Usager inscrit avec succès !")
    print(f"    ID Lecteur : #{nouveau_id}")
    print(f"    Nom : {nom_prenom} ({sexe})")
    print(f"    Catégorie : {niveau}")
    print(f"    Cotisation annuelle : {tarif} F CFA")
    print("=" * 50)
    pause()


def lister_usagers(donnees):
    titre("Liste des Usagers Inscrits")
    if not donnees["usagers"]:
        print("\nAucun usager inscrit pour le moment.")
        pause()
        return

    print(f"\nTotal : {len(donnees['usagers'])} usager(s)")
    print("-" * 88)
    print(f"{'ID':<4} | {'Nom et Prénom':<25} | {'Sexe':<4} | {'Niveau / Catégorie':<28} | {'Contact':<16}")
    print("-" * 88)
    for u in donnees["usagers"]:
        print(f"{u['id']:<4} | {u['nom_prenom'][:23]:<25} | {u['sexe']:<4} | {u['niveau'][:26]:<28} | {u['contact']:<16}")
    print("-" * 88)
    pause()


# --- 3. PRÊTS ET FICHE DE SUIVI (REGISTRE DES LECTEURS) ---

def enregistrer_pret(donnees):
    titre("Enregistrement d'un Prêt d'Ouvrage")
    print("Rappel règlement : Durée maximale d'emprunt = 2 semaines (14 jours).\n")

    # Sélection de l'usager
    if not donnees["usagers"]:
        print("[!] Aucun usager inscrit. Veuillez d'abord inscrire un usager.")
        pause()
        return

    id_u_input = input("Entrez l'ID de l'usager (ou 'L' pour voir la liste) : ").strip()
    if id_u_input.upper() == "L":
        lister_usagers(donnees)
        id_u_input = input("Entrez l'ID de l'usager : ").strip()

    usager = next((u for u in donnees["usagers"] if str(u["id"]) == id_u_input), None)
    if not usager:
        print("[!] Usager introuvable.")
        pause()
        return

    # Vérification des emprunts en cours pour cet usager
    emprunts_en_cours = [
        e for e in donnees["emprunts"]
        if e["id_usager"] == usager["id"] and e["statut"] == "En cours"
    ]
    if len(emprunts_en_cours) >= 3:
        print(f"[!] L'usager {usager['nom_prenom']} a déjà 3 emprunts en cours. Limite atteinte.")
        pause()
        return

    # Sélection du livre
    livres_dispos = [l for l in donnees["livres"] if l["disponible"]]
    if not livres_dispos:
        print("[!] Aucun ouvrage disponible actuellement.")
        pause()
        return

    id_l_input = input("Entrez l'ID du livre à emprunter (ou 'L' pour chercher) : ").strip()
    if id_l_input.upper() == "L":
        rechercher_livres(donnees)
        id_l_input = input("Entrez l'ID du livre : ").strip()

    livre = next((l for l in donnees["livres"] if str(l["id"]) == id_l_input), None)
    if not livre:
        print("[!] Livre introuvable.")
        pause()
        return

    if not livre["disponible"]:
        print(f"[!] L'ouvrage '{livre['titre']}' est déjà emprunté.")
        pause()
        return

    # Contrôle obligatoire de l'état au départ
    print(f"\nContrôle de conformité de l'état (Gestionnaire / Mr Seidou) :")
    print(f"État actuel enregistré : {livre['etat']}")
    conf_etat = input("Confirmer l'état au départ du lecteur (laisser vide pour valider ou saisir nouvel état) : ").strip()
    etat_depart = conf_etat if conf_etat else livre["etat"]
    livre["etat"] = etat_depart

    # Calcul des dates
    maintenant = datetime.now()
    date_emprunt = maintenant.strftime("%Y-%m-%d")
    date_retour_prevue = (maintenant + timedelta(days=DUREE_EMPRUNT_JOURS)).strftime("%Y-%m-%d")

    nouveau_id_pret = max([e["id"] for e in donnees["emprunts"]], default=0) + 1

    fiche_emprunt = {
        "id": nouveau_id_pret,
        # Champs du tableau 4 du document de référence
        "nom_prenom": usager["nom_prenom"],
        "sexe": usager["sexe"],
        "niveau": usager["niveau"],
        "titre_livre": livre["titre"],
        "contact": usager["contact"],
        # Métadonnées opérationnelles
        "id_usager": usager["id"],
        "id_livre": livre["id"],
        "date_emprunt": date_emprunt,
        "date_retour_prevue": date_retour_prevue,
        "date_retour_effective": None,
        "etat_depart": etat_depart,
        "etat_retour": None,
        "statut": "En cours"
    }

    livre["disponible"] = False
    donnees["emprunts"].append(fiche_emprunt)
    sauvegarder_donnees(donnees)

    print("\n" + "=" * 60)
    print(f"[✓] Emprunt enregistré avec succès !")
    print(f"    Lecteur         : {usager['nom_prenom']} ({usager['niveau']})")
    print(f"    Livre           : {livre['titre']}")
    print(f"    Date d'emprunt  : {date_emprunt}")
    print(f"    Délai autorisé  : 2 semaines")
    print(f"    Date de retour max : {date_retour_prevue}")
    print("=" * 60)
    pause()


def retourner_livre(donnees):
    titre("Retour d'un Ouvrage Emprunté")
    emprunts_en_cours = [e for e in donnees["emprunts"] if e["statut"] == "En cours"]
    
    if not emprunts_en_cours:
        print("\nAucun emprunt en cours à retourner.")
        pause()
        return

    print("Emprunts en cours :")
    print("-" * 85)
    print(f"{'ID Prêt':<8} | {'Lecteur':<22} | {'Titre du livre':<26} | {'Retour max':<12}")
    print("-" * 85)
    for e in emprunts_en_cours:
        print(f"#{e['id']:<7} | {e['nom_prenom'][:20]:<22} | {e['titre_livre'][:24]:<26} | {e['date_retour_prevue']:<12}")
    print("-" * 85)

    id_pret_input = input("\nEntrez le numéro ID du prêt à clôturer : ").strip().replace("#", "")
    pret = next((e for e in emprunts_en_cours if str(e["id"]) == id_pret_input), None)

    if not pret:
        print("[!] Prêt introuvable.")
        pause()
        return

    # Contrôle de l'état au retour
    print(f"\nÉtat de l'ouvrage au départ : {pret['etat_depart']}")
    etat_retour = input("État de l'ouvrage au retour [1: Neuf, 2: Bon, 3: Moyen, 4: Dégradé] (défaut: Bon) : ").strip()
    mapping_etat = {"1": "Neuf", "2": "Bon état", "3": "État moyen", "4": "Dégradé"}
    etat_final = mapping_etat.get(etat_retour, pret['etat_depart'])

    date_retour_effective = datetime.now().strftime("%Y-%m-%d")
    pret["date_retour_effective"] = date_retour_effective
    pret["etat_retour"] = etat_final
    pret["statut"] = "Retourné"

    # Mise à jour de la disponibilité du livre
    livre = next((l for l in donnees["livres"] if l["id"] == pret["id_livre"]), None)
    if livre:
        livre["disponible"] = True
        livre["etat"] = etat_final

    sauvegarder_donnees(donnees)

    # Vérification retard
    dt_prevue = datetime.strptime(pret["date_retour_prevue"], "%Y-%m-%d")
    dt_effective = datetime.strptime(date_retour_effective, "%Y-%m-%d")
    if dt_effective > dt_prevue:
        jours_retard = (dt_effective - dt_prevue).days
        print(f"\n[!] ATTENTION : Ouvrage retourné avec un retard de {jours_retard} jour(s) !")
    else:
        print("\n[✓] Ouvrage rendu dans les délais de 2 semaines.")

    print(f"[✓] Retour validé. Le livre '{pret['titre_livre']}' est à nouveau disponible.")
    pause()


def afficher_registre_lecteurs(donnees):
    """Affiche le registre des emprunts conformément au point 4 du document de référence."""
    titre("4. Fiche de Suivi des Emprunts (Registre Lecteurs)")
    if not donnees["emprunts"]:
        print("\nAucun enregistrement dans le registre pour le moment.")
        pause()
        return

    maintenant = datetime.now()
    print("-" * 105)
    print(f"{'Nom et prénom':<22} | {'Sexe':<4} | {'Niveau':<18} | {'Titre de livre':<25} | {'Contact':<14} | {'Statut':<10}")
    print("-" * 105)

    for e in donnees["emprunts"]:
        nom = e["nom_prenom"][:20]
        sexe = e["sexe"]
        niveau = e["niveau"][:16]
        titre_l = e["titre_livre"][:23]
        contact = e["contact"][:12]
        
        statut = e["statut"]
        if statut == "En cours":
            dt_prev = datetime.strptime(e["date_retour_prevue"], "%Y-%m-%d")
            if maintenant > dt_prev:
                statut = "RETARD !"
                
        print(f"{nom:<22} | {sexe:<4} | {niveau:<18} | {titre_l:<25} | {contact:<14} | {statut:<10}")

    print("-" * 105)
    pause()


# --- 4. STATISTIQUES ET RAPPORT D'ACTIVITÉ ---

def afficher_statistiques(donnees):
    titre("Tableau de Bord & Statistiques de la Bibliothèque")

    nb_livres = len(donnees["livres"])
    nb_dispos = sum(1 for l in donnees["livres"] if l["disponible"])
    nb_empruntes = nb_livres - nb_dispos

    nb_usagers = len(donnees["usagers"])
    total_cotisations = sum(u.get("tarif_annuel", 0) for u in donnees["usagers"])

    emprunts_en_cours = [e for e in donnees["emprunts"] if e["statut"] == "En cours"]
    maintenant = datetime.now()
    retards = [
        e for e in emprunts_en_cours 
        if maintenant > datetime.strptime(e["date_retour_prevue"], "%Y-%m-%d")
    ]

    print("\n--- Fonds Documentaire ---")
    print(f"  • Total d'ouvrages répertoriés   : {nb_livres}")
    print(f"  • Ouvrages disponibles           : {nb_dispos}")
    print(f"  • Ouvrages actuellement prêtés   : {nb_empruntes}")

    print("\n--- Usagers & Financement ---")
    print(f"  • Nombre total d'adhérents       : {nb_usagers}")
    print(f"  • Total des cotisations perçues  : {total_cotisations:,} F CFA")

    print("\n--- Prêts & Respect des Délais ---")
    print(f"  • Prêts en cours d'emprunt       : {len(emprunts_en_cours)}")
    print(f"  • Prêts en dépassement (> 2 sem) : {len(retards)}")
    if retards:
        print("    [!] Liste des retards :")
        for r in retards:
            print(f"        - {r['nom_prenom']} ({r['contact']}) : '{r['titre_livre']}' (Prévu le {r['date_retour_prevue']})")

    # Répartition par section
    print("\n--- Répartition par Section ---")
    for section in SECTIONS_CATEGORIES.keys():
        count = sum(1 for l in donnees["livres"] if l["section"] == section)
        print(f"  • {section:<35} : {count} livre(s)")

    pause()


# --- DONNÉES D'EXEMPLE DE DÉMONSTRATION ---

def injecter_donnees_demo(donnees):
    """Permet de remplir la bibliothèque avec des données types conformes au document."""
    if donnees["livres"] or donnees["usagers"]:
        print("\n[!] La bibliothèque contient déjà des données. Action annulée.")
        pause()
        return

    donnees["livres"] = [
        {"id": 1, "titre": "L'Aventure ambiguë", "auteur": "Cheikh Hamidou Kane", "section": "Fonds Général & Littérature", "categorie": "Littérature négro-africaine", "acquisition": "Don en nature", "etat": "Bon état", "disponible": True},
        {"id": 2, "titre": "Une si longue lettre", "auteur": "Mariama Bâ", "section": "Fonds Général & Littérature", "categorie": "Romans", "acquisition": "Acquisition / Partenariat", "etat": "Neuf", "disponible": False},
        {"id": 3, "titre": "Introduction aux Algorithmes", "auteur": "Thomas Cormen", "section": "Fonds Général & Littérature", "categorie": "Informatique et généralités / revues", "acquisition": "Acquisition / Partenariat", "etat": "Bon état", "disponible": True},
        {"id": 4, "titre": "Tintin au Congo", "auteur": "Hergé", "section": "Jeunesse, Sciences & Documentaires", "categorie": "Bande dessinée", "acquisition": "Don en nature", "etat": "État moyen", "disponible": True},
        {"id": 5, "titre": "Atlas Mondial du 21e Siècle", "auteur": "Collectif", "section": "Jeunesse, Sciences & Documentaires", "categorie": "Atlas", "acquisition": "Acquisition / Partenariat", "etat": "Neuf", "disponible": True}
    ]

    donnees["usagers"] = [
        {"id": 1, "nom_prenom": "Aminata Diallo", "sexe": "F", "niveau": "Élèves (1er cycle)", "tarif_annuel": 2000, "contact": "07 01 02 03 04", "date_inscription": "2026-10-01", "actif": True},
        {"id": 2, "nom_prenom": "Moussa Traoré", "sexe": "M", "niveau": "Étudiants", "tarif_annuel": 3000, "contact": "05 11 22 33 44", "date_inscription": "2026-10-15", "actif": True},
        {"id": 3, "nom_prenom": "Fatou Ndiaye", "sexe": "F", "niveau": "Écoliers", "tarif_annuel": 1000, "contact": "01 23 45 67 89", "date_inscription": "2026-11-01", "actif": True}
    ]

    donnees["emprunts"] = [
        {
            "id": 1,
            "nom_prenom": "Aminata Diallo",
            "sexe": "F",
            "niveau": "Élèves (1er cycle)",
            "titre_livre": "Une si longue lettre",
            "contact": "07 01 02 03 04",
            "id_usager": 1,
            "id_livre": 2,
            "date_emprunt": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "date_retour_prevue": (datetime.now() + timedelta(days=9)).strftime("%Y-%m-%d"),
            "date_retour_effective": None,
            "etat_depart": "Neuf",
            "etat_retour": None,
            "statut": "En cours"
        }
    ]

    sauvegarder_donnees(donnees)
    print("\n[✓] Données de démonstration chargées avec succès !")
    pause()


# --- MENU PRINCIPAL ---

def afficher_menu():
    print("""
╔════════════════════════════════════════════════════════════════════╗
║               SYSTÈME DE GESTION DE BIBLIOTHÈQUE                   ║
║           Conforme au Règlement & Fonds Documentaire               ║
╠════════════════════════════════════════════════════════════════════╣
║ 1. GESTION DU FONDS DOCUMENTAIRE                                   ║
║    [1] Ajouter un livre (Section, Catégorie, État, Acquisition)    ║
║    [2] Consulter le catalogue des livres                           ║
║    [3] Rechercher un livre                                         ║
║                                                                    ║
║ 2. GESTION DES USAGERS & ABONNEMENTS                               ║
║    [4] Inscrire un usager (Écolier, Élève, Étudiant, Actif)        ║
║    [5] Liste des usagers                                           ║
║                                                                    ║
║ 3. REGISTRE DES PRÊTS (Délai : 2 semaines)                         ║
║    [6] Enregistrer un prêt (Fiche lecteur & Contrôle de l'état)    ║
║    [7] Enregistrer un retour de livre                              ║
║    [8] Afficher la Fiche de Suivi des Emprunts (Registre Lecteurs) ║
║                                                                    ║
║ 4. TABLEAU DE BORD & SYSTÈME                                       ║
║    [9] Statistiques (Fonds, Cotisations, Retards)                  ║
║    [D] Charger des données de test / démonstration                 ║
║    [Q] Quitter l'application                                       ║
╚════════════════════════════════════════════════════════════════════╝
""")


def main():
    donnees = charger_donnees()
    
    while True:
        effacer_ecran()
        afficher_menu()
        choix = input("Votre sélection : ").strip().upper()

        if choix == "1":
            ajouter_livre(donnees)
        elif choix == "2":
            lister_livres(donnees)
        elif choix == "3":
            rechercher_livres(donnees)
        elif choix == "4":
            inscrire_usager(donnees)
        elif choix == "5":
            lister_usagers(donnees)
        elif choix == "6":
            enregistrer_pret(donnees)
        elif choix == "7":
            retourner_livre(donnees)
        elif choix == "8":
            afficher_registre_lecteurs(donnees)
        elif choix == "9":
            afficher_statistiques(donnees)
        elif choix == "D":
            injecter_donnees_demo(donnees)
        elif choix == "Q":
            sauvegarder_donnees(donnees)
            print("\nMerci d'avoir utilisé le système de gestion de la bibliothèque. À bientôt !\n")
            break
        else:
            print("\nOption invalide, veuillez réessayer.")
            pause()


if __name__ == "__main__":
    main()

