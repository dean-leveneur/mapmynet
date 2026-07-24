# -*- coding: utf-8 -*-

from modele import Graphe, AlgorithmeParcours


def construire_graphe():
    """Construit un réseau de test réutilisable."""
    g = Graphe()
    g.ajouter_noeud("R1", 0, 0, "Routeur 1")
    g.ajouter_noeud("R2", 2, 1, "Routeur 2")
    g.ajouter_noeud("R3", 4, 0, "Routeur 3")
    g.ajouter_noeud("R4", 6, 1, "Routeur 4")
    g.ajouter_noeud("R5", 8, 0, "Routeur 5")
    g.ajouter_lien("R1", "R2", 2)
    g.ajouter_lien("R1", "R3", 5)
    g.ajouter_lien("R2", "R3", 1)
    g.ajouter_lien("R2", "R4", 4)
    g.ajouter_lien("R3", "R4", 1)
    g.ajouter_lien("R4", "R5", 3)
    return g


# ── Tests Graphe ──────────────────────────────────────────────────────────────
print("=== Tests Graphe ===")

g = construire_graphe()

# R1 existe dans le graphe
if g.noeud_existe("R1") == True:
    print(True)
else:
    print(False)

# R99 n'existe pas
if g.noeud_existe("R99") == False:
    print(True)
else:
    print(False)

# R1 est actif par défaut
if g.noeud_actif("R1") == True:
    print(True)
else:
    print(False)

# R1 mis en panne donc inactif
g.changer_etat_noeud("R1", False)
if g.noeud_actif("R1") == False:
    print(True)
else:
    print(False)
g.changer_etat_noeud("R1", True)

# Lien R1-R2 enregistré dans les deux sens
if ("R2" in g.adjacence["R1"]) == True:
    print(True)
else:
    print(False)

if ("R1" in g.adjacence["R2"]) == True:
    print(True)
else:
    print(False)

# Lien avec coût nul ignoré
g.ajouter_lien("R1", "R5", 0)
if ("R5" in g.adjacence["R1"]) == False:
    print(True)
else:
    print(False)

# Suppression de lien
g.supprimer_lien("R1", "R2")
if ("R2" in g.adjacence["R1"]) == False:
    print(True)
else:
    print(False)
g.ajouter_lien("R1", "R2", 2)

# Coordonnées de R1
if g.get_coordonnees("R1") == (0.0, 0.0):
    print(True)
else:
    print(False)

# Nœud inexistant donc None
if g.get_coordonnees("R99") == None:
    print(True)
else:
    print(False)

# Voisin en panne exclu
g.changer_etat_noeud("R2", False)
if ("R2" in g.get_voisins("R1")) == False:
    print(True)
else:
    print(False)
g.changer_etat_noeud("R2", True)


# ── Tests AlgorithmeParcours ──────────────────────────────────────────────────
print("=== Tests AlgorithmeParcours ===")

g = construire_graphe()
algo = AlgorithmeParcours()

# BFS : chemin de R1 à R5
chemin_bfs, _ = algo.bfs(g, "R1", "R5")
if chemin_bfs[0] == "R1" and chemin_bfs[-1] == "R5":
    print(True)
else:
    print(False)

# DFS : chemin de R1 à R5
chemin_dfs, _ = algo.dfs(g, "R1", "R5")
if chemin_dfs[0] == "R1" and chemin_dfs[-1] == "R5":
    print(True)
else:
    print(False)

# Dijkstra : chemin optimal
chemin_dij, cout_dij = algo.dijkstra(g, "R1", "R5")
if chemin_dij == ["R1", "R2", "R3", "R4", "R5"]:
    print(True)
else:
    print(False)

if cout_dij == 7.0:
    print(True)
else:
    print(False)

# A* : même résultat que Dijkstra
chemin_ast, cout_ast = algo.astar(g, "R1", "R5")
if chemin_ast == ["R1", "R2", "R3", "R4", "R5"]:
    print(True)
else:
    print(False)

if cout_ast == 7.0:
    print(True)
else:
    print(False)

# Dijkstra et A* donnent le même coût
if cout_dij == cout_ast:
    print(True)
else:
    print(False)


# ── Tests cas limites ─────────────────────────────────────────────────────────
print("=== Tests cas limites ===")

# Panne de R3 donc Dijkstra contourne, coût = 9
g = construire_graphe()
g.changer_etat_noeud("R3", False)
chemin_panne, cout_panne = algo.dijkstra(g, "R1", "R5")
if "R3" not in chemin_panne:
    print(True)
else:
    print(False)

if cout_panne == 9.0:
    print(True)
else:
    print(False)

# Lien R4-R5 supprimé donc aucun chemin
g2 = construire_graphe()
g2.supprimer_lien("R4", "R5")
chemin_isole, cout_isole = algo.dijkstra(g2, "R1", "R5")
if chemin_isole == []:
    print(True)
else:
    print(False)

if cout_isole == float("inf"):
    print(True)
else:
    print(False)

# Nœud inexistant donc chemin vide
chemin_inv, cout_inv = algo.dijkstra(g2, "R1", "R99")
if chemin_inv == [] and cout_inv == float("inf"):
    print(True)
else:
    print(False)
