"""
Treemap builder using pylab.

Uses algorithm straight from http://hcil.cs.umd.edu/trs/91-03/91-03.html

James Casbon 29/7/2006
"""

import pylab
from matplotlib.patches import Rectangle

def smaller(a,b):
    """return whichever of a and b is inside the other"""
    if a[0] <= b[0] and a[1] >= b[1]:
        return b
    elif a[0] >= b[0] and a[1] <= b[1]:
        return a
    else:
        pass

def is_click_in_area(click, (lower, upper)):
    for dim in range(0,2):
        if click[dim] < lower[dim] or click[dim] > upper[dim]:
            return False
    return True        

class Treemap:
    def __init__(self, tree, iter_method, size_method, color_method, 
                 string_method=str, margin=0.015):
        """create a tree map from tree, using itermethod(node) to walk tree,
        size_method(node) to get object size and color_method(node) to get its 
        color.  Optionally provide a string method called on a node to show 
        which node has been clicked (default str) and a margin (proportion
        in [0,0.5)"""
        self.size_method = size_method
        self.iter_method = iter_method
        self.color_method = color_method
        self.string_method = string_method
        self.areas = {}
        
        self.margin = margin
        
        self.ax = pylab.subplot(111)
        pylab.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.addnode(tree)
        
        pylab.disconnect(pylab.get_current_fig_manager().toolbar._idDrag)
        pylab.connect('motion_notify_event', self.show_node_label)
        pylab.connect('button_press_event', self.zoom_selected)
        
    def addnode(self, node, lower=[0.0,0.0], upper=[1.0,1.0], axis=0):
        axis = axis % 2
        self.draw_rectangle(lower, upper, node, axis)
        self.areas[(tuple(lower), tuple(upper))] = node
        
        (lm, um) = self.add_margins(lower, upper)
        width = um[axis] - lm[axis]
        try:
            for child in self.iter_method(node):
                if self.size_method(child) == 0:
                    continue
                um[axis] = lm[axis] + (width * float(self.size_method(child))) / self.size_method(node)
                
                self.addnode(child, list(lm), list(um), axis + 1)
                lm[axis] = um[axis]
        except TypeError:
            pass
        
    def add_margins(self, lower, upper):
        lower_with_margin = [0,0]
        upper_with_margin = [0,0]
                             
        for dim in [0,1]:
            width = upper[dim] - lower[dim]
            relative_margin = self.margin * width
            assert relative_margin >= 0
            lower_with_margin[dim] = lower[dim] + relative_margin
            upper_with_margin[dim] = upper[dim] - relative_margin
        return (lower_with_margin, upper_with_margin)
        
    def draw_rectangle(self, lower, upper, node, axis):
        r = Rectangle( lower, upper[0]-lower[0], upper[1] - lower[1], 
                   edgecolor='k', 
                   facecolor= self.color_method(node))
        self.ax.add_patch(r)
    
    def get_current_area(self, event):
        click = (event.xdata, event.ydata)
        candidates = [a for a in self.areas if is_click_in_area(click, a)]
        closest_match = reduce(smaller, candidates)
        return closest_match 
    
    def show_node_label(self, event):
        closest_match = self.get_current_area(event)
        label =  self.string_method(self.areas[closest_match])
        pylab.get_current_fig_manager().toolbar.set_message(label)
                
    def zoom_selected(self, event):
        current_area = self.get_current_area(event)
        pylab.get_current_fig_manager().toolbar.push_current()
        pylab.gca().set_xlim(current_area[0][0], current_area[1][0])
        pylab.gca().set_ylim(current_area[0][1], current_area[1][1])
        pylab.get_current_fig_manager().toolbar.draw()
            

if __name__ == '__main__':
    # example using nested lists, iter to walk and random colors
    import operator
    import random
    import pylab
    
    size_cache = {}
    
    def size(thing):
        if isinstance(thing, int) or isinstance(thing, float):
            return thing
        if thing in size_cache:
            return size_cache[thing]
        else:
            size_cache[thing] = reduce(operator.add, [size(x) for x in thing])
            return size_cache[thing]
    
    def random_color(thing):
        return random.random()#colorsys.hsv_to_rgb(0.5, random.random(), 1)
    
    tree= ((5,(3,5,2,(0.1,0.1,0.6),1)), 4, (5,2,(2,3,(3,2, (2,5,2),2)),(3,3)), (3,2,(0.2,0.2,0.2)) )
    
    Treemap(tree, iter, size, random_color, margin=0.01)    

    pylab.show()

