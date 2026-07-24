import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

from algo.modele import Graphe, AlgorithmeParcours


class Fenetre(tk.Tk):
    """Fenêtre principale de l'application, hérite de tk.Tk."""

    def __init__(self):
        super().__init__()

        # Titre et dimensions de la fenêtre
        self.title("Simulateur de Routage")
        self.geometry("1100x700")
        self.minsize(900, 500)

        # Le graphe (données du réseau) et l'algo (calcul de chemin)
        self.graphe = Graphe()
        self.algo = AlgorithmeParcours()
        self.chemin = []  # chemin trouvé par l'algorithme, vide au départ

        # Palette de couleurs (générée sur coolors.co)
        self.fond = "#F0F0F0"
        self.bleu = "#6699CC"
        self.rouge = "#FF3C38"
        self.gris = "#AAAAAA"
        self.vert = "#87BAAB"
        self.orange = "#FF8C42"

        # Panneau de gauche (menu paramètres)
        # pack_propagate(False) empêche le frame de se redimensionner
        self.menu = tk.Frame(self, width=220, padx=10, pady=10, bg=self.fond)
        self.menu.pack(side=tk.LEFT, fill=tk.Y)
        self.menu.pack_propagate(False)

        # Zone de dessin à droite (le canvas)
        # <Configure> se déclenche quand on redimensionne la fenêtre
        self.canvas = tk.Canvas(self, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda event: self.dessiner_graphe())

        # Construction de l'interface puis chargement des données
        self.creer_widgets()
        self.charger_donnees()
        self.remplir_listes()
        self.dessiner_graphe()

    # --------------------------------------------------
    # Construction des widgets (boutons, listes...)
    # --------------------------------------------------
    def creer_widgets(self):
        # Titre de la section paramètres
        tk.Label(self.menu, text="Paramètres", font=("Arial", 13, "bold"), bg=self.fond).pack(pady=(5, 10))

        # Choix du réseau (local ou monde)
        self.combo_reseau = self.ajouter_combo("Réseau :", ["Réseau local", "Réseau monde"])
        self.combo_reseau.current(0)  # "Réseau local" par défaut
        # Quand on change de réseau, on recharge tout
        self.combo_reseau.bind("<<ComboboxSelected>>", lambda event: self.reinitialiser())

        # Choix de l'algorithme
        self.combo_algo = self.ajouter_combo("Algorithme :", ["BFS", "DFS", "Dijkstra", "A*"])
        self.combo_algo.current(2)  # Dijkstra par défaut

        # Choix du routeur source et destination
        self.combo_source = self.ajouter_combo("Source :")
        self.combo_dest = self.ajouter_combo("Destination :")

        # Bouton pour lancer le calcul
        tk.Button(self.menu, text="Calculer le chemin", command=self.calculer,
                  bg=self.bleu, fg="white", font=("Arial", 10, "bold")).pack(fill=tk.X, pady=(5, 5))

        # Bouton pour tout remettre à zéro
        tk.Button(self.menu, text="Réinitialiser", command=self.reinitialiser,
                  bg=self.orange, fg="white").pack(fill=tk.X, pady=(0, 10))

        # Séparateur visuel
        ttk.Separator(self.menu).pack(fill=tk.X, pady=5)

        # Zone d'affichage des résultats
        tk.Label(self.menu, text="Résultats", font=("Arial", 12, "bold"), bg=self.fond).pack(pady=(5, 5))

        tk.Label(self.menu, text="Coût :", bg=self.fond).pack(anchor="w")
        self.lbl_cout = tk.Label(self.menu, text="--", font=("Arial", 11, "bold"), bg=self.fond)
        self.lbl_cout.pack(anchor="w")

        tk.Label(self.menu, text="Chemin :", bg=self.fond).pack(anchor="w", pady=(5, 0))
        # wraplength=200 pour que le texte passe à la ligne s'il est trop long
        self.lbl_chemin = tk.Label(self.menu, text="--", font=("Arial", 11, "bold"),
                                   bg=self.fond, wraplength=200, justify=tk.LEFT)
        self.lbl_chemin.pack(anchor="w", pady=(0, 5))

        ttk.Separator(self.menu).pack(fill=tk.X, pady=5)

        # Section panne de lien
        tk.Label(self.menu, text="Panne lien", font=("Arial", 11, "bold"), bg=self.fond).pack(pady=(5, 5))

        # Les deux combos pour choisir les extrémités du lien à couper
        frame = tk.Frame(self.menu, bg=self.fond)
        frame.pack(fill=tk.X)

        tk.Label(frame, text="De :", bg=self.fond).pack(side=tk.LEFT)
        self.combo_panne_src = ttk.Combobox(frame, width=6, state="readonly")
        self.combo_panne_src.pack(side=tk.LEFT, padx=2)

        tk.Label(frame, text="À :", bg=self.fond).pack(side=tk.LEFT)
        self.combo_panne_dst = ttk.Combobox(frame, width=6, state="readonly")
        self.combo_panne_dst.pack(side=tk.LEFT, padx=2)

        tk.Button(self.menu, text="Couper lien", command=self.supprimer_lien,
                  bg=self.rouge, fg="white").pack(fill=tk.X, pady=(8, 4))

        # Section panne de routeur
        tk.Label(self.menu, text="Panne routeur :", bg=self.fond).pack(anchor="w", pady=(5, 0))
        self.combo_panne_noeud = ttk.Combobox(self.menu, state="readonly")
        self.combo_panne_noeud.pack(fill=tk.X, pady=(0, 4))

        tk.Button(self.menu, text="Toggle panne", command=self.changer_etat_routeur,
                  bg=self.rouge, fg="white").pack(fill=tk.X, pady=(4, 4))

    def ajouter_combo(self, texte, valeurs=None):
        """Crée un label + une liste déroulante et la retourne."""
        tk.Label(self.menu, text=texte, bg=self.fond).pack(anchor="w")
        combo = ttk.Combobox(self.menu, state="readonly", values=valeurs or [])
        combo.pack(fill=tk.X, pady=(0, 8))
        return combo

    # --------------------------------------------------
    # Chargement des fichiers CSV
    # --------------------------------------------------
    def charger_donnees(self):
        # On recommence avec un graphe vide
        self.graphe = Graphe()
        self.chemin = []

        # Dossier "data" à côté du dossier du script
        dossier = os.path.join(os.path.dirname(__file__), "..", "data")

        # Selon le réseau choisi, on prend les fichiers correspondants
        if self.combo_reseau.current() == 1:
            fichier_noeuds = os.path.join(dossier, "noeuds_monde.csv")
            fichier_aretes = os.path.join(dossier, "aretes_monde.csv")
        else:
            fichier_noeuds = os.path.join(dossier, "noeuds.csv")
            fichier_aretes = os.path.join(dossier, "aretes.csv")

        # Lecture des noeuds
        with open(fichier_noeuds, "r", encoding="utf-8") as f:
            lecteur = csv.DictReader(f)
            for ligne in lecteur:
                identifiant = ligne["ID_Routeur"].strip()
                # Certaines colonnes ont des noms différents selon le fichier
                nom = ligne.get("Nom_Routeur", ligne.get("Ville", identifiant)).strip()
                x = float(ligne.get("Coord_X", ligne.get("Longitude", 0)))
                y = float(ligne.get("Coord_Y", ligne.get("Latitude", 0)))
                actif = ligne["Etat"].strip().lower() == "actif"

                self.graphe.ajouter_noeud(identifiant, x, y, nom, actif)

        # Lecture des arêtes
        with open(fichier_aretes, "r", encoding="utf-8-sig") as f:
            lecteur = csv.DictReader(f)
            for ligne in lecteur:
                depart = ligne["Depart"].strip()
                arrivee = ligne.get("Arrivee", ligne.get("Arrivée", "")).strip()
                cout = float(ligne.get("Cout", ligne.get("Coût", 1)))

                self.graphe.ajouter_lien(depart, arrivee, cout)

    # --------------------------------------------------
    # Remplissage des listes déroulantes
    # --------------------------------------------------
    def remplir_listes(self):
        noeuds = self.graphe.get_noeuds()
        noms = [self.nom_noeud(n) for n in noeuds]

        # Dictionnaire inversé : nom affiché -> identifiant interne
        # (les combos affichent les noms, mais on a besoin de l'ID pour les algos)
        self.nom_vers_id = {}
        for n in noeuds:
            self.nom_vers_id[self.nom_noeud(n)] = n

        # On remplit toutes les combos avec les mêmes noms
        for combo in [self.combo_source, self.combo_dest,
                      self.combo_panne_src, self.combo_panne_dst,
                      self.combo_panne_noeud]:
            combo["values"] = noms

        # Sélection par défaut : premier noeud en source, deuxième en destination
        if noms:
            self.combo_source.current(0)
            self.combo_dest.current(min(1, len(noms) - 1))

    def nom_noeud(self, identifiant):
        """Retourne le nom affiché d'un routeur à partir de son identifiant."""
        return self.graphe.noeuds_attr.get(identifiant, {}).get("nom", str(identifiant))

    def id_selectionne(self, combo):
        """Récupère l'identifiant interne du routeur sélectionné dans une combo."""
        return self.nom_vers_id.get(combo.get())

    # --------------------------------------------------
    # Dessin du graphe sur le canvas
    # --------------------------------------------------
    def dessiner_graphe(self):
        # On efface tout et on redessine
        self.canvas.delete("all")

        if not self.graphe.noeuds_attr:
            return  # graphe vide, rien à dessiner

        largeur = self.canvas.winfo_width()
        hauteur = self.canvas.winfo_height()

        # Quand la fenêtre vient de s'ouvrir, le canvas n'a pas encore
        # sa taille finale donc on retente dans 100ms
        if largeur < 10 or hauteur < 10:
            self.after(100, self.dessiner_graphe)
            return

        self.calculer_positions(largeur, hauteur)
        self.dessiner_liens()
        self.dessiner_noeuds()

    def calculer_positions(self, largeur, hauteur):
        """
        Convertit les coordonnées du graphe en pixels sur le canvas.
        On adapte l'échelle pour que tout tienne avec une marge de 50px.
        """
        marge = 50

        # Récupération des bornes du graphe
        xs = [info["x"] for info in self.graphe.noeuds_attr.values()]
        ys = [info["y"] for info in self.graphe.noeuds_attr.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        # On évite la division par 0 si tous les points sont alignés
        distance_x = max(max_x - min_x, 1)
        distance_y = max(max_y - min_y, 1)

        # Échelle commune pour garder les proportions
        echelle = min((largeur - 2 * marge) / distance_x,
                      (hauteur - 2 * marge) / distance_y)

        # Décalage pour centrer le dessin
        decalage_x = marge + ((largeur - 2 * marge) - distance_x * echelle) / 2
        decalage_y = marge + ((hauteur - 2 * marge) - distance_y * echelle) / 2

        # Calcul de la position pixel de chaque noeud
        self.positions = {}
        for identifiant, info in self.graphe.noeuds_attr.items():
            x = decalage_x + (info["x"] - min_x) * echelle
            y = decalage_y + (info["y"] - min_y) * echelle
            self.positions[identifiant] = (x, y)

    def dessiner_liens(self):
        """Dessine tous les câbles du réseau. Ceux du chemin sont en vert et plus épais."""
        liens_du_chemin = self.liens_du_chemin()

        for depart in self.graphe.get_noeuds():
            for arrivee, cout in self.graphe.adjacence.get(depart, {}).items():
                # Le graphe est non orienté donc chaque lien apparaît 2 fois
                # dans adjacence. On ne le dessine qu'une fois en ignorant
                # la direction où depart > arrivee (ordre alphabétique)
                if depart > arrivee:
                    continue

                x1, y1 = self.positions[depart]
                x2, y2 = self.positions[arrivee]

                # On trie les deux extrémités pour comparer avec liens_du_chemin
                lien = tuple(sorted([depart, arrivee]))
                couleur = self.vert if lien in liens_du_chemin else self.gris
                epaisseur = 3 if lien in liens_du_chemin else 1

                self.canvas.create_line(x1, y1, x2, y2, fill=couleur, width=epaisseur)

                # Texte pour le cout
                texte_cout = int(cout) if cout == int(cout) else round(cout, 1)
                self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2 - 8,
                                        text=str(texte_cout), fill="#666666",
                                        font=("Arial", 7))

    def dessiner_noeuds(self):
        """Dessine les routeurs. Bleu = actif, rouge = en panne, halo vert = dans le chemin."""
        rayon = 18

        for identifiant, info in self.graphe.noeuds_attr.items():
            x, y = self.positions[identifiant]

            # Halo vert derrière le noeud s'il fait partie du chemin
            if identifiant in self.chemin:
                self.canvas.create_oval(x - rayon - 4, y - rayon - 4,
                                        x + rayon + 4, y + rayon + 4,
                                        fill=self.vert, outline="")

            # Couleur selon l'état du routeur
            couleur = self.bleu if info["actif"] else self.rouge

            # Cercle du routeur
            self.canvas.create_oval(x - rayon, y - rayon,
                                    x + rayon, y + rayon,
                                    fill=couleur, outline="white", width=2)

            # Nom du routeur au centre
            self.canvas.create_text(x, y, text=info["nom"], fill="white",
                                    font=("Arial", 8, "bold"))

    def liens_du_chemin(self):
        """
        Retourne un set des liens qui composent le chemin trouvé.
        Chaque lien est stocké sous forme de tuple trié (depart, arrivée)
        pour pouvoir comparer facilement sans se soucier de l'ordre.
        """
        liens = set()

        for i in range(len(self.chemin) - 1):
            depart = self.chemin[i]
            arrivee = self.chemin[i + 1]
            liens.add(tuple(sorted([depart, arrivee])))

        return liens

    # --------------------------------------------------
    # Calcul du plus court chemin
    # --------------------------------------------------
    def calculer(self):
        # Récupération des routeurs sélectionnés
        depart = self.id_selectionne(self.combo_source)
        arrivee = self.id_selectionne(self.combo_dest)

        if depart is None or arrivee is None:
            messagebox.showwarning("Attention", "Sélectionnez une source et une destination.")
            return

        # Vérification que les deux routeurs fonctionnent
        if not self.graphe.noeud_actif(depart):
            messagebox.showwarning("Attention", "Le nœud source est en panne.")
            return

        if not self.graphe.noeud_actif(arrivee):
            messagebox.showwarning("Attention", "Le nœud destination est en panne.")
            return

        # On associe chaque nom d'algo à sa méthode dans AlgorithmeParcours
        methodes_algo = {
            "BFS": self.algo.bfs,
            "DFS": self.algo.dfs,
            "Dijkstra": self.algo.dijkstra,
            "A*": self.algo.astar,
        }
        methode = methodes_algo[self.combo_algo.get()]

        # Appel de l'algorithme choisi
        # Chaque méthode retourne (chemin, cout)
        chemin, cout = methode(self.graphe, depart, arrivee)

        if not chemin:
            # Aucun chemin possible entre ces deux routeurs
            self.chemin = []
            self.lbl_cout.config(text="Aucun chemin")
            self.lbl_chemin.config(text="Aucun chemin trouvé")
            self.dessiner_graphe()
            messagebox.showinfo("Résultat", "Aucun chemin trouvé.")
            return

        # Mise à jour de l'affichage avec le résultat
        self.chemin = chemin
        self.lbl_cout.config(text=self.formater_cout(cout))
        self.lbl_chemin.config(text=" → ".join(self.nom_noeud(n) for n in chemin))
        self.dessiner_graphe()

    def formater_cout(self, cout):
        """Affiche le coût de façon lisible : entier si possible, 2 décimales sinon, ∞ pour infini."""
        if cout == float("inf"):
            return "∞"
        if cout == int(cout):
            return str(int(cout))
        return f"{cout:.2f}"

    # --------------------------------------------------
    # Gestion des pannes
    # --------------------------------------------------
    def supprimer_lien(self):
        """Supprime un lien (coupure de câble) entre deux routeurs."""
        depart = self.id_selectionne(self.combo_panne_src)
        arrivee = self.id_selectionne(self.combo_panne_dst)

        if depart is None or arrivee is None:
            messagebox.showwarning("Attention", "Sélectionnez les deux extrémités du lien.")
            return

        # Vérifie que le lien existe vraiment
        if arrivee not in self.graphe.adjacence.get(depart, {}):
            messagebox.showwarning("Attention", "Ce lien n'existe pas.")
            return

        self.graphe.supprimer_lien(depart, arrivee)
        self.effacer_resultat()
        self.dessiner_graphe()

    def changer_etat_routeur(self):
        """Bascule un routeur entre actif et en panne."""
        routeur = self.id_selectionne(self.combo_panne_noeud)

        if routeur is None:
            messagebox.showwarning("Attention", "Sélectionnez un routeur.")
            return

        # Inversion de l'état : actif -> panne, panne -> actif
        etat = self.graphe.noeud_actif(routeur)
        self.graphe.changer_etat_noeud(routeur, not etat)

        self.effacer_resultat()
        self.dessiner_graphe()

    # --------------------------------------------------
    # Réinitialisation
    # --------------------------------------------------
    def effacer_resultat(self):
        """Efface le chemin affiché (après une panne ou une réinitialisation)."""
        self.chemin = []
        self.lbl_cout.config(text="--")
        self.lbl_chemin.config(text="--")

    def reinitialiser(self):
        """Recharge les données depuis les fichiers CSV et efface les résultats."""
        self.charger_donnees()
        self.remplir_listes()
        self.effacer_resultat()
        self.dessiner_graphe()
