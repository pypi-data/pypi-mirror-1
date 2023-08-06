import unittest, ephem, random
import aipy._img as _img, numpy as n

class TestPut(unittest.TestCase):
    def testsanitychecks(self):
        u = n.zeros(100, dtype=n.float)
        v = n.zeros(100, dtype=n.float)
        w = n.zeros(100, dtype=n.float)
        for dtype in [n.double, n.complex]:
            data = n.zeros(100, dtype=dtype)
            wgt = n.zeros(100, dtype=dtype)
            uv = n.zeros((100,100), dtype=dtype)
            bm = n.zeros((100,100), dtype=dtype)
            # Check that a well-formed call works
            self.assertEqual(_img.put(uv, bm, u, v, w, data, wgt), None)
            # Check typechecks of uv,bm,data,wgt
            for bad_dtype in [n.int, n.double, n.complex]:
                if bad_dtype == dtype: continue
                b_uv = uv.astype(bad_dtype)
                b_bm = bm.astype(bad_dtype)
                b_data = data.astype(bad_dtype)
                b_wgt = wgt.astype(bad_dtype)
                self.assertRaises(ValueError,
                    lambda: _img.put(b_uv,bm,u,v,w,data,wgt))
                self.assertRaises(ValueError,
                    lambda: _img.put(uv,b_bm,u,v,w,data,wgt))
                self.assertRaises(ValueError,
                    lambda: _img.put(uv,bm,u,v,w,b_data,wgt))
                self.assertRaises(ValueError,
                    lambda: _img.put(uv,bm,u,v,w,data,b_wgt))
            # Check typechecks of u,v,w
            self.assertRaises(ValueError,
                lambda: _img.put(uv,bm,u.astype(n.long),v,w,data,wgt))
            self.assertRaises(ValueError,
                lambda: _img.put(uv,bm,u,v.astype(n.complex),w,data,wgt))
            self.assertRaises(ValueError,
                lambda: _img.put(uv,bm,u,v,w.astype(n.int),data,wgt))
            # Check shape-checks
            self.assertRaises(ValueError,
                lambda: _img.put(uv.flatten(),bm,u,v,w,data,wgt))
            self.assertRaises(ValueError,
                lambda: _img.put(uv,bm.flatten(),u,v,w,data,wgt))
            self.assertRaises(ValueError,
                lambda: _img.put(uv,bm,n.reshape(u,(10,10)),v,w,data,wgt))
            self.assertRaises(ValueError,
                lambda: _img.put(uv,bm,u,n.reshape(v,(1,10,10)),w,data,wgt))
            self.assertRaises(ValueError,
                lambda: _img.put(uv,bm,u,v,n.reshape(w,(10,10)),data,wgt))
            self.assertRaises(ValueError,
                lambda: _img.put(uv,bm,u,v,w,n.reshape(data,(10,10)),wgt))
            self.assertRaises(ValueError,
                lambda: _img.put(uv,bm,u,v,w,data,n.reshape(wgt,(10,10))))

if __name__ == '__main__':
    unittest.main()
