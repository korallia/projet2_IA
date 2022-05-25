import abc
from math import pi, sqrt
from turtle import distance
from pip import main
from gacvm import Domains, ProblemDefinition
from gaapp import QSolutionToSolvePanel
import numpy as np
from outils import (Ville, TinyTower, SmallTower, MediumTower, LargeTower)
import outils
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
        range[3,1] = 25             

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


        if uqtgui.area_from_QPolygonF(qpoly) < 1:
            return 0
        else:
            return uqtgui.area_from_QPolygonF(qpoly)


class CellTowerCoverageOptimizerSolution:
    def __init__(self, tab_parametres, domain_names):
        self.__tab_parametres = tab_parametres
        self.__nb_tiny_towers = self.__tab_parametres[2][0]
        self.__nb_small_tower = self.__tab_parametres[2][1]
        self.__nb_medium_tower = self.__tab_parametres[2][2]
        self.__nb_large_tower = self.__tab_parametres[2][3]
        self.__nb_total_dimensions = 2*(self.__nb_tiny_towers + self.__nb_small_tower + self.__nb_medium_tower + self.__nb_large_tower)
        self.__domain_names = domain_names
        self.__range = self.calculer_range()
        self.__domaine = Domains(self.__range,  self.__domain_names)
        self.__probleme_definition = ProblemDefinition(self.__domaine, self)

    @property
    def probleme_definition(self):
        return self.__probleme_definition

    def calculer_range(self):
        if (len(self.__domain_names) == 0):
            self.__domain_names = np.array([["Domaine temporaire"]])
            arange = np.zeros((1,2))
            arange[:,1]=1.0
        else:
            arange = np.zeros((self.__nb_total_dimensions,2), dtype=np.float64)
            for current_dimension in range(self.__nb_total_dimensions):
                if current_dimension % 2 == 0:
                    arange[current_dimension,0] = 0
                    arange[current_dimension,1] = self.__tab_parametres[0] #Canvas_width
                else:
                    arange[current_dimension,0] = 0
                    arange[current_dimension,1] = self.__tab_parametres[1] #canvas_height

        return arange


    def __call__(self, solution):

        tableau_tours = []

        outils.create_nb_tower(self.__nb_tiny_towers, TinyTower, tableau_tours )
        outils.create_nb_tower(self.__nb_small_tower, SmallTower, tableau_tours)
        outils.create_nb_tower(self.__nb_medium_tower, MediumTower, tableau_tours)
        outils.create_nb_tower(self.__nb_large_tower, LargeTower, tableau_tours)
        
        for current_index in range(len(tableau_tours)):
            tower = tableau_tours[current_index]
            tower.x += solution[current_index]
            tower.y += solution[current_index+1]

        #Calculate overlapping area between towers
        area_intersection_between_towers = 0
        for i in range(len(tableau_tours)):
            for j in range(len(tableau_tours)-1):
                if i == j:
                    continue

                area_intersection_between_towers += outils.intersection_area(tableau_tours[i], tableau_tours[j])


        #Calcultate total area of coverage by towers
        area_intersection_between_cities_and_towers = 0
        for index_ville in range(len(self.__tab_parametres[3])):
            for index_tour in range(len(tableau_tours)):
                if index_ville == index_tour:
                    continue

                area_intersection_between_cities_and_towers += outils.intersection_area(self.__tab_parametres[3][index_ville], tableau_tours[index_tour])

        #Remove overlapping area in order to not calculate it twice
        if area_intersection_between_cities_and_towers - area_intersection_between_towers > 0:
            area_intersection_between_cities_and_towers-=area_intersection_between_towers

            return area_intersection_between_cities_and_towers
        else:
            return 0 

        #If doesn't enter first condition, there is more overlapping betweens towers than there is total area



        
        
