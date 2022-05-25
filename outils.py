from cmath import pi
from math import asin, hypot, sqrt

class Ville:
    def __init__(self, nom):
        self.nom = nom
        self.x = 0
        self.y = 0
        self.radius = 0
        self.area = pi*(self.radius**2)

class CellTower:
    def __init__(self, cout, coverage_radius):
        self.x = 0
        self.y = 0
        self.cout = cout
        self.radius = coverage_radius
        self.area = pi*(self.radius**2)

class TinyTower(CellTower):
    def __init__(self):
        super().__init__(20000, 10)

class SmallTower(CellTower):
    def __init__(self):
        super().__init__(55000, 20)

class MediumTower(CellTower):
    def __init__(self):
        super().__init__(85000, 30)

class LargeTower(CellTower):
    def __init__(self):
        super().__init__(155000, 45)

def create_nb_tower(nb_towers, type_of_tower, tableau_tours):
    for i in range(nb_towers):
        tableau_tours.append(type_of_tower())    
    return tableau_tours

def intersection_area(cercle1,cercle2):
    hypothenuse = hypot(cercle2.x - cercle1.x, cercle2.y - cercle1.y)
    if hypothenuse < cercle1.radius + cercle2.radius:
        diametre_cercle1 = cercle1.radius**2
        diametre_cercle2 = cercle2.radius**2

        x = (diametre_cercle1- diametre_cercle2 + hypothenuse**2)/(2*hypothenuse)
        y = sqrt(abs(diametre_cercle1-(x**2)))

        if hypothenuse <= abs(cercle2.radius - cercle1.radius):
            return pi*(min(diametre_cercle1, diametre_cercle2))
        else:
            return diametre_cercle1 * asin(y/cercle1.radius) + diametre_cercle2 * asin(y/cercle2.radius) - y * (x + sqrt((x**2) + diametre_cercle2 - diametre_cercle1))
    else:
        return 0
