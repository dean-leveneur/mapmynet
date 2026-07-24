# -*- coding: utf-8 -*-
"""
Rôle MVC : Modèle

Ce fichier contient TOUTE la logique du programme (données + calculs).
Il est indépendant de l'interface graphique.

Il contient 3 classes :
  - Graphe              : stocke les routeurs et les connexions du réseau
  - AlgorithmeRoutage   : classe mère avec les outils partagés par tous les algos
  - AlgorithmeParcours  : contient les 4 algorithmes (BFS, DFS, Dijkstra, A*)
"""

import csv   # pour lire les fichiers .csv (noeuds.csv, aretes.csv)
import math  # pour la fonction sqrt (racine carrée) utilisée dans A*


# ==============================================================================
#  CLASSE GRAPHE
#  Représente le réseau : routeurs = noeuds, câbles = liens avec un coût
# ==============================================================================

class Graphe:
    """
    Un graphe est une structure qui stocke des noeuds (routeurs) et des liens
    (câbles) entre ces noeuds.

    On utilise deux dictionnaires Python :

    1) self.adjacence
       Stocke, pour chaque noeud, la liste de ses voisins et le coût du lien.
       Exemple :
           {
             "R1": {"R2": 2.0, "R3": 5.0},
             "R2": {"R1": 2.0, "R3": 1.0},
             ...
           }
       donc "R1 est connecté à R2 avec un coût de 2, et à R3 avec un coût de 5"

    2) self.noeuds_attr
       Stocke les informations de chaque noeud : position, nom, état (actif/panne).
       Exemple :
           {
             "R1": {"x": 0.0, "y": 0.0, "nom": "Routeur 1", "actif": True},
             ...
           }
    """

    def __init__(self):
        """
        Initialise un graphe VIDE.
        Les deux dictionnaires sont vides au départ.
        """
        self.adjacence = {}    # dictionnaire des voisins de chaque noeud
        self.noeuds_attr = {}  # dictionnaire des infos de chaque noeud


    def ajouter_noeud(self, id_noeud, x, y, nom="", etat=True):
        """
        Ajoute un routeur dans le graphe.

        Paramètres :
            id_noeud : identifiant du routeur, par ex. "R1" ou "Paris"
            x, y     : position sur l'écran (coordonnées pixel ou géographiques)
            nom      : nom affiché dans l'interface, ex. "Routeur 1"
            etat     : True = routeur allumé, False = routeur en panne
        """
        # On crée une entrée vide dans le dictionnaire d'adjacence
        # seulement si ce noeud n'existe pas déjà (pour ne pas écraser ses liens)
        if id_noeud not in self.adjacence:
            self.adjacence[id_noeud] = {}  # {} = pas encore de voisins

        # On stocke les informations du noeud dans noeuds_attr
        # Si le nom est vide, on utilise l'identifiant comme nom par défaut
        self.noeuds_attr[id_noeud] = {
            "x": float(x),                                  # coordonnée horizontale
            "y": float(y),                                  # coordonnée verticale
            "nom": nom if nom != "" else str(id_noeud),     # nom affiché
            "actif": bool(etat)                             # True=allumé, False=panne
        }


    def ajouter_lien(self, u, v, cout):
        """
        Ajoute un câble entre deux routeurs (dans les deux sens).

        Un lien est ignoré si :
        - l'un des deux routeurs n'existe pas dans le graphe
        - le coût est nul ou négatif (ça n'aurait pas de sens réseau)

        Paramètres :
            u    : identifiant du premier routeur
            v    : identifiant du deuxième routeur
            cout : coût du lien (ex. latence en ms, distance en km...)
        """
        # Vérification que les deux routeurs existent
        if not self.noeud_existe(u) or not self.noeud_existe(v):
            return  # on sort de la fonction sans rien faire

        # Vérification que le coût est valide
        if cout <= 0:
            return  # coût nul ou négatif donc on ignore ce lien

        # On enregistre le lien dans les DEUX sens (graphe non orienté)
        # u vers v
        self.adjacence[u][v] = float(cout)
        # v vers u (même coût dans les deux sens)
        self.adjacence[v][u] = float(cout)


    def supprimer_lien(self, u, v):
        """
        Supprime le câble entre deux routeurs (dans les deux sens).
        Sert à simuler une panne de câble.

        Si le lien n'existe pas, la fonction ne fait rien (pas d'erreur).
        """
        # Suppression du côté u vers v
        if u in self.adjacence and v in self.adjacence[u]:
            del self.adjacence[u][v]  # del = supprimer une clé d'un dictionnaire

        # Suppression du côté v vers u
        if v in self.adjacence and u in self.adjacence[v]:
            del self.adjacence[v][u]


    def changer_etat_noeud(self, id_noeud, etat):
        """
        Allume (etat=True) ou éteint (etat=False) un routeur.
        Sert à simuler la panne d'un routeur.

        Un routeur éteint est ignoré par tous les algorithmes.
        """
        if id_noeud in self.noeuds_attr:
            # On modifie uniquement la valeur "actif" dans le dictionnaire
            self.noeuds_attr[id_noeud]["actif"] = bool(etat)


    def charger_donnees(self, fichier_noeuds, fichier_liens):
        """
        Lit deux fichiers CSV et remplit le graphe avec les donnees.

        Format attendu pour noeuds.csv :
            id, nom, x, y, etat
            R1, Routeur 1, 100, 200, True

        Format attendu pour aretes.csv :
            source, destination, cout
            R1, R2, 5

        Leve une exception FileNotFoundError si un fichier est introuvable,
        ou une exception ValueError si les donnees sont mal formatees.
        """
        # --- Lecture du fichier des noeuds ---
        with open(fichier_noeuds, newline="", encoding="utf-8") as f:
            # csv.DictReader lit chaque ligne comme un dictionnaire
            # La première ligne du CSV sert de clés
            for ligne in csv.DictReader(f):
                # On convertit l'état en booléen
                # (True si la cellule vaut "1", "True" ou "true")
                etat = ligne["etat"].strip() in ("1", "True", "true")

                # On ajoute le noeud dans le graphe
                self.ajouter_noeud(
                    ligne["id"].strip(),        # identifiant, ex. "R1"
                    float(ligne["x"]),          # coordonnée x
                    float(ligne["y"]),          # coordonnée y
                    nom=ligne["nom"].strip(),   # nom affiché
                    etat=etat                   # True ou False
                )

        # --- Lecture du fichier des liens ---
        with open(fichier_liens, newline="", encoding="utf-8") as f:
            for ligne in csv.DictReader(f):
                self.ajouter_lien(
                    ligne["source"].strip(),       # routeur de départ
                    ligne["destination"].strip(),  # routeur d'arrivée
                    float(ligne["cout"])           # coût du lien
                )


    def noeud_existe(self, id_noeud):
        """
        Vérifie si un routeur est dans le graphe.
        Retourne True s'il existe, False sinon.
        """
        return id_noeud in self.adjacence


    def noeud_actif(self, id_noeud):
        """
        Vérifie si un routeur est allumé (pas en panne).
        Retourne True s'il est actif, False sinon.

        Retourne aussi False si le noeud n'existe pas du tout.
        """
        if id_noeud not in self.noeuds_attr:
            return False  # le noeud n'existe pas donc considéré comme inactif

        return self.noeuds_attr[id_noeud]["actif"]  # on lit la valeur "actif"


    def get_voisins(self, u):
        """
        Retourne les voisins ACTIFS d'un routeur, avec le coût de chaque lien.

        Les voisins en panne sont automatiquement exclus.
        Si le routeur u est lui-même en panne, retourne un dict vide.

        Retourne : dict { id_voisin: cout }
        Exemple : {"R2": 2.0, "R3": 5.0}
        """
        # Si le noeud n'existe pas ou est en panne donc aucun voisin accessible
        if not self.noeud_existe(u) or not self.noeud_actif(u):
            return {}

        # Compréhension de dictionnaire : on garde uniquement les voisins actifs
        # Pour chaque voisin v et son coût c dans self.adjacence[u],
        # on ne le garde que si ce voisin est actif
        return {v: c for v, c in self.adjacence[u].items() if self.noeud_actif(v)}


    def get_coordonnees(self, id_noeud):
        """
        Retourne les coordonnées (x, y) d'un noeud sous forme de tuple.
        Retourne None si le noeud n'existe pas.

        Utilisé par l'interface graphique pour dessiner les noeuds,
        et par A* pour calculer la distance euclidienne.
        """
        if id_noeud not in self.noeuds_attr:
            return None  # noeud inconnu

        # On retourne un tuple (x, y)
        return self.noeuds_attr[id_noeud]["x"], self.noeuds_attr[id_noeud]["y"]


    def get_noeuds(self):
        """
        Retourne la liste de tous les identifiants de noeuds du graphe.
        Exemple : ["R1", "R2", "R3", "R4", "R5"]
        """
        return list(self.adjacence.keys())  # .keys() = toutes les clés du dict


# ==============================================================================
#  CLASSE ALGORITHME ROUTAGE — classe mère (parent) de AlgorithmeParcours
#  Elle contient les outils communs à tous les algorithmes.
# ==============================================================================

class AlgorithmeRoutage:
    """
    Classe mère de AlgorithmeParcours.

    Elle ne contient pas d'algorithme de calcul de chemin en elle-même,
    mais regroupe des méthodes utilitaires utilisées par BFS, DFS,
    Dijkstra et A* :
        - verifier_entrees     : valide les paramètres avant de lancer un algo
        - reconstruire_chemin  : remonte le chemin depuis l'arrivée vers le départ
        - calculer_bonds       : compte le nombre de sauts dans un chemin
        - distance_euclidienne : calcule la distance à vol d'oiseau entre 2 noeuds
    """

    def verifier_entrees(self, graphe, depart, destination):
        """
        Vérifie que les deux routeurs sont valides avant de lancer un algorithme.

        Conditions vérifiées :
        - Le graphe existe (n'est pas None)
        - Le routeur de départ existe dans le graphe
        - Le routeur de destination existe dans le graphe
        - Le routeur de départ est actif (pas en panne)
        - Le routeur de destination est actif (pas en panne)

        Retourne True si tout est bon, False si quelque chose cloche.
        """
        if graphe is None:
            return False  # pas de graphe du tout

        if not graphe.noeud_existe(depart):
            return False  # le routeur de départ n'existe pas

        if not graphe.noeud_existe(destination):
            return False  # le routeur d'arrivée n'existe pas

        if not graphe.noeud_actif(depart):
            return False  # le routeur de départ est en panne

        if not graphe.noeud_actif(destination):
            return False  # le routeur d'arrivée est en panne

        return True  # tout est bon, on peut lancer l'algorithme


    def reconstruire_chemin(self, parents, destination):
        """
        Reconstruit la liste ordonnée des routeurs du chemin trouvé.

        Tous les algorithmes (BFS, DFS, Dijkstra, A*) utilisent un dictionnaire
        appelé "parents" pour mémoriser d'où l'on vient.
        Exemple : parents = {"R2": "R1", "R3": "R2", "R5": "R3"}
        donc pour aller à R5, on est passé par R3, qui vient de R2, qui vient de R1.

        Cette méthode remonte ce dictionnaire de la DESTINATION vers le DÉPART,
        puis inverse la liste pour avoir l'ordre départ vers destination.

        Retourne : liste ["R1", "R2", "R3", "R5"] ou [] si pas de chemin.
        """
        # Si la destination n'est pas dans parents, c'est qu'elle n'a jamais
        # été atteinte pendant l'exploration donc aucun chemin possible
        if destination not in parents:
            return []

        chemin = []         # liste qui va stocker les noeuds du chemin
        courant = destination  # on commence depuis la fin

        # On remonte de noeud en noeud via le dictionnaire parents
        # jusqu'à atteindre None (qui est la valeur du noeud de départ)
        while courant is not None:
            chemin.append(courant)          # on ajoute le noeud actuel
            courant = parents[courant]      # on passe au noeud précédent

        # À ce stade, chemin = ["R5", "R3", "R2", "R1"] donc ordre inversé
        chemin.reverse()  # on remet dans l'ordre : ["R1", "R2", "R3", "R5"]
        return chemin


    def calculer_bonds(self, chemin):
        """
        Calcule le nombre de sauts (bonds) dans un chemin.

        Un "bond" = traverser un lien entre deux routeurs.
        Un chemin de N routeurs contient N-1 bonds.
        Exemple : ["R1", "R2", "R3"] donc 2 bonds (R1 vers R2 et R2 vers R3)

        Retourne float("inf") si le chemin est vide (aucun chemin trouvé).
        """
        if chemin == []:
            return float("inf")  # "inf" = infini, signifie "pas de chemin"

        return len(chemin) - 1   # nombre de liens = nombre de noeuds - 1


    def distance_euclidienne(self, graphe, u, v):
        """
        Calcule la distance en ligne droite entre deux routeurs.

        Formule : sqrt( (x2-x1)² + (y2-y1)² )
        C'est le théorème de Pythagore appliqué aux coordonnées des noeuds.

        Cette distance est utilisée par A* comme heuristique :
        elle estime la distance restante jusqu'à la destination
        sans suivre les liens, à vol d'oiseau.

        Retourne 0 si l'un des noeuds n'a pas de coordonnées.
        """
        coord_u = graphe.get_coordonnees(u)  # tuple (x, y) du noeud u
        coord_v = graphe.get_coordonnees(v)  # tuple (x, y) du noeud v

        # Si l'un des noeuds n'a pas de coordonnées donc heuristique nulle
        if coord_u is None or coord_v is None:
            return 0

        x1, y1 = coord_u  # décomposition du tuple en deux variables
        x2, y2 = coord_v

        # Théorème de Pythagore : distance = racine( (x2-x1)² + (y2-y1)² )
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# ==============================================================================
#  CLASSE ALGORITHME PARCOURS — hérite de AlgorithmeRoutage
#  Contient les 4 algorithmes : BFS, DFS, Dijkstra, A*
# ==============================================================================

class AlgorithmeParcours(AlgorithmeRoutage):
    """
    Contient les quatre algorithmes de recherche de chemin.

    Hérite de AlgorithmeRoutage, donc a accès à :
        verifier_entrees, reconstruire_chemin, calculer_bonds, distance_euclidienne

    Chaque algorithme prend en entrée (graphe, depart, destination)
    et retourne un tuple (chemin, cout_ou_bonds).
    """

    # --------------------------------------------------------------------------
    #  BFS — Parcours en Largeur (Breadth-First Search)
    # --------------------------------------------------------------------------

    def bfs(self, graphe, depart, destination):
        """
        Parcours en largeur : explore le graphe niveau par niveau.

        Imagine des cercles concentriques autour du point de départ :
        on explore d'abord tous les voisins directs, puis les voisins
        des voisins, etc.

        Garantit le chemin avec le MOINS DE SAUTS (bonds),
        mais ne tient pas compte du coût des liens.

        Structure de données clé : la FILE (FIFO)
        FIFO = First In, First Out = premier entré, premier sorti
        donc comme une file d'attente à la boulangerie

        Retourne : (chemin, nombre_de_bonds) ou ([], inf) si pas de chemin.
        """
        # Vérification que les deux routeurs sont valides
        if not self.verifier_entrees(graphe, depart, destination):
            return [], float("inf")

        # --- Initialisation ---
        file = [depart]          # la file commence avec uniquement le noeud de départ
        visites = [depart]       # liste des noeuds déjà vus (pour éviter les boucles)
        parents = {depart: None} # dictionnaire : parents[noeud] = noeud précédent
                                 # Le départ n'a pas de parent donc None

        # --- Exploration ---
        while len(file) > 0:  # tant qu'il reste des noeuds à explorer

            courant = file.pop(0)  # on prend le PREMIER élément de la file (FIFO)
                                   # pop(0) = retirer et retourner l'élément à l'index 0

            # Si on est arrivé à destination donc on reconstruit et retourne le chemin
            if courant == destination:
                chemin = self.reconstruire_chemin(parents, destination)
                return chemin, self.calculer_bonds(chemin)

            # Pour chaque voisin actif du noeud courant
            for voisin in graphe.get_voisins(courant):
                if voisin not in visites:       # si ce voisin n'a pas encore été vu
                    visites.append(voisin)      # on le marque comme vu
                    parents[voisin] = courant   # on note par où on est arrivé
                    file.append(voisin)         # on l'ajoute à la FIN de la file

        # Si on sort de la boucle sans trouver la destination donc pas de chemin
        return [], float("inf")


    # --------------------------------------------------------------------------
    #  DFS — Parcours en Profondeur (Depth-First Search)
    # --------------------------------------------------------------------------

    def dfs(self, graphe, depart, destination):
        """
        Parcours en profondeur : explore une branche jusqu'au bout,
        puis revient en arrière (backtracking) pour explorer d'autres branches.

        donc NE garantit PAS le chemin optimal (ni en bonds, ni en coût).
        Utile pour explorer tous les chemins possibles ou détecter des cycles.

        Structure de données clé : la PILE (LIFO)
        LIFO = Last In, First Out = dernier entré, premier sorti
        donc comme une pile d'assiettes : on prend toujours celle du dessus

        Retourne : (chemin, nombre_de_bonds) ou ([], inf) si pas de chemin.
        """
        if not self.verifier_entrees(graphe, depart, destination):
            return [], float("inf")

        # --- Initialisation ---
        pile = [depart]          # la pile commence avec le noeud de départ
        visites = [depart]
        parents = {depart: None}

        # --- Exploration ---
        while len(pile) > 0:

            courant = pile.pop()  # on prend le DERNIER élément de la pile (LIFO)
                                  # pop() sans argument = retirer le dernier élément

            if courant == destination:
                chemin = self.reconstruire_chemin(parents, destination)
                return chemin, self.calculer_bonds(chemin)

            # On récupère les voisins sous forme de liste pour pouvoir les inverser
            voisins = list(graphe.get_voisins(courant).keys())
            # On inverse l'ordre pour que le premier voisin soit traité en premier
            # (car on empile dans l'ordre inverse de celui où on veut les traiter)
            voisins.reverse()

            for voisin in voisins:
                if voisin not in visites:
                    visites.append(voisin)
                    parents[voisin] = courant
                    pile.append(voisin)  # on ajoute au SOMMET de la pile

        return [], float("inf")


    # --------------------------------------------------------------------------
    #  Méthode interne : _trouver_min
    #  Utilisée par Dijkstra et A* pour choisir le prochain noeud à traiter
    # --------------------------------------------------------------------------

    def _trouver_min(self, ensemble, valeurs):
        """
        Parcourt une liste de noeuds et retourne celui qui a la plus petite
        valeur dans le dictionnaire "valeurs".

        Le préfixe _ indique que c'est une méthode interne : elle est utilisée
        uniquement par dijkstra() et astar(), pas depuis l'extérieur.

        Exemple :
            ensemble = ["R1", "R2", "R3"]
            valeurs  = {"R1": 5, "R2": 2, "R3": 8}
            donc retourne "R2" car valeurs["R2"] = 2 est le minimum

        Retourne None si la liste est vide.
        """
        if not ensemble:
            return None  # liste vide donc aucun minimum possible

        minimum = ensemble[0]  # on part du premier élément comme minimum provisoire

        for noeud in ensemble:
            # Si la valeur de ce noeud est plus petite que le minimum actuel
            if valeurs[noeud] < valeurs[minimum]:
                minimum = noeud  # on met à jour le minimum

        return minimum  # on retourne l'identifiant du noeud avec la plus petite valeur


    # --------------------------------------------------------------------------
    #  DIJKSTRA — Plus court chemin pondéré
    # --------------------------------------------------------------------------

    def dijkstra(self, graphe, depart, destination):
        """
        Algorithme de Dijkstra : trouve le chemin avec le COÛT TOTAL MINIMUM.

        Principe :
        1. On démarre avec un coût de 0 pour le départ, infini pour tout le reste.
        2. À chaque tour, on choisit le noeud non encore traité avec le plus petit
           coût cumulé (grâce à _trouver_min).
        3. Pour chaque voisin de ce noeud, on calcule le nouveau coût :
               nouveau_coût = coût_du_noeud_courant + coût_du_lien
           Si ce nouveau coût est meilleur que ce qu'on connaissait, on met à jour.
        4. On continue jusqu'à atteindre la destination ou épuiser tous les noeuds.

        Garantit le chemin OPTIMAL (coût minimal) sur un graphe pondéré.

        Retourne : (chemin, cout_total) ou ([], inf) si pas de chemin.
        """
        if not self.verifier_entrees(graphe, depart, destination):
            return [], float("inf")

        # --- Initialisation ---
        # distances[n] = meilleur coût connu pour atteindre n depuis le départ
        # On commence avec tout à l'infini (= "pas encore atteint")
        distances = {n: float("inf") for n in graphe.get_noeuds()}
        distances[depart] = 0  # le départ est à distance 0 de lui-même

        parents = {depart: None}  # pour reconstruire le chemin à la fin

        # ouverts = noeuds pas encore traités définitivement
        ouverts = list(graphe.get_noeuds())
        # fermes = noeuds dont on a trouvé le chemin optimal définitivement
        fermes = []

        # --- Exploration ---
        while ouverts:  # tant qu'il reste des noeuds à traiter

            # On choisit le noeud ouvert avec la plus petite distance connue
            courant = self._trouver_min(ouverts, distances)

            # Si le minimum trouvé est infini, aucun noeud restant n'est accessible
            if courant is None or distances[courant] == float("inf"):
                break  # on arrête la boucle

            # Si on a atteint la destination donc on retourne le résultat
            if courant == destination:
                chemin = self.reconstruire_chemin(parents, destination)
                return chemin, distances[destination]

            ouverts.remove(courant)  # on retire courant des noeuds à traiter
            fermes.append(courant)   # on l'archive comme définitivement traité

            # --- Mise à jour des voisins ---
            for voisin, cout in graphe.get_voisins(courant).items():
                if voisin in fermes:
                    continue  # ce voisin est déjà traité donc on passe

                # Coût pour atteindre voisin en passant par courant
                nouvelle_dist = distances[courant] + cout

                # Si ce nouveau chemin est moins coûteux que ce qu'on savait
                if nouvelle_dist < distances[voisin]:
                    distances[voisin] = nouvelle_dist  # on met à jour le coût
                    parents[voisin] = courant          # on note qu'on passe par courant

        # Si on sort de la boucle sans avoir atteint destination donc pas de chemin
        return [], float("inf")


    # --------------------------------------------------------------------------
    #  A* (A-Star) — Dijkstra guidé par une heuristique géographique
    # --------------------------------------------------------------------------

    def astar(self, graphe, depart, destination):
        """
        Algorithme A* : version améliorée de Dijkstra, plus rapide en pratique.

        Différence avec Dijkstra :
        Dijkstra choisit le noeud avec le plus petit coût RÉEL depuis la source.
        A* choisit le noeud avec le plus petit score f = g + h, où :
            g = coût réel parcouru depuis la source (même que Dijkstra)
            h = estimation du coût RESTANT jusqu'à la destination
                (ici : distance euclidienne = distance à vol d'oiseau)

        L'heuristique h "guide" l'exploration vers la destination,
        ce qui évite d'explorer des noeuds éloignés de la destination.

        Donne le même résultat optimal que Dijkstra,
        mais explore moins de noeuds donc plus rapide sur les grands graphes.

        Retourne : (chemin, cout_total) ou ([], inf) si pas de chemin.
        """
        if not self.verifier_entrees(graphe, depart, destination):
            return [], float("inf")

        # --- Initialisation ---

        # g_score[n] = coût réel depuis le départ jusqu'à n
        # (même chose que "distances" dans Dijkstra)
        g_score = {n: float("inf") for n in graphe.get_noeuds()}
        g_score[depart] = 0  # coût réel pour atteindre le départ = 0

        # f_score[n] = g_score[n] + heuristique(n, destination)
        # C'est le score de priorité utilisé pour choisir le prochain noeud
        f_score = {n: float("inf") for n in graphe.get_noeuds()}
        # Pour le départ, g=0 et h = distance euclidienne vers la destination
        f_score[depart] = self.distance_euclidienne(graphe, depart, destination)

        parents = {depart: None}
        ouverts = [depart]   # noeuds candidats à explorer
        fermes = []          # noeuds définitivement traités

        # --- Exploration ---
        while ouverts:

            # On choisit le noeud avec le plus petit f_score (et non distance)
            # C'est la seule différence avec Dijkstra
            courant = self._trouver_min(ouverts, f_score)

            if courant is None:
                break

            if courant == destination:
                chemin = self.reconstruire_chemin(parents, destination)
                return chemin, g_score[destination]  # on retourne le coût RÉEL

            ouverts.remove(courant)
            fermes.append(courant)

            for voisin, cout in graphe.get_voisins(courant).items():
                if voisin in fermes:
                    continue  # déjà traité définitivement

                # Coût réel pour atteindre voisin en passant par courant
                tentative_g = g_score[courant] + cout

                # Si ce voisin n'est pas encore dans la liste des candidats, on l'ajoute
                if voisin not in ouverts:
                    ouverts.append(voisin)

                # Si on a trouvé un meilleur chemin vers ce voisin
                if tentative_g < g_score[voisin]:
                    parents[voisin] = courant          # on passe par courant
                    g_score[voisin] = tentative_g      # on met à jour le coût réel

                    # f = g réel + h estimé (distance à vol d'oiseau vers destination)
                    f_score[voisin] = tentative_g + self.distance_euclidienne(
                        graphe, voisin, destination
                    )

        return [], float("inf")


# ==============================================================================
#  EXEMPLE D'UTILISATION (exécuté seulement si on lance ce fichier directement)
# ==============================================================================

if __name__ == "__main__":
    # On crée un petit réseau de test avec 5 routeurs
    g = Graphe()
    g.ajouter_noeud("R1", 0, 0, "Routeur 1")
    g.ajouter_noeud("R2", 2, 1, "Routeur 2")
    g.ajouter_noeud("R3", 4, 0, "Routeur 3")
    g.ajouter_noeud("R4", 6, 1, "Routeur 4")
    g.ajouter_noeud("R5", 8, 0, "Routeur 5")

    # On ajoute les liens avec leurs coûts
    g.ajouter_lien("R1", "R2", 2)
    g.ajouter_lien("R1", "R3", 5)
    g.ajouter_lien("R2", "R3", 1)
    g.ajouter_lien("R2", "R4", 4)
    g.ajouter_lien("R3", "R4", 1)
    g.ajouter_lien("R4", "R5", 3)

    # On crée l'objet algorithme
    algo = AlgorithmeParcours()

    # On teste les 4 algorithmes entre R1 et R5
    print("BFS      :", algo.bfs(g, "R1", "R5"))
    print("DFS      :", algo.dfs(g, "R1", "R5"))
    print("Dijkstra :", algo.dijkstra(g, "R1", "R5"))
    print("A*       :", algo.astar(g, "R1", "R5"))
