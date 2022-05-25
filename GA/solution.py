import abc
from math import pi, sqrt
from turtle import distance
from pip import main
from gacvm import Domains, ProblemDefinition
from gaapp import QSolutionToSolvePanel
import numpy as np
import probleme_3_classe_utilitaire
import uqtgui
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QObject, Signal, Slot, QSize, QPointF, QRectF
from PySide6.QtWidgets import  (QApplication, QMainWindow, QWidget,
                                QLabel, QScrollBar, QComboBox, QPushButton, QPlainTextEdit, QCheckBox,
                                QGroupBox, QSplitter, QTabWidget,
                                QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QSizePolicy,
                                QMessageBox)
from PySide6.QtGui import  (QImage, QPixmap, QIcon, QPainter, QFont, QPen, QBrush, QColor, QTransform, QPolygonF)
from __feature__ import snake_case, true_property

class OpenBoxSolution:
    def __init__(self, tab_parametres, domain_names):
        self.__box_width = tab_parametres[0]
        self.__box_height = tab_parametres[1]
        self.__range = self.__calculer_range()
        self.__domaine = Domains(self.__range, domain_names)
        self.__probleme_definition = ProblemDefinition(self.__domaine, self)


    def __calculer_range(self):
    
        range = np.zeros((1,2), dtype=np.float64)
        range[:,0] = min(self.__box_width, self.__box_height)/2 * 0.001
        range[:,1] = min(self.__box_width, self.__box_height)/2 * 0.999

        return range

    @property
    def probleme_definition(self):
        return self.__probleme_definition

    #Fitness function
    def __call__(self, solution):
        largeur_finale = self.__box_width - (solution[0] * 2)
        hauteur_finale = self.__box_height - (solution[0] * 2)
        return largeur_finale * hauteur_finale * solution[0]

class ShapeTransformationOptimizerSolution:
    def __init__(self, tab_parametres, domain_names):
        self.__tab_parametres = tab_parametres
        self.__range = self.__calculer_range()
        self.__domaine = Domains(self.__range, domain_names)
        self.__probleme_definition = ProblemDefinition(self.__domaine , self)
        self.__canvas = QRectF(self.__tab_parametres[3][0], self.__tab_parametres[3][1] ) #Property

    @property
    def probleme_definition(self):
        return self.__probleme_definition

    def __calculer_range(self):
    
        range = np.zeros((4,2), dtype=np.float64)

        range[0,0] = 0
        range[0,1] = self.__tab_parametres[0] - self.__tab_parametres[5]
        range[1,0] = 0
        range[1,1] = self.__tab_parametres[1] - self.__tab_parametres[6]
        range[2,0] = 0
        range[2,1] = 360
        range[3,0] = 1
        range[3,1] = 15             

        return range


    def __call__(self, solution):

        qtransform = QTransform()
        qtransform.translate(solution[0], solution[1])
        qtransform.rotate(solution[2])
        qtransform.scale(solution[3], solution[3])

        tab_points_transformes = []
        for i in range(len(self.__tab_parametres[2])):
            point = qtransform.map(self.__tab_parametres[2][i])
            tab_points_transformes.append(point)

        for i in range(len(tab_points_transformes)):
            if not self.__canvas.contains(tab_points_transformes[i]):
                return 0
        
        qpoly = QPolygonF(tab_points_transformes)
        if len(self.__tab_parametres[4]) != 0:
            for i in range(len(self.__tab_parametres[4])):
                if qpoly.contains_point(self.__tab_parametres[4][i], Qt.WindingFill):
                    return 0
        
        return uqtgui.area_from_QPolygonF(qpoly)



class CellTowerCoverageOptimizerSolution:
    def __init__(self, tab_parametres, domain_names):
        self.tab_parametres = tab_parametres
        self.__nb_tiny_towers = self.tab_parametres[2][0]
        self.__nb_small_tower = self.tab_parametres[2][1]
        self.__nb_medium_tower = self.tab_parametres[2][2]
        self.__nb_large_tower = self.tab_parametres[2][3]
        self.__nb_total_dimensions = 2*(self.__nb_tiny_towers + self.__nb_small_tower + self.__nb_medium_tower + self.__nb_large_tower)
        self.__domain_names = domain_names
        self.range = self.calculer_range()
        self.domaine = Domains(self.range,  self.__domain_names)
        self.probleme_definition = ProblemDefinition(self.domaine, self)


    
    def calculer_range(self):
        # test = self.domain_names
        if (len(self.__domain_names) == 0):
            self.__domain_names = np.array([["Domaine temporaire"]])
            arange = np.zeros((1,2))
            
            arange[:,1]=1.0
        else:

            arange = np.zeros((self.__nb_total_dimensions,2), dtype=np.float64)
            # print(range)
            #TranslationX (max: )

            for current_dimension in range(self.__nb_total_dimensions):
                if current_dimension % 2 == 0:
                    arange[current_dimension,0] = 0
                    arange[current_dimension,1] = self.tab_parametres[0] #Canvas_width
                else:
                    arange[current_dimension,0] = 0
                    arange[current_dimension,1] = self.tab_parametres[1] #canvas_height

        # print(range)
        return arange


        #Fitness function
    def __call__(self, solution):

        tableau_tours = []

        probleme_3_classe_utilitaire.create_nb_tower(self.__nb_tiny_towers, probleme_3_classe_utilitaire.TinyTower, tableau_tours )

        probleme_3_classe_utilitaire.create_nb_tower(self.__nb_small_tower, probleme_3_classe_utilitaire.SmallTower, tableau_tours)

        probleme_3_classe_utilitaire.create_nb_tower(self.__nb_medium_tower, probleme_3_classe_utilitaire.MediumTower, tableau_tours)

        probleme_3_classe_utilitaire.create_nb_tower(self.__nb_large_tower, probleme_3_classe_utilitaire.LargeTower, tableau_tours)

        

        #Appliquer translations
        for current_index in range(len(tableau_tours)):
            tower = tableau_tours[current_index]
            tower.x += solution[current_index]
            tower.y += solution[current_index+1]

        #Check intersections
        area_intersection_between_towers = 0
        for i in range(len(tableau_tours)):
            # tableau_tours[i].x += tableau_tours[i].radius
            # tableau_tours[i].y += tableau_tours[i].radius
            for j in range(len(tableau_tours)-1):
                if i == j:
                    continue


                area_intersection_between_towers += probleme_3_classe_utilitaire.intersection_area(tableau_tours[i], tableau_tours[j])
            # tableau_tours[j].x -= tableau_tours[j].radius
            # tableau_tours[j].y -= tableau_tours[j].radius

                # distance = sqrt((tableau_tours[j].x - tableau_tours[i].x)**2 + (tableau_tours[j].y - tableau_tours[i].y)**2)
                # if distance < (tableau_tours[i].radius + tableau_tours[j].radius): 
                #     radius_intersection = (tableau_tours[i].radius + tableau_tours[j].radius) - distance
                #     pctage_intersection_tour1 = (tableau_tours[i].radius*2)/((tableau_tours[i].radius*2)-radius_intersection)
                #     tableau_tours[i].area -= (tableau_tours[i].area * pctage_intersection_tour1)
                #     # tableau_tours[j].area - (tableau_tours[j].area * pctage_a_enlever)

                #     pctage_intersection_tour2 = (tableau_tours[j].radius*2)/((tableau_tours[j].radius*2)-radius_intersection)
                #     tableau_tours[j].area -= (tableau_tours[j].area * pctage_intersection_tour2)

        #Check villes
        aire_totale = 0
        for current_city in self.tab_parametres[3]:
            aire_totale += current_city.area

        # aire_totale += aire_totale*0.10 #Marge d'erreur
        area_coverage = 0
        #Check covered radius
        area_intersection_between_cities_and_towers = 0
        for index_ville in range(len(self.tab_parametres[3])):
        #     # self.tab_parametres[4][index_ville].x += tableau_tours[index_ville].radius
        #     # self.tab_parametres[4][index_ville].y += tableau_tours[index_ville].radius
            for index_tour in range(len(tableau_tours)):
                if index_ville == index_tour:
                    continue


                area_intersection_between_cities_and_towers += probleme_3_classe_utilitaire.intersection_area(self.tab_parametres[3][index_ville], tableau_tours[index_tour])

        #         distance = sqrt((tableau_tours[index_tour].x - self.tab_parametres[3][index_ville].x)**2 + (tableau_tours[index_tour].y - self.tab_parametres[3][index_ville].y)**2)
        #         if distance < (self.tab_parametres[3][index_ville].radius + tableau_tours[index_tour].radius): 

        #             radius_intersection = (self.tab_parametres[3][index_ville].radius + tableau_tours[index_tour].radius) - distance
        #             pctage_intersection_ville = (self.tab_parametres[3][index_ville].radius*2)/((self.tab_parametres[3][index_ville].radius*2)-radius_intersection)
        #             area_coverage += (self.tab_parametres[3][index_ville].area * pctage_intersection_ville)
        #             # tableau_tours[j].area - (tableau_tours[j].area * pctage_a_enlever)
                    
        #             pctage_intersection_tour = (tableau_tours[index_tour].radius*2)/((tableau_tours[index_tour].radius*2)-radius_intersection)
        #             area_coverage += (tableau_tours[index_tour].area * pctage_intersection_tour)
        # if area_coverage == 0:
        #     return 0
        
        if area_intersection_between_cities_and_towers - area_intersection_between_towers > 0:
            area_intersection_between_cities_and_towers-=area_intersection_between_towers
                # test = (aire_totale/area_intersection_between_cities_and_towers)*100
                # if test is None:
                #     test = 0
            return (aire_totale/area_intersection_between_cities_and_towers)*100
    
        elif area_intersection_between_towers > aire_totale:
            return 0
        else:
            return 0 

            



        
        
