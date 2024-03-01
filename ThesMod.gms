sets
r resources /1*25/
f flights /1*51/
k resource type /1*3/
;
alias(k,kxe);
alias(r,rxe);
parameters
c(r,k,f) cost of assigning resource rk to flight f
cd(f) cost of delay flight f
cc(f) cost of cancelling flight f
b(r,k,f)  if resource rk is to cover any part of a broken trip-pair or aircraft route
g(k,f) total number of resources of type k required for flight f
q(r,k,rxe,kxe) resource compatibility
a(r,k,f) ready time of resource rk for flight f
v(r,k) the duty (usage) limit of resource r
UB_nf /10000/
T(f) expected trip time of flight f
ts(f) the scheduled departure time of flight f
;

*Import c///////////////////////////
$call gdxxrw.exe thesdata.xlsx par=c rng=assignment-cost(c)!A1:BA76  rDim=2 cDim=1
$gdxin thesdata.gdx
$load c
$gdxin
display c;
*Import c///////////////////////////
*Import cd///////////////////////////
$call gdxxrw.exe thesdata.xlsx par=cd rng=delay-cost(cd)!A1:AY2  rDim=0 cDim=1
$gdxin thesdata.gdx
$load cd
$gdxin
display cd;
*Import cd///////////////////////////
*Import cc///////////////////////////
$call gdxxrw.exe thesdata.xlsx par=cc rng=cancellation-cost(cc)!A1:AY2  rDim=0 cDim=1
$gdxin thesdata.gdx
$load cc
$gdxin
display cc;
*Import cc///////////////////////////
b(r,k,f)=1;
*Import g///////////////////////////
$call gdxxrw.exe thesdata.xlsx par=g rng=minimum-resource-requirement(g)!A1:AZ4  rDim=1 cDim=1
$gdxin thesdata.gdx
$load g
$gdxin
display g;
*Import g///////////////////////////
q(k,kxe)=1;
*Import a///////////////////////////
$call gdxxrw.exe thesdata.xlsx par=a rng=ready-time(a)!A1:BA76  rDim=2 cDim=1
$gdxin thesdata.gdx
$load a
$gdxin
display a;
*Import a///////////////////////////
v(r,k)=1500;
T(f)=70;
*Import ts///////////////////////////
$call gdxxrw.exe thesdata.xlsx par=ts rng=scheduled-time(ts)!A1:AY2  rDim=0 cDim=1
$gdxin thesdata.gdx
$load ts
$gdxin
display ts;
*Import ts///////////////////////////




binary variables x(r,k,f),l(f);
integer variables m(f),n(f);
variable z;

m.up(f)=9000;
n.up(f)=9000;


equations
eq1
eq2
*eq3
eq4
eq5
eq6
eq7
eq8
eq9
;

eq1 .. z=e=sum((r,k,f),c(r,k,f)*x(r,k,f))+sum(f,cd(f)*(m(f)-ts(f)))+sum(f,cc(f)*l(f));
eq2(r,k,f).. x(r,k,f) =l= b(r,k,f);
*eq3(r,k)  .. sum(f,x(r,k,f)) =l= 1 ;
eq4(k,f)  .. (1-l(f))*g(k,f) =e= sum(r,x(r,k,f));
eq5(r,k,rxe,kxe,f)$(ord(k)<>ord(kxe)).. (1-q(r,k,rxe,kxe))*(x(r,k,f)+x(rxe,kxe,f)) =l= 1 ;
eq6(r,k,f) .. m(f) =g= a(r,k,f)*x(r,k,f) ;
eq7(r,k,f) .. n(f) =l= v(r,k)*x(r,k,f)+(1-x(r,k,f))*UB_nf ;
eq8(f) .. n(f) =e= m(f) + T(f) ;
eq9(f) .. m(f) =g= ts(f) ;

model thes /all/ ;
solve thes minimizing z using mip;
display x.l,m.l,n.l,l.l,z.l;
