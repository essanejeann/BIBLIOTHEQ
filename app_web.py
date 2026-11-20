"""
Application de gestion de bibliotheque
Interface web locale
"""

import json
import os
import sys
import webbrowser
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template_string

app = Flask(__name__)
DATA_FILE = "bibliotheque_data.json"

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

DUREE_EMPRUNT_JOURS = 14


def charger_donnees():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"livres": [], "usagers": [], "emprunts": []}


def sauvegarder_donnees(donnees):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(donnees, f, indent=4, ensure_ascii=False)


# --- HTML / CSS / JS TEMPLATE MODERNE ET DYNAMIQUE ---
HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bibliothèque Pro - Gestion & Dashboard</title>
    <!-- Google Fonts & Tailwind CDN & Chart.js & Phosphor Icons -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: { sans: ['Plus Jakarta Sans', 'sans-serif'] },
                    colors: {
                        brand: {
                            50: '#eef2ff',
                            100: '#e0e7ff',
                            500: '#6366f1',
                            600: '#4f46e5',
                            700: '#4338ca',
                            900: '#312e81',
                        }
                    }
                }
            }
        }
    </script>
    <style>
        /* Smooth transitions & custom scrollbar */
        * { transition: background-color 0.15s ease, border-color 0.15s ease; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #f1f5f9; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
        .glass-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
        }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 antialiased font-sans flex h-screen overflow-hidden">

    <!-- 1. SIDEBAR LATÉRALE -->
    <aside class="w-64 bg-slate-900 flex-shrink-0 flex flex-col justify-between border-r border-slate-800 text-slate-300 select-none z-20">
        <div>
            <!-- Header Logo -->
            <div class="p-5 flex items-center space-x-3 border-b border-slate-800 bg-slate-950">
                <div class="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center text-white">
                    <i class="ph-bold ph-book text-xl"></i>
                </div>
                <div>
                    <h1 class="font-bold text-white text-base">Bibliothèque</h1>
                    <span class="text-xs text-slate-400">Gestion des prêts</span>
                </div>
            </div>

            <!-- Navigation Links -->
            <nav class="p-3 space-y-1">
                <button onclick="naviger('dashboard')" id="nav-dashboard" class="nav-btn w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg font-medium text-sm transition-colors bg-blue-600 text-white">
                    <i class="ph-bold ph-squares-four text-lg"></i>
                    <span>Tableau de bord</span>
                </button>
                <button onclick="naviger('livres')" id="nav-livres" class="nav-btn w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg font-medium text-sm transition-colors text-slate-300 hover:bg-slate-800 hover:text-white">
                    <i class="ph-bold ph-books text-lg"></i>
                    <span>Fonds documentaire</span>
                </button>
                <button onclick="naviger('usagers')" id="nav-usagers" class="nav-btn w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg font-medium text-sm transition-colors text-slate-300 hover:bg-slate-800 hover:text-white">
                    <i class="ph-bold ph-users text-lg"></i>
                    <span>Usagers & tarifs</span>
                </button>
                <button onclick="naviger('emprunts')" id="nav-emprunts" class="nav-btn w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg font-medium text-sm transition-colors text-slate-300 hover:bg-slate-800 hover:text-white">
                    <i class="ph-bold ph-article text-lg"></i>
                    <span>Registre des prêts</span>
                    <span id="badge-retards" class="hidden ml-auto px-2 py-0.5 text-xs font-semibold bg-red-600 text-white rounded">0</span>
                </button>
            </nav>
        </div>

        <!-- Footer Sidebar -->
        <div class="p-4 border-t border-slate-800 text-xs text-slate-500">
            Délai d'emprunt : 2 semaines
        </div>
    </aside>

    <!-- 2. CONTENU PRINCIPAL -->
    <main class="flex-1 flex flex-col h-screen overflow-hidden bg-slate-50">
        
        <!-- Topbar Bar Header -->
        <header class="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 flex-shrink-0 z-10">
            <div>
                <h2 id="page-title" class="font-bold text-slate-900 text-lg">Tableau de bord</h2>
            </div>

            <!-- Actions Rapides -->
            <div class="flex items-center space-x-3">
                <button onclick="ouvrirModalPret()" class="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold transition-colors shadow-sm">
                    <i class="ph-bold ph-plus text-base"></i>
                    <span>Enregistrer un prêt</span>
                </button>
                <button onclick="ouvrirModalLivre()" class="flex items-center space-x-2 px-4 py-2 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 rounded-lg text-sm font-semibold transition-colors">
                    <i class="ph-bold ph-book-open text-base text-slate-500"></i>
                    <span>Ajouter un ouvrage</span>
                </button>
            </div>
        </header>
            </div>

            <!-- Actions Rapides -->
            <div class="flex items-center space-x-3">
                <button onclick="ouvrirModalPret()" class="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-700 hover:to-indigo-700 text-white rounded-xl text-sm font-semibold shadow-md shadow-brand-500/20 active:scale-95 transition-all">
                    <i class="ph-bold ph-plus-circle text-base"></i>
                    <span>Nouveau Prêt</span>
                </button>
                <button onclick="ouvrirModalLivre()" class="flex items-center space-x-2 px-4 py-2 bg-white hover:bg-slate-50 border border-slate-200 text-slate-700 rounded-xl text-sm font-semibold active:scale-95 transition-all">
                    <i class="ph-bold ph-book-plus text-base text-brand-600"></i>
                    <span>Ajouter Livre</span>
                </button>
            </div>
        </header>

        <!-- Pages Container -->
        <div class="flex-1 overflow-y-auto p-8 space-y-6" id="main-content">

            <!-- PAGE 1 : DASHBOARD -->
            <div id="page-dashboard" class="space-y-6">
                
                <!-- KPI CARDS GRID -->
                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                    
                    <!-- Carte Total Livres -->
                    <div class="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
                        <span class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Fonds documentaire</span>
                        <div class="mt-3">
                            <h3 id="stat-total-livres" class="text-2xl font-bold text-slate-900">0</h3>
                            <p class="text-xs text-slate-500 mt-1">2 sections • 21 rayons</p>
                        </div>
                    </div>

                    <!-- Carte Disponibles -->
                    <div class="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
                        <span class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Disponibles</span>
                        <div class="mt-3">
                            <h3 id="stat-dispos" class="text-2xl font-bold text-slate-900">0</h3>
                            <p id="stat-dispos-pct" class="text-xs text-slate-500 mt-1">100% en rayon</p>
                        </div>
                    </div>

                    <!-- Carte Emprunts Actifs -->
                    <div class="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
                        <span class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Prêts en cours</span>
                        <div class="mt-3">
                            <h3 id="stat-emprunts" class="text-2xl font-bold text-slate-900">0</h3>
                            <p class="text-xs text-slate-500 mt-1">Délai : 14 jours</p>
                        </div>
                    </div>

                    <!-- Carte Retards -->
                    <div id="card-retards" class="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
                        <span class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Retards</span>
                        <div class="mt-3">
                            <h3 id="stat-retards" class="text-2xl font-bold text-slate-900">0</h3>
                            <p id="sub-retards" class="text-xs text-slate-500 mt-1">Dépassement > 2 sem.</p>
                        </div>
                    </div>

                    <!-- Carte Cotisations -->
                    <div class="bg-white rounded-xl p-5 border border-slate-200 shadow-sm">
                        <span class="text-xs font-semibold text-slate-500 uppercase tracking-wide">Cotisations perçues</span>
                        <div class="mt-3">
                            <h3 id="stat-cotisations" class="text-2xl font-bold text-slate-900">0 F</h3>
                            <p id="stat-usagers-count" class="text-xs text-slate-500 mt-1">0 usagers inscrits</p>
                        </div>
                    </div>

                </div>

                <!-- CHARTS ROW -->
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    
                    <!-- Chart 1 : Répartition des Sections -->
                    <div class="bg-white rounded-xl p-5 border border-slate-200 shadow-sm flex flex-col justify-between">
                        <div>
                            <div class="flex items-center justify-between mb-4">
                                <h4 class="font-semibold text-slate-900 text-sm">Répartition par section</h4>
                            </div>
                            <div class="h-56 relative flex items-center justify-center">
                                <canvas id="chartSections"></canvas>
                            </div>
                        </div>
                        <div class="grid grid-cols-2 gap-2 mt-4 pt-4 border-t border-slate-100 text-xs">
                            <div class="flex items-center space-x-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
                                <span class="text-slate-600">Fonds Général</span>
                            </div>
                            <div class="flex items-center space-x-2">
                                <span class="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                                <span class="text-slate-600">Jeunesse & Sc.</span>
                            </div>
                        </div>
                    </div>

                    <!-- Chart 2 : Catégories Majeures -->
                    <div class="bg-white rounded-xl p-5 border border-slate-200 shadow-sm lg:col-span-2">
                        <div class="flex items-center justify-between mb-4">
                            <h4 class="font-semibold text-slate-900 text-sm">Volumes par catégorie</h4>
                        </div>
                        <div class="h-64">
                            <canvas id="chartCategories"></canvas>
                        </div>
                    </div>

                </div>

                <!-- TABLEAU DES SUIVIS D'EMPRUNTS -->
                <div class="bg-white rounded-xl p-6 border border-slate-200 shadow-sm">
                    <div class="flex items-center justify-between mb-4">
                        <div>
                            <h4 class="font-semibold text-slate-900 text-sm">Suivi des prêts en cours</h4>
                            <p class="text-xs text-slate-500">Contrôle du délai de 2 semaines et relance des retards</p>
                        </div>
                        <button onclick="naviger('emprunts')" class="text-xs font-semibold text-blue-600 hover:text-blue-700">
                            Voir le registre complet &rarr;
                        </button>
                    </div>

                    <div class="overflow-x-auto">
                        <table class="w-full text-left text-xs">
                            <thead>
                                <tr class="border-b border-slate-200 text-slate-500 font-semibold bg-slate-50">
                                    <th class="py-2.5 px-3">Lecteur</th>
                                    <th class="py-2.5 px-3">Catégorie</th>
                                    <th class="py-2.5 px-3">Ouvrage</th>
                                    <th class="py-2.5 px-3">Contact</th>
                                    <th class="py-2.5 px-3">Date Prêt</th>
                                    <th class="py-2.5 px-3">Retour Prévu</th>
                                    <th class="py-2.5 px-3 text-center">Statut</th>
                                    <th class="py-2.5 px-3 text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody id="table-dashboard-retards" class="divide-y divide-slate-100 text-slate-700">
                                <!-- Injecté dynamiquement -->
                            </tbody>
                        </table>
                    </div>
                </div>

            </div>

            <!-- PAGE 2 : FONDS DOCUMENTAIRE -->
            <div id="page-livres" class="hidden space-y-6">
                <div class="glass-card rounded-2xl p-6 shadow-sm border border-slate-200/70 space-y-4">
                    
                    <!-- Filtres & Recherche -->
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div class="relative flex-1 max-w-md">
                            <i class="ph ph-magnifying-glass absolute left-3.5 top-3 text-slate-400 text-base"></i>
                            <input type="text" id="search-livres" oninput="filtrerLivres()" placeholder="Rechercher par titre, auteur, rayon..." class="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-brand-500 focus:bg-white transition-all">
                        </div>

                        <!-- Filtres par Section -->
                        <div class="flex items-center space-x-2 text-xs">
                            <button onclick="filtrerSection('tous')" id="filter-sec-tous" class="px-3 py-1.5 rounded-lg font-semibold bg-brand-600 text-white shadow-sm">Tous</button>
                            <button onclick="filtrerSection('Fonds Général & Littérature')" id="filter-sec-1" class="px-3 py-1.5 rounded-lg font-semibold bg-white border border-slate-200 text-slate-600 hover:bg-slate-50">Fonds Général</button>
                            <button onclick="filtrerSection('Jeunesse, Sciences & Documentaires')" id="filter-sec-2" class="px-3 py-1.5 rounded-lg font-semibold bg-white border border-slate-200 text-slate-600 hover:bg-slate-50">Jeunesse & Sc.</button>
                        </div>
                    </div>

                    <!-- Tableau des Livres -->
                    <div class="overflow-x-auto rounded-xl border border-slate-200/60">
                        <table class="w-full text-left text-sm">
                            <thead>
                                <tr class="bg-slate-100/70 text-slate-500 font-bold text-xs uppercase tracking-wider border-b border-slate-200">
                                    <th class="py-3.5 px-4 w-16">ID</th>
                                    <th class="py-3.5 px-4">Titre</th>
                                    <th class="py-3.5 px-4">Auteur</th>
                                    <th class="py-3.5 px-4">Section / Catégorie</th>
                                    <th class="py-3.5 px-4">Acquisition</th>
                                    <th class="py-3.5 px-4">État</th>
                                    <th class="py-3.5 px-4 text-center">Disponibilité</th>
                                    <th class="py-3.5 px-4 text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody id="table-livres-body" class="divide-y divide-slate-100 font-medium text-slate-700 bg-white">
                                <!-- Rempli dynamiquement -->
                            </tbody>
                        </table>
                    </div>

                </div>
            </div>

            <!-- PAGE 3 : USAGERS & ABONNEMENTS -->
            <div id="page-usagers" class="hidden space-y-6">
                <div class="glass-card rounded-2xl p-6 shadow-sm border border-slate-200/70 space-y-4">
                    
                    <div class="flex items-center justify-between">
                        <div class="relative w-80">
                            <i class="ph ph-magnifying-glass absolute left-3.5 top-3 text-slate-400 text-base"></i>
                            <input type="text" id="search-usagers" oninput="filtrerUsagers()" placeholder="Rechercher un adhérent..." class="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-brand-500 focus:bg-white transition-all">
                        </div>
                        <button onclick="ouvrirModalUsager()" class="flex items-center space-x-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-sm font-semibold shadow-md active:scale-95 transition-all">
                            <i class="ph-bold ph-user-plus text-base"></i>
                            <span>Inscrire un Usager</span>
                        </button>
                    </div>

                    <!-- Tableau Usagers -->
                    <div class="overflow-x-auto rounded-xl border border-slate-200/60">
                        <table class="w-full text-left text-sm">
                            <thead>
                                <tr class="bg-slate-100/70 text-slate-500 font-bold text-xs uppercase tracking-wider border-b border-slate-200">
                                    <th class="py-3.5 px-4 w-16">ID</th>
                                    <th class="py-3.5 px-4">Nom et Prénom</th>
                                    <th class="py-3.5 px-4">Sexe</th>
                                    <th class="py-3.5 px-4">Catégorie d'usager</th>
                                    <th class="py-3.5 px-4">Tarif Annuel</th>
                                    <th class="py-3.5 px-4">Contact</th>
                                    <th class="py-3.5 px-4">Date Adhésion</th>
                                    <th class="py-3.5 px-4 text-center">Statut</th>
                                </tr>
                            </thead>
                            <tbody id="table-usagers-body" class="divide-y divide-slate-100 font-medium text-slate-700 bg-white">
                                <!-- Rempli dynamiquement -->
                            </tbody>
                        </table>
                    </div>

                </div>
            </div>

            <!-- PAGE 4 : REGISTRE DES PRÊTS (FICHE DE SUIVI SECTION 4) -->
            <div id="page-emprunts" class="hidden space-y-6">
                <div class="glass-card rounded-2xl p-6 shadow-sm border border-slate-200/70 space-y-4">
                    
                    <div class="flex items-center justify-between">
                        <div>
                            <h3 class="font-bold text-slate-900 text-base">Fiche de Suivi des Emprunts (Registre Lecteurs)</h3>
                            <p class="text-xs text-slate-500">Conforme à la section 4 du règlement officiel • Durée de prêt : 2 semaines</p>
                        </div>
                        <div class="flex items-center space-x-3">
                            <button onclick="window.print()" class="flex items-center space-x-2 px-3 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold transition-all">
                                <i class="ph-bold ph-printer text-sm"></i>
                                <span>Imprimer Registre</span>
                            </button>
                            <button onclick="ouvrirModalPret()" class="flex items-center space-x-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-sm font-semibold shadow-md active:scale-95 transition-all">
                                <i class="ph-bold ph-plus text-base"></i>
                                <span>Enregistrer Prêt</span>
                            </button>
                        </div>
                    </div>

                    <!-- Tableau Registre -->
                    <div class="overflow-x-auto rounded-lg border border-slate-200">
                        <table class="w-full text-left text-sm">
                            <thead>
                                <tr class="bg-slate-100 text-slate-700 font-semibold text-xs border-b border-slate-200">
                                    <th class="py-3 px-4">Nom et prénom</th>
                                    <th class="py-3 px-4">Sexe</th>
                                    <th class="py-3 px-4">Niveau</th>
                                    <th class="py-3 px-4">Titre de livre</th>
                                    <th class="py-3 px-4">Contact</th>
                                    <th class="py-3 px-4">Date Emprunt</th>
                                    <th class="py-3 px-4">Retour Prévu</th>
                                    <th class="py-3 px-4 text-center">Statut</th>
                                    <th class="py-3 px-4 text-right">Action</th>
                                </tr>
                            </thead>
                            <tbody id="table-emprunts-body" class="divide-y divide-slate-100 font-medium text-slate-700 bg-white">
                                <!-- Rempli dynamiquement -->
                            </tbody>
                        </table>
                    </div>

                </div>
            </div>

        </div>
    </main>

    <!-- ==================== MODALS (FENÊTRES POPUPS INTERACTIVES) ==================== -->

    <!-- MODAL 1 : NOUVEAU PRÊT -->
    <div id="modal-pret" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-xl w-full max-w-lg shadow-xl border border-slate-200 overflow-hidden">
            <div class="px-6 py-4 bg-slate-900 text-white flex justify-between items-center">
                <h3 class="font-bold text-base">Enregistrer un prêt d'ouvrage</h3>
                <button onclick="fermerModal('modal-pret')" class="text-slate-400 hover:text-white"><i class="ph-bold ph-x text-lg"></i></button>
            </div>
            <form id="form-pret" onsubmit="soumettrePret(event)" class="p-6 space-y-4">
                <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">Lecteur *</label>
                    <select id="pret-usager" required class="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-blue-600"></select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">Ouvrage disponible *</label>
                    <select id="pret-livre" required class="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-blue-600"></select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-slate-700 mb-1">État de l'ouvrage au départ (contrôle Mr Seidou) *</label>
                    <select id="pret-etat" class="w-full p-2 bg-slate-50 border border-slate-300 rounded-lg text-sm focus:outline-none focus:border-blue-600">
                        <option value="Neuf">Neuf</option>
                        <option value="Bon état" selected>Bon état</option>
                        <option value="État moyen">État moyen</option>
                        <option value="Dégradé">Dégradé</option>
                    </select>
                </div>
                <div class="p-3 bg-slate-50 border border-slate-200 rounded-lg text-xs text-slate-600">
                    <span class="font-semibold text-slate-800">Règle officielle :</span> Durée maximale d'emprunt fixée à <strong>2 semaines (14 jours)</strong>.
                </div>
                <div class="pt-2 flex justify-end space-x-3">
                    <button type="button" onclick="fermerModal('modal-pret')" class="px-4 py-2 border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg text-sm font-medium">Annuler</button>
                    <button type="submit" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-semibold">Valider le prêt</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL 2 : NOUVEAU LIVRE -->
    <div id="modal-livre" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl w-full max-w-lg shadow-2xl border border-slate-200 overflow-hidden">
            <div class="p-6 bg-slate-900 text-white flex justify-between items-center">
                <div class="flex items-center space-x-2">
                    <i class="ph-bold ph-book-open text-2xl text-brand-400"></i>
                    <h3 class="font-bold text-lg">Ajouter un Ouvrage au Fonds</h3>
                </div>
                <button onclick="fermerModal('modal-livre')" class="text-white/80 hover:text-white"><i class="ph-bold ph-x text-xl"></i></button>
            </div>
            <form id="form-livre" onsubmit="soumettreLivre(event)" class="p-6 space-y-4">
                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Titre de l'ouvrage *</label>
                    <input type="text" id="livre-titre" required placeholder="Ex: L'Aventure ambiguë" class="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:border-brand-500">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Auteur(s)</label>
                    <input type="text" id="livre-auteur" placeholder="Ex: Cheikh Hamidou Kane" class="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:border-brand-500">
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Section officielle *</label>
                        <select id="livre-section" onchange="mettreAJourCategoriesForm()" class="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:border-brand-500 font-medium">
                            <option value="Fonds Général & Littérature">Fonds Général & Littérature</option>
                            <option value="Jeunesse, Sciences & Documentaires">Jeunesse, Sciences & Documentaires</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Catégorie / Rayon *</label>
                        <select id="livre-categorie" class="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:border-brand-500 font-medium"></select>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Modalité d'acquisition *</label>
                        <select id="livre-acquisition" class="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:border-brand-500">
                            <option value="Don en nature">Don en nature</option>
                            <option value="Acquisition auprès des maisons d'édition (partenariat)">Acquisition / Partenariat</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase mb-1">État initial de l'ouvrage *</label>
                        <select id="livre-etat" class="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs focus:outline-none focus:border-brand-500">
                            <option value="Neuf">Neuf</option>
                            <option value="Bon état" selected>Bon état</option>
                            <option value="État moyen">État moyen</option>
                            <option value="Dégradé">Dégradé</option>
                        </select>
                    </div>
                </div>
                <div class="pt-2 flex justify-end space-x-3">
                    <button type="button" onclick="fermerModal('modal-livre')" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm font-semibold">Annuler</button>
                    <button type="submit" class="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white rounded-xl text-sm font-bold shadow-md">Enregistrer</button>
                </div>
            </form>
        </div>
    </div>

    <!-- MODAL 3 : NOUVEL USAGER -->
    <div id="modal-usager" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-white rounded-xl w-full max-w-lg shadow-xl border border-slate-200 overflow-hidden">
            <div class="px-6 py-4 bg-slate-900 text-white flex justify-between items-center">
                <h3 class="font-bold text-base">Inscription d'un usager</h3>
                <button onclick="fermerModal('modal-usager')" class="text-slate-400 hover:text-white"><i class="ph-bold ph-x text-lg"></i></button>
            </div>
            <form id="form-usager" onsubmit="soumettreUsager(event)" class="p-6 space-y-4">
                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Nom et Prénom *</label>
                    <input type="text" id="usager-nom" required placeholder="Ex: Aminata Diallo" class="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:border-emerald-500">
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Sexe *</label>
                        <select id="usager-sexe" class="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:border-emerald-500">
                            <option value="M">Masculin (M)</option>
                            <option value="F">Féminin (F)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Contact (Téléphone) *</label>
                        <input type="text" id="usager-contact" required placeholder="Ex: 07 01 02 03 04" class="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:border-emerald-500">
                    </div>
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-700 uppercase mb-1">Catégorie d'usager & Tarif officiel *</label>
                    <select id="usager-cat" class="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-sm focus:outline-none focus:border-emerald-500 font-semibold">
                        <option value="Écoliers">Écoliers — 1 000 F / an</option>
                        <option value="Élèves (1er cycle)">Élèves (1er cycle) — 2 000 F / an</option>
                        <option value="Étudiants">Étudiants — 3 000 F / an</option>
                        <option value="Personnes avec source de revenus">Personnes avec source de revenus — 5 000 F / an</option>
                    </select>
                </div>
                <div class="pt-2 flex justify-end space-x-3">
                    <button type="button" onclick="fermerModal('modal-usager')" class="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-sm font-semibold">Annuler</button>
                    <button type="submit" class="px-5 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-sm font-bold shadow-md">Valider l'Inscription</button>
                </div>
            </form>
        </div>
    </div>

    <!-- TOAST NOTIFICATION CONTAINER -->
    <div id="toast-container" class="fixed bottom-5 right-5 z-50 space-y-2"></div>

    <!-- ==================== SCRIPT APPLICATIF JS ==================== -->
    <script>
        // Variables globales
        let db = { livres: [], usagers: [], emprunts: [] };
        let sectionFiltreActive = 'tous';
        let chartSections = null;
        let chartCategories = null;

        const SECTIONS_CATEGORIES = {
            "Fonds Général & Littérature": [
                "Nouveautés", "Nouveaux horizons", "Usuels, encyclopédies", "Romans", "Théâtre",
                "Littérature négro-africaine", "Science sociale Afrique", "Littérature française",
                "Informatique et généralités / revues", "Philosophie / Religion"
            ],
            "Jeunesse, Sciences & Documentaires": [
                "Bande dessinée", "Album", "Littérature jeunesse, contes et légendes",
                "Histoire et Géographie", "Langue, SVT", "Sciences sociales",
                "Médecine", "Sciences techniques", "Art et loisirs", "Documentaire", "Atlas"
            ]
        };

        // --- CHARGEMENT INITIAL ---
        document.addEventListener('DOMContentLoaded', () => {
            chargerDonnees();
            mettreAJourCategoriesForm();
        });

        async function chargerDonnees() {
            try {
                const res = await fetch('/api/donnees');
                db = await res.json();
                mettreAJourTout();
            } catch (err) {
                afficherToast('Erreur de chargement des données', 'danger');
            }
        }

        function mettreAJourTout() {
            mettreAJourDashboard();
            rendreTableauLivres();
            rendreTableauUsagers();
            rendreTableauEmprunts();
            remplirSelectsPret();
        }

        // --- GESTION DE LA NAVIGATION ---
        function naviger(pageId) {
            ['dashboard', 'livres', 'usagers', 'emprunts'].forEach(p => {
                document.getElementById('page-' + p).classList.add('hidden');
                const btn = document.getElementById('nav-' + p);
                btn.className = 'nav-btn w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg font-medium text-sm transition-colors text-slate-300 hover:bg-slate-800 hover:text-white';
            });

            document.getElementById('page-' + pageId).classList.remove('hidden');
            const activeBtn = document.getElementById('nav-' + pageId);
            activeBtn.className = 'nav-btn w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg font-medium text-sm transition-colors bg-blue-600 text-white';

            const titres = {
                dashboard: 'Tableau de bord',
                livres: 'Catalogue du fonds documentaire',
                usagers: 'Gestion des usagers & abonnements',
                emprunts: 'Fiche de suivi des emprunts (Registre lecteurs)'
            };
            document.getElementById('page-title').textContent = titres[pageId];

            if (pageId === 'dashboard') {
                mettreAJourGraphiques();
            }
        }

        // --- DASHBOARD & GRAPHIQUES ---
        function mettreAJourDashboard() {
            const totalLivres = db.livres.length;
            const dispos = db.livres.filter(l => l.disponible).length;
            const empruntsActifs = db.emprunts.filter(e => e.statut === 'En cours');
            
            const now = new Date();
            const retards = empruntsActifs.filter(e => new Date(e.date_retour_prevue) < now);
            const totalCotisations = db.usagers.reduce((acc, u) => acc + (u.tarif_annuel || 0), 0);

            // Mettre à jour les KPIs
            document.getElementById('stat-total-livres').textContent = totalLivres;
            document.getElementById('stat-dispos').textContent = dispos;
            document.getElementById('stat-dispos-pct').textContent = totalLivres ? Math.round((dispos / totalLivres) * 100) + '% disponible' : '0%';
            document.getElementById('stat-emprunts').textContent = empruntsActifs.length;
            
            document.getElementById('stat-retards').textContent = retards.length;
            const badgeRetards = document.getElementById('badge-retards');
            if (retards.length > 0) {
                badgeRetards.textContent = retards.length;
                badgeRetards.classList.remove('hidden');
                document.getElementById('sub-retards').textContent = `${retards.length} retard(s) détecté(s)`;
                document.getElementById('sub-retards').className = 'text-xs text-red-600 font-medium mt-1';
            } else {
                badgeRetards.classList.add('hidden');
                document.getElementById('sub-retards').textContent = 'Aucun retard';
                document.getElementById('sub-retards').className = 'text-xs text-slate-500 mt-1';
            }

            document.getElementById('stat-cotisations').textContent = totalCotisations.toLocaleString('fr-FR') + ' F';
            document.getElementById('stat-usagers-count').textContent = `${db.usagers.length} usagers enregistrés`;

            // Remplir tableau suivi des emprunts
            const tbody = document.getElementById('table-dashboard-retards');
            tbody.innerHTML = '';
            
            if (empruntsActifs.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" class="text-center py-6 text-slate-400 italic">Aucun emprunt en cours actuellement.</td></tr>`;
            } else {
                empruntsActifs.forEach(e => {
                    const estEnRetard = new Date(e.date_retour_prevue) < now;
                    const diffDays = Math.ceil((now - new Date(e.date_retour_prevue)) / (1000 * 60 * 60 * 24));
                    
                    const tr = document.createElement('tr');
                    tr.className = estEnRetard ? 'bg-red-50/50 hover:bg-red-50/80 transition-colors' : 'hover:bg-slate-50 transition-colors';
                    tr.innerHTML = `
                        <td class="py-2.5 px-3 font-semibold text-slate-900">${e.nom_prenom}</td>
                        <td class="py-2.5 px-3 text-slate-600">${e.niveau}</td>
                        <td class="py-2.5 px-3 text-slate-800">${e.titre_livre}</td>
                        <td class="py-2.5 px-3 font-mono text-slate-600">${e.contact}</td>
                        <td class="py-2.5 px-3 text-slate-500">${e.date_emprunt}</td>
                        <td class="py-2.5 px-3 ${estEnRetard ? 'text-red-700 font-semibold' : 'text-slate-700'}">${e.date_retour_prevue}</td>
                        <td class="py-2.5 px-3 text-center">
                            ${estEnRetard 
                                ? `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-50 text-red-700 border border-red-200">En retard (${diffDays} j)</span>` 
                                : `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">En cours</span>`}
                        </td>
                        <td class="py-2.5 px-3 text-right">
                            <button onclick="cloturerPret(${e.id})" class="px-2.5 py-1 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 rounded text-xs font-medium transition-colors">
                                Valider retour
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            }

            mettreAJourGraphiques();
        }

        function mettreAJourGraphiques() {
            const sec1 = db.livres.filter(l => l.section === "Fonds Général & Littérature").length;
            const sec2 = db.livres.filter(l => l.section === "Jeunesse, Sciences & Documentaires").length;

            // 1. Donut Chart
            const ctx1 = document.getElementById('chartSections').getContext('2d');
            if (chartSections) chartSections.destroy();
            chartSections = new Chart(ctx1, {
                type: 'doughnut',
                data: {
                    labels: ['Fonds Général & Littérature', 'Jeunesse, Sciences & Documentaires'],
                    datasets: [{
                        data: [sec1 || 1, sec2 || 1],
                        backgroundColor: ['#6366f1', '#34d399'],
                        borderWidth: 3,
                        borderColor: '#ffffff',
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: { legend: { display: false } }
                }
            });

            // 2. Bar Chart Categories
            const categories = ["Romans", "Informatique et généralités / revues", "Bande dessinée", "Atlas", "Littérature négro-africaine", "Théâtre"];
            const counts = categories.map(cat => db.livres.filter(l => l.categorie === cat).length);

            const ctx2 = document.getElementById('chartCategories').getContext('2d');
            if (chartCategories) chartCategories.destroy();
            chartCategories = new Chart(ctx2, {
                type: 'bar',
                data: {
                    labels: categories,
                    datasets: [{
                        label: 'Ouvrages inventoriés',
                        data: counts,
                        backgroundColor: '#6366f1',
                        borderRadius: 8,
                        barThickness: 24
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, ticks: { stepSize: 1, precision: 0 } },
                        x: { grid: { display: false } }
                    }
                }
            });
        }

        // --- MODULE LIVRES ---
        function filtrerSection(sec) {
            sectionFiltreActive = sec;
            ['tous', '1', '2'].forEach(id => {
                const btn = document.getElementById('filter-sec-' + id);
                btn.className = 'px-3 py-1.5 rounded-lg font-semibold bg-white border border-slate-200 text-slate-600 hover:bg-slate-50';
            });

            if (sec === 'tous') document.getElementById('filter-sec-tous').className = 'px-3 py-1.5 rounded-lg font-semibold bg-brand-600 text-white shadow-sm';
            else if (sec.startsWith('Fonds')) document.getElementById('filter-sec-1').className = 'px-3 py-1.5 rounded-lg font-semibold bg-brand-600 text-white shadow-sm';
            else document.getElementById('filter-sec-2').className = 'px-3 py-1.5 rounded-lg font-semibold bg-brand-600 text-white shadow-sm';

            rendreTableauLivres();
        }

        function filtrerLivres() {
            rendreTableauLivres();
        }

        function rendreTableauLivres() {
            const motCle = document.getElementById('search-livres')?.value.toLowerCase() || '';
            const tbody = document.getElementById('table-livres-body');
            tbody.innerHTML = '';

            const livresFiltres = db.livres.filter(l => {
                const correspondSection = sectionFiltreActive === 'tous' || l.section === sectionFiltreActive;
                const texte = `${l.titre} ${l.auteur} ${l.categorie} ${l.section}`.toLowerCase();
                const correspondRecherche = !motCle || texte.includes(motCle);
                return correspondSection && correspondRecherche;
            });

            if (livresFiltres.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-slate-400 italic">Aucun ouvrage trouvé.</td></tr>`;
                return;
            }

            livresFiltres.forEach(l => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-50/80 transition-colors';
                tr.innerHTML = `
                    <td class="py-3 px-4 font-mono text-xs text-slate-400">#${l.id}</td>
                    <td class="py-3 px-4 font-bold text-slate-900">${l.titre}</td>
                    <td class="py-3 px-4 text-slate-600">${l.auteur}</td>
                    <td class="py-3 px-4">
                        <span class="inline-block px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 text-slate-700">${l.categorie}</span>
                    </td>
                    <td class="py-3 px-4 text-xs text-slate-500">${l.acquisition}</td>
                    <td class="py-3 px-4">
                        <span class="inline-block px-2 py-0.5 rounded text-xs font-medium ${l.etat === 'Neuf' ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-600'}">${l.etat}</span>
                    </td>
                    <td class="py-3 px-4 text-center">
                        ${l.disponible 
                            ? `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800">Disponible</span>`
                            : `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800">Emprunté</span>`}
                    </td>
                    <td class="py-3 px-4 text-right space-x-1">
                        <button onclick="supprimerLivre(${l.id})" class="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-all" title="Supprimer">
                            <i class="ph-bold ph-trash text-base"></i>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // --- MODULE USAGERS ---
        function filtrerUsagers() {
            rendreTableauUsagers();
        }

        function rendreTableauUsagers() {
            const motCle = document.getElementById('search-usagers')?.value.toLowerCase() || '';
            const tbody = document.getElementById('table-usagers-body');
            tbody.innerHTML = '';

            const usagersFiltres = db.usagers.filter(u => {
                return !motCle || `${u.nom_prenom} ${u.niveau} ${u.contact}`.toLowerCase().includes(motCle);
            });

            if (usagersFiltres.length === 0) {
                tbody.innerHTML = `<tr><td colspan="8" class="text-center py-8 text-slate-400 italic">Aucun usager enregistré.</td></tr>`;
                return;
            }

            usagersFiltres.forEach(u => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-slate-50/80 transition-colors';
                tr.innerHTML = `
                    <td class="py-3 px-4 font-mono text-xs text-slate-400">#${u.id}</td>
                    <td class="py-3 px-4 font-bold text-slate-900">${u.nom_prenom}</td>
                    <td class="py-3 px-4"><span class="px-2 py-0.5 rounded text-xs font-bold ${u.sexe === 'F' ? 'bg-pink-100 text-pink-700' : 'bg-blue-100 text-blue-700'}">${u.sexe}</span></td>
                    <td class="py-3 px-4 text-slate-700 font-medium">${u.niveau}</td>
                    <td class="py-3 px-4 font-mono font-bold text-indigo-600">${(u.tarif_annuel || 0).toLocaleString('fr-FR')} F CFA</td>
                    <td class="py-3 px-4 font-mono text-slate-600">${u.contact}</td>
                    <td class="py-3 px-4 text-slate-500 text-xs">${u.date_inscription || '-'}</td>
                    <td class="py-3 px-4 text-center">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800">Adhérent Actif</span>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // --- MODULE EMPRUNTS (REGISTRE SECTION 4) ---
        function rendreTableauEmprunts() {
            const tbody = document.getElementById('table-emprunts-body');
            tbody.innerHTML = '';

            if (db.emprunts.length === 0) {
                tbody.innerHTML = `<tr><td colspan="9" class="text-center py-8 text-slate-400 italic">Aucun enregistrement dans la fiche de suivi.</td></tr>`;
                return;
            }

            const now = new Date();
            db.emprunts.forEach(e => {
                const estEnRetard = e.statut === 'En cours' && new Date(e.date_retour_prevue) < now;
                const tr = document.createElement('tr');
                tr.className = estEnRetard ? 'bg-red-50/40 hover:bg-red-50/70 transition-colors' : 'hover:bg-slate-50 transition-colors';
                
                tr.innerHTML = `
                    <td class="py-3 px-4 font-semibold text-slate-900">${e.nom_prenom}</td>
                    <td class="py-3 px-4"><span class="px-2 py-0.5 rounded text-xs font-medium ${e.sexe === 'F' ? 'bg-pink-50 text-pink-700 border border-pink-200' : 'bg-blue-50 text-blue-700 border border-blue-200'}">${e.sexe}</span></td>
                    <td class="py-3 px-4 text-slate-600">${e.niveau}</td>
                    <td class="py-3 px-4 text-slate-800">${e.titre_livre}</td>
                    <td class="py-3 px-4 font-mono text-slate-600 text-xs">${e.contact}</td>
                    <td class="py-3 px-4 text-slate-500 text-xs">${e.date_emprunt}</td>
                    <td class="py-3 px-4 text-xs ${estEnRetard ? 'text-red-700 font-semibold' : 'text-slate-700'}">${e.date_retour_prevue}</td>
                    <td class="py-3 px-4 text-center">
                        ${e.statut === 'Retourné' 
                            ? `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">Retourné</span>`
                            : estEnRetard 
                                ? `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-50 text-red-700 border border-red-200">En retard</span>`
                                : `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">En cours</span>`}
                    </td>
                    <td class="py-3 px-4 text-right">
                        ${e.statut === 'En cours' 
                            ? `<button onclick="cloturerPret(${e.id})" class="px-2.5 py-1 bg-white hover:bg-slate-50 border border-slate-300 text-slate-700 rounded text-xs font-medium transition-colors">Valider retour</button>`
                            : `<span class="text-xs text-slate-400">Clôturé</span>`}
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // --- ACTIONS FORMULAIRES & MODALS ---
        function ouvrirModal(id) { document.getElementById(id).classList.remove('hidden'); }
        function fermerModal(id) { document.getElementById(id).classList.add('hidden'); }

        function ouvrirModalPret() {
            remplirSelectsPret();
            ouvrirModal('modal-pret');
        }

        function ouvrirModalLivre() {
            ouvrirModal('modal-livre');
        }

        function ouvrirModalUsager() {
            ouvrirModal('modal-usager');
        }

        function mettreAJourCategoriesForm() {
            const sec = document.getElementById('livre-section').value;
            const selectCat = document.getElementById('livre-categorie');
            selectCat.innerHTML = '';
            (SECTIONS_CATEGORIES[sec] || []).forEach(c => {
                const opt = document.createElement('option');
                opt.value = c;
                opt.textContent = c;
                selectCat.appendChild(opt);
            });
        }

        function remplirSelectsPret() {
            const selU = document.getElementById('pret-usager');
            const selL = document.getElementById('pret-livre');
            if (!selU || !selL) return;

            selU.innerHTML = '';
            db.usagers.forEach(u => {
                const opt = document.createElement('option');
                opt.value = u.id;
                opt.textContent = `${u.nom_prenom} (${u.niveau}) - ${u.contact}`;
                selU.appendChild(opt);
            });

            selL.innerHTML = '';
            const dispos = db.livres.filter(l => l.disponible);
            dispos.forEach(l => {
                const opt = document.createElement('option');
                opt.value = l.id;
                opt.textContent = `${l.titre} [${l.categorie}] - État: ${l.etat}`;
                selL.appendChild(opt);
            });
        }

        async function soumettrePret(e) {
            e.preventDefault();
            const uId = parseInt(document.getElementById('pret-usager').value);
            const lId = parseInt(document.getElementById('pret-livre').value);
            const etat = document.getElementById('pret-etat').value;

            if (!uId || !lId) {
                afficherToast("Veuillez sélectionner un lecteur et un livre disponible.", "danger");
                return;
            }

            const res = await fetch('/api/emprunts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_usager: uId, id_livre: lId, etat_depart: etat })
            });

            if (res.ok) {
                fermerModal('modal-pret');
                afficherToast("Prêt enregistré avec succès (Délai : 2 semaines)", "success");
                chargerDonnees();
            } else {
                const err = await res.json();
                afficherToast(err.message || "Erreur lors du prêt", "danger");
            }
        }

        async function cloturerPret(id) {
            const res = await fetch(`/api/emprunts/${id}/retour`, { method: 'POST' });
            if (res.ok) {
                afficherToast("Retour de livre validé et remis en rayon.", "success");
                chargerDonnees();
            } else {
                afficherToast("Erreur lors de la clôture", "danger");
            }
        }

        async function soumettreLivre(e) {
            e.preventDefault();
            const payload = {
                titre: document.getElementById('livre-titre').value,
                auteur: document.getElementById('livre-auteur').value || 'Inconnu',
                section: document.getElementById('livre-section').value,
                categorie: document.getElementById('livre-categorie').value,
                acquisition: document.getElementById('livre-acquisition').value,
                etat: document.getElementById('livre-etat').value
            };

            const res = await fetch('/api/livres', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                fermerModal('modal-livre');
                document.getElementById('form-livre').reset();
                mettreAJourCategoriesForm();
                afficherToast("Ouvrage ajouté au catalogue !", "success");
                chargerDonnees();
            }
        }

        async function supprimerLivre(id) {
            if (!confirm("Voulez-vous supprimer cet ouvrage du fonds documentaire ?")) return;
            const res = await fetch(`/api/livres/${id}`, { method: 'DELETE' });
            if (res.ok) {
                afficherToast("Ouvrage supprimé.", "success");
                chargerDonnees();
            }
        }

        async function soumettreUsager(e) {
            e.preventDefault();
            const payload = {
                nom_prenom: document.getElementById('usager-nom').value,
                sexe: document.getElementById('usager-sexe').value,
                niveau: document.getElementById('usager-cat').value,
                contact: document.getElementById('usager-contact').value
            };

            const res = await fetch('/api/usagers', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                fermerModal('modal-usager');
                document.getElementById('form-usager').reset();
                afficherToast("Usager inscrit avec succès !", "success");
                chargerDonnees();
            }
        }

        async function chargerDemo() {
            if (!confirm("Charger les données de démonstration conformes au document officiel ?")) return;
            const res = await fetch('/api/demo', { method: 'POST' });
            if (res.ok) {
                afficherToast("Données de démonstration chargées !", "success");
                chargerDonnees();
            }
        }

        // --- TOAST NOTIFICATIONS ---
        function afficherToast(msg, type = 'success') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            const bg = type === 'success' ? 'bg-emerald-600' : 'bg-rose-600';
            const icon = type === 'success' ? 'ph-check-circle' : 'ph-warning-circle';

            toast.className = `${bg} text-white px-4 py-3 rounded-xl shadow-xl flex items-center space-x-2 text-sm font-semibold transform transition-all duration-300 translate-y-5 opacity-0`;
            toast.innerHTML = `<i class="ph-bold ${icon} text-lg"></i><span>${msg}</span>`;
            
            container.appendChild(toast);
            setTimeout(() => {
                toast.classList.remove('translate-y-5', 'opacity-0');
            }, 10);

            setTimeout(() => {
                toast.classList.add('opacity-0', 'translate-y-2');
                setTimeout(() => toast.remove(), 300);
            }, 3500);
        }
    </script>
</body>
</html>
"""


# ==================== ROUTES DE L'API REST ====================

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route("/api/donnees", methods=["GET"])
def get_donnees():
    return jsonify(charger_donnees())


@app.route("/api/livres", methods=["POST"])
def ajouter_livre():
    donnees = charger_donnees()
    req = request.json
    nouveau_id = max([l["id"] for l in donnees["livres"]], default=0) + 1
    livre = {
        "id": nouveau_id,
        "titre": req.get("titre"),
        "auteur": req.get("auteur") or "Inconnu",
        "section": req.get("section"),
        "categorie": req.get("categorie"),
        "acquisition": req.get("acquisition"),
        "etat": req.get("etat", "Bon état"),
        "disponible": True
    }
    donnees["livres"].append(livre)
    sauvegarder_donnees(donnees)
    return jsonify({"success": True, "livre": livre})


@app.route("/api/livres/<int:id>", methods=["DELETE"])
def supprimer_livre(id):
    donnees = charger_donnees()
    donnees["livres"] = [l for l in donnees["livres"] if l["id"] != id]
    sauvegarder_donnees(donnees)
    return jsonify({"success": True})


@app.route("/api/usagers", methods=["POST"])
def ajouter_usager():
    donnees = charger_donnees()
    req = request.json
    nouveau_id = max([u["id"] for u in donnees["usagers"]], default=0) + 1
    niveau = req.get("niveau")
    tarif = TARIFS_ABONNEMENT.get(niveau, 0)

    usager = {
        "id": nouveau_id,
        "nom_prenom": req.get("nom_prenom"),
        "sexe": req.get("sexe", "M"),
        "niveau": niveau,
        "tarif_annuel": tarif,
        "contact": req.get("contact"),
        "date_inscription": datetime.now().strftime("%Y-%m-%d"),
        "actif": True
    }
    donnees["usagers"].append(usager)
    sauvegarder_donnees(donnees)
    return jsonify({"success": True, "usager": usager})


@app.route("/api/emprunts", methods=["POST"])
def enregistrer_emprunt():
    donnees = charger_donnees()
    req = request.json
    id_u = req.get("id_usager")
    id_l = req.get("id_livre")

    usager = next((u for u in donnees["usagers"] if u["id"] == id_u), None)
    livre = next((l for l in donnees["livres"] if l["id"] == id_l), None)

    if not usager or not livre or not livre.get("disponible"):
        return jsonify({"success": False, "message": "Usager ou livre invalide ou indisponible"}), 400

    maintenant = datetime.now()
    date_emprunt = maintenant.strftime("%Y-%m-%d")
    date_retour_prevue = (maintenant + timedelta(days=DUREE_EMPRUNT_JOURS)).strftime("%Y-%m-%d")
    nouveau_id = max([e["id"] for e in donnees["emprunts"]], default=0) + 1

    etat_depart = req.get("etat_depart") or livre["etat"]
    livre["disponible"] = False
    livre["etat"] = etat_depart

    fiche_emprunt = {
        "id": nouveau_id,
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
        "etat_depart": etat_depart,
        "etat_retour": None,
        "statut": "En cours"
    }

    donnees["emprunts"].append(fiche_emprunt)
    sauvegarder_donnees(donnees)
    return jsonify({"success": True, "emprunt": fiche_emprunt})


@app.route("/api/emprunts/<int:id>/retour", methods=["POST"])
def retourner_emprunt(id):
    donnees = charger_donnees()
    pret = next((e for e in donnees["emprunts"] if e["id"] == id), None)
    if not pret:
        return jsonify({"success": False, "message": "Prêt introuvable"}), 404

    date_retour = datetime.now().strftime("%Y-%m-%d")
    pret["date_retour_effective"] = date_retour
    pret["statut"] = "Retourné"

    livre = next((l for l in donnees["livres"] if l["id"] == pret["id_livre"]), None)
    if livre:
        livre["disponible"] = True

    sauvegarder_donnees(donnees)
    return jsonify({"success": True})


@app.route("/api/demo", methods=["POST"])
def charger_demo():
    donnees = charger_donnees()
    donnees["livres"] = [
        {"id": 1, "titre": "L'Aventure ambiguë", "auteur": "Cheikh Hamidou Kane", "section": "Fonds Général & Littérature", "categorie": "Littérature négro-africaine", "acquisition": "Don en nature", "etat": "Bon état", "disponible": True},
        {"id": 2, "titre": "Une si longue lettre", "auteur": "Mariama Bâ", "section": "Fonds Général & Littérature", "categorie": "Romans", "acquisition": "Acquisition / Partenariat", "etat": "Neuf", "disponible": False},
        {"id": 3, "titre": "Introduction aux Algorithmes", "auteur": "Thomas Cormen", "section": "Fonds Général & Littérature", "categorie": "Informatique et généralités / revues", "acquisition": "Acquisition / Partenariat", "etat": "Bon état", "disponible": True},
        {"id": 4, "titre": "Tintin au Congo", "auteur": "Hergé", "section": "Jeunesse, Sciences & Documentaires", "categorie": "Bande dessinée", "acquisition": "Don en nature", "etat": "État moyen", "disponible": True},
        {"id": 5, "titre": "Atlas Mondial du 21e Siècle", "auteur": "Collectif", "section": "Jeunesse, Sciences & Documentaires", "categorie": "Atlas", "acquisition": "Acquisition / Partenariat", "etat": "Neuf", "disponible": True},
        {"id": 6, "titre": "Le Petit Prince", "auteur": "Antoine de Saint-Exupéry", "section": "Jeunesse, Sciences & Documentaires", "categorie": "Littérature jeunesse, contes et légendes", "acquisition": "Don en nature", "etat": "Bon état", "disponible": True},
        {"id": 7, "titre": "Revue Scientifique Africaine", "auteur": "Académie des Sciences", "section": "Fonds Général & Littérature", "categorie": "Informatique et généralités / revues", "acquisition": "Acquisition / Partenariat", "etat": "Neuf", "disponible": True}
    ]

    donnees["usagers"] = [
        {"id": 1, "nom_prenom": "Aminata Diallo", "sexe": "F", "niveau": "Élèves (1er cycle)", "tarif_annuel": 2000, "contact": "07 01 02 03 04", "date_inscription": "2026-10-01", "actif": True},
        {"id": 2, "nom_prenom": "Moussa Traoré", "sexe": "M", "niveau": "Étudiants", "tarif_annuel": 3000, "contact": "05 11 22 33 44", "date_inscription": "2026-10-15", "actif": True},
        {"id": 3, "nom_prenom": "Fatou Ndiaye", "sexe": "F", "niveau": "Écoliers", "tarif_annuel": 1000, "contact": "01 23 45 67 89", "date_inscription": "2026-11-01", "actif": True},
        {"id": 4, "nom_prenom": "Dr. Jean Kouassi", "sexe": "M", "niveau": "Personnes avec source de revenus", "tarif_annuel": 5000, "contact": "07 88 99 00 11", "date_inscription": "2026-11-10", "actif": True}
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
            "date_emprunt": (datetime.now() - timedelta(days=17)).strftime("%Y-%m-%d"),
            "date_retour_prevue": (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            "date_retour_effective": None,
            "etat_depart": "Neuf",
            "etat_retour": None,
            "statut": "En cours"
        }
    ]

    sauvegarder_donnees(donnees)
    return jsonify({"success": True})


def ouvrir_fenetre():
    url = "http://127.0.0.1:5000"
    # Tente d'ouvrir en mode Application native Microsoft Edge (sans barre d'adresse)
    try:
        os.system(f'start msedge --app="{url}"')
    except Exception:
        webbrowser.open(url)


if __name__ == "__main__":
    import threading
    import time

    # Configuration encodage console Windows
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    def launch_browser():
        time.sleep(1.2)
        ouvrir_fenetre()

    threading.Thread(target=launch_browser, daemon=True).start()
    print("\n" + "=" * 60)
    print(" SERVEUR BIBLIOTHEQUE PRO DEMARRE SUR http://127.0.0.1:5000")
    print("=" * 60 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=False)


