"""Transfer Functions Plotter

This package implements a Plotter of Transfer functions with PID
controllers simulation, based on module 'controlsystems' package.

To run this application you'll need the package matplotlib, built with
QT4 support, and the dependencies.

    $ tf-plotter

If you need some help with the use, or can help with the development,
please contact the author via email or visit our project website:

http://pycontrolsystems.com/

All the help is welcome! :)

"""

#TODO: include tf-plotter.desktop
#TODO: improve the documentation

__all__ = ['tfPlotter']

__author__ = 'Rafael Goncalves Martins'
__email__ = 'rafael@rafaelmartins.com'

__description__ = 'A Plotter of Transfer functions with PID controller'\
    ' simulation.'
__url__ = 'http://pycontrolsystems.com/'
__copyright__ = '(c) 2009 %s' % __author__
__license__ = 'GPLv2'

__version__ = '1.0rc1'
__status__ = 'Beta'


from sys import prefix
from os.path import exists, dirname

from PyQt4 import QtCore, QtGui
from plotter_ui import Ui_Plotter

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from controlsystems.types import *
from controlsystems.discretization import *
from controlsystems.pid_simulation import *
from controlsystems.error import *

from controlsystems import __description__ as desc

class GuiError(Exception):
    
    def __init__(self, parent, e):
        QtGui.QMessageBox.critical(
            parent,
            'Error',
            "An error was occurred: %s" % e
        )


class tfPlotter(QtGui.QMainWindow):
    
    def __init__(self, parent=None):

        QtGui.QMainWindow.__init__(self, parent)

        self.ui = Ui_Plotter()
        self.ui.setupUi(self)
        
        #icon stuff
        icon_path = ''
        if exists('%s/share/pixmaps/cartesian.png' % prefix):
            icon_path = '%s/share/pixmaps/cartesian.png' % prefix
        elif exists('%s/../../icons/cartesian.png' % dirname(__file__)):
            icon_path = '%s/../../icons/cartesian.png' \
                % dirname(__file__)
        if icon_path != '':
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal,\
                QtGui.QIcon.Off)
            self.setWindowIcon(icon)
        
        geom = self.ui.graph.geometry()
        
        self.fig = Figure()
        self.ui.graph = FigureCanvas(self.fig)
        self.ui.graph.setGeometry(geom)
        self.ui.graph.setParent(self.ui.centralwidget)
        
        self.axes = self.fig.add_subplot(111)
        
        QtCore.QObject.connect(self.ui.plot, QtCore.SIGNAL("clicked()"),\
            self.draw)
        QtCore.QObject.connect(self.ui.grid,\
            QtCore.SIGNAL("stateChanged(int)"), self.toggle_grid)
        QtCore.QObject.connect(self.ui.actionSave,\
            QtCore.SIGNAL("triggered()"), self.save_plot)
        QtCore.QObject.connect(self.ui.actionAbout_TFP,\
            QtCore.SIGNAL("triggered()"), self.about_tfp)
        QtCore.QObject.connect(self.ui.actionAbout_PCS,\
            QtCore.SIGNAL("triggered()"), self.about_pcs)
        QtCore.QObject.connect(self.ui.actionAbout_QT,\
            QtCore.SIGNAL("triggered()"), self.about_qt)
        QtCore.QObject.connect(self.ui.PID,\
            QtCore.SIGNAL("toggled(bool)"), self.toggle_input)
        QtCore.QObject.connect(self.ui.t_method,\
            QtCore.SIGNAL("currentIndexChanged(int)"), self.toggle_tmethod)
        
        self.toggle_tmethod()
        
    def draw(self):
        
        self.axes.clear()
        
        g = self.__get_tf().simplify()
        
        if self.ui.sample_time.text().isEmpty():
            raise GuiError(self, 'You need to specify a Sample Time')
        if self.ui.sim_time.text().isEmpty():
            raise GuiError(self, 'You need to specify a Simulation Time')
                
        sample_time = self.ui.sample_time.value()
        sim_time = self.ui.sim_time.value()
        
        if (sim_time/sample_time) > 10000:
            
            reply = QtGui.QMessageBox.question(
                self,
                'Alert',
                'Your sample time is much smaller than your simulation '\
                    'time. Continue?',
                QtGui.QMessageBox.Yes,
                QtGui.QMessageBox.No
            )
            
            if reply == QtGui.QMessageBox.No:
                return
        
        method = self.__get_nmethod()
        
        if self.ui.PID.isChecked():
            
            t_method = self.__get_tmethod()
            
            if t_method != None:
                # do PID controller tuning
                
                try:
                    kp, ki, kd = t_method(g, sample_time, sim_time,\
                        method)
                except ZeroDivisionError:
                    raise GuiError(self, 'Invalid "Ziegler-Nichols" '\
                        'parameters')
            
                self.ui.kp.setValue(kp)
                self.ui.ki.setValue(ki)
                self.ui.kd.setValue(kd)
            
            else:
                kp = self.ui.kp.value()
                ki = self.ui.ki.value()
                kd = self.ui.kd.value()
            
            if self.ui.pid_action.currentIndex() == 0:
                g_ = TransferFunction([kd, kp, ki], [1, 0])
            elif self.ui.pid_action.currentIndex() == 1:
                g_ = TransferFunction([kp], [1])
            elif self.ui.pid_action.currentIndex() == 2:
                g_ = TransferFunction([ki], [1, 0])
            else:
                g_ = TransferFunction([kd, 0, 0], [1, 0])
            
            my_g = (g_ * g).feedback_unit()
                    
        if self.ui.ramp.isChecked():
            aux = g * TransferFunction([1], [1,0])
        elif self.ui.parabola.isChecked():
            aux = g * TransferFunction([1], [1,0,0])
        else:
            aux = g
        
        try:
            t, y = method(aux, sample_time, sim_time)
            if self.ui.PID.isChecked():
                t1, y1 = method(my_g, sample_time, sim_time)
        except ControlSystemsError, e:
            raise GuiError(self, e)
        
        if self.ui.PID.isChecked():
            y_range = (max([max(y), max(y1)]) - min([min(y), min(y1)]))\
                * 0.1
        else:
            y_range = (max(y) - min(y)) * 0.1
        
        if self.ui.PID.isChecked():
            self.axes.plot(t, y, t1, y1)
        else:
            self.axes.plot(t, y)
        
        if self.ui.PID.isChecked():
            self.axes.axis([0, sim_time, min([min(y), min(y1)])-y_range,\
                max([max(y), max(y1)])+y_range])
        else:
            self.axes.axis([0, sim_time, min(y)-y_range, max(y)+y_range])
        
        self.axes.grid(self.ui.grid.isChecked())
        self.ui.graph.draw()

    def toggle_grid(self):
        
        self.axes.grid(self.ui.grid.isChecked())
        self.ui.graph.draw()
    
    def toggle_input(self):
        
        if self.ui.PID.isChecked():
            self.ui.step.setChecked(True)
        
        self.ui.input_box.setEnabled(not self.ui.PID.isChecked())
    
    def toggle_tmethod(self):
        
        if self.ui.PID.isChecked():
            self.ui.gains.setEnabled(self.ui.t_method.currentIndex() == 0)
    
    def save_plot(self):
        
        path = QtGui.QFileDialog.getSaveFileName(
            self, 
            'Save file',
            '', 
            'Images (*.png *.eps)'
        )
        
        if path:
            try:
                self.ui.graph.print_figure(str(path))
            except:
                raise GuiError(self, 'Failed to save: %s' % path)

    def __get_tf(self):
        
        num_ = self.ui.tf_num.text()
        den_ = self.ui.tf_den.text()
        
        num = self.__str2list(num_)
        den = self.__str2list(den_)
        
        if len(num) == 0 or len(den) == 0:
            raise GuiError(self, 'Invalid Transfer Function.')
        
        return TransferFunction(num, den)
    
    def __str2list(self, str):
        
        lst = str.split(' ')
        
        aux = []
        
        for coeff in lst:
            
            if coeff != '':
                aux_, ok = coeff.toFloat()
                if ok:
                    aux.append(aux_)
                else:
                    raise GuiError(self, 'Invalid coeficients of the '\
                        'Transfer Function')
        
        return aux

    def __get_nmethod(self):
        
        if self.ui.n_method.currentIndex() == 0:
            return Euler
        if self.ui.n_method.currentIndex() == 1:
            return RK2
        if self.ui.n_method.currentIndex() == 2:
            return RK3
        return RK4

    def __get_tmethod(self):
        
        if self.ui.t_method.currentIndex() == 1:
            return ZieglerNichols
        if self.ui.t_method.currentIndex() == 2:
            return CohenCoon
        if self.ui.t_method.currentIndex() == 3:
            return ChienHronesReswick0
        if self.ui.t_method.currentIndex() == 4:
            return ChienHronesReswick20
        return None
        

    def about_tfp(self):
        
        QtGui.QMessageBox.about(
            self,
            'About Transfer Functions Plotter',
            '"Transfer Functions Plotter" is a simple and easy to use '\
            'tool to plot transfer functions responses for some sources '\
            '(step, ramp, parabola) using some numerical methods (Euler,'\
            ' RK2, RK3, RK4), and simulates an PID controller, using '\
            'tuning methods (Manual, Ziegler-Nichols, Cohen-Coon, '\
            'Chien-Hrones-Reswick 0%, Chien-Hrones-Reswick 20%).'
        )
    
    def about_pcs(self):
        
        QtGui.QMessageBox.about(
            self,
            'About Python Control Systems',
            desc
        )

    def about_qt(self):
        
        QtGui.QMessageBox.aboutQt(self)
