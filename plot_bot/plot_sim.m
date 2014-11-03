%---- const parameters ------
t=100;
Px=0;
Py=0;
Qx=1000;
Qy=0;
%----- position setup -------
x0=300;
y0=300;
x1=500;
y1=600;
%---- init plotting ---------
figure;hold on
tmpx=[x0:(x1-x0)/t:x1];
tmpy=[y0:(y1-y0)/t:y1];
plot(tmpx,tmpy,'-')
set(gca, 'YDir', 'reverse')
axis([0 1000 0 1000]);

%----- mapping --------------
a=sqrt((tmpx-Px).^2+(tmpy-Py).^2);
b=sqrt((tmpx-Qx).^2+(tmpy-Qy).^2);
%----- simulate -------------
simx=zeros(1,t+1);
simy=zeros(1,t+1);
for i=1:t+1
   ty = eval(subs(subs(Sx(1),A,a(i)),B,b(i)));
   tx = eval(subs(subs(Sy(1),A,a(i)),B,b(i)));
   simx(i)=1000-tx;
   simy(i)=ty;
end

plot(simx,simy,'-xr')
















