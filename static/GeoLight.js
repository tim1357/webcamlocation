/*
solar(1429325922.61) 
$solarTime 
[1] 44.805 
 
$eqnTime 
[1] 0.5098267 
 
$sinSolarDec 
[1] 0.1853324 
 
$cosSolarDec 
[1] 0.9826759 
*/
function solar(tm){
  rad=Math.PI/180.;
  Jd = parseInt(tm)/86400+2440587.5;
  Jc = (Jd-2451545)/36525;
  L0 = (280.46646+Jc*(36000.76983+0.0003032*Jc))%360;
  M = 357.52911+Jc*(35999.05029-0.0001537*Jc);
  e = 0.016708634-Jc*(0.000042037+0.0000001267*Jc);
  eqctr = Math.sin(rad*M)*(1.914602-Jc*(0.004817+0.000014*Jc))+
    Math.sin(rad*2*M)*(0.019993-0.000101*Jc)+
    Math.sin(rad*3*M)*0.000289;


  lambda0 = L0 + eqctr
  
  omega = 125.04-1934.136*Jc
  lambda = lambda0-0.00569-0.00478*Math.sin(rad*omega);
  
  
  seconds = 21.448-Jc*(46.815+Jc*(0.00059-Jc*(0.001813)));
  obliq0 = 23+(26+(seconds/60))/60
  
  omega = 125.04-1934.136*Jc;
  obliq = obliq0 + 0.00256*Math.cos(rad*omega);
  
  y = Math.pow(Math.tan(rad*obliq/2),2);
  eqnTime = 4/rad*(y*Math.sin(rad*2*L0) -
                      2*e*Math.sin(rad*M) +
                      4*e*y*Math.sin(rad*M)*Math.cos(rad*2*L0) -
                      0.5*y*y*Math.sin(rad*4*L0) -
                      1.25*e*e*Math.sin(rad*2*M));
  solarDec = Math.asin(Math.sin(rad*obliq)*Math.sin(rad*lambda));
  sinSolarDec = Math.sin(solarDec);
  cosSolarDec = Math.cos(solarDec);
  
  solarTime = ((Jd-0.5)%1*1440+eqnTime)/4;

  return {solarTime:solarTime,
       eqnTime:eqnTime,
       sinSolarDec:sinSolarDec,
       cosSolarDec:cosSolarDec};
  

}


//Type =1 -> tfirst is sunrise

function coord(tFirst,tSecond,type){
  degElevation = -6;
  tol=0;
  if (type==1){rise=tFirst;set=tSecond;} else{rise=tSecond;set=tFirst;}
  rad = Math.PI/180;
  sr = solar(rise);
  ss = solar(set);
  cosz = Math.cos(rad*(90-degElevation));
  if (sr.solarTime<ss.solarTime){temp=360;}else{temp=0};
  lon = -(sr.solarTime+ss.solarTime+temp)/2;
  hourAngle = sr.solarTime+lon-180;
  a = sr.sinSolarDec;
  b = sr.cosSolarDec*Math.cos(rad*hourAngle);
  x = (a*cosz-Math.sign(a)*b*Math.sqrt(a*a+b*b-cosz*cosz))/(a*a+b*b)
  lat1 =null;
  if (Math.abs(a)>tol){lat1= Math.asin(x)/rad;};
  hourAngle = ss.solarTime+lon-180;
  a = ss.sinSolarDec;
  b = ss.cosSolarDec*Math.cos(rad*hourAngle);
  x = (a*cosz-Math.sign(a)*b*Math.sqrt(a*a+b*b-cosz*cosz))/(a*a+b*b);
  lat2 =null;
  if(Math.abs(a)>tol){lat2=Math.asin(x)/rad;}
  return {lon:lon,lat:(lat1+lat2)/2};

}