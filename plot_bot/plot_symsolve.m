clear
syms x y A B
f1 = sym('(x-0)^2+(y-1000)^2=A^2')
f2 = sym('(x-0)^2+(y-0)^2=B^2')
S=solve(f1,f2,x,y,'IgnoreAnalyticConstraints',true)
Sx = simple(S.x)
Sy = simple(S.y)