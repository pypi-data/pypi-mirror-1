#Copyright (c) 2007 Simon Wittber
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in
#all copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.


class Rect(object):
    """
    The Rect class is used for storing and manipulating rectangular areas.

    It has left, bottom, width and height attributes, which are automatically
    changed by assignment to the right, top, topleft, topright, bottomleft, 
    bottomright or center properties.

    Rects can be added to greater a greater containing rectangle, or a 
    Rect.union classmethod is available to sum a list of Rect objects.

    The collidepoint and intersects methods are used for collision testing.

    Eg:
    >> Rect((0,0,10,10)).collidepoint((2,2))
    >> True
    >> Rect((0,0,10,10)).collidepoint((20,20))
    >> False

    This Rect class is different to the Pygame Rect class, in that is stores
    coordinates internally as floats, and uses a left-handed coordinate
    system.


    """
    def __init__(self, xywh):
        """
        xywh must be a 4 tuple or a rect instance.
        """
        if isinstance(xywh, Rect):
            self.left = xywh.left
            self.bottom = xywh.bottom
            self.width = xywh.width
            self.height = xywh.height
        else:
            self.left, self.bottom, self.width, self.height = (float(i) for i in xywh)

    def __repr__(self):
        return "%s((%s,%s,%s,%s))" % (self.__class__.__name__, self.left, self.bottom, self.width, self.height)

    def __iter__(self):
        return (i for i in (self.left, self.bottom, self.width, self.height))

    def set_top(self, s):
        self.bottom = s - self.height
    def get_top(self):
        return self.bottom + self.height
    top = property(get_top, set_top)

    def set_right(self, s):
        self.left = s - self.width
    def get_right(self):
        return self.left + self.width
    right = property(get_right, set_right)

    def set_center(self, xy):
        self.left = xy[0] - (self.width*0.5)
        self.bottom = xy[1] - (self.height*0.5)
    def get_center(self):
        return self.left + (self.width*0.5), self.bottom + (self.height*0.5)
    center = property(get_center, set_center)

    def set_topleft(self, xy):
        self.left = xy[0]
        self.top = xy[1]
    def get_topleft(self):
        return self.top, self.left
    topleft = property(get_topleft, set_topleft)

    def set_topright(self, xy):
        self.right = xy[0]
        self.top = xy[1]
    def get_topright(self):
        return self.top, self.right
    topright = property(get_topright, set_topright)

    def set_bottomright(self, xy):
        self.right = xy[0]
        self.bottom = xy[1]
    def get_bottomright(self):
        return self.bottom, self.right
    bottomright = property(get_bottomright, set_bottomright)

    def set_bottomleft(self, xy):
        self.left= xy[0]
        self.bottom = xy[1]
    def get_bottomleft(self):
        return self.bottom, self.left
    bottomleft = property(get_bottomleft, set_bottomleft)

    def __add__(self, other):
        left = min(self.left, other.left)
        bottom = min(self.bottom, other.bottom)
        right = max(self.right, other.right)
        top = max(self.top, other.top)
        return Rect((left, bottom, right-left, top-bottom))

    def add(self, other):
        """
        Add another rect to this rect, expanding as needed.
        """
        self.left = min(self.left, other.left)
        self.bottom = min(self.bottom, other.bottom)
        self.width = max(self.right, other.right) - self.left
        self.height = max(self.top, other.top) - self.bottom

    @classmethod
    def union(cls, others):
        """
        Return a rect which covers all rects in others.
        """
        others = list(others)
        left, bottom, width, height = others.pop()
        right = left + width
        top = bottom + height
        for other in others:
            if other.left < left: left = other.left
            if other.bottom < bottom: bottom = other.bottom
            if other.right > right: right = other.right
            if other.top > top: top = other.top
        return cls((left, bottom, right-left, top-bottom))

    def collidepoint(self, xy):
        """
        Test if a point intersects with this rect.
        """
        x,y = xy
        return x >= self.left and x <= (self.left + self.width) and y >= self.bottom and y <= (self.bottom + self.height)

    def intersects(self, other):
        """
        Test if a rect intersects with this rect.
        """
        if other.bottom <= self.top and other.top >= self.bottom:
            if other.right >= self.left and other.left <= self.right:
                return True
        return False






