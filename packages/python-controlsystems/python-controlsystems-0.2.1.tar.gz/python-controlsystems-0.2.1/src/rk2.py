#-*- encoding: utf-8 -*-
#
#       rk2.py
#       
#       Copyright 2009 Rafael G. Martins <rafael@rafaelmartins.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

from transferfunction import TransferFunction
from statespace import StateSpace
from matrix import Matrix, Zeros, Identity
from error import ControlSystemsError

def RK2(g, sample_time, total_time):
    
    if not isinstance(g, TransferFunction):
        raise ControlSystemsError('Parameter must be a Transfer Function')

    ss = StateSpace(g)
    
    samples = int(total_time/sample_time) + 1
    
    t = [sample_time * a for a in range(samples)]
    
    x = Zeros(ss.a.rows, 1)
    y = []
    
    eye = Identity(ss.a.rows)
    
    a1 = ss.a * ss.a
    a2 = ss.a.mult(2) + a1.mult(sample_time)
    a3 = a2.mult(0.5)
    a4 = ss.a.mult(sample_time)
    a5 = a4*ss.b + ss.b.mult(2)
    a6 = eye + a3.mult(sample_time)
    a7 = a5.mult(sample_time/2)
    
    for i in range(samples):
        x = a6*x + a7
        y.append((ss.c*x)[0][0] + ss.d[0][0])

    return t, y

if __name__ == '__main__':
   
    g = TransferFunction([1], [1, 2, 3])
    
    print RK2(g, 0.01, 10)
