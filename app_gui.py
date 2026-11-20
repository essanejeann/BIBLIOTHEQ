"""
Application Graphique (GUI) de Gestion de Bibliothèque avec Tableau de Bord (Dashboard)
Conforme au Document de Référence :
- Classification du Fonds Documentaire (2 Sections, 21 Catégories)
- Conditions d'Emprunt (2 semaines) et Tarifs d'Abonnement (Écoliers, Élèves, Étudiants, Actifs)
- Registre des Lecteurs (Fiche de Suivi des Emprunts)
- Modalités d'acquisition et Contrôle systématique de l'état
"""

import json
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
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
    "Écoliers": 1000,
    "Élèves (1er cycle)": 2000,
    "Étudiants": 3000,
    "Personnes avec source de revenus": 5000
}

DUREE_EMPRUNT_JOURS = 14  # 2 semaines


# --- CHARGEMENT ET SAUVEGARDE DES DONNÉES ---
def charger_donnees():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"livres": [], "usagers": [], "emprunts": []}


def sauvegarder_donnees(donnees):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(donnees, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Erreur de Sauvegarde", f"Impossible d'enregistrer : {e}")


# --- CLASSE PRINCIPALE DE L'APPLICATION ---
class BibliothequeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Système de Gestion de Bibliothèque & Dashboard")
        self.geometry("1180x760")
        self.minsize(980, 650)
        self.configure(bg="#0f172a")

        # Chargement des données
        self.donnees = charger_donnees()

        # Styles et Thème Moderne
        self.configurer_styles()

        # Conteneur Principal (Sidebar à gauche + Zone de contenu à droite)
        self.creer_layout_principal()

        # Afficher le Dashboard par défaut
        self.afficher_page("dashboard")

    def configurer_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        # Style Treeview (Tableaux)
        self.style.configure(
            "Treeview",
            background="#ffffff",
            foreground="#1e293b",
            rowheight=30,
            fieldbackground="#ffffff",
            font=("Segoe UI", 10)
        )
        self.style.configure(
            "Treeview.Heading",
            background="#f1f5f9",
            foreground="#0f172a",
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )
        self.style.map("Treeview", background=[("selected", "#3b82f6")], foreground=[("selected", "#ffffff")])

        # Style Boutons ttk
        self.style.configure(
            "Primary.TButton",
            background="#2563eb",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=8
        )
        self.style.map("Primary.TButton", background=[("active", "#1d4ed8")])

        self.style.configure(
            "Success.TButton",
            background="#10b981",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=8
        )
        self.style.map("Success.TButton", background=[("active", "#059669")])

        self.style.configure(
            "Danger.TButton",
            background="#ef4444",
            foreground="#ffffff",
            font=("Segoe UI", 10, "bold"),
            borderwidth=0,
            padding=8
        )
        self.style.map("Danger.TButton", background=[("active", "#dc2626")])

    def creer_layout_principal(self):
        # 1. Barre Latérale (Sidebar)
        self.sidebar = tk.Frame(self, bg="#1e293b", width=240)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # En-tête Sidebar
        lbl_logo = tk.Label(
            self.sidebar,
            text="📚 BIBLIOTHÈQUE",
            bg="#1e293b",
            fg="#f8fafc",
            font=("Segoe UI", 15, "bold"),
            pady=20
        )
        lbl_logo.pack(fill="x")

        lbl_desc = tk.Label(
            self.sidebar,
            text="Fonds & Suivi des Prêts",
            bg="#1e293b",
            fg="#94a3b8",
            font=("Segoe UI", 9)
        )
        lbl_desc.pack(fill="x", pady=(0, 20))

        # Boutons de navigation
        self.nav_btns = {}
        pages = [
            ("dashboard", "📊  Tableau de Bord"),
            ("livres", "📖  Fonds Documentaire"),
            ("usagers", "👥  Usagers & Abonnements"),
            ("emprunts", "📝  Registre des Prêts")
        ]

        for p_id, p_nom in pages:
            btn = tk.Button(
                self.sidebar,
                text=p_nom,
                anchor="w",
                padx=20,
                pady=12,
                bg="#1e293b",
                fg="#cbd5e1",
                activebackground="#334155",
                activeforeground="#ffffff",
                relief="flat",
                font=("Segoe UI", 10, "bold"),
                cursor="hand2",
                command=lambda pid=p_id: self.afficher_page(pid)
            )
            btn.pack(fill="x", pady=2)
            self.nav_btns[p_id] = btn

        # 2. Zone de Contenu Principale
        self.conteneur = tk.Frame(self, bg="#f8fafc")
        self.conteneur.pack(side="right", fill="both", expand=True)

        # Pages
        self.frames = {
            "dashboard": tk.Frame(self.conteneur, bg="#f8fafc"),
            "livres": tk.Frame(self.conteneur, bg="#f8fafc"),
            "usagers": tk.Frame(self.conteneur, bg="#f8fafc"),
            "emprunts": tk.Frame(self.conteneur, bg="#f8fafc")
        }

        for f in self.frames.values():
            f.grid(row=0, column=0, sticky="nsew")

        self.conteneur.grid_rowconfigure(0, weight=1)
        self.conteneur.grid_columnconfigure(0, weight=1)

    def afficher_page(self, page_id):
        # Mettre à jour l'apparence des boutons de navigation
        for pid, btn in self.nav_btns.items():
            if pid == page_id:
                btn.configure(bg="#2563eb", fg="#ffffff")
            else:
                btn.configure(bg="#1e293b", fg="#cbd5e1")

        frame = self.frames[page_id]
        frame.tkraise()

        # Rafraîchir les données de la page
        if page_id == "dashboard":
            self.rafraichir_dashboard()
        elif page_id == "livres":
            self.rafraichir_livres()
        elif page_id == "usagers":
            self.rafraichir_usagers()
        elif page_id == "emprunts":
            self.rafraichir_emprunts()

    # =========================================================================
    # 1. MODULE DASHBOARD (TABLEAU DE BORD)
    # =========================================================================
    def rafraichir_dashboard(self):
        frame = self.frames["dashboard"]
        for child in frame.winfo_children():
            child.destroy()

        # En-tête
        hdr = tk.Frame(frame, bg="#ffffff", height=70, padx=25, pady=15)
        hdr.pack(fill="x")
        tk.Label(
            hdr,
            text="Tableau de Bord - Gestion de la Bibliothèque",
            font=("Segoe UI", 16, "bold"),
            bg="#ffffff",
            fg="#0f172a"
        ).pack(side="left")

        btn_act = tk.Button(
            hdr,
            text="🔄 Actualiser",
            font=("Segoe UI", 9, "bold"),
            bg="#f1f5f9",
            fg="#0f172a",
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
            command=self.rafraichir_dashboard
        )
        btn_act.pack(side="right")

        # Contenu défilable ou ventilé
        body = tk.Frame(frame, bg="#f8fafc", padx=25, pady=20)
        body.pack(fill="both", expand=True)

        # Calculs statistiques
        total_livres = len(self.donnees["livres"])
        livres_dispos = sum(1 for l in self.donnees["livres"] if l["disponible"])
        emprunts_en_cours = [e for e in self.donnees["emprunts"] if e["statut"] == "En cours"]
        
        maintenant = datetime.now()
        retards = [
            e for e in emprunts_en_cours
            if maintenant > datetime.strptime(e["date_retour_prevue"], "%Y-%m-%d")
        ]
        total_usagers = len(self.donnees["usagers"])
        total_cotisations = sum(u.get("tarif_annuel", 0) for u in self.donnees["usagers"])

        # Ligne de Cartes KPI
        kpi_frame = tk.Frame(body, bg="#f8fafc")
        kpi_frame.pack(fill="x", pady=(0, 20))

        cartes = [
            ("TOTAL OUVRAGES", str(total_livres), "#3b82f6", "Livres inventoriés"),
            ("DISPONIBLES", str(livres_dispos), "#10b981", f"{total_livres - livres_dispos} empruntés"),
            ("EMPRUNTS EN COURS", str(len(emprunts_en_cours)), "#8b5cf6", "Délai max : 2 sem"),
            ("RETARDS DÉTECTÉS", str(len(retards)), "#ef4444" if retards else "#64748b", "À relancer"),
            ("TOTAL COTISATIONS", f"{total_cotisations:,} F", "#0ea5e9", f"{total_usagers} usagers inscrits")
        ]

        for i, (titre_kpi, val_kpi, couleur, soustitre) in enumerate(cartes):
            card = tk.Frame(kpi_frame, bg="#ffffff", bd=1, relief="solid", highlightthickness=0)
            card.configure(highlightbackground="#e2e8f0", highlightcolor="#e2e8f0")
            card.pack(side="left", fill="both", expand=True, padx=5)

            # Barre colorée au sommet
            top_bar = tk.Frame(card, bg=couleur, height=4)
            top_bar.pack(fill="x")

            inner = tk.Frame(card, bg="#ffffff", padx=15, pady=12)
            inner.pack(fill="both", expand=True)

            tk.Label(inner, text=titre_kpi, font=("Segoe UI", 8, "bold"), fg="#64748b", bg="#ffffff").pack(anchor="w")
            tk.Label(inner, text=val_kpi, font=("Segoe UI", 18, "bold"), fg="#0f172a", bg="#ffffff").pack(anchor="w", pady=3)
            tk.Label(inner, text=soustitre, font=("Segoe UI", 8), fg="#94a3b8", bg="#ffffff").pack(anchor="w")

        # Zone inférieure : Graphique de répartition + Tableau des alertes/retards
        bottom_frame = tk.Frame(body, bg="#f8fafc")
        bottom_frame.pack(fill="both", expand=True)

        # Colonne Gauche : Répartition par section (Document Officiel)
        gauche = tk.Frame(bottom_frame, bg="#ffffff", bd=1, relief="solid")
        gauche.configure(highlightbackground="#e2e8f0", highlightcolor="#e2e8f0")
        gauche.pack(side="left", fill="both", expand=True, padx=(0, 10))

        tk.Label(
            gauche,
            text="Fonds Documentaire par Section",
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff",
            fg="#0f172a",
            padx=15,
            pady=12
        ).pack(anchor="w")

        # Calcul par section
        sec1_nom = "Fonds Général & Littérature"
        sec2_nom = "Jeunesse, Sciences & Documentaires"
        c1 = sum(1 for l in self.donnees["livres"] if l.get("section") == sec1_nom)
        c2 = sum(1 for l in self.donnees["livres"] if l.get("section") == sec2_nom)
        max_c = max(c1, c2, 1)

        graph_box = tk.Frame(gauche, bg="#ffffff", padx=15, pady=10)
        graph_box.pack(fill="both", expand=True)

        for sec_titre, count, col in [(sec1_nom, c1, "#3b82f6"), (sec2_nom, c2, "#10b981")]:
            row = tk.Frame(graph_box, bg="#ffffff", pady=8)
            row.pack(fill="x")
            pct = int((count / max(total_livres, 1)) * 100)
            tk.Label(row, text=f"{sec_titre} : {count} livre(s) ({pct}%)", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#334155").pack(anchor="w")
            
            # Barre de progression personnalisée
            bar_bg = tk.Frame(row, bg="#e2e8f0", height=12)
            bar_bg.pack(fill="x", pady=4)
            bar_fill = tk.Frame(bar_bg, bg=col, height=12, width=int(350 * (count / max_c)))
            bar_fill.place(x=0, y=0)

        # Détail des catégories majeures
        tk.Label(graph_box, text="Détail des Catégories Clés :", font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#64748b", pady=10).pack(anchor="w")
        for cat in ["Romans", "Informatique et généralités / revues", "Bande dessinée", "Atlas", "Littérature négro-africaine"]:
            cnt = sum(1 for l in self.donnees["livres"] if l.get("categorie") == cat)
            tk.Label(graph_box, text=f"  • {cat:<36} : {cnt}", font=("Segoe UI", 9), bg="#ffffff", fg="#475569").pack(anchor="w")

        # Colonne Droite : Alertes de retards et emprunts à suivre
        droite = tk.Frame(bottom_frame, bg="#ffffff", bd=1, relief="solid")
        droite.configure(highlightbackground="#e2e8f0", highlightcolor="#e2e8f0")
        droite.pack(side="right", fill="both", expand=True, padx=(10, 0))

        tk.Label(
            droite,
            text="⚠️ Emprunts en Retard ou Urgents (> 2 semaines)",
            font=("Segoe UI", 11, "bold"),
            bg="#ffffff",
            fg="#dc2626" if retards else "#0f172a",
            padx=15,
            pady=12
        ).pack(anchor="w")

        cols_alert = ("Lecteur", "Livre", "Contact", "Retour Prévu")
        tree_alert = ttk.Treeview(droite, columns=cols_alert, show="headings", height=8)
        for col in cols_alert:
            tree_alert.heading(col, text=col)
            tree_alert.column(col, width=110, anchor="w")

        tree_alert.pack(fill="both", expand=True, padx=12, pady=10)

        if retards:
            for r in retards:
                tree_alert.insert("", "end", values=(r["nom_prenom"], r["titre_livre"], r["contact"], r["date_retour_prevue"]))
        else:
            tree_alert.insert("", "end", values=("Aucun retard", "Tous les prêts", "sont conformes", "au délai de 2 sem."))

    # =========================================================================
    # 2. MODULE LIVRES (FONDS DOCUMENTAIRE)
    # =========================================================================
    def rafraichir_livres(self):
        frame = self.frames["livres"]
        for child in frame.winfo_children():
            child.destroy()

        # En-tête avec Recherche et Bouton Ajouter
        hdr = tk.Frame(frame, bg="#ffffff", height=70, padx=25, pady=15)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Catalogue du Fonds Documentaire", font=("Segoe UI", 16, "bold"), bg="#ffffff", fg="#0f172a").pack(side="left")

        btn_add = tk.Button(
            hdr,
            text="➕ Ajouter un Ouvrage",
            font=("Segoe UI", 9, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            relief="flat",
            padx=15,
            pady=6,
            cursor="hand2",
            command=self.ouvrir_dialogue_ajouter_livre
        )
        btn_add.pack(side="right")

        # Barre de Filtres
        filter_bar = tk.Frame(frame, bg="#f8fafc", padx=25, pady=10)
        filter_bar.pack(fill="x")

        tk.Label(filter_bar, text="Rechercher :", font=("Segoe UI", 10, "bold"), bg="#f8fafc", fg="#334155").pack(side="left", padx=(0, 5))
        self.entry_search_livre = tk.Entry(filter_bar, font=("Segoe UI", 10), width=35)
        self.entry_search_livre.pack(side="left", padx=5)
        self.entry_search_livre.bind("<KeyRelease>", lambda e: self.filtrer_tableau_livres())

        btn_suppr = tk.Button(
            filter_bar,
            text="🗑️ Supprimer sélection",
            font=("Segoe UI", 9),
            bg="#fee2e2",
            fg="#b91c1c",
            relief="flat",
            padx=10,
            pady=3,
            cursor="hand2",
            command=self.supprimer_livre_selectionne
        )
        btn_suppr.pack(side="right")

        # Tableau des Livres
        table_frame = tk.Frame(frame, bg="#f8fafc", padx=25, pady=(0, 20))
        table_frame.pack(fill="both", expand=True)

        cols = ("ID", "Titre", "Auteur", "Section", "Catégorie", "Acquisition", "État", "Disponibilité")
        self.tree_livres = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        widths = {"ID": 50, "Titre": 200, "Auteur": 140, "Section": 180, "Catégorie": 160, "Acquisition": 140, "État": 90, "Disponibilité": 95}
        for col in cols:
            self.tree_livres.heading(col, text=col)
            self.tree_livres.column(col, width=widths.get(col, 100), anchor="w")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_livres.yview)
        self.tree_livres.configure(yscrollcommand=scroll.set)
        self.tree_livres.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.filtrer_tableau_livres()

    def filtrer_tableau_livres(self):
        mot_cle = self.entry_search_livre.get().strip().lower()
        for item in self.tree_livres.get_children():
            self.tree_livres.delete(item)

        for l in self.donnees["livres"]:
            texte_complet = f"{l['titre']} {l['auteur']} {l['categorie']} {l['section']}".lower()
            if not mot_cle or mot_cle in texte_complet:
                dispo = "Disponible" if l["disponible"] else "Emprunté"
                self.tree_livres.insert("", "end", values=(
                    l["id"],
                    l["titre"],
                    l["auteur"],
                    l["section"],
                    l["categorie"],
                    l["acquisition"],
                    l["etat"],
                    dispo
                ))

    def ouvrir_dialogue_ajouter_livre(self):
        dlg = tk.Toplevel(self)
        dlg.title("Ajouter un nouvel ouvrage")
        dlg.geometry("520x560")
        dlg.configure(bg="#ffffff")
        dlg.grab_set()

        tk.Label(dlg, text="Nouvel Ouvrage (Fonds Documentaire)", font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#0f172a").pack(pady=15)

        form = tk.Frame(dlg, bg="#ffffff", padx=25)
        form.pack(fill="both", expand=True)

        def row(label_text):
            r = tk.Frame(form, bg="#ffffff", pady=5)
            r.pack(fill="x")
            tk.Label(r, text=label_text, font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#334155").pack(anchor="w")
            return r

        # Titre
        r1 = row("Titre de l'ouvrage *")
        e_titre = tk.Entry(r1, font=("Segoe UI", 10), width=45)
        e_titre.pack(fill="x")

        # Auteur
        r2 = row("Auteur(s)")
        e_auteur = tk.Entry(r2, font=("Segoe UI", 10), width=45)
        e_auteur.pack(fill="x")

        # Section
        r3 = row("Section (Règlement officiel) *")
        cb_section = ttk.Combobox(r3, values=list(SECTIONS_CATEGORIES.keys()), state="readonly", font=("Segoe UI", 9))
        cb_section.current(0)
        cb_section.pack(fill="x")

        # Catégorie (en cascade)
        r4 = row("Catégorie / Rayon *")
        cb_cat = ttk.Combobox(r4, values=SECTIONS_CATEGORIES[cb_section.get()], state="readonly", font=("Segoe UI", 9))
        cb_cat.current(0)
        cb_cat.pack(fill="x")

        def on_section_change(event):
            sec = cb_section.get()
            cats = SECTIONS_CATEGORIES.get(sec, [])
            cb_cat.configure(values=cats)
            if cats:
                cb_cat.current(0)

        cb_section.bind("<<ComboboxSelected>>", on_section_change)

        # Modalité d'acquisition
        r5 = row("Modalité d'acquisition")
        cb_acq = ttk.Combobox(r5, values=["Don en nature", "Acquisition auprès des maisons d'édition (partenariat)"], state="readonly", font=("Segoe UI", 9))
        cb_acq.current(0)
        cb_acq.pack(fill="x")

        # État initial
        r6 = row("État de l'ouvrage au départ (Contrôle systématique)")
        cb_etat = ttk.Combobox(r6, values=["Neuf", "Bon état", "État moyen", "Dégradé"], state="readonly", font=("Segoe UI", 9))
        cb_etat.current(1)
        cb_etat.pack(fill="x")

        def valider():
            titre = e_titre.get().strip()
            if not titre:
                messagebox.showwarning("Validation", "Le titre est obligatoire.", parent=dlg)
                return

            nouveau_id = max([l["id"] for l in self.donnees["livres"]], default=0) + 1
            livre = {
                "id": nouveau_id,
                "titre": titre,
                "auteur": e_auteur.get().strip() or "Inconnu",
                "section": cb_section.get(),
                "categorie": cb_cat.get(),
                "acquisition": cb_acq.get(),
                "etat": cb_etat.get(),
                "disponible": True
            }

            self.donnees["livres"].append(livre)
            sauvegarder_donnees(self.donnees)
            dlg.destroy()
            self.filtrer_tableau_livres()
            messagebox.showinfo("Succès", f"L'ouvrage '{titre}' a été ajouté avec succès.")

        btn_box = tk.Frame(dlg, bg="#ffffff", pady=15)
        btn_box.pack(fill="x")
        tk.Button(btn_box, text="Enregistrer l'ouvrage", bg="#2563eb", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=8, cursor="hand2", command=valider).pack()

    def supprimer_livre_selectionne(self):
        sel = self.tree_livres.selection()
        if not sel:
            messagebox.showwarning("Sélection", "Veuillez sélectionner un ouvrage à supprimer.")
            return

        item = self.tree_livres.item(sel[0])
        livre_id = item["values"][0]
        titre = item["values"][1]

        if messagebox.askyesno("Confirmation", f"Êtes-vous sûr de vouloir supprimer l'ouvrage #{livre_id} : '{titre}' ?"):
            self.donnees["livres"] = [l for l in self.donnees["livres"] if l["id"] != livre_id]
            sauvegarder_donnees(self.donnees)
            self.filtrer_tableau_livres()

    # =========================================================================
    # 3. MODULE USAGERS & ABONNEMENTS
    # =========================================================================
    def rafraichir_usagers(self):
        frame = self.frames["usagers"]
        for child in frame.winfo_children():
            child.destroy()

        hdr = tk.Frame(frame, bg="#ffffff", height=70, padx=25, pady=15)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Gestion des Usagers & Abonnements", font=("Segoe UI", 16, "bold"), bg="#ffffff", fg="#0f172a").pack(side="left")

        btn_add = tk.Button(
            hdr,
            text="➕ Inscrire un Usager",
            font=("Segoe UI", 9, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            relief="flat",
            padx=15,
            pady=6,
            cursor="hand2",
            command=self.ouvrir_dialogue_ajouter_usager
        )
        btn_add.pack(side="right")

        # Table des Usagers
        table_frame = tk.Frame(frame, bg="#f8fafc", padx=25, pady=20)
        table_frame.pack(fill="both", expand=True)

        cols = ("ID", "Nom et Prénom", "Sexe", "Catégorie / Niveau", "Tarif Annuel", "Contact", "Date Adhésion")
        self.tree_usagers = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        widths = {"ID": 50, "Nom et Prénom": 220, "Sexe": 60, "Catégorie / Niveau": 200, "Tarif Annuel": 120, "Contact": 140, "Date Adhésion": 120}
        for col in cols:
            self.tree_usagers.heading(col, text=col)
            self.tree_usagers.column(col, width=widths.get(col, 100), anchor="w")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_usagers.yview)
        self.tree_usagers.configure(yscrollcommand=scroll.set)
        self.tree_usagers.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for u in self.donnees["usagers"]:
            self.tree_usagers.insert("", "end", values=(
                u["id"],
                u["nom_prenom"],
                u["sexe"],
                u["niveau"],
                f"{u.get('tarif_annuel', 0):,} F CFA",
                u["contact"],
                u.get("date_inscription", "-")
            ))

    def ouvrir_dialogue_ajouter_usager(self):
        dlg = tk.Toplevel(self)
        dlg.title("Inscription d'un Usager")
        dlg.geometry("480x480")
        dlg.configure(bg="#ffffff")
        dlg.grab_set()

        tk.Label(dlg, text="Inscription & Tarification d'Abonnement", font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#0f172a").pack(pady=15)

        form = tk.Frame(dlg, bg="#ffffff", padx=25)
        form.pack(fill="both", expand=True)

        def row(label_text):
            r = tk.Frame(form, bg="#ffffff", pady=5)
            r.pack(fill="x")
            tk.Label(r, text=label_text, font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#334155").pack(anchor="w")
            return r

        r1 = row("Nom et prénom *")
        e_nom = tk.Entry(r1, font=("Segoe UI", 10), width=45)
        e_nom.pack(fill="x")

        r2 = row("Sexe *")
        cb_sexe = ttk.Combobox(r2, values=["M (Masculin)", "F (Féminin)"], state="readonly", font=("Segoe UI", 9))
        cb_sexe.current(0)
        cb_sexe.pack(fill="x")

        r3 = row("Catégorie d'usager (Règlement officiel) *")
        categories_options = [
            f"{cat} - {tarif:,} F / an" for cat, tarif in TARIFS_ABONNEMENT.items()
        ]
        cb_cat = ttk.Combobox(r3, values=categories_options, state="readonly", font=("Segoe UI", 9))
        cb_cat.current(0)
        cb_cat.pack(fill="x")

        r4 = row("Contact (Téléphone / Adresse) *")
        e_contact = tk.Entry(r4, font=("Segoe UI", 10), width=45)
        e_contact.pack(fill="x")

        def valider():
            nom = e_nom.get().strip()
            contact = e_contact.get().strip()
            if not nom or not contact:
                messagebox.showwarning("Validation", "Nom et contact sont obligatoires.", parent=dlg)
                return

            cat_sel = cb_cat.get().split(" - ")[0]
            tarif = TARIFS_ABONNEMENT.get(cat_sel, 0)
            sexe = "F" if "F" in cb_sexe.get() else "M"

            nouveau_id = max([u["id"] for u in self.donnees["usagers"]], default=0) + 1
            nouvel_usager = {
                "id": nouveau_id,
                "nom_prenom": nom,
                "sexe": sexe,
                "niveau": cat_sel,
                "tarif_annuel": tarif,
                "contact": contact,
                "date_inscription": datetime.now().strftime("%Y-%m-%d"),
                "actif": True
            }

            self.donnees["usagers"].append(nouvel_usager)
            sauvegarder_donnees(self.donnees)
            dlg.destroy()
            self.rafraichir_usagers()
            messagebox.showinfo("Succès", f"L'usager '{nom}' a été enregistré avec la cotisation : {tarif:,} F CFA.")

        btn_box = tk.Frame(dlg, bg="#ffffff", pady=15)
        btn_box.pack(fill="x")
        tk.Button(btn_box, text="Valider l'Inscription", bg="#2563eb", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=8, cursor="hand2", command=valider).pack()

    # =========================================================================
    # 4. MODULE PRÊTS (REGISTRE DES LECTEURS - SECTION 4 DU DOC)
    # =========================================================================
    def rafraichir_emprunts(self):
        frame = self.frames["emprunts"]
        for child in frame.winfo_children():
            child.destroy()

        hdr = tk.Frame(frame, bg="#ffffff", height=70, padx=25, pady=15)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Fiche de Suivi des Emprunts (Registre Lecteurs)", font=("Segoe UI", 16, "bold"), bg="#ffffff", fg="#0f172a").pack(side="left")

        btn_box = tk.Frame(hdr, bg="#ffffff")
        btn_box.pack(side="right")

        btn_retour = tk.Button(
            btn_box,
            text="📥 Enregistrer un Retour",
            font=("Segoe UI", 9, "bold"),
            bg="#10b981",
            fg="#ffffff",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.ouvrir_dialogue_retour
        )
        btn_retour.pack(side="left", padx=5)

        btn_pret = tk.Button(
            btn_box,
            text="➕ Nouvel Emprunt",
            font=("Segoe UI", 9, "bold"),
            bg="#2563eb",
            fg="#ffffff",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.ouvrir_dialogue_pret
        )
        btn_pret.pack(side="left", padx=5)

        # Tableau Conforme au Document de Référence
        table_frame = tk.Frame(frame, bg="#f8fafc", padx=25, pady=20)
        table_frame.pack(fill="both", expand=True)

        cols = ("ID", "Nom et prénom", "Sexe", "Niveau", "Titre de livre", "Contact", "Date Prêt", "Date Limite (2 sem)", "Statut")
        self.tree_emprunts = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        widths = {"ID": 45, "Nom et prénom": 170, "Sexe": 50, "Niveau": 150, "Titre de livre": 200, "Contact": 110, "Date Prêt": 95, "Date Limite (2 sem)": 110, "Statut": 90}
        for col in cols:
            self.tree_emprunts.heading(col, text=col)
            self.tree_emprunts.column(col, width=widths.get(col, 100), anchor="w")

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_emprunts.yview)
        self.tree_emprunts.configure(yscrollcommand=scroll.set)
        self.tree_emprunts.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        maintenant = datetime.now()
        for e in self.donnees["emprunts"]:
            statut = e["statut"]
            if statut == "En cours":
                dt_p = datetime.strptime(e["date_retour_prevue"], "%Y-%m-%d")
                if maintenant > dt_p:
                    statut = "RETARD ⚠️"

            self.tree_emprunts.insert("", "end", values=(
                f"#{e['id']}",
                e["nom_prenom"],
                e["sexe"],
                e["niveau"],
                e["titre_livre"],
                e["contact"],
                e["date_emprunt"],
                e["date_retour_prevue"],
                statut
            ))

    def ouvrir_dialogue_pret(self):
        if not self.donnees["usagers"]:
            messagebox.showwarning("Avertissement", "Aucun usager inscrit. Veuillez d'abord inscrire un usager.")
            return

        livres_dispos = [l for l in self.donnees["livres"] if l["disponible"]]
        if not livres_dispos:
            messagebox.showwarning("Avertissement", "Aucun livre disponible actuellement.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Enregistrer un Emprunt (Délai 2 semaines)")
        dlg.geometry("520x450")
        dlg.configure(bg="#ffffff")
        dlg.grab_set()

        tk.Label(dlg, text="Nouveau Prêt d'Ouvrage", font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#0f172a").pack(pady=15)

        form = tk.Frame(dlg, bg="#ffffff", padx=25)
        form.pack(fill="both", expand=True)

        def row(label_text):
            r = tk.Frame(form, bg="#ffffff", pady=5)
            r.pack(fill="x")
            tk.Label(r, text=label_text, font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#334155").pack(anchor="w")
            return r

        # Usager
        r1 = row("Sélectionner l'Usager *")
        usagers_options = [f"#{u['id']} - {u['nom_prenom']} ({u['niveau']})" for u in self.donnees["usagers"]]
        cb_u = ttk.Combobox(r1, values=usagers_options, state="readonly", font=("Segoe UI", 9))
        cb_u.current(0)
        cb_u.pack(fill="x")

        # Livre
        r2 = row("Sélectionner l'Ouvrage Disponible *")
        livres_options = [f"#{l['id']} - {l['titre']} [{l['etat']}]" for l in livres_dispos]
        cb_l = ttk.Combobox(r2, values=livres_options, state="readonly", font=("Segoe UI", 9))
        cb_l.current(0)
        cb_l.pack(fill="x")

        # État au départ
        r3 = row("Contrôle systématique de l'état au départ (Mr Seidou) *")
        cb_etat = ttk.Combobox(r3, values=["Neuf", "Bon état", "État moyen", "Dégradé"], state="readonly", font=("Segoe UI", 9))
        cb_etat.current(1)
        cb_etat.pack(fill="x")

        # Infos règle
        info_frame = tk.Frame(form, bg="#eff6ff", padx=10, pady=8, bd=1, relief="solid")
        info_frame.configure(highlightbackground="#bfdbfe", highlightcolor="#bfdbfe")
        info_frame.pack(fill="x", pady=10)
        date_retour_calcul = (datetime.now() + timedelta(days=DUREE_EMPRUNT_JOURS)).strftime("%d/%m/%Y")
        tk.Label(
            info_frame,
            text=f"📌 Règle officielle : Durée autorisée = 2 semaines (14 jours).\nRetour limite calculé au : {date_retour_calcul}",
            bg="#eff6ff",
            fg="#1e40af",
            font=("Segoe UI", 9)
        ).pack(anchor="w")

        def valider():
            u_id = int(cb_u.get().split(" - ")[0].replace("#", ""))
            l_id = int(cb_l.get().split(" - ")[0].replace("#", ""))

            usager = next(u for u in self.donnees["usagers"] if u["id"] == u_id)
            livre = next(l for l in self.donnees["livres"] if l["id"] == l_id)

            maintenant = datetime.now()
            date_emprunt = maintenant.strftime("%Y-%m-%d")
            date_retour_prevue = (maintenant + timedelta(days=DUREE_EMPRUNT_JOURS)).strftime("%Y-%m-%d")

            nouveau_id_pret = max([e["id"] for e in self.donnees["emprunts"]], default=0) + 1

            fiche_emprunt = {
                "id": nouveau_id_pret,
                "nom_prenom": usager["nom_prenom"],
                "sexe": usager["sexe"],
                "niveau": usager["niveau"],
                "titre_livre": livre["titre"],
                "contact": usager["contact"],
                "id_usager": usager["id"],
                "id_livre": livre["id"],
                "date_emprunt": date_emprunt,
                "date_retour_prevue": date_retour_prevue,
                "date_retour_effective": None,
                "etat_depart": cb_etat.get(),
                "etat_retour": None,
                "statut": "En cours"
            }

            livre["disponible"] = False
            livre["etat"] = cb_etat.get()
            self.donnees["emprunts"].append(fiche_emprunt)
            sauvegarder_donnees(self.donnees)

            dlg.destroy()
            self.rafraichir_emprunts()
            messagebox.showinfo("Succès", f"Prêt #{nouveau_id_pret} enregistré avec succès.\nDate retour maximale : {date_retour_prevue}")

        btn_box = tk.Frame(dlg, bg="#ffffff", pady=15)
        btn_box.pack(fill="x")
        tk.Button(btn_box, text="Confirmer l'Emprunt", bg="#2563eb", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=8, cursor="hand2", command=valider).pack()

    def ouvrir_dialogue_retour(self):
        emprunts_en_cours = [e for e in self.donnees["emprunts"] if e["statut"] == "En cours"]
        if not emprunts_en_cours:
            messagebox.showinfo("Information", "Aucun emprunt en cours à retourner.")
            return

        dlg = tk.Toplevel(self)
        dlg.title("Validation d'un Retour de Livre")
        dlg.geometry("500x380")
        dlg.configure(bg="#ffffff")
        dlg.grab_set()

        tk.Label(dlg, text="Clôture de Prêt & Contrôle au Retour", font=("Segoe UI", 13, "bold"), bg="#ffffff", fg="#0f172a").pack(pady=15)

        form = tk.Frame(dlg, bg="#ffffff", padx=25)
        form.pack(fill="both", expand=True)

        def row(label_text):
            r = tk.Frame(form, bg="#ffffff", pady=5)
            r.pack(fill="x")
            tk.Label(r, text=label_text, font=("Segoe UI", 9, "bold"), bg="#ffffff", fg="#334155").pack(anchor="w")
            return r

        r1 = row("Sélectionner l'Emprunt en cours *")
        options = [f"#{e['id']} - {e['nom_prenom']} : '{e['titre_livre']}'" for e in emprunts_en_cours]
        cb_e = ttk.Combobox(r1, values=options, state="readonly", font=("Segoe UI", 9))
        cb_e.current(0)
        cb_e.pack(fill="x")

        r2 = row("État de l'ouvrage au retour *")
        cb_etat = ttk.Combobox(r2, values=["Neuf", "Bon état", "État moyen", "Dégradé"], state="readonly", font=("Segoe UI", 9))
        cb_etat.current(1)
        cb_etat.pack(fill="x")

        def valider():
            e_id = int(cb_e.get().split(" - ")[0].replace("#", ""))
            pret = next(e for e in self.donnees["emprunts"] if e["id"] == e_id)

            date_retour_effective = datetime.now().strftime("%Y-%m-%d")
            pret["date_retour_effective"] = date_retour_effective
            pret["etat_retour"] = cb_etat.get()
            pret["statut"] = "Retourné"

            livre = next((l for l in self.donnees["livres"] if l["id"] == pret["id_livre"]), None)
            if livre:
                livre["disponible"] = True
                livre["etat"] = cb_etat.get()

            sauvegarder_donnees(self.donnees)
            dlg.destroy()
            self.rafraichir_emprunts()

            # Message si retard
            dt_prevue = datetime.strptime(pret["date_retour_prevue"], "%Y-%m-%d")
            dt_effective = datetime.strptime(date_retour_effective, "%Y-%m-%d")
            if dt_effective > dt_prevue:
                retard = (dt_effective - dt_prevue).days
                messagebox.showwarning("Retour Validé", f"Retour validé avec {retard} jour(s) de retard (délai officiel dépassé).")
            else:
                messagebox.showinfo("Retour Validé", "Ouvrage rendu dans les délais de 2 semaines. Livre à nouveau disponible.")

        btn_box = tk.Frame(dlg, bg="#ffffff", pady=15)
        btn_box.pack(fill="x")
        tk.Button(btn_box, text="Valider le Retour", bg="#10b981", fg="#ffffff", font=("Segoe UI", 10, "bold"), relief="flat", padx=20, pady=8, cursor="hand2", command=valider).pack()

    # =========================================================================
    # DONNÉES DÉMO
    # =========================================================================
    def charger_demo(self):
        if self.donnees["livres"] or self.donnees["usagers"]:
            if not messagebox.askyesno("Attention", "Des données existent déjà. Voulez-vous charger des données de démonstration supplémentaires ?"):
                return

        demo_livres = [
            {"id": 1, "titre": "L'Aventure ambiguë", "auteur": "Cheikh Hamidou Kane", "section": "Fonds Général & Littérature", "categorie": "Littérature négro-africaine", "acquisition": "Don en nature", "etat": "Bon état", "disponible": True},
            {"id": 2, "titre": "Une si longue lettre", "auteur": "Mariama Bâ", "section": "Fonds Général & Littérature", "categorie": "Romans", "acquisition": "Acquisition / Partenariat", "etat": "Neuf", "disponible": False},
            {"id": 3, "titre": "Introduction aux Algorithmes", "auteur": "Thomas Cormen", "section": "Fonds Général & Littérature", "categorie": "Informatique et généralités / revues", "acquisition": "Acquisition / Partenariat", "etat": "Bon état", "disponible": True},
            {"id": 4, "titre": "Tintin au Congo", "auteur": "Hergé", "section": "Jeunesse, Sciences & Documentaires", "categorie": "Bande dessinée", "acquisition": "Don en nature", "etat": "État moyen", "disponible": True},
            {"id": 5, "titre": "Atlas Mondial du 21e Siècle", "auteur": "Collectif", "section": "Jeunesse, Sciences & Documentaires", "categorie": "Atlas", "acquisition": "Acquisition / Partenariat", "etat": "Neuf", "disponible": True}
        ]

        demo_usagers = [
            {"id": 1, "nom_prenom": "Aminata Diallo", "sexe": "F", "niveau": "Élèves (1er cycle)", "tarif_annuel": 2000, "contact": "07 01 02 03 04", "date_inscription": "2026-10-01", "actif": True},
            {"id": 2, "nom_prenom": "Moussa Traoré", "sexe": "M", "niveau": "Étudiants", "tarif_annuel": 3000, "contact": "05 11 22 33 44", "date_inscription": "2026-10-15", "actif": True},
            {"id": 3, "nom_prenom": "Fatou Ndiaye", "sexe": "F", "niveau": "Écoliers", "tarif_annuel": 1000, "contact": "01 23 45 67 89", "date_inscription": "2026-11-01", "actif": True}
        ]

        demo_emprunts = [
            {
                "id": 1,
                "nom_prenom": "Aminata Diallo",
                "sexe": "F",
                "niveau": "Élèves (1er cycle)",
                "titre_livre": "Une si longue lettre",
                "contact": "07 01 02 03 04",
                "id_usager": 1,
                "id_livre": 2,
                "date_emprunt": (datetime.now() - timedelta(days=16)).strftime("%Y-%m-%d"),
                "date_retour_prevue": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
                "date_retour_effective": None,
                "etat_depart": "Neuf",
                "etat_retour": None,
                "statut": "En cours"
            }
        ]

        self.donnees["livres"] = demo_livres
        self.donnees["usagers"] = demo_usagers
        self.donnees["emprunts"] = demo_emprunts
        sauvegarder_donnees(self.donnees)
        self.rafraichir_dashboard()
        messagebox.showinfo("Données chargées", "Données de démonstration chargées avec succès !")


if __name__ == "__main__":
    app = BibliothequeApp()
    app.mainloop()

