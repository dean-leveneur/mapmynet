"""
MapMyNet — Simulateur de routage réseau interactif

Point d'entrée de l'application. Lance l'interface graphique Tkinter.
"""

from gui.gui import Fenetre

if __name__ == "__main__":
    app = Fenetre()
    app.mainloop()