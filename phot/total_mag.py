#!/usr/bin/env python

# really dangerous blind way to fit asymptotic mag

import sys,os
try:
  import numpy.numarray as numarray
except:
  import numarray
import operator, math, random
NPRE, NPOST = 0, 0                    # Disables pre and post condition checks

def iszero(z):  return abs(z) < .000001
def getreal(z):
    try:
        return z.real
    except AttributeError:
        return z
def getimag(z):
    try:
        return z.imag
    except AttributeError:
        return 0
def getconj(z):
    try:
        return z.conjugate()
    except AttributeError:
        return z

separator = [ '', '\t', '\n', '\n----------\n', '\n===========\n' ]

class Table(list):
    dim = 1
    concat = list.__add__      # A substitute for the overridden __add__ method
    def __getslice__( self, i, j ):
        return self.__class__( list.__getslice__(self,i,j) )
    def __init__( self, elems ):
        list.__init__( self, elems )
        if len(elems) and hasattr(elems[0], 'dim'): self.dim = elems[0].dim + 1
    def __str__( self ):
        return separator[self.dim].join( map(str, self) )
    def map( self, op, rhs=None ):
        '''Apply a unary operator to every element in the matrix or a binary operator to corresponding
        elements in two arrays.  If the dimensions are different, broadcast the smaller dimension over
        the larger (i.e. match a scalar to every element in a vector or a vector to a matrix).'''
        if rhs is None:                                                 # Unary case
            return self.dim==1 and self.__class__( map(op, self) ) or self.__class__( [elem.map(op) for elem in self] )
        elif not hasattr(rhs,'dim'):                                    # List / Scalar op
            return self.__class__( [op(e,rhs) for e in self] )
        elif self.dim == rhs.dim:                                       # Same level Vec / Vec or Matrix / Matrix
            assert NPRE or len(self) == len(rhs), 'Table operation requires len sizes to agree'
            return self.__class__( map(op, self, rhs) )
        elif self.dim < rhs.dim:                                        # Vec / Matrix
            return self.__class__( [op(self,e) for e in rhs]  )
        return self.__class__( [op(e,rhs) for e in self] )         # Matrix / Vec
    def __mul__( self, rhs ):  return self.map( operator.mul, rhs )
    def __div__( self, rhs ):  return self.map( operator.div, rhs )
    def __sub__( self, rhs ):  return self.map( operator.sub, rhs )
    def __add__( self, rhs ):  return self.map( operator.add, rhs )
    def __rmul__( self, lhs ):  return self*lhs
    def __rdiv__( self, lhs ):  return self*(1.0/lhs)
    def __rsub__( self, lhs ):  return -(self-lhs)
    def __radd__( self, lhs ):  return self+lhs
    def __abs__( self ): return self.map( abs )
    def __neg__( self ): return self.map( operator.neg )
    def conjugate( self ): return self.map( getconj )
    def real( self ): return self.map( getreal  )
    def imag( self ): return self.map( getimag )
    def flatten( self ):
        if self.dim == 1: return self
        return reduce( lambda cum, e: e.flatten().concat(cum), self, [] )
    def prod( self ):  return reduce(operator.mul, self.flatten(), 1.0)
    def sum( self ):  return reduce(operator.add, self.flatten(), 0.0)
    def exists( self, predicate ):
        for elem in self.flatten():
            if predicate(elem):
                return 1
        return 0
    def forall( self, predicate ):
        for elem in self.flatten():
            if not predicate(elem):
                return 0
        return 1
    def __eq__( self, rhs ):  return (self - rhs).forall( iszero )

class Vec(Table):
    def dot( self, otherVec ):  return reduce(operator.add, map(operator.mul, self, otherVec), 0.0)
    def norm( self ):  return math.sqrt(abs( self.dot(self.conjugate()) ))
    def normalize( self ):  return self / self.norm()
    def outer( self, otherVec ):  return Mat([otherVec*x for x in self])
    def cross( self, otherVec ):
        'Compute a Vector or Cross Product with another vector'
        assert len(self) == len(otherVec) == 3, 'Cross product only defined for 3-D vectors'
        u, v = self, otherVec
        return Vec([ u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0] ])
    def house( self, index ):
        'Compute a Householder vector which zeroes all but the index element after a reflection'
        v = Vec( Table([0]*index).concat(self[index:]) ).normalize()
        t = v[index]
        sigma = 1.0 - t**2
        if sigma != 0.0:
            t = v[index] = t<=0 and t-1.0 or -sigma / (t + 1.0)
            v /= t
        return v, 2.0 * t**2 / (sigma + t**2)
    def polyval( self, x ):
        'Vec([6,3,4]).polyval(5) evaluates to 6*x**2 + 3*x + 4 at x=5'
        return reduce( lambda cum,c: cum*x+c, self, 0.0 )
    def ratval( self, x ):
        'Vec([10,20,30,40,50]).ratfit(5) evaluates to (10*x**2 + 20*x + 30) / (40*x**2 + 50*x + 1) at x=5.'
        degree = len(self) / 2
        num, den = self[:degree+1], self[degree+1:] + [1]
        return num.polyval(x) / den.polyval(x)

class Matrix(Table):
    __slots__ = ['size', 'rows', 'cols']
    def __init__( self, elems ):
        'Form a matrix from a list of lists or a list of Vecs'
        Table.__init__( self, hasattr(elems[0], 'dot') and elems or map(Vec,map(tuple,elems)) )
        self.size = self.rows, self.cols = len(elems), len(elems[0])
    def tr( self ):
        'Tranpose elements so that Transposed[i][j] = Original[j][i]'
        return Mat(zip(*self))
    def star( self ):
        'Return the Hermetian adjoint so that Star[i][j] = Original[j][i].conjugate()'
        return self.tr().conjugate()
    def diag( self ):
        'Return a vector composed of elements on the matrix diagonal'
        return Vec( [self[i][i] for i in range(min(self.size))] )
    def trace( self ): return self.diag().sum()
    def mmul( self, other ):
        'Matrix multiply by another matrix or a column vector '
        if other.dim==2: return Mat( map(self.mmul, other.tr()) ).tr()
        assert NPRE or self.cols == len(other)
        return Vec( map(other.dot, self) )
    def augment( self, otherMat ):
        'Make a new matrix with the two original matrices laid side by side'
        assert self.rows == otherMat.rows, 'Size mismatch: %s * %s' % (`self.size`, `otherMat.size`)
        return Mat( map(Table.concat, self, otherMat) )
    def qr( self, ROnly=0 ):
        'QR decomposition using Householder reflections: Q*R==self, Q.tr()*Q==I(n), R upper triangular'
        R = self
        m, n = R.size
        for i in range(min(m,n)):
            v, beta = R.tr()[i].house(i)
            R -= v.outer( R.tr().mmul(v)*beta )
        for i in range(1,min(n,m)): R[i][:i] = [0] * i
        R = Mat(R[:n])
        if ROnly: return R
        Q = R.tr().solve(self.tr()).tr()       # Rt Qt = At    nn  nm  = nm
        self.qr = lambda r=0, c=`self`: not r and c==`self` and (Q,R) or Matrix.qr(self,r) #Cache result
        assert NPOST or m>=n and Q.size==(m,n) and isinstance(R,UpperTri) or m<n and Q.size==(m,m) and R.size==(m,n)
        assert NPOST or Q.mmul(R)==self and Q.tr().mmul(Q)==eye(min(m,n))
        return Q, R
    def _solve( self, b ):
        '''General matrices (incuding) are solved using the QR composition.
        For inconsistent cases, returns the least squares solution'''
        Q, R = self.qr()
        return R.solve( Q.tr().mmul(b) )
    def solve( self, b ):
        'Divide matrix into a column vector or matrix and iterate to improve the solution'
        if b.dim==2: return Mat( map(self.solve, b.tr()) ).tr()
        assert NPRE or self.rows == len(b), 'Matrix row count %d must match vector length %d' % (self.rows, len(b))
        x = self._solve( b )
        diff = b - self.mmul(x)
        maxdiff = diff.dot(diff)
        for i in range(10):
            xnew = x + self._solve( diff )
            diffnew = b - self.mmul(xnew)
            maxdiffnew = diffnew.dot(diffnew)
            if maxdiffnew >= maxdiff:  break
            x, diff, maxdiff = xnew, diffnew, maxdiffnew
            #print >> sys.stderr, i+1, maxdiff
        assert NPOST or self.rows!=self.cols or self.mmul(x) == b
        return x
    def rank( self ):  return Vec([ not row.forall(iszero) for row in self.qr(ROnly=1) ]).sum()

class Square(Matrix):
    def lu( self ):
        'Factor a square matrix into lower and upper triangular form such that L.mmul(U)==A'
        n = self.rows
        L, U = eye(n), Mat(self[:])
        for i in range(n):
            for j in range(i+1,U.rows):
                assert U[i][i] != 0.0, 'LU requires non-zero elements on the diagonal'
                L[j][i] = m = 1.0 * U[j][i] / U[i][i]
                U[j] -= U[i] * m
        assert NPOST or isinstance(L,LowerTri) and isinstance(U,UpperTri) and L*U==self
        return L, U
    def __pow__( self, exp ):
        'Raise a square matrix to an integer power (i.e. A**3 is the same as A.mmul(A.mmul(A))'
        assert NPRE or exp==int(exp) and exp>0, 'Matrix powers only defined for positive integers not %s' % exp
        if exp == 1: return self
        if exp&1: return self.mmul(self ** (exp-1))
        sqrme = self ** (exp/2)
        return sqrme.mmul(sqrme)
    def det( self ):  return self.qr( ROnly=1 ).det()
    def inverse( self ):  return self.solve( eye(self.rows) )
    def hessenberg( self ):
        '''Householder reduction to Hessenberg Form (zeroes below the diagonal)
        while keeping the same eigenvalues as self.'''
        for i in range(self.cols-2):
            v, beta = self.tr()[i].house(i+1)
            self -= v.outer( self.tr().mmul(v)*beta )
            self -= self.mmul(v).outer(v*beta)
        return self
    def eigs( self ):
        'Estimate principal eigenvalues using the QR with shifts method'
        origTrace, origDet = self.trace(), self.det()
        self = self.hessenberg()
        eigvals = Vec([])
        for i in range(self.rows-1,0,-1):
            while not self[i][:i].forall(iszero):
                shift = eye(i+1) * self[i][i]
                q, r = (self - shift).qr()
                self = r.mmul(q) + shift
            eigvals.append( self[i][i] )
            self = Mat( [self[r][:i] for r in range(i)] )
        eigvals.append( self[0][0] )
        assert NPOST or iszero( (abs(origDet) - abs(eigvals.prod())) / 1000.0 )
        assert NPOST or iszero( origTrace - eigvals.sum() )
        return Vec(eigvals)

class Triangular(Square):
    def eigs( self ):  return self.diag()
    def det( self ):  return self.diag().prod()

class UpperTri(Triangular):
    def _solve( self, b ):
        'Solve an upper triangular matrix using backward substitution'
        x = Vec([])
        for i in range(self.rows-1, -1, -1):
            assert NPRE or self[i][i], 'Backsub requires non-zero elements on the diagonal'
            x.insert(0, (b[i] - x.dot(self[i][i+1:])) / self[i][i] )
        return x

class LowerTri(Triangular):
    def _solve( self, b ):
        'Solve a lower triangular matrix using forward substitution'
        x = Vec([])
        for i in range(self.rows):
            assert NPRE or self[i][i], 'Forward sub requires non-zero elements on the diagonal'
            x.append( (b[i] - x.dot(self[i][:i])) / self[i][i] )
        return x

def Mat( elems ):
    'Factory function to create a new matrix.'
    m, n = len(elems), len(elems[0])
    if m != n: return Matrix(elems)
    if n <= 1: return Square(elems)
    for i in range(1, len(elems)):
        if not iszero( max(map(abs, elems[i][:i])) ):
            break
    else: return UpperTri(elems)
    for i in range(0, len(elems)-1):
        if not iszero( max(map(abs, elems[i][i+1:])) ):
            return Square(elems)
    return LowerTri(elems)

def polyfit( (xvec, yvec), degree=2 ):
    'Solves Vandermonde design matrix for approximating polynomial coefficients'
    return Mat([ [x**n for n in range(degree,-1,-1)] for x in xvec ]).solve(Vec(yvec))

def genmat(m, n, func):
    if not n: n=m
    return Mat([ [func(i,j) for i in range(n)] for j in range(m) ])

def zeroes(m=1, n=None):
    'Zero matrix with side length m-by-m or m-by-n.'
    return genmat(m,n, lambda i,j: 0)

def eye(m=1, n=None):
    'Identity matrix with side length m-by-m or m-by-n'
    return genmat(m,n, lambda i,j: i==j)

def hilb(m=1, n=None):
    'Hilbert matrix with side length m-by-m or m-by-n.  Elem[i][j]=1/(i+j+1)'
    return genmat(m,n, lambda i,j: 1.0/(i+j+1.0))

def rand(m=1, n=None):
    'Random matrix with side length m-by-m or m-by-n'
    return genmat(m,n, lambda i,j: random.random())

if __name__ == '__main__':

  file=open(sys.argv[-1],'r')
  x=[] ; y=[]
  while 1:
    line=file.readline()
    if not line: break
    x.append(math.log10(float(line.split()[0])))
    y.append(float(line.split()[1]))
  file.close()

  lum=-2.5*math.log10((10.**(y[-1]/-2.5)/2.))
  r=[] ; s=[]
  for tmp in y:
    if tmp < lum:
      r.append(x[y.index(tmp)])
      s.append(tmp)
  data=numarray.array([r,s])
  a,b,c=polyfit(data,2)
  x0=-b/(2.*a)
  print 'Asymptotic Radius = ','%8.5g' % x0
  print 'Total Mag         = ','%8.5g' % (a*x0**2+b*x0+c)
