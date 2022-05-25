import abc
import random
from tkinter.messagebox import NO
from turtle import width
from pip import main
from gacvm import Domains, Parameters, ProblemDefinition
from gaapp import QSolutionToSolvePanel
from solution import *
import numpy as np

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QObject, Signal, Slot, QSize, QPointF, QRectF, QSignalBlocker
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
        
    # REDEFINED ABSTRACT METHODS
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
        #Epoch, strategies, etc.
        return self.__default_parametres


class OpenBoxSolutionPanel(SolutionPanel):
    box_width_changed = Signal(int)
    box_height_changed = Signal(int)


    def __init__(self):
        self.__domain_names = np.array(["Coupe:"])
        self.__problem_name = "Open Box Problem"
        self.__description = "Bonne vieille description."
        self.__summary = "Maximize the total volume that a box formed from a rectangular surface can have."
        self.__default_parametres = None

        super().__init__(self.__problem_name, self.__description, self.__summary)
  

        self.__tab_parametres = []

        self.__box_width = 250
        self.__box_height = 250
        self.__box_cut = 0

        self.__visualization_label_width = 500
        self.__visualization_label_height = 500
        self.__visualization_pixmap_width = 500
        self.__visualization_pixmap_height = 500

        self.__box_coordinates = []
        self.__canvas_coordinates = [QPointF(0, 0), QPointF(500, 250)]


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
        self.__width_help_button = QPushButton("!")
        self.__height_scrollbar_layout = QHBoxLayout()
        self.__height_text_label = QLabel("Height")
        self.__height_scrollbar = QScrollBar()
        self.__height_value_label = QLabel(f"{self.__box_height}px")
        self.__height_help_button = QPushButton("!")

        self.__width_scrollbar.orientation = Qt.Horizontal
        self.__width_scrollbar.minimum = 1
        self.__width_scrollbar.maximum = self.__visualization_label_width
        self.__height_scrollbar.orientation = Qt.Horizontal
        self.__height_scrollbar.minimum = 1
        self.__height_scrollbar.maximum = self.__visualization_label_height

        self.__visualization_groupbox = QGroupBox("Visualization")
        self.__visualization_layout = QVBoxLayout()
        self.__visualization_label = QLabel()
        self.__visualization_pixmap = QPixmap(500, 500)

        self.__visualization_label.set_fixed_size(QSize(self.__visualization_label_width, self.__visualization_label_height))
        self.__visualization_pixmap.scaled(QSize(self.__visualization_pixmap_width, self.__visualization_pixmap_height))
        self.__visualization_label.style_sheet = "border:1px solid black; background-color: #204774"
        self.__visualization_pixmap.fill(QtGui.QColor("lightblue"))

        self.__visualization_label.pixmap = self.__visualization_pixmap


        self.__width_scrollbar.valueChanged.connect(self.update_scroll)
        self.__height_scrollbar.valueChanged.connect(self.update_scroll)
        self.__width_scrollbar.valueChanged.connect(self.__generate_box)
        self.__height_scrollbar.valueChanged.connect(self.__generate_box)

        self.__width_scrollbar_layout.add_widget(self.__width_text_label)
        self.__width_scrollbar_layout.add_widget(self.__width_scrollbar)
        self.__width_scrollbar_layout.add_widget(self.__width_value_label)
        self.__width_scrollbar_layout.add_widget(self.__width_help_button)

        self.__height_scrollbar_layout.add_widget(self.__height_text_label)
        self.__height_scrollbar_layout.add_widget(self.__height_scrollbar)
        self.__height_scrollbar_layout.add_widget(self.__height_value_label)
        self.__height_scrollbar_layout.add_widget(self.__height_help_button)



        self.__parameters_layout.add_layout(self.__width_scrollbar_layout)
        self.__parameters_layout.add_layout(self.__height_scrollbar_layout)



        self.__parameters_groupbox.set_layout(self.__parameters_layout)
        self.__main_layout.add_widget(self.__parameters_groupbox)


        self.__visualization_layout.add_widget(self.__visualization_label)
        self.__visualization_groupbox.set_layout(self.__visualization_layout)
        self.__main_layout.add_widget(self.__visualization_groupbox)


        self.set_layout(self.__main_layout)
        self.__generate_box()

        #DOIT D?FINIR LE WIDGET (scrollbars, etc.)

    @Slot()
    def update_scroll(self):
        self.__box_width = self.__width_scrollbar.value
        self.__box_height = self.__height_scrollbar.value
        self.__width_value_label.text = (f"{self.__box_width}px")
        self.__height_value_label.text = (f"{self.__box_height}px")
        self.box_width_changed.emit(self.__box_width)
        self.box_height_changed.emit(self.__box_height)
        # self.open_box_solution.box_width = self.__box_width
        # self.open_box_solution.box_height = self.__box_height
        self.__tab_parametres[0] = self.__box_width
        self.__tab_parametres[1] = self.__box_height
        self.__visualization_pixmap.fill(QtGui.QColor("lightblue"))
        self.__box_cut = 0



    @property
    def box_width(self):
        return self.__box_width

    @property
    def box_height(self):
        return self.__box_height

            
    @property
    def problem_definition(self):
        open_box_solution = OpenBoxSolution(self.__tab_parametres, self.__domain_names)
        return open_box_solution.probleme_definition

    @Slot()
    def __generate_box(self):
        center = QPointF(self.__visualization_pixmap_width/2, self.__visualization_pixmap_height)
        # local
        # x = parentX + math.floor((parentWidth - width) / 2)
        # local
        # y = parentY + math.floor((parentHeight - height) / 2)

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

    def paint_event(self, event):
        painter = QPainter()
        # self.__visualization_pixmap.fill(QtGui.QColor("lightblue"))
        painter.begin(self.__visualization_pixmap)
        painter.set_brush(QBrush(QColor(0, 80, 115)))
        pen = QPen()
        pen.set_width(1.0)
        pen.set_color = QColor(0, 255, 0)
        painter.set_pen(pen)
        painter.set_render_hint(QPainter.Antialiasing, True)
        box = QPolygonF(self.__box_coordinates)
        # x = parentX + math.floor((parentWidth - width) / 2)

        box.translate((self.__visualization_pixmap_width - self.__box_width)/2, (self.__visualization_pixmap_height - self.__box_height)/2)

        painter.draw_polygon(box)
        self.__visualization_label.pixmap = self.__visualization_pixmap
        painter.end()
        self.__box_coordinates.clear()

    def _update_from_simulation(self, ga=None):
        if ga: #GA est available on est en cours de simulation
            self.__box_cut = ga.history.best_solution
            self.__visualization_pixmap.fill(QtGui.QColor("lightblue"))
            self.__generate_box()
            # for chromosome in ga.population:
            #     #dimension1 = chromosome[0]
            #     pass
            # chromosome = ga.history.best_solution #
        else: #Pas en simulation (pas de pop)
            pass
            
class ShapeTransformationOptimizerSolutionPanel(SolutionPanel):
    def __init__(self ):
        
        self.__tab_parametres = []

        self.__default_parametres = None
        self.__domain_names = np.array([["Translation X:"], ["Translation Y:"], ["Rotation:"], ["Scaling:"]])
        self.__problem_name = "Shape Transformation Optimizer"
        self.__problem_description = "Bonne vieille description"
        self.__problem_summary = "Determine the transformation needed to be applied to a shape in order to find, without colliding with randomly generated obstacles, its largest possible area."
        

        super().__init__(self.__problem_name, self.__problem_description, self.__problem_summary)

        self.__visualization_label_width = 700
        self.__visualization_label_height = 500
        self.__visualization_pixmap_width = 700
        self.__visualization_pixmap_height = 500
      
        self.__nb_obstacles = 3
        self.__obstacles_coordinates = []
        self.__obstacles_coordinates_memoire = []
        self.__best_solution = [0, 0, 0, 0]
        self.__generation = []

        self.__current_shape = []
        self.__current_shape_width = 0
        self.__current_shape_height = 0
        self.__bon_vieux_pentagone = [QPointF(100, 0), QPointF(125, 25), QPointF(110, 50), QPointF(90, 50) ,QPointF(75, 25)]
        self.__bon_vieux_triangle = [QPointF(100, 0), QPointF(115, 25), QPointF(55, 25)]
        self.__bon_vieux_rectangle = [QPointF(100, 0), QPointF(150, 0),QPointF(150, 25), QPointF(0, 25)]
        self.__canvas_coordinates = [QPointF(0, 0), QPointF(700, 500)] 

        self.__dictonary_form = {"--": None,
                                "Bon vieux rectangle": self.__bon_vieux_rectangle,
                                "Bon vieux triangle": self.__bon_vieux_triangle,
                                "Bon vieux pentagone": self.__bon_vieux_pentagone  }
        

       
        #Forme qui sera append, viendra d'une property
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
        self.__obstacle_count_scrollbar_help_button = QPushButton("!")

        self.__generate_obstacles_button = QPushButton("Generate obstacles")
        self.__generate_obstacles_button.clicked.connect(self.generate_random_points)


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
        self.__width_scrollbar.valueChanged.connect(self.update_scroll)
        self.__height_scrollbar.valueChanged.connect(self.update_scroll)
        self.__obstacle_count_scrollbar.valueChanged.connect(self.update_scroll)
        


        self.__visualization_label.set_fixed_size(QSize(self.__visualization_label_width, self.__visualization_label_height))
        self.__visualization_pixmap.scaled(QSize(self.__visualization_pixmap_width, self.__visualization_pixmap_height))
        self.__visualization_label.style_sheet = "border:1px solid black; background-color: #204774"
        self.__visualization_pixmap.fill(QtGui.QColor("darkgrey"))

        self.__visualization_label.pixmap = self.__visualization_pixmap


        self.__width_scrollbar.orientation = Qt.Horizontal
        self.__height_scrollbar.orientation = Qt.Horizontal
        self.__obstacle_count_scrollbar.orientation = Qt.Horizontal
        self.__obstacle_count_scrollbar.maximum = 50


        self.__shape_selection_combobox.add_items(self.__dictonary_form.keys())
        self.__shape_selection_combobox.currentTextChanged.connect(self.update_scroll)

        self.__width_scrollbar_layout.add_widget(self.__width_text_label)
        self.__width_scrollbar_layout.add_widget(self.__width_scrollbar)
        self.__width_scrollbar_layout.add_widget(self.__width_value_label)
    
        self.__height_scrollbar_layout.add_widget(self.__height_text_label)
        self.__height_scrollbar_layout.add_widget(self.__height_scrollbar)
        self.__height_scrollbar_layout.add_widget(self.__height_value_label)

        self.__obstacle_count_scrollbar_layout.add_widget(self.__obstacle_count_scrollbar_text_label)
        self.__obstacle_count_scrollbar_layout.add_widget(self.__obstacle_count_scrollbar)
        self.__obstacle_count_scrollbar_layout.add_widget(self.__obstacle_count_scrollbar_value)
        self.__obstacle_count_scrollbar_layout.add_widget(self.__obstacle_count_scrollbar_help_button)

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
        
        


    @Slot()
    def update_scroll(self):
        self.__visualization_pixmap_width = self.__width_scrollbar.value
        self.__visualization_pixmap_height = self.__height_scrollbar.value
        self.__width_value_label.text = (f"{self.__visualization_pixmap_width}px")
        self.__height_value_label.text = (f"{self.__visualization_pixmap_height}px")
        self.__visualization_pixmap.scaled(QSize(self.__visualization_pixmap_width, self.__visualization_pixmap_height))
        self.__nb_obstacles = self.__obstacle_count_scrollbar.value
        # self.generate_random_points
        self.__obstacle_count_scrollbar_value.text = (f"{self.__nb_obstacles} obstacles")
        self.__current_shape = self.__dictonary_form[self.__shape_selection_combobox.current_text]
        self.__find_shape_height_and_width_from_coordinates_and_canvas_coordinates()
        self.__tab_parametres[0] = self.__visualization_pixmap_width
        self.__tab_parametres[1] = self.__visualization_pixmap_height 
        self.__tab_parametres[2] = self.__current_shape
        self.__tab_parametres[3] = self.__canvas_coordinates
        self.__tab_parametres[4] = self.__obstacles_coordinates
        self.__tab_parametres[5] = self.__current_shape_width
        self.__tab_parametres[6] = self.__current_shape_height
        self.problem_definition


    @property
    def visualization_pixmap_width(self):
        return self.__visualization_pixmap_width

    @property
    def visualization_pixmap_height(self):
        return self.__visualization_pixmap_height


    @property
    def problem_definition(self):
        shape_transformation_solution = ShapeTransformationOptimizerSolution(self.__tab_parametres, self.__domain_names)


        return  shape_transformation_solution.probleme_definition

    @Slot()
    def generate_random_points(self):
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
        self.problem_definition           
        # self.update()

    def paint_event(self, event):
        # painter = QPainter(self.__visualization_pixmap)
        # painter.set_background(QBrush(QColor(0, 255, 0)))

        
        if len(self.__obstacles_coordinates) != 0:
            painter = QPainter()
            painter.begin(self.__visualization_pixmap)
            painter.set_brush(QBrush(QColor(0, 255, 0)))
            pen = QPen()
            pen.set_width(5.0)
            pen.set_color = QColor(0, 255, 0)

            painter.set_pen(pen)
            painter.set_render_hint(QPainter.Antialiasing,True)
            painter.draw_points(self.__obstacles_coordinates)
            self.__visualization_label.pixmap = self.__visualization_pixmap
            self.__obstacles_coordinates_memoire = self.__obstacles_coordinates
            
            painter.end()
            # self.__obstacles_coordinates.clear()

        self.__visualization_pixmap.fill("darkgrey")

        painter = QPainter()
        painter.begin(self.__visualization_pixmap)
        pen = QPen()
        pen.set_width(5.0)
        pen.set_color = QColor(255, 255, 255)

        painter.set_pen(pen)
        painter.set_render_hint(QPainter.Antialiasing, True)
        painter.draw_points(self.__obstacles_coordinates_memoire)

        poly = QPolygonF(self.__current_shape)
        if self.__best_solution[0] > 0:
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
            qtransform.translate(self.__best_solution[0], self.__best_solution[1])
            qtransform.rotate(self.__best_solution[2])
            qtransform.scale(self.__best_solution[3], self.__best_solution[3])
            poly_transformed = qtransform.map(poly)
            painter.draw_polygon(poly_transformed)

        else:
            painter.draw_polygon(poly)

        # painter.draw_rect(10, 10, 100, 100)
        # self.__bon_vieux_rectangle = painter.draw_rect(10, 10, 100, 100)
        # self.__bon_vieux_rectangle.translate(100, 50)
        painter.end()
        self.__visualization_label.pixmap = self.__visualization_pixmap
            

        # self.__visualization_label.pixmap = self.__visualization_pixmap

   
        
    def _update_from_simulation(self, ga=None):
        if ga: #GA est available on est en cours de simulation
            self.__best_solution = ga.history.best_solution
            # print(ga)
            self.__generation = ga.population
            # for chromosome in ga.population:
            #     #dimension1 = chromosome[0]
            #     pass
            # chromosome = ga.history.best_solution #
        else: #Pas en simulation (pas de pop)
            pass

class CellTowerCoverageOptimizerSolutionPanel(SolutionPanel):
    def __init__(self):
        self.__domain_names = np.array(["Coupe:"])
        self.__problem_name = "Cell Tower Coverage Optimizer"
        self.__description = "Bonne vieille description."
        self.__summary = "Maximize the total volume that a box formed from a rectangular surface can have."
        self.__default_parametres = None
        self.__city_coordinates = []

        super().__init__(self.__problem_name, self.__description, self.__summary)

        self.__city_number = 1
        self.__budget = 0
        self.__map_width = 0
        self.__map_height = 0
        self.__cities = [["Montréal", 100, 100, 50]]

        #self.__selected_city = self.__cities[0]
        self.__ratio_covered = 0
        self.__total_price = 0

        self.__tab_parametres = []
        self.__tab_parametres.append(self.__city_number)
        self.__tab_parametres.append(self.__budget)
        self.__tab_parametres.append(self.__cities)
        # self.__tab_parametres.append(self.__canvas_coordinates)

        self.__visualization_label_width = 500
        self.__visualization_label_height = 500
        self.__visualization_pixmap_width = 500
        self.__visualization_pixmap_height = 500

        self.__canvas_coordinates = [QPointF(0, 0), QPointF(500, 500)]

        self.__dictonary_form = {"--": None,
                                 # "Tower 1": self.__tower_one,
                                 # "Tower 2": self.__tower_two,
                                 # "Tower 3": self.__tower_tree
                                 # "Tower 4": self.__tower_tree
                                 }

        # self.__tab_parametres.append(self.CEQU'ONVEUTAFFICHERAUDEBUT)

        self.__main_layout = QHBoxLayout()
        self.__parameters_groupbox = QGroupBox("Parameters")
        self.__parameters_layout = QVBoxLayout()

        self.__city_number_scrollbar_layout = QHBoxLayout()
        self.__city_number_text_label = QLabel("Number of city")
        self.__city_number_scrollbar = QScrollBar()
        self.__city_number_value_label = QLabel(f"{self.__city_number} cities")
        self.__generate_cities_button = QPushButton("Generate cities")

        self.__budget_scrollbar_layout = QHBoxLayout()
        self.__budget_text_label = QLabel("Budget:")
        self.__budget_scrollbar = QScrollBar()
        self.__budget_value_label = QLabel(f"{self.__budget}px")

        self.__map_width_scrollbar_layout = QHBoxLayout()
        self.__map_width_text_label = QLabel("Map width")
        self.__map_width_scrollbar = QScrollBar()
        self.__map_width_scrollbar_value = QLabel(f"{self.__budget}")
        self.__map_width_scrollbar_help_button = QPushButton("!")

        self.__map_height_scrollbar_layout = QHBoxLayout()
        self.__map_height_text_label = QLabel("Map height")
        self.__map_height_scrollbar = QScrollBar()
        self.__map_height_scrollbar_value = QLabel(f"{self.__budget}")
        self.__map_height_scrollbar_help_button = QPushButton("!")


        self.__city_selection_layout = QHBoxLayout()
        self.__city_selection_text = QLabel("City")
        self.__city_selection_combobox = QComboBox()

        self.__visualization_groupbox = QGroupBox("Visualization")
        self.__visualization_layout = QVBoxLayout()
        self.__visualization_label = QLabel()
        self.__visualization_pixmap = QPixmap(700, 500)

        self.__city_number_scrollbar.minimum = 1
        self.__city_number_scrollbar.maximum = 50
        self.__city_number_scrollbar.value = self.__visualization_pixmap_width
        self.__city_number_scrollbar.minimum_width = 100
        self.__budget_scrollbar.minimum = 0
        self.__budget_scrollbar.maximum = 1000000000
        self.__budget_scrollbar.value = self.__visualization_pixmap_height
        self.__budget_scrollbar.fixed_width = 50


        self.__visualization_label.set_fixed_size(
            QSize(self.__visualization_label_width, self.__visualization_label_height))
        self.__visualization_pixmap.scaled(QSize(self.__visualization_pixmap_width, self.__visualization_pixmap_height))
        self.__visualization_label.style_sheet = "border:1px solid black; background-color: #204774"
        self.__visualization_pixmap.fill(QtGui.QColor("lightblue"))

        self.__visualization_label.pixmap = self.__visualization_pixmap

        self.__city_number_scrollbar.orientation = Qt.Horizontal
        self.__budget_scrollbar.orientation = Qt.Horizontal
        self.__map_width_scrollbar.orientation = Qt.Horizontal
        self.__map_width_scrollbar.maximum = 50
        self.__map_height_scrollbar.orientation = Qt.Horizontal
        self.__map_height_scrollbar.maximum = 50

        self.__city_number_scrollbar_layout.add_widget(self.__city_number_text_label)
        self.__city_number_scrollbar_layout.add_widget(self.__city_number_scrollbar)
        self.__city_number_scrollbar_layout.add_widget(self.__city_number_value_label)

        self.__budget_scrollbar_layout.add_widget(self.__budget_text_label)
        self.__budget_scrollbar_layout.add_widget(self.__budget_scrollbar)
        self.__budget_scrollbar_layout.add_widget(self.__budget_value_label)

        self.__map_width_scrollbar_layout.add_widget(self.__map_width_text_label)
        self.__map_width_scrollbar_layout.add_widget(self.__map_width_scrollbar)
        self.__map_width_scrollbar_layout.add_widget(self.__map_width_scrollbar_value)

        self.__map_height_scrollbar_layout.add_widget(self.__map_height_text_label)
        self.__map_height_scrollbar_layout.add_widget(self.__map_height_scrollbar)
        self.__map_height_scrollbar_layout.add_widget(self.__map_height_scrollbar_value)

        self.__city_selection_layout.add_widget(self.__city_selection_text)
        self.__city_selection_layout.add_widget(self.__city_selection_combobox)

        self.__parameters_layout.add_stretch()
        self.__parameters_layout.add_layout(self.__city_number_scrollbar_layout)
        self.__parameters_layout.add_widget(self.__generate_cities_button)
        self.__parameters_layout.add_layout(self.__budget_scrollbar_layout)
        self.__parameters_layout.add_layout(self.__map_width_scrollbar_layout)
        self.__parameters_layout.add_layout(self.__map_height_scrollbar_layout)
        self.__parameters_layout.add_layout(self.__city_selection_layout)
        self.__parameters_layout.add_stretch()

        # City

        self.__city_groupbox = QGroupBox("City")
        self.__city_layout = QVBoxLayout()
        self.__city_name_layout = QHBoxLayout()
        self.__city_x_coordinate_layout = QHBoxLayout()
        self.__city_y_coordinate_layout = QHBoxLayout()
        self.__city_radius_layout = QHBoxLayout()

        self.__city_name_text_label = QLabel(f"Name: {self.__get_city_info(0)}")
        self.__city_x_coordinate_text_label = QLabel("X:")
        self.__city_y_coordinate_text_label = QLabel("Y:")
        self.__city_radius_text_label = QLabel("Radius:")

        self.__city_x_coordinate_scrollbar = QScrollBar()
        self.__city_x_coordinate_scrollbar.orientation = Qt.Horizontal
        self.__city_x_coordinate_scrollbar.maximum = 500

        self.__city_y_coordinate_scrollbar = QScrollBar()
        self.__city_y_coordinate_scrollbar.orientation = Qt.Horizontal
        self.__city_y_coordinate_scrollbar.maximum = 500

        self.__city_radius_scrollbar = QScrollBar()
        self.__city_radius_scrollbar.orientation = Qt.Horizontal
        self.__city_radius_scrollbar.maximum = 100
        self.__city_radius_scrollbar.minimum = 1


        self.__city_x_coordinate_label = QLabel(f"{self.__get_city_info(1)}")
        self.__city_y_coordinate_label = QLabel(f"{self.__get_city_info(2)}")
        self.__city_radius_label = QLabel(f"{self.__get_city_info(3)} km")


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
        self.__city_number_scrollbar.valueChanged.connect(self.update_scroll)
        self.__budget_scrollbar.valueChanged.connect(self.update_scroll)
        self.__map_width_scrollbar.valueChanged.connect(self.update_scroll)

        self.__generate_cities_button.clicked.connect(self.generate_city)

        self.__city_selection_combobox.currentIndexChanged.connect(self.update_city_selection)

        self.__city_x_coordinate_scrollbar.valueChanged.connect(self.update_scroll_selection)
        self.__city_y_coordinate_scrollbar.valueChanged.connect(self.update_scroll_selection)
        self.__city_radius_scrollbar.valueChanged.connect(self.update_scroll_selection)

        #Connect End

       #self.__city_x_coordinate_scrollbar.set_value = self.__selected_city[1]
       # self.__city_y_coordinate_scrollbar.set_value = self.__selected_city[2]
        #self.__city_radius_scrollbar.set_value = self.__selected_city[3]
        #self.__city_x_coordinate_scrollbar.value = self.__selected_city[1]
       # self.__city_y_coordinate_scrollbar.value = self.__selected_city[2]
       # self.__city_radius_scrollbar.value = self.__selected_city[3]

    @Slot()
    def generate_city(self):
        self.__cities.clear()
        for i in range(self.__city_number):
            new_city = [f"City{i}", random.randrange(0, self.__visualization_pixmap_width),
                        random.randrange(0, self.__visualization_pixmap_height),
                        random.randrange(1, 100)]
            self.__cities.append(new_city)
        self.populate_city_combobox()

    def rename_city(self):
        pass

    def __get_city_info(self, info):
        return self.__cities[self.__city_selection_combobox.current_index][info]

    def __set_city_info(self, info, value):
        self.__cities[self.__city_selection_combobox.current_index][info] = value

    @Slot()
    def update_city_selection(self):
       # self.__selected_city = self.__cities[self.__city_selection_combobox.current_index]
        self.__city_name_text_label.text = self.__get_city_info(0)
        #self.__city_x_coordinate_scrollbar.set_value = self.__get_city_info(0)
        #Self.__city_y_coordinate_scrollbar.set_value = self.__get_city_info(0)
        #self.__city_radius_scrollbar.set_value = self.__get_city_info(0)
        blocker_x = QSignalBlocker(self.__city_x_coordinate_scrollbar)
        blocker_y = QSignalBlocker(self.__city_y_coordinate_scrollbar)
        blocker_r = QSignalBlocker(self.__city_radius_scrollbar)

        self.__city_x_coordinate_scrollbar.value = self.__get_city_info(1)
        self.__city_y_coordinate_scrollbar.value = self.__get_city_info(2)
        self.__city_radius_scrollbar.value = self.__get_city_info(3)
        blocker_x.unblock()
        blocker_y.unblock()
        blocker_r.unblock()
        self.__city_x_coordinate_label.text = f"{self.__get_city_info(1)}"
        self.__city_y_coordinate_label.text = f"{self.__get_city_info(2)}"
        self.__city_radius_label.text = f"{self.__get_city_info(3)}"

    @Slot()
    def update_scroll_selection(self):

        self.__set_city_info(1, self.__city_x_coordinate_scrollbar.value)
        self.__set_city_info(2, self.__city_y_coordinate_scrollbar.value)
        self.__set_city_info(3, self.__city_radius_scrollbar.value)

        self.__city_x_coordinate_label.text = f"{self.__city_x_coordinate_scrollbar.value}"
        self.__city_y_coordinate_label.text = f"{self.__city_y_coordinate_scrollbar.value}"
        self.__city_radius_label.text = f"{self.__city_radius_scrollbar.value}"


    @Slot()
    def populate_city_combobox(self):
        self.__city_selection_combobox.clear()
        for city in self.__cities:
            self.__city_selection_combobox.add_item(city[0])
        self.update_city_selection()



    @Slot()
    def update_scroll(self):
        self.__city_number = self.__city_number_scrollbar.value
        self.__budget = self.__budget_scrollbar.value

        self.__city_number_value_label.text = (f"{self.__city_number}")
        self.__budget_value_label.text = (f"{self.__budget}$")
        self.__tab_parametres[0] = self.__city_number
        self.__tab_parametres[1] = self.__budget

    @property
    def visualization_pixmap_width(self):
        return self.__visualization_pixmap_width

    @property
    def visualization_pixmap_height(self):
        return self.__visualization_pixmap_height

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
            painter.draw_ellipse(QPointF(city[1], city[2]), city[3], city[3])
            painter.set_pen(pen2)
            painter.draw_point(QPointF(city[1], city[2]))


        painter.set_pen(pen)
        painter.set_render_hint(QPainter.Antialiasing, True)

        self.__visualization_label.pixmap = self.__visualization_pixmap

        painter.end()
        # self.__obstacles_coordinates.clear()
        # self.__visualization_label.pixmap = self.__visualization_pixmap

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
