NAME test
* Max problem is converted into Min one
ROWS
 N  OBJ
 G  const1  
 G  const2  
COLUMNS
    MARKER    'MARKER'                 'INTORG'
    x1        OBJ       -7
    x1        const1    1
    x1        const2    3
    x2        OBJ       -3
    x2        const1    2
    x2        const2    1
    x3        OBJ       -4
    x3        const1    3
    x3        const2    1
    MARKER    'MARKER'                 'INTEND'
RHS
    RHS1      const1    8
    RHS1      const2    5
BOUNDS
 LI BND1      x1        0
 LI BND1      x2        0
 LI BND1      x3        0
ENDATA
