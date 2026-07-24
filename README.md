# MapMyNet

**Simulateur de routage réseau interactif**

Projet realise en 2e annee de cycle preparatoire - INSA Lyon, departement informatique (3IF).

---

## Description

MapMyNet est un simulateur de routage réseau qui permet de visualiser un réseau de routeurs, de calculer le chemin optimal entre deux points grâce à différents algorithmes de parcours de graphe, et de simuler des pannes de liens ou de routeurs.

**Algorithmes implémentés :**

| Algorithme  | Description |
|-------------|-------------|
| **BFS**     | Parcours en largeur — minimise le nombre de sauts |
| **DFS**     | Parcours en profondeur — exploration exhaustive |
| **Dijkstra**| Plus court chemin sur graphe pondéré — optimal |
| **A\***     | Dijkstra guidé par heuristique géographique — plus rapide sur les grands réseaux |

**Fonctionnalités :**

- Interface graphique Tkinter avec visualisation du graphe
- Sélection entre deux réseaux : local (routeurs fictifs) et monde (villes mondiales)
- Calcul et affichage du chemin optimal (en surbrillance verte)
- Simulation de pannes : coupure de liens, extinction de routeurs
- Réinitialisation complète du réseau

---

## Structure du projet

```
mapmynet/
├── algo/
│   └── modele.py        # Modèle MVC : Graphe + algorithmes de routage
├── data/
│   ├── noeuds.csv        # Réseau local — nœuds
│   ├── aretes.csv        # Réseau local — liens
│   ├── noeuds_monde.csv  # Réseau monde — nœuds (villes)
│   └── aretes_monde.csv  # Réseau monde — liaisons
├── gui/
│   └── gui.py            # Vue MVC : interface graphique Tkinter
├── test/
│   └── tests.py          # Tests unitaires
├── main.py               # Point d'entrée de l'application
├── README.md
└── .gitignore
```

---

## Installation

### Prérequis

- **Python 3.x** (testé sur Python 3.10+)
- **Tkinter** (inclus par défaut avec Python sur Windows, macOS et Linux)

> Sur Linux, si Tkinter est absent :
> ```bash
> sudo apt install python3-tk
> ```

Aucune bibliothèque tierce n'est nécessaire — pas de `pip install`.

### Lancement

```bash
cd mapmynet
python main.py
```

L'interface graphique s'ouvre automatiquement.

---

## Utilisation

1. **Choisir un réseau** — sélectionnez « Réseau local » ou « Réseau monde » dans le menu déroulant.
2. **Choisir un algorithme** — BFS, DFS, Dijkstra ou A\*.
3. **Définir la source et la destination** — deux menus déroulants listant les routeurs.
4. **Calculer** — cliquez sur « Calculer le chemin ».
5. **Simuler une panne** — coupez un lien ou désactivez un routeur, puis recalculez.

### Tests

```bash
cd test
python tests.py
```

---

## Auteurs

- **Dean Leveneur**
- Walid Bouknia
- Enzo Grivot
- Arnaud Yock-Nam
- Margaux Lambolez

---

## Licence

Projet pedagogique - INSA Lyon.