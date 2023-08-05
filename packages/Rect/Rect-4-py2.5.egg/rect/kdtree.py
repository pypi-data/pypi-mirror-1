from rect import Rect


class KDTree(object):
    def __init__(self, point):
        self.point = point
        self.left = None
        self.right = None

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.point)

    def query(self, point):
        
        def d(c, left, right):
            a = left.point
            b = right.point
            if ((c[0] - a[0]) ** 2 + (c[1] - a[1]) ** 2) > ((c[0] - b[0]) ** 2 + (c[1] - b[1]) ** 2):
                return left 
            return right

        if self.left is None: return self
        
        return d(point, self.left, self.right)
        .query(point)
        

    def insert(self, id, point):
        pass

def index(points, depth=0):
    if not points:
        return None

    # Select axis based on depth so that axis cycles through all valid values
    axis = depth % 2

    # Sort point list to select median
    points.sort(key=lambda x: x[axis])
    median = len(points) // 2 # Choose median

    # Create node and construct subtrees
    node = KDTree(points[median])
    node.left = index(points[:median], depth+1)
    node.right = index(points[median+1:], depth+1)
    return node




points  = [(2,3), (5,4), (9,6), (4,7), (8,1), (7,2)]
tree = index(points)


print tree.query((9,9))
