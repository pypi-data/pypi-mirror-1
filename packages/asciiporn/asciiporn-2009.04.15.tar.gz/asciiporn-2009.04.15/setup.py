README = """
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

here are some quick example usage (within an ssh terminal):

  >>> ## print image file as colorized ascii art in ssh terminal
  >>> from asciiporn import img2txt
  >>> print img2txt("mario.gif")

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
"mario.gif".  its a fairly large image, so u prolly want to scale it down
to 0.5 (or less):
  >>> colortxt = asciiporn.img2txt("mario.gif", scale = 0.5)
  >>> print( colortxt )

  ... beautiful color image appears ^_-

  >>> plaintxt = asciiporn.img2plaintxt("mario.gif", scale = 0.5)
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
  >>> plaintxt = asciiporn.img2plaintxt('mario.gif', scale = 0.5, invert = True)
  >>> print( plaintxt )

  ... b/w img w/ colors inverted.  may look funny now :/
      but it'll b normal when pasted in document

################################################################################
RECENT CHANGELOG:
20090407
  fixed installation bugs
  added retro-gif feature
20090328
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



## init
NAME = "asciiporn"
MANIFEST = """
screenshot_mario.gif
screenshot_plot.gif

MANIFEST
README
setup.py

asciiporn/__init__.py
asciiporn/main.py
asciiporn/mario.gif
asciiporn/lucida06x10.bmp

asciiporn/weave/__init__.py
asciiporn/weave/accelerate_tools.py
asciiporn/weave/ast_tools.py
asciiporn/weave/base_info.py
asciiporn/weave/base_spec.py
asciiporn/weave/build_tools.py
asciiporn/weave/bytecodecompiler.py
asciiporn/weave/c_spec.py
asciiporn/weave/catalog.py
asciiporn/weave/common_info.py
asciiporn/weave/converters.py
asciiporn/weave/cpp_namespace_spec.py
asciiporn/weave/doc
asciiporn/weave/doc/tutorial.html
asciiporn/weave/dumb_shelve.py
asciiporn/weave/dumbdbm_patched.py
asciiporn/weave/examples
asciiporn/weave/examples/array3d.py
asciiporn/weave/examples/binary_search.py
asciiporn/weave/examples/cast_copy_transpose.py
asciiporn/weave/examples/dict_sort.py
asciiporn/weave/examples/fibonacci.py
asciiporn/weave/examples/functional.py
asciiporn/weave/examples/increment_example.py
asciiporn/weave/examples/md5_speed.py
asciiporn/weave/examples/object.py
asciiporn/weave/examples/print_example.py
asciiporn/weave/examples/py_none.py
asciiporn/weave/examples/ramp.c
asciiporn/weave/examples/ramp.py
asciiporn/weave/examples/ramp2.py
asciiporn/weave/examples/support_code_example.py
asciiporn/weave/examples/swig2_example.py
asciiporn/weave/examples/swig2_ext.h
asciiporn/weave/examples/swig2_ext.i
asciiporn/weave/examples/tuple_return.py
asciiporn/weave/examples/vq.py
asciiporn/weave/examples/vtk_example.py
asciiporn/weave/examples/wx_example.py
asciiporn/weave/examples/wx_speed.py
asciiporn/weave/ext_tools.py
asciiporn/weave/info.py
asciiporn/weave/inline_tools.py
asciiporn/weave/platform_info.py
asciiporn/weave/scxx
asciiporn/weave/scxx/README.txt
asciiporn/weave/scxx/dict.h
asciiporn/weave/scxx/list.h
asciiporn/weave/scxx/notes.txt
asciiporn/weave/scxx/number.h
asciiporn/weave/scxx/object.h
asciiporn/weave/scxx/scxx.h
asciiporn/weave/scxx/sequence.h
asciiporn/weave/scxx/str.h
asciiporn/weave/scxx/tuple.h
asciiporn/weave/scxx/weave_imp.cpp
asciiporn/weave/setup.py
asciiporn/weave/size_check.py
asciiporn/weave/slice_handler.py
asciiporn/weave/standard_array_spec.py
asciiporn/weave/swig2_spec.py
asciiporn/weave/swigptr.py
asciiporn/weave/swigptr2.py
asciiporn/weave/tests
asciiporn/weave/tests/scxx_timings.py
asciiporn/weave/tests/test_ast_tools.py
asciiporn/weave/tests/test_build_tools.py
asciiporn/weave/tests/test_c_spec.py
asciiporn/weave/tests/test_catalog.py
asciiporn/weave/tests/test_ext_tools.py
asciiporn/weave/tests/test_inline_tools.py
asciiporn/weave/tests/test_scxx.py
asciiporn/weave/tests/test_scxx_dict.py
asciiporn/weave/tests/test_scxx_object.py
asciiporn/weave/tests/test_scxx_sequence.py
asciiporn/weave/tests/test_size_check.py
asciiporn/weave/tests/test_slice_handler.py
asciiporn/weave/tests/test_standard_array_spec.py
asciiporn/weave/tests/test_wx_spec.py
asciiporn/weave/tests/weave_test_utils.py
asciiporn/weave/vtk_spec.py
asciiporn/weave/weave_version.py
asciiporn/weave/wx_spec.py
"""



import imp, os, subprocess, sys; from distutils import command, core, dist; DEBUG = 0
if sys.version_info[0] is not 2: raise Exception("asciiporn requires Python 2.x")
if sys.version_info[1] < 6: raise Exception("asciiporn requires Python 2.6 or higher")
def quicktest(): DISTRIBUTION.run_command("build"); system("python -c 'import %s; %s.quicktest()'" % (NAME, NAME))
def system(cmd): print( cmd ); return subprocess.check_call(cmd, shell = True)



## dependency check
print( """
  %s requires:
    Python 2.6
    Python Imaging Library
    numpy
  make sure these packages are installed before running setup
""" % NAME )
def missing_dependency(name, url):
  raise Exception("""

  %s requires %s
  please download & install %s from:

  %s

  or from ur os distro.
  then quit this shell & rerun setup in a new shell
""" % (NAME, name, name, url))
try: imp.find_module("PIL")
except: missing_dependency("Python Imaging Library", "http://www.pythonware.com/products/pil/")
try: imp.find_module("numpy")
except: missing_dependency("numpy", "http://www.scipy.org/Download")



## developer stuff cmdclass
class dev(core.Command):
  description = "setup commands for developer"
  user_options = [
    ("doc", None, "print doc"),
    ("pkginfo", None, "create pkg-info"),
    ("quicktest", None, "run quick tests"),
    ]
  def initialize_options(self):
    for x in self.user_options: setattr(self, x[0], x[1])
  def finalize_options(self): pass
  def run(self):
    quicktest()
    if self.doc: system("python -c 'import asciiporn; help(asciiporn)'")
    elif self.pkginfo: DISTRIBUTION.metadata.write_pkg_file(open("PKG-INFO", "w"))
    elif self.quicktest: pass



## custom Distribution class
class Distribution(dist.Distribution):
  def __init__(self, *args, **kwds):
    dist.Distribution.__init__(self, *args, **kwds); global DISTRIBUTION; DISTRIBUTION = self; import asciiporn
    self.cmdclass["dev"] = dev; self.metadata.__dict__.update(asciiporn.main.__metadata__)
  def run_command(self, command):
    cmd_obj = self.get_command_obj(command)
    def null(*args, **kwds): pass
    cmd_obj.byte_compile = null ## disable byte compiling
    if command == "sdist": quicktest() ## pre sdist
    dist.Distribution.run_command(self, command)

    if 0 or DEBUG:
      print( "DEBUG command = %s, cmd_obj = %s, sub_cmd = %s" % (command, cmd_obj, cmd_obj.get_sub_commands()) )
      if 1 and command in "install sdist".split(" "):
        print( "DEBUG %s attr" % command )
        for k, x in sorted(cmd_obj.__dict__.items()): print( "\t", k, "\t", x )

    if command == "build":
      force = cmd_obj.force
      open("MANIFEST", "w").write(MANIFEST)
      open("README", "w").write(README)

    if command == "install":
      install_path = os.path.join(cmd_obj.install_lib, "asciiporn")
      system("cp -a asciiporn/weave %s" % install_path)
      system("cp -a asciiporn/mario.gif %s" % install_path)

    if command == "sdist":
      if os.path.exists("index_html"): src = cmd_obj.archive_files[0]; dst = "index_html/%s" % os.path.basename(src); system("cp -a %s %s" % (src, dst))



## main loop
core.setup(
  distclass = Distribution, ## custom Distribution class
  packages = ["asciiporn"],
  py_modules = [],
  classifiers = [
  "Development Status :: 3 - Alpha",
  # "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "Intended Audience :: End Users/Desktop",
  "Intended Audience :: Science/Research",
  "License :: OSI Approved :: GNU General Public License (GPL)",
  "Natural Language :: English",
  "Operating System :: POSIX",
  "Operating System :: POSIX :: Linux",
  "Operating System :: Unix",
  "Programming Language :: C",
  "Programming Language :: Python",
  "Programming Language :: Python :: 2.6",
  # "Programming Language :: Python :: 2.7",
  "Topic :: Multimedia",
  "Topic :: Multimedia :: Graphics",
  "Topic :: Multimedia :: Graphics :: 3D Modeling",
  "Topic :: Multimedia :: Graphics :: 3D Rendering",
  # "Topic :: Multimedia :: Graphics :: Capture",
  # "Topic :: Multimedia :: Graphics :: Capture :: Digital Camera",
  # "Topic :: Multimedia :: Graphics :: Capture :: Scanners",
  # "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
  # "Topic :: Multimedia :: Graphics :: Editors",
  # "Topic :: Multimedia :: Graphics :: Editors :: Raster-Based",
  # "Topic :: Multimedia :: Graphics :: Editors :: Vector-Based",
  "Topic :: Multimedia :: Graphics :: Graphics Conversion",
  # "Topic :: Multimedia :: Graphics :: Presentation",
  "Topic :: Multimedia :: Graphics :: Viewers",
  "Topic :: Scientific/Engineering",
  # "Topic :: Scientific/Engineering :: Artificial Intelligence",
  # "Topic :: Scientific/Engineering :: Astronomy",
  # "Topic :: Scientific/Engineering :: Atmospheric Science",
  # "Topic :: Scientific/Engineering :: Bio-Informatics",
  # "Topic :: Scientific/Engineering :: Chemistry",
  # "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
  # "Topic :: Scientific/Engineering :: GIS",
  # "Topic :: Scientific/Engineering :: Human Machine Interfaces",
  "Topic :: Scientific/Engineering :: Image Recognition",
  # "Topic :: Scientific/Engineering :: Information Analysis",
  # "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
  "Topic :: Scientific/Engineering :: Mathematics",
  # "Topic :: Scientific/Engineering :: Medical Science Apps.",
  # "Topic :: Scientific/Engineering :: Physics",
  "Topic :: Scientific/Engineering :: Visualization",
  # "Topic :: Software Development",
  "Topic :: Software Development :: Libraries",
  "Topic :: Software Development :: Libraries :: Python Modules",
  # "Topic :: System :: Emulators",
  # "Topic :: System :: Shells",
  # "Topic :: System :: System Shells",
  # "Topic :: Utilities",
  ])
