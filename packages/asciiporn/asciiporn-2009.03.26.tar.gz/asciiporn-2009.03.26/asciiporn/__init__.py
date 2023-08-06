"""
################################################################################
asciiporn is designed for interactive graphics viewing within an ssh terminal
by converting graphics into colorized ascii-art. asciiporn has 256 color support
& is partially written in c for efficent graphics rendering.
asciiporn can easily render 24 bit megapixel graphics on a 1ghz 500mb machine

screenshots of both image viewing & plotting r included w/ this distribution.
asciiporn is hard-coded with lucida-console font, but courier font will work
as well. the screenshots show putty ssh w/ lucida-console 5pt.

how to enable 256 color in putty:  http://www.emacswiki.org/emacs/PuTTY#toc2
how to enable 256 color in xterm:  http://www.frexx.de/xterm-256-notes/
how to enable 256 color in screen: http://www.frexx.de/xterm-256-notes/

for quick example usage, remotely run python in an ssh terminal:

  >>> ## print image file as colorized ascii art in ssh terminal
  >>> from asciiporn import img2txt
  >>> print img2txt("mario.jpg")

  >>> ## plot several math functions in ssh terminal
  >>> from asciiporn import plot
  >>> from math import cos, sin, pi
  >>> print plot(ft = [cos, sin], tmin = 0.0, tmax = 2*pi)

  >>> ## plot 3d function in ssh terminal
  >>> from asciiporn import plot3d
  >>> from math import sin, pi
  >>> print plot3d(
  ...   ftz = lambda t, z: sin(t + t*z), ## 3d function
  ...   tmin = 0.0, tmax = 2*pi,         ## t parameter
  ...   zmin = 0.0, zmax = 0.25,         ## z parameter
  ... )

AUTHOR:
  kai zhu
  kaizhu256@gmail.com

REQUIREMENTS:
- posix os
- Python Imaging Library  http://www.pythonware.com/products/pil
- numpy                   http://www.scipy.org/Download

PSEUDOMETHOD:
  asciiporn uses ".." syntax notation for pseudomethods
  goto: http://pypi.python.org/pypi/pseudomethod
  for more details about this feature

API:
  asciiporn module:
  - img2plaintxt - converts image file to portable plain txt
                   u can copy & paste in documents
  - img2txt - converts image to high-quality colorized txt
              for display on terminals supporting 256 color (putty, xterm...)
  - plot - plot multiple 2d functions
  - plot3d - plots a 3d function that takes in 2 parameters

INSTALL:
  python setup.py build
  python setup.py install
  python setup.py dev --quicktest

################################################################################
PLOT USAGE:

2d plots take 3 main arguments:
  ft - a list of functions to plot
  tmin, tmax - range of t

  >>> import asciiporn, numpy
  >>> asciiporn.plot(
  ...   ft = [                  ## list of single argument functions f(t)
  ...     numpy.cos,
  ...     numpy.sin,
  ...     lambda t: numpy.sin(t + 0.25),
  ...     ],
  ...   tmin = 0.0, tmax = 7.0, ## range of t
  ... )



SIDEVIEW Y:    Z  0 to 2    Y  -0.99983900113 to 1.0    T  0.0 to 7.0    MIN MAX
l?*~_-----_>cC}lTl{7Tx_--------------------------------------------_+*Tll'*+_---
|    T, ,r',*l      '_ ),                                        .(         `-_
|      a_ /           )_ \_                                    ,*             ,(
|    ,C ~C             `.  ,                                  )              )
|   )  >  \              \  \                                /              /  (
|  /  /    \              '_ ^                              '             _^  '
| (  '      '_             `_ )                            '              ' ,'
|r _'                       `c '_                        ,'             ,' ,
(  '           _              c `                       ,              ,' ,
| '            `c              c `_                    ,              ,  .
|'              `c              _ `                   ,              ,' +
 ----------------`---------------L-`-------------- --.--------------,'-+--------
|                  _              c `_              .              ,' +
|                   _             `C `             .              ,' +
|                                      c          .              .  ,
|                    `C              ,  c        ,              ,  )
|                      ,              . ?c      )              )  /
|                       x              t  .    /              <  /
|                        \              \  \  (              / _*
|                         '_             '_ ;C             ,' ,'
|                           x             (%) x           x _x
|                            '<         _>' ?x_'C       >'_r'
|------------------------------`*<____>r------`*<{jy_yj1+*'---------------------



3d plots have 2 extra arguments:
  zmin, zmax - range of z

  >>> import asciiporn, numpy
  >>> asciiporn.plot3d(
  ...   ftz = lambda t, z: numpy.sin(t + t*z), ## 3d function f(t, z)
  ...   tmin = 0.0, tmax = 7.0,                ## range of t
  ...   zmin = 0.0, zmax = 0.25,               ## range of z
  ... )



SIDEVIEW Y:    Z  0.0 to 0.25    Y  -0.999 to 0.9999    T  0.0 to 7.0    MIN MAX
|---------`WDHbPgHHbmW_---------------------------------------------_mH&&EHH&&EH
|        q88''    'b&EHD_                                         _mdHH&&QmH&&dm
|      _M&W`        NEHHbW_                                      s8&mHH8&gHF8&dm
|     _HHl           #HHb&&p                                   `=bM@mjjD@d@]hIdH
|    _HF'             ]Hb&&IL                                  j]kM@m&ahMgk]uHB'
|   _bg                ]b&&IHm`                               sdkAUh$kkUP$F]l+'
|  `8h                  3&&IHm#`                             ?hm]k[hdFElP]F%nl
|  HC                    d&Imm&8`                           (UhhEk1{jJk[1j]L`
| M'                      8dHb&&d_                         _dPUR]k{hRF}P[6i'
|j'                        mHm&&dH`                       _]ahUg]k[3B}jCf]
_C                         `Hb&&dHH_                      Ak}1U%]6UC&jFh+`
'----------------- ---------'b&&mmm&_------ -------------s$k4hU%]]CnjFjT`-------
|                            3&&mmH@@,                  cI$]kppA}}nhB]J`
|                             8&$mH&&8_                -Dhd]dUhA]}{3&J'
|                             `gmHH8&dH`              _aMM$kaUh%]]huj
|                              `mHH&&dHH_            `jg@Qd&4MKd}aPl`
|                               'HH8@HHH&_          _]jgDMdk}UUdk}T`
|                                'H&8HHH&&,         @mHaDMdkk@@HA*
|                                 '&&dHH&&dL       q8mmb&#dkE@@d'
|                                  ?&EDH&&dHH_   `g&Wmmb&8dH$&@'
|                                   ?dHH&&EHH&p``mb&8mmD8&dHbl`
|                                    `WH&&EHH&&8HHb&EHHD&8dF'
|--------------------------------------'NMEHH&&EHHb&EHHbMPl---------------------

TOPVIEW Z:  Z  0.0 to 0.25  (top to bottom)  Y  -0.9999 to 0.9999  T  0.0 to 7.0
 DOGKz1(7Lx\:,-'`   `._~>r?;tfVne6H MQpZaV}oTY?+(,!'` `'-_>+|/Cc[]KPRg  8REnVSt7
 DOGKX3(7/vi:_-`    `-_~iv/YcS{aZqm &8qI4yzts7r~i'-`  `-'i~r7stjy4Iq8& dqEa{jtYL
 DAG5X3cY/vi~_.`   `'-,:|xJT=3y4U9  Wm0EXnFTY?\(_!.` `'!,:\l^)Fn3U9mN m%Za{j=Y?x
 DAZ5{jcY?r>~_.`   `''!(+lsCf}neR8 $gRI4yz=slx*i'.' `'-_(+rYT2[]GO6D D9U5X3=T?r*
 DAZa{jt;?r>!'.`   `._~i|/YcoV5GOd BH9GXnF)Y?\:_-'` `.!i~vLstj{3PhbN HqE][fCsx*i
 DAZa{jt;l|(!'.`   `._~irL7=j{4U9 @D6OK][oT7r*>'.' `'-_(\|Y)FnXGqd# bAZa[ft;l+(~
 mqEaVoCsl|(,-'    '.,:\vJ)2}yeR8 &bhP3{jts?\:,-'` `.'i*r7Jo[VawmW  OG5XSc;?r>!_
 mqEnVoCs^+:,-'   `'-!(+^;tSkuGOd WmAeV[oTYr*>'.` `'!,(vL^)fy4PhQ  8U4z1cY?ri!'.
 mqEnkS)Jx*:_-'   `'-~>|l7(j{50h  gRZK{jtsl\:,!'` '-'>*|YT2k3U9H  Hqwy}27/v\:'.'
 mqeukS)Lx*~_.`   `.'~|r/)F1ywqH $d9U3}2TY|*>'-` `.!,:v7J=zXGO6W dOZu[fCLv\:,.``
 mqeu[fTLv\~'.`   `._:*xLtfkueOm #%0EVfcslx:,!'` `-_(+|^)S{KZRg  9IKVSt;x*(,-`
 mReu[fT/v\!'.`   '-_(+^sco{5Gh @DhP5uF(Y?\>'-' `'!,:vLJ=z]eAHB Hqeu1FTL|i~'.`
 mRe][27/ri!''`  `'-,>|l;=3z4U8 $89e1noC/r*i!.` `._(+|Ytj{5w%D  OZaV2)Jxi~_.`
 mRP]}27?ri!-'`  `''!ir?72}]PRd #H0a]zt^Lv:_-' `'!i~x7J2}Xeh8  8UKXjts^+:_.`   `
 dRP]}FY?|>,-'   `.'!\vLTSknZA  D%I5{ST/|*>!.` `.'(\?;)zyawH# dAPy1FYl|>,-'    '
 d6Py1F;l|>,-'   `._~*xJCjXKI9 $8hGX}oslv:,-' `'!,*r/Cok3IhD  9InkfC/ri~-'`   '-
 d6wy1=;l+(_.`   `-_:+l;c1yw68 #HAKyftY|+>_.` `.'>\L^tjVGOm  86w{oc;x\:_.`   `._
 d6wz3=s^+(_.`   '-,(r?7=[uEA  DRZ3kF(7x~i!'` '!,:r/T2n4ZRQ dAEu3=7?+(,-`   `'_~
 d6wz3(s^*(_.`  `''!>vLT2V5G% $8qUV[=J?\(_-` `.'>*?^tjuGAH# p04zSCJxi~'.`   '-~i
 d6wz3(sx*:'.`  `''!ixJ)fXKUh NdAGyft^|*>'.` `-,:v/C2n1ZRQ  qe]}(Yl+:_.`   `._(+
 d04XjcJx\:''`  `.'~\^stoywRH W6wKkFTYx:,!' `''>*|^tfya9b& 9GaVST/ri,-'   `.'~*x
 d04XjcJv\~-'`  `._:*lY(3uEAm gpI3[=Jl+(_-` `.,:vlT2n3I6W m6wzj(Jx\:''`  `''!>vL
 d04XocLv\~-'   `-,(+/7F}aG9 @d9GVj);?~i!.` '-i~r/)jyK0d& 8Gakf)?|>!.`   '-,(+/T



asciiporn can also plot user-supplied (y,t) datapoint pairs:

  >>> import asciiporn, numpy
  >>> t =  numpy.arange(1000)   ## create t coord datapoints
  >>> y =  numpy.sin( 0.01*t )  ## create y coord datapoints
  >>> yt = list(zip( y, t ))    ## create (y,t) datapoint pairs
  >>> asciiporn.plot( yt = yt )



SIDEVIEW Y:    Z  0 to 0    Y  -0.99999 to 0.99999    T  0.0 to 999.0    MIN MAX
|--------_<?l'*c-------------------------------------------->*'lt<--------------
|       >'      \_                                        ~'      '_
|      /         `c                                      /          ,
|     ^           `                                     /            >
|    /                                                 v              v
|   /               `                                 ,                c
|  ,                 '                                                 `
|                     Y                              ^                  \.
| '                                                 /                    ,
|/                     -                           ,
|                       \                                                 `
'----------- ------------L----------- ------------/------------------------:----
|                                                s
|                         ^                                                 `
|                          l                    ^                            \.
|                           c                  /                              >
|                           `                 ,                                c
|                            ^                                                 `
|                             \              '
|                              Y           _'
|                               \         _'
|                                \_      .'
|---------------------------------`>_,_.*---------------------------------------



################################################################################
IMAGE USAGE:

in this example, u'll b loading the image file included w/ this distribution,
"mario.jpg".  its a fairly large image, so u prolly want to scale it down
to 0.5 (or less):
  >>> colortxt = asciiporn.img2txt("mario.jpg", scale = 0.5)
  >>> print( colortxt )

  ... beautiful color image appears ^_-

  >>> plaintxt = asciiporn.img2plaintxt("mario.jpg", scale = 0.5)
  >>> print( plaintxt )

  ... rather plain b/w img -_-, but u can copy & paste in documents ...



~   L_        '_-s+     _   ?}@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
'   `{' _~ ` 't` 7~-- `  ^  f@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@M@@@@@@@@@@@@@@@@@@@@
_,-),?j{WY+=+j ` ^7^   ` `   H@@@@@@@@@@@@@@@@@@@@@@@MQk9ZIV7=?IM@@@@@@@@@@@@@@@
t' ~``nvi;f*o7L? `L~     `   &#M@M$@@@@@@@@@@@@@@@@@P`/r`,_S^?`>^JT@{M@@@@@@@@@@
rr| + _` _^^LFFLW#W5| > '__`{PRy$y@Wf$N)i'fRM@@@@MM$r`^]g@`{~]{{rg>!'`}@@@@@@@@@
  *'    '`^!_ ^@&My;r,'p&#MV` 'ujmr)` `Lr( {_`R?@r= `_^'MPM#&B$f1Bp=` -]@@@@@@@@
    -r,r9` `_`J]3@$[`P`AVN-   -=yE `  _i ` ^`Li~i !YL `kj`'@MNMg@#Wggp{#@@@@@@@@
'`  i' l|'  F _]I]/#P )vAL >pqA}&_`  !J x?g1>LV'i~l+ _  ?Vu__|V@@@@@$${1@@@@@@@@
 `       '`` '-h$g@@@&$w])#R[X/NF^>-t,r-=`/hTW=~x!'!^`+gg@@&M#&W@@@@Mu#M@@@@@@@@
      `  _'  jg@@@@@M@@@@Mwm@p`#gj/c^ `' 9`   v `` _Vg@M@@@@@@M@@M@@@gD{kM@@@@@@
`      _ _3H##&@Mg#@@@@@@p#N4@Wu9Mx`` _ `!1 !`|   (&@@@W@@@@@@@@$M@M@M@Wj`}M@@@@
!| !_   _[2c3d@M&@@Q$&p@@$@WWM@Wb)/` s-+c `s '   g@$@@$M@@@@@@@M$$@@M$M@$p_=@@@@
  _``  +^lYSiH@M@@@@@@Md@@5=aa=EMVp`/`iNL +r  `r@&@@@@M$@@@@@@$W@@@@#&#@@@W=(MMM
``, +  F'c{^)(@@@@@@@@@@M@=]I7=w])$=_ _J^x``_  q$@@@@@M&g@@@@@#&&&&&&&&@W$$K]J^V
_>!{z-L7Ji_HLYE={[$@@@$$$&=jA][b^^VJ=++v=l_`-Cu@@@&M@MM@@M@MM$M@VMMW@@@@#W&1   =
   ~?LcY=sVcmggmmA6pk]Q#IVd$==]1scY[ {|){7i!=(q@@EE$@@M$@M&AMM#@@MMN$$$M&M@W  'v
      {-L#MMPP%9PM@#&$MWW},`'rUWB|i#!)i_J|V|Vf%AM$MWG@WEg]jyy]{gg]YI?)l{A#@@e _`
   `` !tl^    `  ` '?A@@#@Ewy'`^[=kEi}^ !^`v_ dQ=]jw###M@&$$$@$$@@M&mgp1}g]&#  +
     ?         '  `    ^#$W$g&wa{8Vh=r_VJ,?_` ]i_g@@@@M@@@@W@#@@@#MM@@@@@@R (WRT
'   `           `  '     ' ?@#d3^``e~,V(-`!  r`g&@M@F5``' `^^`ff@M@@@@@@@M_ a}i
    _ ,       ``~  `   {`    ``,   ^_,i-+2 7)_pMF^ '   's_^ ```   '`>=EM&g[g[A
    _ j `>`'  {  icx_T^'|  VV]?/ `  gy`J*|gypPgp    ! ` '__        ,_w&&$$N@Mm
_     j ]>' _ ` T/|nr_'   '_*wj? `(`-'_g&&@@M#@$Nu!    `   '  `  ` !XW@@@$#bd$
    ,_=!tRL!>^  '~^~`    `~ v#&6^- xr@W@&@M@@$@M@hc  ^^    T=f3~-({GW$@@@@M@&M
'   ' M'j{>vL {  ]^R{(!  ,Lc]Age}Lv+^]I{$F}][L^jjRCn!x_ `i_wgW{y/=[@@$@M@@@@@$^
+  '   9[M0P{,,_V/dQL+rVi-wd$##$}yAn@'` _V>'^s')~^W@[c9yCnM&&$$QQ_J@@W@@@&$M#^
   !    3#aF]T~^/V4M&4[w{W&WMM5&$Vtt`   _t7=yL+VV]@W&73^i7E=p#]&]}b9#MM@MM$`
        gEPVCc>]=&M@Wg&Y^kV]@@{#{'``   )NwEe+#Vy]$R[^kk/zL9gwq#&&#U}&@@MN@@p   `
        ~AR-`^}wlvBMVEL{+'/^V^jW=r`V` ' @M@EWMqWP^'=Mj{Vri}2g&NMhgmp@W$@$@M$ + `
   `   ^ ^MJ__`}~_^)v~It>L' )'-|`  T`   W$W@W&*T`   sZ=m@csX8&NM@@&@#E@AW@@@p{_'
    '     J{^i+`L`|iLXC _>|^_' >`      I@6BW@K j#&ELoll=mEILVM@M&&M%M@MMW@@@$ojL
           'izzzv>!|_^(`}+J'YY`      '3X@MM@@FS@@WN@B_!{#e@E[ggg@@@&MM]#@@@@@B@g
             !_=[j>_[z{p{o_^J=XS;/1__}&MgpWgpj#mgpp{GY  sQq#&wMW@@@B$N###@M@M@@@
             `kW{AA[}@#tts |`31&]WwaW]AV$A@@M@M@@&@M@C   '=YWV[Q[F$G&a@@@@MM@@@@
             'C|VC=)t>)^!  ~`^^3pIJ}Wg==}P[@$FEMA@V$wVT  !!1,>(||`s=@M#$@@@@@@@@
          '&[ Y['(v^^ J` _``*J^dYVe]_={y$=@>=[L'wVI&Ae _{=NgZ(ccg##=WWMM@@@@#MWP
     ' |]!@WR }u{cc!L '{>{|`7^ iJC}}JM+xY^Y9'`^_`YzYVA1{@X@@M==^IXe@W@@@M@@@@@l=
  ,__wkV'L'#M_`JYC(i'C_Y+cj '` ``o]=!V^|-^jjxCr^(`M'T'&Aq#MW@bk@a$8$&@#@$@@R'i=]
yWV=y??T)+!?XE`_')*c/|vJ^^    ^~s r+ri` /vtt ^`^-s(^(oVw]$#$dmB&$A8#q&M@#Wl+'-{A
@$4=a])=VJ'L>>^+ '-C-ir{i__ >~>'`t`)r^>(i-J7_?~  ,i}z==VY=&]e49@#@@A&@@l^(^_?}^T
WGiY/[kzt'=^r_` _   (}__ C  `  {`>rLx' ~=(n~`'Y'_r_Jc`,'(`wVC7^Y0M$VJ !'-x_^^Y +
&J|-~vVr^'{ '|| >L       Ji`' _ l^ ^  i'''vT ' _~` ! ` ^~7W[V^ J__' i`|`7>>ju^C-
=[`+T+! `'`_!{x_?+'`  L _J  ^i~iJ` `V~']=(sCY+>   '~ s(1]@-Ll'  _>`!| ` l, L^!VF
L-~'| - 'Jt!!t-^`` t{J'^` `t`'c!C^`V'^ VkLL/r'   >''i]+' |';V'_-`Y^s!L{+ ,tTi{rr
X2!^` {V(_?*/C~`|'Y ```>'~'`~`l'`{?|+7tVliiiJ{ - c   ^)' r  `-`'YV  Lit+{Tv+!!r_
`})>i -S^==l[i-` Y~ i_~  o^?-!x'^Ltr*VL?S=)  ~7 V``' L `|` C`  ` _ `^!`i!vs)^)-r
~_( ^`zzzL1|`Yv^`!! ~(`t+t!|l t`^ ov-+t~!Y^`   `,_``(!_ `'~ `` 'Y' |- ^^ s|F(`?k
`_=V'?oL*v  `  ~ ?t`'_ ^)- V _|rJc{ L>)_^]v;{`|`> )`x  _  x_s= ' ' `- ``iT)s7i-r
LL]iCinji  ^ ,`'- ``vX_C+l` -Yr>r2#&M-}=]?J={`|~    '' ''~ > `- ~{_`, `+''^!?,`X
j-}vVL+ ^`_  !)v>_L(~r| ^'` vL`xc&@WM//o{Y_MM^'`T  -'' x''x _ C)!(^v` `_(i ` tJ!
>c[/|`' ^ VL|J'+f|^VLL!)Yt^Vi'J-t@##jVVVJ?Vfl  '>   r`xV'J,`|` V>>ii`^- '_ `)^ '
`~^_(!  c_JL(CiJ?xiTv`!s{^ L,`_Y $MKt_]]^~(V  +     g` `L ++ ! ?~ `(     JV>   _
` T}=`{=- 7ut,^u^LL=iir_ i_`_Li' @8_f~[!{uS__ ```  #@& 7'TC_^o t_   *``'`{' >-
  Y)~:->vrx-YYtcoYJJx''?_)_tj^ viu{c3|/]-n`'' V'i  &]NC J>^_  ` ^!`/{` J' ^V `{?
' tt-v{ lT !|+{-Lii )^L)`*oviYJJ-o{zY{{'L!>`V&&g _ @&Akv  V^)vYx!' `  ^`_ ` +L>
   (lr=-r)J+u| x^i ?`_+`C;ni,vVVt7S|)/lT~|` dM@Mp UAN&E  s ~^i`_  i (_'' >   _ )
   >x>t+__>~`r?`^~(`)  -`'+uLfcc{jj-}-|^(+=->Vs@@b@$&@*-`_ ``` `v` ^ -`(L- _`  {
   V _]>r`~`  ! ``( ~(-lrTx{7{tVVLwgp{yvV|![|^=M@W&BmWW  Ci^``|   {|l^``' _V _ >
pp (gM@K`  `  '' t`'- {-t+zz_=iyb&@@M@MNF]?V'~%#@#@@M@&/^agpp ^ ` |'!i!  ''_~ C`
NWagM$P   'v~rs's' !?==|^Sc[=LzA&@@#W@#@E1^=^ &$&A$M@&@$@M@@$`' ` ``_ |||)_```
&W@@$''LMMj^`si V>>zV=^jF=-^'cT#@@@@B@M##WVTJ&#@M@MgM&$@N@MM# c`   'x' !-''rrr '
&&&A^ @&@$#P```i^?=7Vt^V*V===sy$&@M@M&@WM@^`VW@@M@@@@MgIb}ZW  > ' '   { '_  _ ^,
@Me'  m#M@#A  _f=[k^_?V{JJ{`}8^@WN@@M#MM@n+tq@@W$$$M@@MM@W&^^    `{~  ~ _  C``'{
#M ` {ZA@WW@c?=j=-{ifYV^rYV=)rFV@&Z#M#W$Lvs }M@@M@@@6$MMMM_ ^   ``''^   r` s''L(
} `'' @MM@$@=_bvrt(^^i-}-_jt=-jz('FMM@{zJTs_?@P3@$#M@Bb7^` -`T  ``  ^)iJ_J >L^J;
W  _`nB#@M#T_V+tSc{L >Vrr]+=|*jSi=L* oAr^bi  o]s_w3K@{@~`   '_ `  `^ '  ` ``|)~r
^` r^x@Li=]{)!^>cVxJ>(V~t^J3i^=}!>[zr,7ztt{_ ^#XFwu9#]yj^  '   `l `7'   ~s !t`7^
x ^kT` '{i{! jNT~>^-'-jb-{TTVr|!'*r-xcVt !  `))]W[_g9d&>` `     ``v`t|| ' _ 7tc+
[  J/C`~{Yt!y+)`xJ))))J=L!ri)=V=LJn-i-^f7X7 _!r]@mMQ@@AAv    _` J'i`l't_{`i!_iCJ
W^_Jk=v`|,LwT>_^rr||||VL3__=r=i^ _ Y'xtXj`^_ _-^Z#sMU&j2{   ^      J |'t7v 'i!n)
zL''?^`_?YLr^ sr|TV-+?!'+|[Y]'CY]jY^?i+iuL> ^ --Tsja]kIgL,  `_  ~i` _ '- >`'-jLu
!C `  `w3Y^ `~(-+--3~sJ71l^i^^L>|?{+^``L - ` ^ ^>7cmQdkzC  & '_`'`L' ```(?_' ~ll
r r`+vvr~ xJ__==={f=Ls_L7iVr V?T3`l`-]'t|^_   ' Y`=u}l^ s  ]` -' ' `,|_i`t`t~,Lr
   -+7  !_^+(----'VSVc>zzl?`L=~ioV'x`^)*>T`       x+>77'^ %$` !!^~'`  !x``'{`Y[-
``V{  ` Vrr-)?///?VC~l?>zx|_st{-oJ!xf+>!{=r!         _ _  #$` !  `|  `J,`` `!`!~
  L`+_Jvi7++^='r?+n^T?[c!_,S?{{iF~( !^FL~ 'Y   `      ' -NNMY !  {   >, _,` `i+[
ci   ` _`x_rr>_|'r>>`jY( (_kk|`{J)s_^L|V--+ ` ` -   !'>)kkMeT s^|T {>L C''^'!-~r



actually, the plaintxt prolly won't look well when pasted,
b/c most document readers invert the color:
  >>> plaintxt = asciiporn.img2plaintxt('mario.jpg', scale = 0.5, invert = True)
  >>> print( plaintxt )

  ... b/w img w/ colors inverted.  may look funny now :/
      but it'll b normal when pasted in document

################################################################################
RECENT CHANGELOG:
  removed py3to2 requirement
  update documentation
20090103
  rewrote 3d plotter
  fixed more 64bit issues
20081123
  fixed bug where 64bit gets truncated to 32 on 32bit machine
  256 color support
20081119
  fixed bugs in setup.py
"""



import os, sys
if sys.version_info[1] < 6: raise Exception("asciiporn requires Python 2.6 or higher")



__author__ = "kai zhu"
__author_email__ = "kaizhu256@gmail.com"
__description__ = """
view color images & scientific plots in ssh terminal
(screenshots using putty ssh terminal included)
"""
__download_url__ = None
__keywords__ = None
__license__ = "GPL"
__maintainer__ = None
__maintainer_email__ = None
__obsoletes__ = None
__platforms__ = None
__provides__ = None
__requires__ = ["PIL", "numpy"]
__url__ = "http://pypi.python.org/pypi/asciiporn"
__version__ = "2009.03.26"
## end setup info



if "DEBUG" not in globals(): DEBUG = 0 ## True prints debug info



import ast, collections, re ## pseudomethod parser
class parser(ast.NodeTransformer):
  def parse(self, s, fpath, mode):
    # s = s.replace(".items()", ".iteritems()").replace(".keys()", ".iterkeys()").replace(".values()", ".itervalues()")
    s = s.replace("__next__", "next") ## PEP3114  Renaming iterator.next() to iterator.__next__()

    s = s.replace("..", ".__pseudomethod__.").replace("__pseudomethod__..", "..").replace("..__pseudomethod__", "..") ## parse pseudomethod syntax
    s = s.replace("\nfrom .__pseudomethod__.", "\nfrom ..").replace(" from .__pseudomethod__.", " from ..") ## ignore .. notation in relative imports
    node = ast.parse(s, fpath, mode); node = self.visit(node); return node ## parse pseudomethod node

  ## recursively print nodes in ast object for debugging
  @staticmethod
  def printnode(node, depth = ""):
    s = node.__dict__.items()
    s = "    ".join("%s %r" % x for x in sorted(node.__dict__.items()))
    print( "%s%s\t%s" % (depth, str(type(node)), s) )
    for x in ast.iter_child_nodes(node): parser.printnode(x, depth = depth + " ")

  ## hack node if it contains __pseudomethod__ attr
  def visit_Call(self, node):
    x = node.func
    if type(x) is ast.Attribute:
      x = x.value
      if type(x) is ast.Attribute and x.attr == "__pseudomethod__": ## a..b(...) -> b(a, ...)
        node.args.insert(0, node.func.value.value)
        node.func = ast.copy_location(
          ast.Name(node.func.attr, ast.Load()), ## new node
          node.func) ## old node
    for x in ast.iter_child_nodes(node): self.visit(x) ## recurse
    return node



import imp ## import hook
class _importer(object):
  py3k_syntax = None ## identifier
  magic = "\nfrom __future__ import py3k_syntax\n"

  def __init__(self):
    sys.meta_path[:] = [self] + [x for x in sys.meta_path if not hasattr(x, "py3k_syntax")] ## restore sys.meta_path
    sys.path_importer_cache = {} ## reset cache

  def find_module(self, mname, path = None):
    if 0 and DEBUG: print( "py3k_syntax find_module(mname = %s, path = %s)" % (mname, path) )

    if path and len(path) is 1:
      x = path[0] + "."
      if mname[:len(x)] == x: mname = mname[len(x):] ## import from package

    try: file, fpath, desc = imp.find_module(mname, path if path else sys.path); tp = desc[2]
    except ImportError: return

    if tp is imp.PY_SOURCE: pass
    elif tp is imp.PKG_DIRECTORY: fpath += "/__init__.py"; file = open(fpath)
    else: return

    s = "\n" + file.read() + "\n"; file.close()
    if self.magic not in s: return ## no py3k_syntax magic found in file
    s = s.replace(self.magic, "\nfrom __future__ import with_statement, division, print_function; from asciiporn import *\n", 1)
    s = s[1:-1] ## preserve lineno (for debugging)

    self.found = s, fpath, desc, tp; return self

  def load_module(self, mname):
    s, fpath, desc, tp = self.found
    if 0 and DEBUG: print( "py3k_syntax load_module(mname = %s, fpath = %s, desc = %s)" % (mname, fpath, desc) )

    if mname in sys.modules: m = sys.modules[mname]; new = None ## if exist: use existing module
    else: m = sys.modules[mname] = imp.new_module(mname); new = True ## else: new module
    try:
      node = parser().parse(s, fpath, "exec")
      c = compile(node, fpath, "exec"); exec(c, m.__dict__)
      if tp is imp.PKG_DIRECTORY: m.__path__ = [os.path.dirname(fpath)] ## package.__path__
      m.__file__ = fpath; m.__loader__ = self.load_module; return m
    except:
      if new: del sys.modules[mname] ## if new module fails loading, del from sys.modules
      print( "\nFAILED py3k_syntax load_module(mname = %s, fpath = %s, desc = %s)\n" % (mname, fpath, desc) ) ## notify user exception originated from failed py3k_syntax import
      raise
importer = _importer()



import __builtin__ as builtins, itertools
if 1: ## builtins
  filter = itertools.ifilter
  filterfalse = itertools.ifilterfalse
  map = itertools.imap
  range = xrange
  zip = itertools.izip
  zip_longest = itertools.izip_longest
  def oct(x): return builtins.oct(x).replace("0", "0o", 1)
  def reload(m):
    try:
      if not importer.find_module(m.__name__, path = [os.path.dirname(m.__file__)]): raise ImportError
    except: return builtins.reload(m)
    return importer.load_module(m.__name__)



if "_asciiporn" in globals(): reload(_asciiporn)
import _asciiporn; from _asciiporn import *; from _asciiporn import _asarray
