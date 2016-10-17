def jack_knife(x,xsig):
  if len(x) == 0: return 'NaN','NaN','NaN','NaN','NaN','NaN','NaN'
  if len(x) == 1: return x[0],0.,x[0],0.,len(x),'NaN','NaN'
  xmean1=0. ; sig1=0.
  for tmp in x:
    xmean1=xmean1+tmp
  try:
    xmean1=xmean1/len(x)
  except:
    return 'NaN','NaN','NaN','NaN','NaN','NaN','NaN'
  for tmp in x:
    sig1=sig1+(tmp-xmean1)**2
  try:
    sig1=(sig1/(len(x)-1))**0.5
  except:
    return 'NaN','NaN','NaN','NaN','NaN','NaN','NaN'

# do top and bottom jackknife to find best sigma
  x.sort()
  xm=0. ; s=0.
  for tmp in x[1:]:
    xm=xm+tmp
  xm=xm/(len(x)-1)
  for tmp in x[1:]:
    s=s+(tmp-xm)**2
  try:
    s=(s/(len(x)-2))**0.5
    if s < sig1:
      xmean1=xm
      sig1=s
  except:
    pass
  xm=0. ; s=0.
  for tmp in x[:-1]:
    xm=xm+tmp
  xm=xm/(len(x)-1)
  for tmp in x[:-1]:
    s=s+(tmp-xm)**2
  try:
    s=(s/(len(x)-2))**0.5
    if s < sig1:
      xmean1=xm
      sig1=s
  except:
    pass

  xmean2=xmean1 ; sig2=sig1
  xold=xmean2+0.001*sig2
  its=0
  npts=0
  while (xold != xmean2 and its < 100):
    xold=xmean2
    its+=1
    dum=0.
    npts=0
    for tmp in x:
      if abs(tmp-xold) < xsig*sig2:
        npts+=1
        dum=dum+tmp
#    print npts,dum
    try:
      xmean2=dum/npts
    except:
      return xmean1,sig1,'NaN','NaN',len(x),'NaN','NaN'
    dum=0.
    for tmp in x:
      if abs(tmp-xold) < xsig*sig2:
        dum=dum+(tmp-xmean2)**2
    try:
      sig2=(dum/(npts-1))**0.5
    except:
      return xmean1,sig1,'NaN','NaN',len(x),'NaN','NaN'
  return xmean1,sig1,xmean2,sig2,len(x),npts,its
