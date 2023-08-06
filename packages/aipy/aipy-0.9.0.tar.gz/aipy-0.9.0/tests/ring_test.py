import unittest, numpy as n

sqrt2 = n.sqrt(2)
def circ(dim, r, thresh=.4):
    '''Generate a circle of specified radius (r) in pixel
    units.  Determines sub-pixel weighting using adaptive mesh refinement.
    Mesh refinement terminates at pixels whose side length is <= the specified
    threshold (thresh).'''
    x,y = n.indices((dim,dim), dtype=n.float)
    x -= dim/2 ; y -= dim/2
    rin,rout = int(r/sqrt2)-1, int(r)+1
    d1,d2,d3,d4 = dim/2-rout,dim/2-rin,dim/2+rin,dim/2+rout
    # If big circle, start as 1 and set a bounding box to 0.  
    # If small, start as 0 and set a bounded box to 1.
    if r > dim/2:
        rv = n.ones((dim,dim), dtype=n.float)
        rv[d1:d4,d1:d4] = 0
    else:
        rv = n.zeros((dim,dim), dtype=n.float)
        rv[d2:d3,d2:d3] = 1
    # Select 4 rects that contain boundary areas and evaluate them in detail
    for a1,a2,a3,a4 in ((d1,d2,d1,d4), (d3,d4,d1,d4), 
            (d2,d3,d1,d2), (d2,d3,d3,d4)):
        x_, y_ = x[a1:a2,a3:a4], y[a1:a2,a3:a4]
        rs = n.sqrt(x_**2 + y_**2)
        # Get rough answer
        rv_ = (rs <= r).astype(n.float)
        # Fine-tune the answer
        brd = n.argwhere(n.abs(rs.flatten() - r) < 1 / sqrt2).flatten()
        rv_.flat[brd] = _circ(x_.flat[brd], y_.flat[brd], r, 1., thresh)
        # Set rectangle in the actual matrix
        rv[a1:a2,a3:a4] = rv_
    return rv
def _circ(x, y, r, p, thresh):
    # Subdivide into 9 pixels
    p /= 3.
    x0,x1,x2 = x, x+p, x-p
    y0,y1,y2 = y, y+p, y-p
    x = n.array([x0,x0,x0,x1,x1,x1,x2,x2,x2]).flatten()
    y = n.array([y0,y1,y2,y0,y1,y2,y0,y1,y2]).flatten()
    r2 = x**2 + y**2
    # Get the rough answer
    rv = (r2 <= r**2).astype(n.float) * p**2
    # Fine-tune the answer
    if p > thresh:
        brd = n.argwhere(n.abs(n.sqrt(r2) - r) < p / sqrt2).flatten()
        rv[brd] = _circ(x[brd], y[brd], r, p, thresh)
    rv.shape = (9, rv.size / 9)
    rv = rv.sum(axis=0)
    return rv

class TestCirc(unittest.TestCase):
    def testcirc(self):
        for r in range(1, 100, 10):
            c = circ(1000, float(r), thresh=.01)
            self.assertAlmostEqual(c.sum(), n.pi*r**2, 1)
            x = n.random.randint(1000, size=100)
            y = n.random.randint(1000, size=100)
            sample = c[x,y]
            x -= 500; y -= 500
            r2 = x**2 + y**2
            ins = n.where(r2 < (r-1)**2, sample, 1)
            self.assertTrue(n.all(ins == 1))
            outs = n.where(r2 > (r+1)**2, sample, 0)
            self.assertTrue(n.all(outs == 0))
       
if __name__ == '__main__':
    unittest.main() 
