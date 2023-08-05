
import sys
from qt import *
from qtcanvas import *

class MainWindow(QWidget):
    def __init__(self,parent = None,name = None,fl = 0):
        QWidget.__init__(self,parent,name,fl)
        self.box = QVBoxLayout(self)
        self.canvas = QCanvas(self,name)
        self.view = QCanvasView(self)
        self.box.addWidget(self.view)
        self.view.setCanvas(self.canvas)
        painter = QPainter()
        painter.setPen(QColor(1,1,1))
        s = self.size()
        self.canvas.resize(s.width(),s.height())
##        self.image0 = QPixmap()
##        self.image0.loadFromData(image0_data,"PNG")
        if not name:
            self.setCaption("Simulation Display")
            
        # test code
##        self.node1 = Node(self.canvas, pos=(10,10,2))
##        self.node2 = Node(self.canvas,pos=(100,100,2))
##        self.edge = Edge(self.canvas,(10,10,100,100))
        self.map = Map('limites.map',self.canvas)
        self.canvas.update()
        self.view.resize(self.view.sizeHint())
        
class Canvas(QCanvas):
    pass
    
class Node(QCanvasRectangle):
    def __init__(self,canvas,width=50.,height=50., name='Node',pos=(1,1,2),color=(0.,255.,0.)):
        QCanvasRectangle.__init__(self,canvas)
        x,y,z = pos
        r,g,b = color
        painter = QPainter()
        self.setBrush(QBrush(QColor(r,g,b)))
        self.setPen(QPen(Qt.black))
        self.setSize(width,height)
        self.setX(float(x))
        self.setY(float(y))
        self.setZ(float(z))
        self.label = self.setLabel(canvas,name,(x,y-width/2.,z))
        self.label.setText(name)
        #self.drawShape(painter)
        self.show()
    def setLabel(self,canvas,text,pos):
        """
        Set the node label
        """
        x,y,z = pos
        l = QCanvasText(canvas)
        l.setText(text)
        l.setColor(Qt.black)
        l.setFont(QFont('Times',12,50))
        painter = QPainter()
        self.setX(float(x))
        self.setY(float(y))
        self.setZ(float(1))
        l.show()
        return l

class Line(QCanvasLine):
    def __init__(self,canvas, points, color=(0,0,0)):
        QCanvasLine.__init__(self,canvas)
        r,g,b = color
        self.setPen(QPen(QColor(r,g,b),1))
        xa,ya,xb,yb = points
        self.setPoints(xa,ya,xb,yb)
        self.setZ(3)
        self.show()
class Edge(Line):
    pass
class Map:
    """
    Draws maps as poligons
    """
    def __init__(self,fname, canvas):
        #self.display = visual.display(title='Brasil', ambient=0.5)
        self.canvas = canvas
        self.Reader(fname)
        
        
    def Reader(self, fname):
        """
        Reads Grass 5.x ascii vector files.
        """
        f = open(fname,'r')
        all = f.readlines()
        f.close()
        pol = []
        inicioP = [all.index(i) for i in all if i.startswith('B')]
        for i in inicioP:
            size = int(all[i].split()[-1])
            a = [i.split() for i in all[i+1:i+1+size]]
            #print a
            for n,i in enumerate(a[:-1]):
                x1,y1,x2,y2 = float(i[1]),float(i[0]),float(a[n+1][1]),float(a[n+1][0])
                Line(self.canvas,(850+10*x1,-10*y1+50,850+10*x2,-10*y2+50))
            #self.dbound(pta) #Draws the polygon
        self.canvas.update()
            
    def dbound(self,pol):
        """
        Draws a polygon
        pol: list of points forming the polygon
        canvas: Canvas where it'll be drawn
        """
        P = QCanvasPolygon(self.canvas)
        P.setPen(QPen(Qt.black,10))
        P.setPoints(pol)
        P.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    QObject.connect(app,SIGNAL("lastWindowClosed()"),app,SLOT("quit()"))
    w = MainWindow()
    app.setMainWidget(w)
    w.show()
    app.exec_loop()
