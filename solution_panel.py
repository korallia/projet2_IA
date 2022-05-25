import abc
import random
import string
from tkinter.messagebox import NO
from turtle import width
from pip import main
from gacvm import Domains, Parameters, ProblemDefinition
from gaapp import QSolutionToSolvePanel
from outils import (Ville, TinyTower, SmallTower, MediumTower, LargeTower)
import outils
from solution import *
import numpy as np

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QObject, Signal, Slot, QSize, QPointF, QRectF
from PySide6.QtWidgets import  (QApplication, QMainWindow, QWidget,
                                QLabel, QScrollBar, QComboBox, QPushButton, QPlainTextEdit, QCheckBox,
                                QGroupBox, QSplitter, QTabWidget,
                                QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QSizePolicy,
                                QMessageBox)
from PySide6.QtGui import  (QImage, QPixmap, QIcon, QPainter, QFont, QPen, QBrush, QColor)
from __feature__ import snake_case, true_property

class SolutionPanel(QSolutionToSolvePanel):
    def __init__(self, name, description, summary):
        super().__init__()
        self.__name = name
        self.__description = description
        self.__summary = summary
        self.__default_parametres = None
        
    @property
    def name(self):
        return self.__name

    @property
    def summary(self):
        return self.__summary

    @property
    def description(self):
        return self.__description

    @property
    def default_parameters(self):
        self.__default_parametres = Parameters()
        return self.__default_parametres


class OpenBoxSolutionPanel(SolutionPanel):
    box_width_changed = Signal(int)
    box_height_changed = Signal(int)

    def __init__(self):
        self.__domain_names = np.array(["Coupe:"])
        self.__problem_name = "Open Box Problem"
        self.__description = "After selecting the width and height of the rectangular surface for which we want to calculate the optimal volume, press START in the control panel to start the genetic algorithm. The AI will return the value of the sides of the squares to cut in each corner of the surface to form the box. The Genetic Algorithm parameters, for this problem, have very little effect on the result, as the AI converges very quickly on an optimal answer."
        self.__summary = "Maximize the total volume that a box formed from a rectangular surface can have."

        super().__init__(self.__problem_name, self.__description, self.__summary)
  
        self.__tab_parametres = []
        self.__default_value = 250
        self.__box_width = self.__default_value
        self.__box_height = self.__default_value
        self.__box_cut = 0
        self.__box_coordinates = []
        self.__canvas_coordinates = [QPointF(0, 0), QPointF(500, 250)]
        
        self.__visualization_label_width = 500
        self.__visualization_label_height = 500
        self.__visualization_pixmap_width = 500
        self.__visualization_pixmap_height = 500

        self.__tab_parametres.append(self.__box_width)
        self.__tab_parametres.append(self.__box_height)
        self.__tab_parametres.append(self.__visualization_pixmap_width)
        self.__tab_parametres.append(self.__visualization_pixmap_height)
        self.__tab_parametres.append(self.__canvas_coordinates)
        self.__tab_parametres.append(self.__box_coordinates)

        self.__main_layout = QHBoxLayout()
        self.__parameters_groupbox = QGroupBox("Parameters")
        self.__parameters_layout = QVBoxLayout()
        self.__width_scrollbar_layout = QHBoxLayout()
        self.__width_text_label = QLabel("Width")
        self.__width_scrollbar = QScrollBar()
        self.__width_value_label = QLabel(f"{self.__box_width}px")
        self.__width_reset_button = QPushButton("!")
        self.__height_scrollbar_layout = QHBoxLayout()
        self.__height_text_label = QLabel("Height")
        self.__height_scrollbar = QScrollBar()
        self.__height_value_label = QLabel(f"{self.__box_height}px")
        self.__height_reset_button = QPushButton("!")

        self.__visualization_groupbox = QGroupBox("Visualization")
        self.__visualization_layout = QVBoxLayout()
        self.__visualization_label = QLabel()
        self.__visualization_pixmap = QPixmap(500, 500)

        self.__width_scrollbar.orientation = Qt.Horizontal
        self.__width_scrollbar.minimum = 1
        self.__width_scrollbar.maximum = self.__visualization_label_width
        self.__width_scrollbar.value = self.__default_value
        self.__height_scrollbar.orientation = Qt.Horizontal
        self.__height_scrollbar.minimum = 1
        self.__height_scrollbar.maximum = self.__visualization_label_height
        self.__height_scrollbar.value = self.__default_value

        self.__visualization_label.set_fixed_size(QSize(self.__visualization_label_width, self.__visualization_label_height))
        self.__visualization_pixmap.scaled(QSize(self.__visualization_pixmap_width, self.__visualization_pixmap_height))
        self.__visualization_label.style_sheet = "border:1px solid black; background-color: #204774"
        self.__visualization_pixmap.fill(QtGui.QColor("lightblue"))
        self.__visualization_label.pixmap = self.__visualization_pixmap

        self.__width_scrollbar.valueChanged.connect(self.__update_problem_parameters)
        self.__height_scrollbar.valueChanged.connect(self.__update_problem_parameters)
        self.__width_scrollbar.valueChanged.connect(self.__generate_box)
        self.__height_scrollbar.valueChanged.connect(self.__generate_box)
        self.__height_reset_button.clicked.connect(self.__reset_height)
        self.__width_reset_button.clicked.connect(self.__reset_width)

        self.__width_scrollbar_layout.add_widget(self.__width_text_label)
        self.__width_scrollbar_layout.add_widget(self.__width_scrollbar)
        self.__width_scrollbar_layout.add_widget(self.__width_value_label)
        self.__width_scrollbar_layout.add_widget(self.__width_reset_button)
        self.__height_scrollbar_layout.add_widget(self.__height_text_label)
        self.__height_scrollbar_layout.add_widget(self.__height_scrollbar)
        self.__height_scrollbar_layout.add_widget(self.__height_value_label)
        self.__height_scrollbar_layout.add_widget(self.__height_reset_button)

        self.__parameters_layout.add_layout(self.__width_scrollbar_layout)
        self.__parameters_layout.add_layout(self.__height_scrollbar_layout)

        self.__parameters_groupbox.set_layout(self.__parameters_layout)
        self.__main_layout.add_widget(self.__parameters_groupbox)

        self.__visualization_layout.add_widget(self.__visualization_label)
        self.__visualization_groupbox.set_layout(self.__visualization_layout)
        self.__main_layout.add_widget(self.__visualization_groupbox)

        self.set_layout(self.__main_layout)
        self.__generate_box()

   
    @property
    def problem_definition(self):
        open_box_solution = OpenBoxSolution(self.__tab_parametres, self.__domain_names)
        return open_box_solution.probleme_definition

    @Slot()
    def __reset_width(self):
        self.__box_width = self.__default_value
        self.__width_scrollbar.value = self.__default_value

    @Slot()
    def __reset_height(self):
        self.__box_height = self.__default_value
        self.__height_scrollbar.value = self.__default_value

    @Slot()
    def __update_problem_parameters(self):
        self.__box_width = self.__width_scrollbar.value
        self.__box_height = self.__height_scrollbar.value
        self.__width_value_label.text = (f"{self.__box_width}px")
        self.__height_value_label.text = (f"{self.__box_height}px")
        self.box_width_changed.emit(self.__box_width)
        self.box_height_changed.emit(self.__box_height)
        self.__tab_parametres[0] = self.__box_width
        self.__tab_parametres[1] = self.__box_height
        self.__visualization_pixmap.fill(QtGui.QColor("lightblue"))

    @Slot()
    def __generate_box(self):
        center = QPointF(self.__visualization_pixmap_width/2, self.__visualization_pixmap_height)
        point_top_left_1 = QPointF(0 + self.__box_cut, 0)
        point_top_left_2 = QPointF(0 + self.__box_cut, 0 + self.__box_cut)
        point_top_left_3 = QPointF(0, 0+self.__box_cut)

        point_bottom_left_1 = QPointF(0, self.__box_height - self.__box_cut)
        point_bottom_left_2 = QPointF(0 + self.__box_cut, self.__box_height - self.__box_cut)
        point_bottom_left_3 = QPointF(0 + self.__box_cut, self.__box_height)

        point_bottom_right_1 = QPointF(self.__box_width - self.__box_cut, self.__box_height)
        point_bottom_right_2 = QPointF(self.__box_width - self.__box_cut, self.__box_height - self.__box_cut)
        point_bottom_right_3 = QPointF(self.__box_width, self.__box_height - self.__box_cut)

        point_top_right_1 = QPointF(self.__box_width, 0 + self.__box_cut)
        point_top_right_2 = QPointF(self.__box_width - self.__box_cut, 0 + self.__box_cut)
        point_top_right_3 = QPointF(self.__box_width - self.__box_cut, 0)

        self.__box_coordinates.append(point_top_left_1)
        self.__box_coordinates.append(point_top_left_2)
        self.__box_coordinates.append(point_top_left_3)

        self.__box_coordinates.append(point_bottom_left_1)
        self.__box_coordinates.append(point_bottom_left_2)
        self.__box_coordinates.append(point_bottom_left_3)

        self.__box_coordinates.append(point_bottom_right_1)
        self.__box_coordinates.append(point_bottom_right_2)
        self.__box_coordinates.append(point_bottom_right_3)

        self.__box_coordinates.append(point_top_right_1)
        self.__box_coordinates.append(point_top_right_2)
        self.__box_coordinates.append(point_top_right_3)

    def _update_from_simulation(self, ga=None):
        if ga:
            self.__box_cut = ga.history.best_solution
            self.__visualization_pixmap.fill(QtGui.QColor("lightblue"))
            self.__generate_box()
        else: 
            pass

    def paint_event(self, event):
        painter = QPainter()
        painter.begin(self.__visualization_pixmap)
        painter.set_brush(QBrush(QColor(0, 80, 115)))
        pen = QPen()
        pen.set_width(1.0)
        pen.set_color = QColor(0, 255, 0)
        painter.set_pen(pen)
        painter.set_render_hint(QPainter.Antialiasing, True)
        box = QPolygonF(self.__box_coordinates)
        box.translate((self.__visualization_pixmap_width - self.__box_width)/2, (self.__visualization_pixmap_height - self.__box_height)/2)

        painter.draw_polygon(box)
        self.__visualization_label.pixmap = self.__visualization_pixmap
        painter.end()
        self.__box_coordinates.clear()

class ShapeTransformationOptimizerSolutionPanel(SolutionPanel):
    def __init__(self ):
        
        self.__domain_names = np.array([["Translation X:"], ["Translation Y:"], ["Rotation:"], ["Scaling:"]])
        self.__problem_name = "Shape Transformation Optimizer"
        self.__problem_description = "After selecting a shape out of the three options, choose the size of the canvas as well as the number of obstacles to place, then press start to let the AI determine which transformations (translation on the X axis, translation on the Y axis, rotation, and scaling) to apply to the shape in order to maximize its area without colliding with the obstacles. To potentially achieve better results, modify the Genetic Algorithm's parameters and/or try the new Mutation strategy, as it will explore more of the surface in search of an optimal result."
        self.__problem_summary = "Determine the transformation needed to be applied to a shape in order to find, without colliding with randomly generated obstacles, its largest possible area."
        
        super().__init__(self.__problem_name, self.__problem_description, self.__problem_summary)

        self.__tab_parametres = []

        self.__visualization_label_width = 700
        self.__visualization_label_height = 500
        self.__visualization_pixmap_width = 700
        self.__visualization_pixmap_height = 500
      
        self.__nb_obstacles = 3
        self.__obstacles_coordinates = []
        self.__obstacles_coordinates_memoire = []
        self.__best_shape_transformation = [0, 0, 0, 0]
        self.__generation = []
        self.__current_shape = []
        self.__current_shape_width = 0
        self.__current_shape_height = 0

        #METTRE POINTS MILIEU À 0
        self.bon_vieux_pentagone = [QPointF(0, -5), QPointF(5, 0), QPointF(5, 5), QPointF(-5, 5) ,QPointF(-5, 0)]
        self.bon_vieux_triangle = [QPointF(-10, -5), QPointF(10, -5), QPointF(0, 5)]
        self.__bon_vieux_rectangle = [QPointF(-10, -5), QPointF(10, -5),QPointF(10, 5), QPointF(-10, 5)]
        self.__canvas_coordinates = [QPointF(0, 0), QPointF(700, 500)] 

        self.__shape_dictionary = {
                                "Bon vieux rectangle": self.__bon_vieux_rectangle,
                                "Bon vieux triangle": self.__bon_vieux_triangle,
                                "Bon vieux pentagone": self.__bon_vieux_pentagone  }
        
        self.__tab_parametres.append(self.__visualization_pixmap_width) 
        self.__tab_parametres.append(self.__visualization_pixmap_height)
        self.__tab_parametres.append(self.__current_shape)
        self.__tab_parametres.append(self.__canvas_coordinates)
        self.__tab_parametres.append(self.__obstacles_coordinates)
        self.__tab_parametres.append(self.__current_shape_width)
        self.__tab_parametres.append(self.__current_shape_height)

        self.__main_layout = QHBoxLayout()
        self.__parameters_groupbox = QGroupBox("Parameters")
        self.__parameters_layout = QVBoxLayout()
        self.__width_scrollbar_layout = QHBoxLayout()
        self.__width_text_label = QLabel("Width")
        self.__width_scrollbar = QScrollBar()
        self.__width_value_label = QLabel(f"{self.__visualization_pixmap_width}px")
        
        self.__height_scrollbar_layout = QHBoxLayout()
        self.__height_text_label = QLabel("Height")
        self.__height_scrollbar = QScrollBar()
        self.__height_value_label = QLabel(f"{self.__visualization_pixmap_height}px")
    
        self.__obstacle_count_scrollbar_layout = QHBoxLayout()
        self.__obstacle_count_scrollbar_text_label = QLabel("Obstacle count")
        self.__obstacle_count_scrollbar = QScrollBar()
        self.__obstacle_count_scrollbar_value = QLabel(f"{self.__nb_obstacles}")
        self.__obstacle_count_scrollbar_reset_button = QPushButton("!")

        self.__generate_obstacles_button = QPushButton("Generate obstacles")

        self.__shape_selection_layout = QHBoxLayout()
        self.__shape_selection_text = QLabel("Shape")
        self.__shape_selection_combobox = QComboBox()

        self.__visualization_groupbox = QGroupBox("Visualization")
        self.__visualization_layout = QVBoxLayout()
        self.__visualization_label = QLabel()
        self.__visualization_pixmap = QPixmap(700, 500)

        self.__width_scrollbar.minimum = 200
        self.__width_scrollbar.maximum = 700
        self.__width_scrollbar.value = self.__visualization_pixmap_width
        self.__width_scrollbar.fixed_width = 50
        self.__height_scrollbar.minimum = 200
        self.__height_scrollbar.maximum = 500
        self.__height_scrollbar.value = self.__visualization_pixmap_height
        self.__height_scrollbar.fixed_width = 50

        self.__width_scrollbar.orientation = Qt.Horizontal
        self.__height_scrollbar.orientation = Qt.Horizontal
        self.__obstacle_count_scrollbar.orientation = Qt.Horizontal
        self.__obstacle_count_scrollbar.maximum = 49

        self.__visualization_label.set_fixed_size(QSize(self.__visualization_label_width, self.__visualization_label_height))
        self.__visualization_pixmap.scaled(QSize(self.__visualization_pixmap_width, self.__visualization_pixmap_height))
        self.__visualization_label.style_sheet = "border:1px solid black; background-color: #204774"
        self.__visualization_pixmap.fill(QtGui.QColor("lightblue"))
        self.__visualization_label.pixmap = self.__visualization_pixmap
        self.__shape_selection_combobox.add_items(self.__shape_dictionary.keys())

        self.__width_scrollbar.valueChanged.connect(self.__update_problem_parameters)
        self.__height_scrollbar.valueChanged.connect(self.__update_problem_parameters)
        self.__obstacle_count_scrollbar.valueChanged.connect(self.__update_problem_parameters)
        self.__obstacle_count_scrollbar_reset_button.clicked.connect(self.__reset_obstacle_count)
        self.__generate_obstacles_button.clicked.connect(self.__generate_random_points)
        self.__shape_selection_combobox.currentTextChanged.connect(self.__update_problem_parameters)

        self.__width_scrollbar_layout.add_widget(self.__width_text_label)
        self.__width_scrollbar_layout.add_widget(self.__width_scrollbar)
        self.__width_scrollbar_layout.add_widget(self.__width_value_label)
        self.__height_scrollbar_layout.add_widget(self.__height_text_label)
        self.__height_scrollbar_layout.add_widget(self.__height_scrollbar)
        self.__height_scrollbar_layout.add_widget(self.__height_value_label)

        self.__obstacle_count_scrollbar_layout.add_widget(self.__obstacle_count_scrollbar_text_label)
        self.__obstacle_count_scrollbar_layout.add_widget(self.__obstacle_count_scrollbar)
        self.__obstacle_count_scrollbar_layout.add_widget(self.__obstacle_count_scrollbar_value)
        self.__obstacle_count_scrollbar_layout.add_widget(self.__obstacle_count_scrollbar_reset_button)

        self.__shape_selection_layout.add_widget(self.__shape_selection_text)
        self.__shape_selection_layout.add_widget(self.__shape_selection_combobox)
        
        self.__parameters_layout.add_stretch()
        self.__parameters_layout.add_layout(self.__width_scrollbar_layout)
        self.__parameters_layout.add_layout(self.__height_scrollbar_layout)
        self.__parameters_layout.add_layout(self.__obstacle_count_scrollbar_layout)
        self.__parameters_layout.add_widget(self.__generate_obstacles_button)
        self.__parameters_layout.add_layout(self.__shape_selection_layout)
        self.__parameters_layout.add_stretch()

        self.__visualization_layout.add_widget(self.__visualization_label)
        
        self.__parameters_groupbox.set_layout(self.__parameters_layout)
        self.__visualization_groupbox.set_layout(self.__visualization_layout)

        self.__main_layout.add_widget(self.__parameters_groupbox)
        self.__main_layout.add_widget(self.__visualization_groupbox)

        self.set_layout(self.__main_layout)


    @property
    def problem_definition(self):
        shape_transformation_solution = ShapeTransformationOptimizerSolution(self.__tab_parametres, self.__domain_names)
        return shape_transformation_solution.probleme_definition

    @Slot()
    def __reset_obstacle_count(self):
        self.__nb_obstacles = 3
        self.__obstacle_count_scrollbar.value = 3

    @Slot()
    def __update_problem_parameters(self):
        self.__visualization_pixmap_width = self.__width_scrollbar.value
        self.__visualization_pixmap_height = self.__height_scrollbar.value
        self.__width_value_label.text = (f"{self.__visualization_pixmap_width}px")
        self.__height_value_label.text = (f"{self.__visualization_pixmap_height}px")
        self.__visualization_pixmap.scaled(QSize(self.__visualization_pixmap_width, self.__visualization_pixmap_height))
        self.__nb_obstacles = self.__obstacle_count_scrollbar.value
        self.__obstacle_count_scrollbar_value.text = (f"{self.__nb_obstacles} obstacles")
        self.__current_shape = self.__shape_dictionary[self.__shape_selection_combobox.current_text]
        self.__find_shape_height_and_width_from_coordinates_and_canvas_coordinates()
        self.__tab_parametres[0] = self.__visualization_pixmap_width
        self.__tab_parametres[1] = self.__visualization_pixmap_height 
        self.__tab_parametres[2] = self.__current_shape
        self.__tab_parametres[3] = self.__canvas_coordinates
        self.__tab_parametres[4] = self.__obstacles_coordinates
        self.__tab_parametres[5] = self.__current_shape_width
        self.__tab_parametres[6] = self.__current_shape_height

    @Slot()
    def __generate_random_points(self):
        self.__obstacles_coordinates.clear()  
        while len(self.__obstacles_coordinates) != self.__nb_obstacles:  
            x = random.randrange(0, self.__visualization_pixmap_width)
            y = random.randrange(0, self.__visualization_pixmap_height)
            new_point = QPointF(x, y)
            
            if new_point in self.__obstacles_coordinates:
                x = random.randint(0, self.__visualization_pixmap_width)
                y = random.randint(0, self.__visualization_pixmap_height)
                new_point = QPointF(x, y)
                self.__obstacles_coordinates.append(new_point)
                
            else:
                self.__obstacles_coordinates.append(new_point)

        self.__tab_parametres[4] = self.__obstacles_coordinates
     

    
    def __find_shape_height_and_width_from_coordinates_and_canvas_coordinates(self):
        self.__canvas_coordinates = [QPointF(0, 0), QPointF( self.__visualization_pixmap_width,  self.__visualization_pixmap_height)]
        
        if len(self.__current_shape) == 3:
            self.__current_shape_width = self.__current_shape[1].x() - self.__current_shape[2].x()
            self.__current_shape_height = self.__current_shape[1].y() - self.__current_shape[0].y()
        elif len(self.__current_shape) == 4:
            self.__current_shape_width = self.__current_shape[2].x() - self.__current_shape[0].x()
            self.__current_shape_height = self.__current_shape[2].y() - self.__current_shape[1].y()
        elif len(self.__current_shape) == 5:
            self.__current_shape_width = self.__current_shape[1].x() - self.__current_shape[4].x()
            self.__current_shape_height = self.__current_shape[2].y() - self.__current_shape[0].y()

    def _update_from_simulation(self, ga=None):
        if ga: 
            self.__best_shape_transformation = ga.history.best_solution
            self.__generation = ga.population
        else: 
            pass


    def paint_event(self, event):

        if len(self.__obstacles_coordinates) != 0:
            painter = QPainter()
            painter.begin(self.__visualization_pixmap)
            painter.set_brush(QBrush(QColor(0, 80, 115)))
            pen = QPen()
            pen.set_width(5.0)
            pen.set_color = QColor(0, 255, 0)

            painter.set_pen(pen)
            painter.set_render_hint(QPainter.Antialiasing,True)
            painter.draw_points(self.__obstacles_coordinates)
            self.__visualization_label.pixmap = self.__visualization_pixmap
            self.__obstacles_coordinates_memoire = self.__obstacles_coordinates
            
            painter.end()

        self.__visualization_pixmap.fill("lightblue")

        painter = QPainter()
        painter.begin(self.__visualization_pixmap)
        painter.set_brush(QBrush(QColor(0, 80, 115)))
        pen = QPen()
        pen.set_width(5.0)
        pen.set_color = QColor(255, 255, 255)

        painter.set_pen(pen)
        painter.set_render_hint(QPainter.Antialiasing, True)
        painter.draw_points(self.__obstacles_coordinates_memoire)

        poly = QPolygonF(self.__current_shape)
        if self.__best_shape_transformation[0] > 0:
            pen.set_width(2.0)
            painter.set_pen(pen)
            for i in self.__generation:
                poly_generation = poly
                qtransform = QTransform()
                qtransform.translate(i[0], i[1])
                qtransform.rotate(i[2])
                qtransform.scale(i[3], i[3])
                poly_transformed = qtransform.map(poly)
                painter.draw_polygon(poly_transformed)
            painter.set_brush(QBrush(QColor(255, 0, 0)))
            painter.set_pen(pen)

            qtransform = QTransform()
            qtransform.translate(self.__best_shape_transformation[0], self.__best_shape_transformation[1])
            qtransform.rotate(self.__best_shape_transformation[2])
            qtransform.scale(self.__best_shape_transformation[3], self.__best_shape_transformation[3])
            poly_transformed = qtransform.map(poly)
            painter.draw_polygon(poly_transformed)

        else:
            painter.draw_polygon(poly)

        painter.end()
        self.__visualization_label.pixmap = self.__visualization_pixmap
            

class CellTowerCoverageOptimizerSolutionPanel(SolutionPanel):
    def __init__(self):
        self.__tab_parametres = []
        self.__total_area = 0
        self.__tableau_tours = [0,0,0,0]
        self.__domain_names = None
        self.define_domain_names(self.__tableau_tours)
        # self.__domain_names = np.array([["Coupe:"], ["Coupe:"],["Coupe:"],["Coupe:"],["Coupe:"],["Coupe:"], ["Coupe:"], ["Coupe:"]])
        self.__nb_total_tours = 0
        self.__problem_name = "Cell Tower Coverage Optimizer"
        self.__description = "After selecting the number of cities that need cell tower coverage, generate them with the GENERATE button, then adjust their X and Y positions, as well as their radius by cycling through them with the combobox. When you are satisfied with the positioning, start the Genetic algorithm by pressing START to witness in real-time as the AI finds the optimal positioning of the towers. A price will be determined which depends on the area that needs to be covered, as well as the coverage offered by differently-sized cell towers and their current market price. To potentially achieve better results, modify the Genetic Algorithm's parameters and/or try the new Mutation strategy, as it will explore more of the surface in search of an optimal result." 
        self.__summary = "Determine the optimal placement of Cell towers in a region in order to offer the neighboring cities access to the wireless network."
        self.__default_parametres = None
        # self.__nb_tiny_towers = 1
        # self.__nb_small_tower = 1
        # self.__nb_medium_tower = 1
        # self.__nb_large_tower = 1
        

        self.__city_coordinates = []



        super().__init__(self.__problem_name, self.__description, self.__summary)

        # self.__city_number = 3
        self.__budget = 0
        self.__map_width = 0
        self.__map_height = 0
        self.__cities = []
        # self.__tab_parametres.append(self.__cities)
        self.__ratio_covered = 0
        self.__total_price = 0
        self.__city_quantity = 0
        

        # self.__nb_de_villes = 0
        # self.__villes = [probleme_3_classe_utilitaire.Ville(100,100,50, "BloopVille"), probleme_3_classe_utilitaire.Ville(250,150,42,"FuckOffCity"), probleme_3_classe_utilitaire.Ville(300,200,75,"Sorel")]


        self.__tab_parametres.append(700)
        self.__tab_parametres.append(500)
        self.__tab_parametres.append(self.__tableau_tours)
        self.__tab_parametres.append(self.__cities)

        self.__visualization_label_width = 500
        self.__visualization_label_height = 500
        self.__visualization_pixmap_width = 500
        self.__visualization_pixmap_height = 500

        self.__canvas_coordinates = [QPointF(0, 0), QPointF(500, 500)]

        # self.__dictonary_form = {"--": None,
        #                          # "Tower 1": self.__tower_one,
        #                          # "Tower 2": self.__tower_two,
        #                          # "Tower 3": self.__tower_tree
        #                          # "Tower 4": self.__tower_tree
        #                          }
        

        #CREATE WIDGIES
        # ADD PARAMETERS WIDGIES
        #SET WIDGIES

        self.__main_layout = QHBoxLayout()

        self.__parameters_groupbox = QGroupBox("Parameters")
        self.__parameters_layout = QVBoxLayout()

        self.__city_quantity_scrollbar_layout = QHBoxLayout()
        self.__city_quantity_text_label = QLabel("Number of city")
        self.__city_quantity_scrollbar = QScrollBar()
        self.__city_quantity_value_label = QLabel()
        self.__generate_cities_button = QPushButton("Generate cities")

        # self.__budget_scrollbar_layout = QHBoxLayout()
        # self.__budget_text_label = QLabel("Budget:")
        # self.__budget_scrollbar = QScrollBar()
        # self.__budget_value_label = QLabel(f"{self.__budget}px")

        # self.__map_width_scrollbar_layout = QHBoxLayout()
        # self.__map_width_text_label = QLabel("Map width")
        # self.__map_width_scrollbar = QScrollBar()
        # self.__map_width_scrollbar_value = QLabel(f"{self.__budget}")
        # self.__map_width_scrollbar_help_button = QPushButton("!")

        # self.__map_height_scrollbar_layout = QHBoxLayout()
        # self.__map_height_text_label = QLabel("Map height")
        # self.__map_height_scrollbar = QScrollBar()
        # self.__map_height_scrollbar_value = QLabel(f"{self.__budget}")
        # self.__map_height_scrollbar_help_button = QPushButton("!")


        self.__city_selection_layout = QHBoxLayout()
        self.__city_selection_text = QLabel("City")
        self.__city_selection_combobox = QComboBox()

        self.__city_quantity_scrollbar.minimum = 0
        self.__city_quantity_scrollbar.maximum = 50
        self.__city_quantity_scrollbar.value = self.__visualization_pixmap_width
        self.__city_quantity_scrollbar.fixed_width = 50

        self.__city_quantity_scrollbar.orientation = Qt.Horizontal

        # self.__budget_scrollbar.minimum = 0
        # self.__budget_scrollbar.maximum = 1000000000
        # self.__budget_scrollbar.value = self.__visualization_pixmap_height
        # self.__budget_scrollbar.fixed_width = 50

        self.__visualization_groupbox = QGroupBox("Visualization")
        self.__visualization_layout = QVBoxLayout()
        self.__visualization_label = QLabel()
        self.__visualization_pixmap = QPixmap(700, 500)

        self.__visualization_label.set_fixed_size(
            QSize(self.__visualization_label_width, self.__visualization_label_height))
        self.__visualization_pixmap.scaled(QSize(self.__visualization_pixmap_width, self.__visualization_pixmap_height))
        self.__visualization_label.style_sheet = "border:1px solid black; background-color: #204774"
        self.__visualization_pixmap.fill(QtGui.QColor("lightblue"))

        self.__visualization_label.pixmap = self.__visualization_pixmap

        
        # self.__budget_scrollbar.orientation = Qt.Horizontal
        # self.__map_width_scrollbar.orientation = Qt.Horizontal
        # self.__map_width_scrollbar.maximum = 50
        # self.__map_height_scrollbar.orientation = Qt.Horizontal
        # self.__map_height_scrollbar.maximum = 50

        self.__city_quantity_scrollbar_layout.add_widget(self.__city_quantity_text_label)
        self.__city_quantity_scrollbar_layout.add_widget(self.__city_quantity_scrollbar)
        self.__city_quantity_scrollbar_layout.add_widget(self.__city_quantity_value_label)

        # self.__budget_scrollbar_layout.add_widget(self.__budget_text_label)
        # self.__budget_scrollbar_layout.add_widget(self.__budget_scrollbar)
        # self.__budget_scrollbar_layout.add_widget(self.__budget_value_label)

        # self.__map_width_scrollbar_layout.add_widget(self.__map_width_text_label)
        # self.__map_width_scrollbar_layout.add_widget(self.__map_width_scrollbar)
        # self.__map_width_scrollbar_layout.add_widget(self.__map_width_scrollbar_value)

        # self.__map_height_scrollbar_layout.add_widget(self.__map_height_text_label)
        # self.__map_height_scrollbar_layout.add_widget(self.__map_height_scrollbar)
        # self.__map_height_scrollbar_layout.add_widget(self.__map_height_scrollbar_value)

        self.__city_selection_layout.add_widget(self.__city_selection_text)
        self.__city_selection_layout.add_widget(self.__city_selection_combobox)

        self.__parameters_layout.add_stretch()
        self.__parameters_layout.add_layout(self.__city_quantity_scrollbar_layout)
        self.__parameters_layout.add_widget(self.__generate_cities_button)
        # self.__parameters_layout.add_layout(self.__budget_scrollbar_layout)
        # self.__parameters_layout.add_layout(self.__map_width_scrollbar_layout)
        # self.__parameters_layout.add_layout(self.__map_height_scrollbar_layout)
        self.__parameters_layout.add_layout(self.__city_selection_layout)
        self.__parameters_layout.add_stretch()

        # City
        self.__city_groupbox = QGroupBox("City")
        self.__city_layout = QVBoxLayout()
        self.__city_name_layout = QHBoxLayout()
        self.__city_x_coordinate_layout = QHBoxLayout()
        self.__city_y_coordinate_layout = QHBoxLayout()
        self.__city_radius_layout = QHBoxLayout()

        self.__city_name_text_label = QLabel()
        self.__city_x_coordinate_text_label = QLabel("X:")
        self.__city_y_coordinate_text_label = QLabel("Y:")
        self.__city_radius_text_label = QLabel("Radius:")

        self.__city_x_coordinate_scrollbar = QScrollBar()
        self.__city_x_coordinate_scrollbar.orientation = Qt.Horizontal
        self.__city_x_coordinate_scrollbar.minimum = 0
        self.__city_x_coordinate_scrollbar.maximum = 500

        self.__city_y_coordinate_scrollbar = QScrollBar()
        self.__city_y_coordinate_scrollbar.orientation = Qt.Horizontal
        self.__city_y_coordinate_scrollbar.minimum = 0
        self.__city_y_coordinate_scrollbar.maximum = 500

        self.__city_radius_scrollbar = QScrollBar()
        self.__city_radius_scrollbar.orientation = Qt.Horizontal
        self.__city_radius_scrollbar.minimum = 0
        self.__city_radius_scrollbar.maximum = 100


        self.__city_x_coordinate_label = QLabel()
        self.__city_y_coordinate_label = QLabel()
        self.__city_radius_label = QLabel()


        # Rename
        self.__rename_city_layout = QHBoxLayout()
        # self.__rename_city_text_edit = QInputDialog()
        # self.__rename_city_text_edit.set_window_title("pipi")

        # self.__rename_city_layout.add_widget(self.__rename_city_text_edit)

        # Rename End

        self.__city_name_layout.add_widget(self.__city_name_text_label)
        self.__city_x_coordinate_layout.add_widget(self.__city_x_coordinate_text_label)
        self.__city_x_coordinate_layout.add_widget(self.__city_x_coordinate_scrollbar)
        self.__city_x_coordinate_layout.add_widget(self.__city_x_coordinate_label)

        self.__city_y_coordinate_layout.add_widget(self.__city_y_coordinate_text_label)
        self.__city_y_coordinate_layout.add_widget(self.__city_y_coordinate_scrollbar)
        self.__city_y_coordinate_layout.add_widget(self.__city_y_coordinate_label)

        self.__city_radius_layout.add_widget(self.__city_radius_text_label)
        self.__city_radius_layout.add_widget(self.__city_radius_scrollbar)
        self.__city_radius_layout.add_widget(self.__city_radius_label)

        self.__city_layout.add_layout(self.__city_name_layout)
        self.__city_layout.add_layout(self.__rename_city_layout)
        self.__city_layout.add_layout(self.__city_x_coordinate_layout)
        self.__city_layout.add_layout(self.__city_y_coordinate_layout)
        self.__city_layout.add_layout(self.__city_radius_layout)


        # City end
        self.__visualization_layout.add_widget(self.__visualization_label)
        self.__parameters_groupbox.set_layout(self.__parameters_layout)
        self.__visualization_groupbox.set_layout(self.__visualization_layout)

        self.__main_layout.add_widget(self.__parameters_groupbox)
        self.__main_layout.add_widget(self.__city_groupbox)
        self.__main_layout.add_widget(self.__visualization_groupbox)
        self.__city_groupbox.set_layout(self.__city_layout)

        self.set_layout(self.__main_layout)

        #Connect
        self.__city_quantity_scrollbar.valueChanged.connect(self.__update_problem_parameters)
        # self.__budget_scrollbar.valueChanged.connect(self.update_scroll)
        # self.__map_width_scrollbar.valueChanged.connect(self.update_scroll)

        self.__generate_cities_button.clicked.connect(self.generate_city_objects)

        self.__city_selection_combobox.currentIndexChanged.connect(self.update_city_selection)
        self.__city_x_coordinate_scrollbar.valueChanged.connect(self.update_scroll_selection)
        self.__city_y_coordinate_scrollbar.valueChanged.connect(self.update_scroll_selection)
        self.__city_radius_scrollbar.valueChanged.connect(self.update_scroll_selection)


        #Connect End
        #self.generate_city_objects()



    @property
    def visualization_pixmap_width(self):
        return self.__visualization_pixmap_width

    @property
    def visualization_pixmap_height(self):
        return self.__visualization_pixmap_height

    @property
    def problem_definition(self):
        # test = self.define_domain_names()
        cell_tower_coverage_optimizer_solution = CellTowerCoverageOptimizerSolution(self.__tab_parametres, self.__domain_names)

        return  cell_tower_coverage_optimizer_solution.probleme_definition

    @Slot()
    def generate_city_objects(self):
        self.__cities.clear()
        for i in range(self.__city_quantity):
            ville = outils.Ville(f"City{i}")
            ville.x = random.randrange(0, self.__visualization_pixmap_width)
            ville.y = random.randrange(0, self.__visualization_pixmap_height)
            ville.radius = random.randrange(0, 50)
            ville.area = pi*(ville.radius**2)
            # new_city = [f"City{i}", random.randrange(0, self.__visualization_pixmap_width), #GENERE X
            #             random.randrange(0, self.__visualization_pixmap_height), 
            #             random.randrange(0, 100)] #RAYON
            self.__cities.append(ville)
        self.fill_city_combobox()
        self.update_city_selection
        self.__tab_parametres[3] = self.__cities
        self.find_total_nb_of_each_tower()
        self.problem_definition

    @Slot()
    def fill_city_combobox(self):
        self.__city_selection_combobox.clear()
        for city in self.__cities:
            self.__city_selection_combobox.add_item(city.nom)
        self.problem_definition

    #À RETOUCHER
    @Slot()
    def __update_problem_parameters(self):
        self.__city_quantity = self.__city_quantity_scrollbar.value
        # self.__budget = self.__budget_scrollbar.value

        self.__city_quantity_value_label.text = (f"{self.__city_quantity}")
        # self.__budget_value_label.text = (f"{self.__budget}$")
        # self.__tab_parametres[0] = self.__city_number
        # self.__tab_parametres[1] = self.__budget
        self.problem_definition



    @Slot()
    def paint_event(self, event):
        # painter = QPainter(self.__visualization_pixmap)
        # painter.set_background(QBrush(QColor(0, 255, 0)))
        self.__visualization_pixmap.fill("lightblue")
        painter = QPainter()

        painter.begin(self.__visualization_pixmap)
        painter.set_brush(QBrush(QColor(0, 255, 0)))
        pen = QPen()
        pen.set_width(1.0)
        pen.set_color = QColor(0, 255, 0)

        painter.set_render_hint(QPainter.Antialiasing, True)

        pen2 = QPen()
        pen2.set_width(10.0)
        pen2.set_color = QColor(0, 255, 0) 

        for city in self.__cities:
            painter.set_pen(pen)
            painter.draw_ellipse(QPointF(city.x, city.y), city.radius, city.radius)
            painter.set_pen(pen2)
            painter.draw_point(QPointF(city.x, city.y))


        painter.set_pen(pen)
        painter.set_render_hint(QPainter.Antialiasing, True)

        self.__visualization_label.pixmap = self.__visualization_pixmap

        painter.end()
        # self.__obstacles_coordinates.clear()
        # self.__visualization_label.pixmap = self.__visualization_pixmap
        

    def rename_city(self):
        pass

    def update_city_selection(self):
        self.__city_name_text_label.text = self.__cities[self.__city_selection_combobox.current_index].nom

        self.__city_x_coordinate_scrollbar.set_value = self.__cities[self.__city_selection_combobox.current_index].x
        self.__city_y_coordinate_scrollbar.set_value = self.__cities[self.__city_selection_combobox.current_index].y
        self.__city_radius_scrollbar.set_value = self.__cities[self.__city_selection_combobox.current_index].radius

        self.__city_x_coordinate_scrollbar.value = self.__cities[self.__city_selection_combobox.current_index].x
        self.__city_y_coordinate_scrollbar.value = self.__cities[self.__city_selection_combobox.current_index].y
        self.__city_radius_scrollbar.value = self.__cities[self.__city_selection_combobox.current_index].radius

        self.__city_x_coordinate_label.text = f"{self.__cities[self.__city_selection_combobox.current_index].x}"
        self.__city_y_coordinate_label.text = f"{self.__cities[self.__city_selection_combobox.current_index].y}"
        self.__city_radius_label.text = f"{self.__cities[self.__city_selection_combobox.current_index].radius}"

    def update_scroll_selection(self):
        
        self.__cities[self.__city_selection_combobox.current_index].x = self.__city_x_coordinate_scrollbar.value
        # self.__cities[self.__city_selection_combobox.current_index][2]  = self.__city_y_coordinate_scrollbar.value
        # self.__cities[self.__city_selection_combobox.current_index][3]  = self.__city_radius_scrollbar.value

        self.__city_x_coordinate_label.text = f"{self.__city_x_coordinate_scrollbar.value}"
        self.__city_y_coordinate_label.text = f"{self.__city_y_coordinate_scrollbar.value}"
        self.__city_radius_label.text = f"{self.__city_radius_scrollbar.value}"
        
        self.__tab_parametres[3] = self.__cities
        self.find_total_nb_of_each_tower()


    def define_domain_names(self, tableau_tour):
        # tableau_tiny_towers = []
        # tableau_small_towers = []
        # tableau_medium_towers = []
        # tableau_large_towers = []
        nb_tours = tableau_tour[0] + tableau_tour[1] + tableau_tour[2] + tableau_tour[3]
        tableau_towers = np.zeros((nb_tours * 2)).astype(str)
        print(tableau_towers)

        for i in range(nb_tours * 2):
            current_tower = int(i/2+1)
            if i < tableau_tour[0] * 2:
                if i % 2 == 0:
                    
                    tableau_towers[i]="Tiny Tower" + str(current_tower) + "Translation X"
                else:
                    tableau_towers[i]=(f"Tiny Tower{str(current_tower)} Translation Y")
            elif i < tableau_tour[0] * 2 + tableau_tour[1] * 2:
                current_tower -= tableau_tour[0]
                if i % 2 == 0:
                    tableau_towers[i]=(f"Small Tower{str(current_tower)} Translation X")
                else:
                    tableau_towers[i]=(f"Small Tower{str(current_tower)} Translation Y")
            elif i < tableau_tour[0] * 2 + tableau_tour[1] * 2 + tableau_tour[2] * 2:
                current_tower -= (tableau_tour[0] + tableau_tour[1])
                if i % 2 == 0:
                    tableau_towers[i]=(f"Medium Tower{str(current_tower)} Translation X")
                else:
                    tableau_towers[i]=(f"Medium Tower{str(current_tower)} Translation Y")
            elif i < tableau_tour[0] * 2 + tableau_tour[1] * 2 + tableau_tour[2] * 2 + tableau_tour[3] * 2:
                current_tower -= (tableau_tour[0] + tableau_tour[1] + tableau_tour[2])
                if i % 2 == 0:
                    tableau_towers[i]=(f"Large Tower{str(current_tower)} Translation X")
                else:
                    tableau_towers[i]=(f"Large Tower{str(current_tower)} Translation Y")

        # for i in range(self.__tableau_tours[1] * 2):
        #     if i % 2 == 0:
        #         tableau_towers.append(f"Small Tower{i+1} Translation X")
        #     else:
        #         tableau_towers.append(f"Small Tower{i+1} Translation Y")
        # for i in range(self.__tableau_tours[2] * 2):
        #     if i % 2 == 0:
        #         tableau_towers.append(f"Medium Tower{i+1} Translation X")
        #     else:
        #         tableau_towers.append(f"Medium Tower{i+1} Translation Y")
        # for i in range(self.__tableau_tours[3] * 2):
        #     if i % 2 == 0:
        #         tableau_towers.append(f"Large Tower{i+1} Translation X")
        #     else:
        #         tableau_towers.append(f"Large Tower{i+1} Translation Y")

        # tableau_towers = [tableau_tiny_towers, tableau_small_towers, tableau_medium_towers, tableau_large_towers]
        # tableau_towers.append(tableau_tiny_towers)
        # tableau_towers.append(tableau_small_towers)
        # tableau_towers.append(tableau_medium_towers)
        # tableau_towers.append(tableau_large_towers)


        self.__domain_names = tableau_towers

    def find_total_area_of_cities(self):
        total_area = 0
        for city in self.__cities:
            total_area += city.area
        return total_area

    def find_total_nb_of_each_tower(self):

        aire_a_couvrir = self.find_total_area_of_cities()
        aire_couverte = 0
        nb_tiny_towers = 1
        nb_small_towers = 0
        nb_medium_towers = 0
        nb_large_towers = 0
        
        while aire_couverte < aire_a_couvrir:
            if aire_a_couvrir-aire_couverte >  outils.LargeTower().area *4 :
                nb_large_towers += 1
                aire_couverte += outils.LargeTower().area
            elif aire_a_couvrir-aire_couverte >  outils.MediumTower().area *3 :
                nb_medium_towers += 1
                aire_couverte += outils.MediumTower().area
            elif  aire_a_couvrir-aire_couverte >  outils.SmallTower().area *2 :
                nb_small_towers += 1
                aire_couverte += outils.SmallTower().area
            else:
                nb_tiny_towers += 1
                aire_couverte += outils.TinyTower().area
        

       
        self.__nb_total_tours = nb_tiny_towers + nb_small_towers + nb_medium_towers + nb_large_towers
        self.__tab_parametres[2] = [nb_tiny_towers,nb_small_towers,nb_medium_towers,nb_large_towers]
        self.define_domain_names(self.__tab_parametres[2])

    def _update_from_simulation(self, ga=None):
        if ga:  # GA est available on est en cours de simulation
            pass
            # print(ga)
            # print(ga.history)
            # print(ga.history.best_solution)
            # for chromosome in ga.population:
            #     #dimension1 = chromosome[0]
            #     pass
            # chromosome = ga.history.best_solution #
        else:  # Pas en simulation (pas de pop)
            pass