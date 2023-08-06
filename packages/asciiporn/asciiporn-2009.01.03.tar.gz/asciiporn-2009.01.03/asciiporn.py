"""
################################################################################
this is a moderately complex python3.0 script for performing fast, high quality
graphics -> ascii conversions.  it relies on py3to2 in order to use PIL &
numpy extension modules.  for performance, portions of it have been inlined w/
direct C code using scipy.weave.
asciiporn can easily render & display megapixel images on a 1ghz 500mb machine.

asciiporn's main purpose is to provide ascii-converted, high-quality,
color-3d plots within an interactive python txt terminal.
however, its fast txt-rendering engine can also b used for viewing image files.
screenshots of both applications r included w/ this distribution.

if something fails, try updating ur install of py3to2 to the latest version @:
http://pypi.python.org/pypi/py3to2

how to enable 256 color in putty: http://www.emacswiki.org/emacs/PuTTY#toc2
how to enable 256 color in xterm: http://www.frexx.de/xterm-256-notes/

asciiporn is hard-coded to use lucida-console font, but courier font will work
as well.  the screenshots show putty ssh w/ lucida-console 5pt.

AUTHOR:
  kai zhu
  kaizhu@ugcs.caltech.edu

REQUIREMENTS:
- posix/unix os (Windows currently unsupported)
- py3to2                  http://pypi.python.org/pypi/py3to2
- numpy                   http://www.scipy.org/Download
- Python Imaging Library  http://www.pythonware.com/products/pil

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

start up the py3to2 interpreter by typing "py3to2" in ur terminal &
import asciiporn:

  $ py3to2

  Python 2.6.py3to2 (r26:66714, Nov 18 2008, 00:56:43)
  [GCC 3.4.6 20060404 (Red Hat 3.4.6-10)] on linux2
  Type "help", "copyright", "credits" or "license" for more information.
  >>>
  >>> import asciiporn, numpy
  created...
  py3k server starting...
  >>> ...py3k server started w/...
  >>>

2d plots take 2 main arguments:
  y - a list of functions to plot
  trange - t domain

  >>> asciiporn.plot(
  ...   y = [             # list of single argument functions
          numpy.cos,
          numpy.sin,
          lambda t: numpy.sin(t + 0.25),
          ],
  ...   trange = [0, 7],  # range of t
  ... )


SIDEVIEW Y...
l7Y~_-----_>r'llT''7*s_--------------------------------------------_^*'llTi(_---
|   `T+ `(`,r'      Tc`Y_                                        .C         `>,
|     (*)_/`         `*_`>`                                    _*             _(
|    ,' iC             'v `C                                  .'             .``
|   .``/' \`             \``i                               `/             `/ `*
|  /  Y    '              '` \`                            ``             `* `'
|_/ `c      '_             '_ '`                          _'             _' _`
|> `'        ``             `` ``                        ,'             `' .`
c `i          `,             `, '_                      ,`             ,` .'
|`i            `_             `_ ``                    _`             _` _
_'              `_             `c ``                  .'             _' _`
 ----------------``-------------'`-`,---------------- '-------------.'-.`-------
|                 ',             '` `,              ,'             ,' .`
|                  `,             `_ '_            _`             ,` .'
|                   `_             `_ ``          _`             _` )
|                    ``             `. ',        .'             .' .`
|                     '_             `_ `_      )              )' (`
|                      `v             `i `,    (              .``/
|                        \`             \``i `/             `/ `*
|                         '_             ?_ J'             _` _C
|                          'v             'v'`.`          /'_/`
|                            '(`        `>' '(`'L      `>'_v'
|------------------------------`*L_,,_.r`-----`*L_~,_.r_>r'---------------------


3d plots have an extra argument:
  zrange - z domain

  >>> asciiporn.plot3d(
  ...   y = lambda t, z: numpy.sin(t + t*z)  # y is now a fnc taking 2 args (t, z)
  ...   trange = [0, 7],                     # range of t
  ...   zrange = [0, 0.25],                  # range of z
  ... )


SIDEVIEW Y...
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

TOPVIEW Z...
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

  >>> t =  numpy.arange(1000)   # create t coord datapoints
  >>> y =  numpy.sin( 0.01*t )  # create y coord datapoints
  >>> yt = list(zip( y, t ))    # create (y,t) datapoint pairs
  >>> asciiporn.plot( yt = yt )


SIDEVIEW Y...
|--------_(?ll*C-------------------------------------------_>C''Y(`-------------
|      `/l     `X_                                        y'      Jc
|     _/         `c                                     `/`        'v
|    _^           ?L                                    /           `v
|   `/             ?_                                  /             `v
|   /               J_                                ,`              ?c
|  ,`                )                               ~'                `_
| ~'                 `Y                             _*                  \
|_^                   `c                            7                   `Y
|/                     J_                          s`                    `c
,`                      \                         _'                      ^`
C----------- -----------`v----------- -----------`r------------------------Y----
|                        ?_                      v                         `c
|                         \                     ~'                          `_
|                          Y                   _^                            \
|                          `c                  /                             `v
|                           `_                ,                               ?c
|                            \               ,'                                `
|                             \             _C
|                             `Y           _^
|                              `V`        _*
|                                \_      )'
|---------------------------------'>_,_.*---------------------------------------

################################################################################
IMAGE USAGE:

in this example, u'll b loading the image file included w/ this distribution,
"mario.jpg".  its a fairly large image, so u prolly want to scale it down
to 0.5 (or less):
  >>> colortxt = asciiporn.img2txt("mario.jpg", scale = 0.5)
  >>> print( colortxt )

  ... beautiful color image appears ^_-

  >>> plaintxt = asciiporn.img2plaintxt("mario.jpg", scale = 0.3)
  >>> print( plaintxt )

  ... rather plain b/w img -_-, but u can copy & paste in documents ...


  @@$  !vvV*._ + !+~,_ (?  _ @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  7$$  `X g&gp+`Y-L`'\'T(L`  w$@@$@@@@M'}r_*V@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
       - `@@@b    L   r~M[ 4Y,w'i`(~Vkr\{#4ggp@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
       (> `Zfl `  '   |q&@gKg]@n>,Z'l lg@MW@MK@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
  '`   a   '!'   +   o=@@Z$@9MWY!> ,_a@M@@$@@$M3M@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
       }   ``  ' l(LtiL@M@$#m=@1T_`Yd@@M@@$@@#$R'[MN@@@@@@@@@@@@@@@@@@@@@@@@@@@@
F}>_   A>' `   '    (S##WWNIAj7G!`2L$M8W$}g$jD$@``!>LI#@@@@@@@@@@@@@@@@@M@@@@@@@
*)[-T  @    `      _`   ` `fw&|T!v `k&@M@@@@@MMhT=i ` }w@@@@@@@@@@@@@@@@@@M@@@@@
 ` ?   3   `'      `>-  ',` !Yx p\gp{l  ` `  GMgM ` _`r  }$@@@@M@@@@@@@@@@@@@M@@
    '  N     `      )P '!1`  3)l@MMMWk(( Vy^a#@@@` '`)~`j!  `{#@M@M@@@@@@@@@@M@@
$j _   a   `     `' '=m=TkRga@$M` _(f3Mw-$8G##M$l  `' | ~?j_  73@@M@@@@@@@@@MM@@
@W@@p JV  '         `ilfETjJJ3^'~dWguliI_W@&A&M@  ' '_'   -Jt> , @M@@@MM@@@M@@$@
g@@@@p `          '   (s(_r_\ `  gbMwMp\[Wq&&#@@Mg#g$yj,` \~=L  ,_ @@M@@@@@@@@@@
@M@@@@b   ``      ` ' 'yew#|-3V]EAMM@&$ 'AV3Zw##@@@$$@@Wy{ Lyj     '  fM@@@@M@@@
@MM@@@@p  g    `     /#f_ '7t`{y~!=>7N]L}mty&@M@MI&k@A@$AM#@@M'- _    ,_,_@@$!(I
@@@@@@@@@&#    '_ptL^=fv~--y_|'_(x/\'LCeS@@&W&W]YT)[c\)7fWM&m``AD!  r~Y}'7#'LGM$
@$@M@@@@@@@&_ (WVM7]'!'`! `` T>`-YS   r',J `'``(`i3'=,-` [R}@#Mgg_g@&p*'__Q7MAW@
@@$@@M@@@@@@M(?>vnj`|`r`_ `_``! _v+` ' z ' `t~x~-(7}?_,-' ]}OMM@@M@$@@ `&@#)UX6#
M@WZ%w@@@M@@Mh~rt'+-i)=`''`v `'`~'i>|'  > oC|`)\'rvn^'(_ !WTn[M@@M@@@$ `$@$posZ'
@MMM@@@@@@&@@\7 _C= -`!` ^`?` t&Ncm6'`!  > i>`'_-'T!rV' ' [W`{\&$  N@$ }@@@#gqa_
jcRf#@@@$@@@R`Y   -_'t'?`'i Y|=MT+>l` 1`` Y'r `'J'  _' `  RE~i\'@~ ]&@p#@$A#@W&M
&M@m&@@@$@@W' `_@*`_'r'Lj|`LL'rYicJqp &L`' `_| -''  /_'   _]=`\ggp ]FW$$R&y@MM@#
@@@M@@@@@@@& (g$Y '+`-!r~r'iT(^?\1~3@pAF`'l'` `_    |Vr   'T{@M@M@K''sh{=AW$M@@$
MM@@$@@@M@$#(y@w@me=k`''7,j|cnq#M@x!E@M$gg```>r``_ )'iLL    fM@@@@B+`~i=WV9M@#MM
#M@M$$@MM@#DVM#$@%#F=&r>!(L(3jA@&$c@@MMZ{I  '> '` L!`tn(`_`  i##$@@$ ~_wy&@$@#WE
MMPMPl``jQ@]kYIM@M'(#@P=?_='>\##MF|@@M@MM'`' r '>!~7i7ry+!_   '3@&$MM&N@@M@@@M@B
     ( ryo@Ew`*T'w`>b@]`S]ij-=(^--'`tZAL    - ! Ts('~ oVc_`    3@M@M@Z}&@@@@@@@&
 ' ' ''`' >`iF`_W9`_ccvJt??-sfYXC]! !k#@     ,,?S,riv/v}^!`    A#@@#N$@@M@@$@W&M
 _!   ` '   '``'lTx'_\' 2j-w(7zLL'>_''&3`,  J  \`yr  _=Avs`i@$e@@@@$RR$@@MM@]g&&
` r`   `   ~E@apg| `i-t1?L,-}+T_|r\   i?`E    ` +T'`(i^Ss_Ti;`V$M@@M!'J@#&@@@M@M
i|`       ' #AM@@W  F`j+\'{Li'viyr|    _dk l`r  ,!i| ``'==[j=&&@@MM_}C '  'q@W##
 -   `  ' ''`(qw#  >_'7 !r~'k|'Y|/_`L `  `  >`|t r+  `_`+'PFj@$@#@'_$#L  !-|Y&G$
 `    (     a@WMh3_L'_'+'~yrf|?S)uX`l>     !  ` )!\!\     '__@@@@}pQWWR    !!@@$
 '     g_   /#$@R``v >( ``T`|_i)p`j''     !` _ (v(iJr ' *`__#B@@W@@RWI1     '(M@
 ` ` ' @@B    @W`T|j!' `(^`r|jj[w-^>    i `'_ |( \\Yx`, _'i@&M@N$WWW#Mf      `d@
 `     P$]k   }B'`,>(\ -`x)!\??' t  `       '''`? i~'_`JsC*Z@@@$$@#@j'    `   tY


actually, the plaintxt prolly won't look well when pasted,
b/c most document readers invert the color:
  >>> plaintxt = asciiporn.img2plaintxt('mario.jpg', scale = 0.3, invert = True)
  >>> print( plaintxt )

  ... b/w img w/ colors inverted.  may look funny now :/
      but it'll b normal when pasted in document


@@   @$Mb$RM$M&$NM#@@@@$@#@M@*           _,
@@ggg@@$@#F`'@@$#M&Wg&MNM@@@$P_ ____  yNWMMMg_
M@@@@@@W$M   }@@M@NMM$&$6M@$AMR#@M#@&&$&qjE'f4_
M@@M@@M$$@&gp@@@@@&@@&$#`''@Pk&$$E&#@#$#'''  TL
M@@@@@@k$@&$M$MM$$@@@$w `^t [Y]dMQ&@MP`      iJ&_
@@@@@M@b@@MM$@@@@@@@BMhs ___i==]#W@#Bv    ((_' =]m_,
[I}M@@@U#@MM&M@@M@@W$ggg}l[Nhg@VM@&Mt~/i=>J(uaj!M&ABAw,
&#k${@@1@@@@@@@@@@@@@@MM@M@mjkNFN@@@M{,pyZj,_``@A&M#N&&p
@M&$&&@{&@@$@@@&M@&M@@@@M@MMM@@$@W#@h@M$@M@@@# '(@@@#@M$&Ma__
@@$M@M@y$M@@@$@@@@&@M@MMMM#$AE]M@__,L#@@MWGFE_  wM@@NM@#$BN@@py             '
{M@M@@@f#@@#M@@@@M$#M)[EEr}$Xy=j&##M%Wg=X=&YA  a@@@@M@#$gMWM@AMw
|>  M@@eM@M@@M@M@@@@@b#$4g#&#p@$$$'(}gB@#j*PC`( @M@B@@&@#&V$@@$M#y}
'    3$@@@@@@@@@@@@$@@@$@@MM@@#@@]GgD'}WgFc'`j; '`'`rh@M@&M@{$@$&&#E
      @M@@@@@@@@@@@@@@Mp$p[gWWHjtg)x>^k@&aw#=r    (i _ O@@$MMw&M@@$$B@Mg_``
       #M@M@@@@@@@@@M$Hg&&&@#M]W&A6Mbmj@PyA@7   _A=AkMK>+,/._qNM@M@@MMMMW&1_w#MM
    '    `J$@@@@#$[&#@mNgAM$@MMMW&&&#$@mPs]'fTg#k#kbR@GpWt[/Y@@k}M@#M]kqM$j&$)cE
            @M@$@T##M&##@@$&@@#WWWW@@@@$@{@@M$##MMNN$#&&@bkzu]'*J@' 'U$gM@NU'yJ
 s          dM=#@$@###&@&$@@M&#$@&@WW@$WM@@@W@W@@M%$MN@@@$d&ju+  `    M$' `@AWR)
  _w*)  `   -g@$@NdW@@N@@$@@w#M@#@M&MM@B@$##M@@MM@$@MHN@@@1@$=>r _,'((@$  `@WWMM
 _ '`_   '  \MW&##RWgM&@@@@&&$Wj3W#&@@MM##MM@WW@MWQMW%@@M@gQ%]E(HM@b ~MM' _-')(@
rRLPk`   ' iZ&@&$@M##&&NM@W#WN@u$MAMW&MMM@$@@M@$@@@$W&@@@MWYA$#}_@@@`_E(t2=` ''X
```''`      #@@@R@B]WM@#$@@@MWWA@8@W#@(@WW@W$$&%%&#@&M@#@@WV9MM&rU$[lgR-g#J' `>#
  '        X$@Fiw@&&M@gMN@@@#M8BM&WWY$7@MMMM$M#$@@@MM@@M@@&$I'    &g&$=y#V
         r_3@k='_f$5gMMNMM@MbQR'i0&$=(`FPf@@M@#M@@@@####@@@@1'  ` `@@@k$E7\ ' '_
 '   q __R*@W{' `'lgP[&&9&#G@M_` _$R'>)~#y@$&MM@$@@$&#M#&MMM@p_'   >&M&ML'`   L#
1gpgyM##j& $]WW\7-@M!j]@@@@#@#1p_yWb+''!jN@@@@@W@M&$$R@A@M@$@@&^    f['>( `'  C[
@@@@$M@MNMgpa@AM$&&#wyQ@N#N@W#@@#g#@UEaQ@@N$@@##A@WW@M&&$A@M@$@W     =n'_   `7`T
@#W@&&g@M@@&M@W@R#@M@MMW$e@@MAM@&MA@[jbC@@@M@B@@9M$@WW#MW#@&@@$>` ` _=+!   '  '=
B#$@@@M@@M$@MM@@Wg#MM@&&[$%#2&$#MM&$W$Wy&&M@$#M#@AWM@9NIN@@MR1N    '_'k|`   ~?i+
&$#@M@@@M@@$@u]$MN@&@@@@#ggNBW@Wwq#@$&@@@AM@@@@@@M&$M@@k&XMMN&\7|  }M@ggp`( ' `}
@@&&@@@@M@&@g;?J @&@&E$$#@@@@@@WWMM@@@@MyVM@$&M@M&@@@@WWp4E@y7     &f#@@#@M#j++`
M&&@M@@@@@M@$$m?S@&AW@W&@@#M8WM&@&9$#&@M@MM@@@&#$&M#MM&M@Aq4#-' ` g#(C@@@&@$yL(A
M@#@@@#$$@@@B]-,#&%p@@W@M@@#@&M&#MM@$@@@@@@@M@@@@M&@W@@M@WW@$_    ]IvbmMMM@@@bJr
@@M@@@$c@@M@$p  3@B$$@N##bM$@$ad&&&@@@@@$M$M@@MM@MW$@@@@$$##\    +^wJ-w@@@@@$#]T
@@@M@@@i_[@@@M>'W}@W@@#&@w#WM@X@@$@@M@@@$@#@@@M@@@M$MkM@M$]k`' Jm4F_lyg@@@@@@#b?
@&@$@#$aKj@@@@E2###W@@@N&M@$@@@@&#@@@M@@@$@M@W##&@gg@#@MW#AA   !z'~]Zg&@$MMM@@@W

################################################################################
RECENT CHANGELOG:
20090103
  rewrote 3d plotter
  fixed more 64bit issues
20081123
  fixed bug where 64bit  gets truncated to 32 on 32bit machine
  256 color support
20081119
  fixed bugs in setup.py
"""
__author__ =	"kai zhu"
__author_email__ =	"kaizhu@ugcs.caltech.edu"
__description__ =	"""
ssh terminal-based, high-quality, 3d plotter & image viewer.
(screenshots using putty ssh terminal included)
"""
__download_url__ =	None
__keywords__ =	None
__license__ =	"BSD"
__maintainer__ =	None
__maintainer_email__ =	None
__obsoletes__ =	None
__platforms__ =	None
__provides__ =	None
__requires__ =	["PIL", "py3to2", "numpy"]
__url__ = "http://pypi.python.org/pypi/asciiporn"
__version__  = "2009.01.03"
## end setup info

## import asciiporn; reload(asciiporn); from asciiporn import *
from __future__ import py3k_syntax
import itertools, os, sys; from itertools import *
import numpy, weave; from numpy import *
if "DEBUG" not in globals(): DEBUG = 0
if "YRES" not in globals(): YRES = 1 / 3
def quicktest():
  img2plaintxt.test()
  img2txt.test()
  plot3d.test()

if 1: ######## general
  def echo(x): return x

  def enumerate(arr, i = None):
    if i: return zip(count(i), arr)
    return builtins.enumerate(arr)

  def flatten(*arr): return arr ..walktree() ..tuple()

  def isint(x):
    try: x & 0; return True
    except: return False

  def _profile(exe, n = None, lines = 64):
    import cProfile as profile; import pstats
    if n is not None: exe = 'for i in range({0}): {1}'.format(n, exe)
    x = pstats.Stats(profile.Profile().run(exe)).sort_stats('time'); x.print_stats(lines); return x

  def screensize(): import re; s = system("stty -a"); row, col = re.search("rows .*?(\d*).*?columns .*?(\d*)", s).groups(); return int(row), int(col)

  def shapes(*arr): return [shape(x) for x in arr]

  def strjoin(s, _ = ""): return _.join(s)

  def system(exe): import subprocess; exe = subprocess.Popen(exe, shell = 1, stdout = subprocess.PIPE, close_fds = 1).stdout; s = exe.read(); exe.close(); return s

  def walktree(tree, iterable = iterable, not_ = None, depth = -1):
    def walk(tree, depth):
      if iterable(tree) and depth:
        for x in tree:
          for y in walk(x, depth - 1): yield y
      else: yield tree
    if not_: istree = lambda x: not isleaf(x)
    return walk(tree, depth)

######## class
class savestate(object): ## use when subclassing extensions to allow serialization of  self.__dict__
  def __savestate__(self): state = self.__dict__.copy(); state["__self__"] = self; return state

  @staticmethod
  def __loadstate__(state): state = state.copy(); self = state["__self__"]; del state["__self__"]; self.__dict__ = state; return self

class _asarray(ndarray, savestate): ## array w/ serializable states
  def __new__(self, arr, dtype = None, order = None):
    arr = numpy.asarray(arr, dtype, order)
    try: self = ndarray.__new__(self, arr.shape, arr.dtype, arr.data)
    except: return  _asarray.__new__(self, arr.copy(), dtype, order)
    if arr.strides: self.strides = arr.strides
    return self

if 1: ######## math
  EPS = MachAr().eps; TINY = MachAr().tiny; HUGE = MachAr().huge
  STD = 0.682689492137085897170465091264075844955825933453208781974788900; STD2 = 0.954499736103641585599434725666933125056447552596643132032668000
  array = numpy.array
  rng = random.random
  stdev = numpy.std
  variance = numpy.var

  # def asnd(n, arr, dtype = None, contiguous = True, transpose = None):
    # arr = asarray(arr, dtype = dtype)
    # if arr.ndim != 3: arr = arr.reshape(r_[1, -1, arr.shape[-2:]][-3:])
    # if transpose: arr = arr.T
    # if contiguous and not arr.flags.contiguous: arr = arr.copy()
    # return arr

  def as2d(arr, dtype = None, transpose = None, contiguous = None):
    arr = asarray(arr, dtype = dtype)
    if arr.size == 0: return arr.reshape(0, 0)
    arr = arr.reshape(-1, arr.shape[-1])
    if transpose: arr = arr.T
    if contiguous and not arr.flags.contiguous: arr = arr.copy()
    return arr

  # def as3d(arr, dtype = None, contiguous = True):
    # arr = asarray(arr, dtype = dtype)
    # if arr.ndim != 3: arr = arr.reshape(r_[1, -1, arr.shape[-2:]][-3:])
    # if contiguous and not arr.flags.contiguous: arr = arr.copy()
    # return arr

  def as64(x):
    if iterable(x): return asarray(x, dtype = int64)
    return int64(x)

  def bitshift64(a, b): return as64(a) << as64(b)

  def divceil(a, b): return (a + b - 1) // b

  def divround(a, b): return (a + (b >> 1)) // b

  # def find2nd(arr, x):
    # arr = as2d(arr, contiguous = True); n = arr.shape[-1]; x = (arr == reshape(x, (-1, 1))) ..asarray(dtype = uint8)
    # out = repeat(n, len(x)); out.fill(n); weave.inline("""
    # for(int i = 0; i < Nx[0]; i++) {
    # for(int j = 0; j < Nx[1]; j++) {
    # if(x[j]) {out[i] = j; break;}
    # } x += Nx[1];}""", ("out", "x")); return arange(len(out)), out

  def find2nd(arr, x):
    arr = as2d(arr, contiguous = True); x = reshape(x, (-1, 1))
    arr = asarray(arr == x, dtype = uint8); x = repeat(arr.shape[-1], len(arr)); weave.inline("""
    int i; const int Ni = Narr[0];
    int j; const int Nj = Narr[1];
    for(i = 0; i < Ni; i++, arr += Nj) {
    for(j = 0; j < Nj; j++) {
    if(arr[j]) {x[i] = j; break;}}}""", ("arr", "x")); return arange(len(x)), x

  # def _histogram(arr):
    # arr = asarray(arr, dtype = int); n = arr.max() + 1; assert arr.ndim == 1 and n < 0x10000, (arr.shape, arr.dtype, n); h = zeros(n, int)
    # weave.inline("""for(int i = 0; i < Narr[0]; i++, arr++){h[*arr] += 1;}""", ("arr", "h"))
    # return h

  def histogram2nd(arr):
    arr = as2d(arr, dtype = int, contiguous = True); n = arr.max() + 1
    assert 0 <= arr.min() <= n < 0x10000, (arr.shape, arr.dtype, arr.min(), n)
    h = zeros((len(arr), n), int)
    weave.inline("""
    int i; const int Ni = Narr[0];
    int j; const int Nj = Narr[1];
    const int Nh1 = Nh[1];
    for(i = 0; i < Ni; i++, h += Nh1) {
    for(j = 0; j < Nj; j++, arr++) {h[*arr] += 1;}}""", ("arr", "h")); return h

  def invzero(x, nan = nan): return 1 / x if x else nan

  ## refactor datapoints so that its evenly distributed along t-axis & # of points is a power-of-2
  def itp2(y = None, n = None, **kwds):
    y, t = dataZYT(y = y, parseonly = True, **kwds); y = y.T
    if any(t[:-1] > t[1:]): cll = t.argsort(); y = y[cll]; t = t[cll] ## sort along t-axis
    cll = t[:-1] == t[1:]
    if cll.any(): cll ^= True; y = y[cll]; t = t[cll] ## remove t duplicates
    if len(t) <= 2: return y.T, t
    if n is None: n = 1 << (len(t) ..log2() ..ceil() ..int()) ## next highest power-of-2
    dt = t[1:] - t[:-1]
    if n == len(t) and 1 - dt.min() / dt.max() < 4 * EPS: return y.T, t ## already evenly spaced & power-of-2

    y0, t0 = y, t; t = linspace(t0[0], t0[-1], n); y = empty((n, y0.shape[1]), dtype = float); y[[0, -1]] = y0[[0, -1]]
    d1 = (y0[1:] - y0[:-1]) * (1 / (t0[1:] - t0[:-1])[:, newaxis]) ## 1st derivative
    d2 = (y0[2:] - y0[:-2]) * (1 / (t0[2:] - t0[:-2])[:, newaxis]) ## 2nd derivative
    arr = transpose( (y0[1:-1], d1[:-1], d2), (1, 2, 0) ); itr = zip(t0[2:], arr); _t0 = -inf
    for i, _t in enumerate(t[1:-1], 1):
      while _t >= _t0: _t0, f = itr.next()
      dt = _t0 - _t; y[i] = dot(f, (1, dt, 0.5 * dt)) ## itp to 2nd order
    return y.T, t

  def monotonic(arr):
    if all(arr[1:] >= arr[:-1]): return 1
    elif all(arr[1:] <= arr[:-1]): return -1
    return 0

  def orequal(arr, i, x):
    arr = asarray(arr); i = asarray(i); x = asarray(x); assert i.shape == x.shape
    weave.inline("""for(int j = 0; j < Ni[0]; j++){arr[*i] |= *x; i++; x++;}""", ("arr", "i", "x"))
    return arr

  ## efficient 64 bit population count
  def popcount64(x):
    x = x - ((x >> 1) & 0x5555555555555555) ## count 2 bits
    x = ((x >> 2) & 0x3333333333333333) + (x & 0x3333333333333333) ## count 4 bits
    x = ((x >> 4) + x) & 0x0f0f0f0f0f0f0f0f ## count 8 bits
    x += x >> 8 ## count 16 bits
    x += x >> 16 ## count 32 bits
    x += x >> 32 ## count 64 bits
    return x & 127

  def rotate3d(x, y, z, t):
    inv = 1 / sqrt(x * x + y * y + z * z); x, y, z = x * inv, y * inv, z * inv; c = cos(t); s = sin(t); d = 1-c
    return [[x * x * d+c,   x * y * d-z * s, z * x * d+y * s],
            [x * y * d+z * s, y * y * d+c,   y * z * d-x * s],
            [z * x * d-y * s, y * z * d+x * s, z * z * d+c  ]] ..asarray()

  def roundint(x, dtype = int):
    if iterable(x): return asarray(x).round() ..asarray(dtype)
    return dtype(round(x))

  def ystack(*args): return vstack(as2d(x) for x in args)

  def zeropad(y, n): y = as2d(y); return (y, zeros((len(y), n))) ..hstack()

######## img2txt
class _img2txt(object):
  global X
  _ = ord(" ") ## convenience var for whitespace
  buf = empty(0, dtype = int64) ## internal buffer for outputting txt
  color = empty(0, dtype = int64) ## internal color buffer for outputting txt
  fres = r_[10, 6] ## row x col resolution of a character block
  mask = bitshift64(1, fres.prod()) - 1
  lucida = "AAAAAAAAAAAAQRAEARAAAIqiAAAAAAAAAEX5ylcUAACEVxwMRT0EAIBYKQylRgAAAKE4Zpt5AAAE\nQQAAAAAAADBCEARBIDAAA4EgCIIQAwAAsRkKAAAAAAAAEMRHEAAAAAAAAMAwCAEAAAAeAAAAAAAA\nAADAMAAAIAQhDCEIAQCAE0VRFDkAAIBREARBfAAAgANBCCF4AACAB0EMBDkAAADCKMmHIAAAgCcI\nDgQ5AAAAJwTNFDkAAIAHIQQhCAAAgBMlThQ5AACAE0UehBwAAAAAMAzAMAAAAAAwDMAwCAEAAEDM\nwEAAAAAAAD / wAwAAAAAEBmYEAACAJ0EIARAAAIAXdVUfeAAAAMMokieFAADAE0VPFD0AAAAnBEEg\ncAAAwBNFURQ9AACAJwiOIHgAAIAnCI4gCAAAACcEWSRxAABAFEVfFEUAAMBHEARBfAAAgIMgCIIY\nAABAlBRDkUQAAIAgCIIgeAAAQLRtV1VFAABANF1VlkUAAIATRVEUOQAAwBNFTxAEAACAE0VRFDkw\nAMCRJEeRRAAAACcIDAQ5AADARxAEQRAAAEAURVEUOQAAQBhJksIQAABAVFXVoygAAEAoMQgjhQAA\nQKQoBEEQAADAByGEEHwAABxBEARBEBwAgSAQBAJBIAAOgiAIgiAOAABBKIoSAQAAAAAAAAAAPwAE\nAgAAAAAAAAAAOBAn+QAAQRA0UxQ9AAAAAHhBEHgAABAEeVGUWQAAAAA40Rd4AAAYQXgEQRAAAAAA\neFGUWZADQRB0UxRFAAAIADgIgiAAAAgAOAiCIMgBgiBIiqFIAAAHQRAEQRAAAAAAfFVVVQAAAAB0\nUxRFAAAAADhRFDkAAAAANFMUPUEAAAB4UZRZEAQAAGiWIAgAAAAAcAIDOQAAAEF4BEFgAAAAAERR\nlF0AAAAARIqiEAAAAACUbStJAAAAAEQKoUQAAAAAhJLEMMQAAAB8CCF8AAAcQRACQRAcAARBEARB\nEAQADoIgEIIgDgAAAABnDgAAAAAAAAAAAAAA\n" ## lucida console 06x10 bitmap font encoded in 64 bits - use str2font to decode

  ## predefined colors
  bwrgbcmy = "0x000000 0xFFFFFF 0xFF0000 0x00FF00 0x0000FF 0x00A8EC 0xE3007B 0xF9F400"
  bwrgbcmy = ( eval(x) for x in bwrgbcmy.split(" ") ) ..asarray()
  rgbi = (36, 6, 1) ..asarray(dtype = uint8) ## set color channels to 8bit - numpy defaults to 64 bits, wasting space by order of magnitude

  ## color map
  clrmap = "  ".join( "\33[38;5;231m%c\33[0m" % x for x in range(128) )
  clrmap = "  ".join(( clrmap, clrmap.replace("231", "231;7") ))
  i = arange(16, 232) ## rgb666
  X = clrmap; clrmap = "  ".join( X.replace("231", str(x)) for x in i )
  clrmap = clrmap.split("  ") ..ravel()
  if True: clrmap[:256] = " " ## replace null clrmap -> efficient blanks - background must b set to black
  rgb = clrmap[ord(" ") + 128::256] ..asarray()

  if 0 and DEBUG:
    print( clrmap[256:768] ..strjoin() )
    print( "".join(rgb) )

  ## print an array in row, col format - for debugging
  def printd(self, arr):
    if isinstance(arr, int64): arr = [arr & bitshift64(1, i) for i in range(self.fres.prod())] ..asarray(dtype = bool).reshape(self.fres)
    for x in arr[:-1]: print( "".join(str(int(x)) if x else "." for x in x) )
    print( "".join(str(int(x)) if x else "_" for x in arr[-1]) )

  ## internal fnc for importing font bitmaps
  def importfont(self, file):
    DEBUG = self.DEBUG; from PIL import Image; fres = self.fres
    font = Image.open(file).getdata() ..asarray(dtype = int64)
    if DEBUG: font = font.reshape(fres * (6, 16)); self.printd(font[:fres[0]])

    font = font.reshape(6, fres[0], 16, fres[1]).transpose(0, 2, 1, 3) .reshape(r_[6 * 16, fres.prod()])
    for i, x in enumerate(font.T): font[:, 0] |= bitshift64(x, i)
    font = font[:, 0]
    if DEBUG:
      for x in font[1:1 + 2]: self.printd(x); print()
    return font

  def font2str(self, font): import base64; return base64.encodestring(font.tostring())
  def str2font(self, s): import base64; s = base64.decodestring(s); return ndarray(len(s) // 8, dtype = int64, buffer = s)

  def __init__(self, plaintxt = True):
    self.plaintxt = plaintxt; fres = self.fres

    arr = self.str2font(self.lucida); arr = arr[..., newaxis].repeat(5, axis = -1) ## original
    arr[..., 1] >>= fres[1] ## shift up
    arr[..., 2] <<= fres[1] ## shift down
    cll = 1 ..bitshift64(arange(0, fres.prod(), fres[1], dtype = int64)) ..sum() ^ self.mask ## cll left boundary
    x = arr[..., 3]; x &= cll; x >>= 1 ## shift left
    x = arr[..., 4]; x <<= 1; x &= cll ## shift right
    if 0 and DEBUG:
      for x in arr[17, :5]: self.printd(x)
    # if type(self) is _img2txt:
      # self.printd(self.mask)
      # self.printd(cll)
      # print( type(cll), x.dtype, shapes(cll, arr), builtins.bin(cll) )
      # for x in arr[-50]: self.printd(x)

    fbmp = arr ## bmp of font
    ford = arange(32, 128); assert len(ford) == len(fbmp) ## maps fbmp -> ord
    fpop = popcount64(fbmp[:, 0])

    if not plaintxt: ## include inverted color
      fbmp = (fbmp, fbmp ^ self.mask) ..concatenate(axis = 0)
      ford = r_[ford, ford + 128]; fpop = r_[fpop, fres.prod() - fpop]
      fpop[-1] = 0 ## redundant fres.prod()

    cll = [0] + [i for i, x in enumerate(fpop) if x] ## cll whitespace
    fbmp, ford, fpop = (x[cll] for x in (fbmp, ford, fpop))

    cll = fpop.argsort() ## sort by population count
    fbmp, ford, fpop = (x[cll] for x in (fbmp, ford, fpop))
    self.level = level = fpop.mean() * 255 / fres.prod()

    # if 1: hst = _histogram(fpop)
    hst = histogram2nd(fpop)[0]
    # if 1: assert all(x == hst)
    hst = [list(x) for x in enumerate(hst) if x[1]] ..array() ## cll whitespace in histogram

    bin = [0]; i = n = 0
    for a, b in hst[1:]:
      if n < 16: n += b ## binsize
      else: bin.append(a); n = b
    bin = asarray( [0] + bin[:-1] + [fres.prod() + 1] * 2 )
    a = zip(bin[0::3], bin[3::3])
    b = zip(bin[1::3], bin[4::3])
    c = zip(bin[2::3], bin[5::3])

    fbin = transpose((bin[1:-2], bin[2:-1])); fbin[0, 0] = 1 ## ignore whitespace
    fmap = flatten(zip_longest(a, b, c))
    if None in fmap: fmap = fmap[:fmap.index(None)]
    fmap = fmap ..reshape((-1, 2))
    fmap = find2nd(fpop, fmap.T.flat[:])[1].reshape(2, -1).T
    assert len(fmap) == len(fbin)

    if 0 and DEBUG:
      print( "level", level )
      print( "fpop", fpop )
      print( "hst", hst )
      print( "fbin", fbin )
      print( "fmap", fmap )

    fmap = [(a, fbmp[a:b]) for a, b in fmap]
    chrmap = [chr(x) for x in range(128)] ## chrmap
    if not plaintxt: chrmap += ["\33[7m%s\33[0m" % x for x in chrmap] ## include inverted color
    self.chrmap = chrmap = asarray(chrmap)
    if 0 and DEBUG: print( chrmap[ford] ..strjoin() ) ## print chrmap in ascending density

    self.fbmp = fbmp; self.ford = ford; self.fpop = fpop; self.fbin = fbin; self.fmap = fmap

  ## fill buf w/ data
  def fill(self, arr):
    fres = self.fres; self.res = res = divceil(arr.shape, fres) ## res
    if not all(arr.shape // fres == res): x = arr; arr = zeros(res * fres, dtype = bool); arr[:x.shape[0], :x.shape[1]] = x ## resize canvas
    if len(self.buf) != res.prod(): self.buf = empty(res.prod(), dtype = int64) ## resize buf
    buf = self.buf; buf.fill(0) ## clear buf
    arr = asarray(arr, dtype = bool) .reshape(res[0], fres[0], res[1], fres[1]) .transpose(1, 3, 0, 2) .reshape(fres.prod(), -1) ## create blocks
    for i, x in enumerate(arr != 0): buf |= bitshift64(x, i) ## fill buf
    return self

  ## draw algorithm - interpolates block -> ascii chr
  def itp(self, wmatch = 1, wmismatch = 2, whitespace = True):
    buf = self.buf; self.pop = pop = popcount64(buf)
    for (a, b), (c, f) in zip(self.fbin, self.fmap):
      cll = (a <= pop) & (pop < b)
      if not cll.any(): continue
      x = buf[cll]; f = f.T[..., newaxis]
      y = popcount64(x & f) ## match
      y[0] *= wmatch ## weight original match
      y[0] -= popcount64(x ^ f[0]) * wmismatch ## subtract mismatch
      y = y.sum(axis = 0); y = y.argsort(axis = 0)[-1] + c; ## tally weights & pick highest
      if not whitespace: y[y == 0] = 1
      buf[cll] = self.ford[y]
    buf[buf == 0] = self._; return self

  def tostr(self):
    if self.plaintxt or self.color is None: return "\n".join( "".join(self.chrmap[x]) for x in self.buf.reshape(self.res) )
    buf = self.buf | (self.color ..asarray(dtype = uint16) << 8)
    return "\n".join( "".join(self.clrmap[x]) for x in buf.reshape(self.res) )

  def load(self, file, scale = 1, invert = None, **kwds): ## must be a file or filename
    from PIL import Image; img = Image.open(file) ## import img
    fres = self.fres[::-1]; res = asarray(img.size) * scale / fres; res = ceil(res).astype(int) * fres ## make res multiple of fres
    if not all(res == img.size): img = img.resize(res) ## resize img

    gray = img.convert("L"); arr = gray.getdata() ..asarray(dtype = uint8) ## auto-level
    if invert: arr ^= -1
    x = arr.mean(); level = self.level
    if x and x != level:
      cll = arr <= x; x = arr[cll]; x -= x.min(); x *= level / (x.max() or 1); arr[cll] = x ## <= mean
      cll = cll ^ True; x = arr[cll]; x -= x.min(); x *= (255 - level) / (x.max() or 1); x += level; arr[cll] = x ## > mean
      gray.putdata(arr)
    arr = gray.convert("1").getdata() ..asarray(dtype = bool).reshape(res[::-1]) ## dither

    self.res = res[::-1] // fres[::-1] ## save res
    self.fill(arr).itp(**kwds) ## itp

    if not self.plaintxt and img.mode in ("CYMK", "RGB"):
      color = (img if img.mode == "RGB" else img.convert("RGB")).resize(self.res[::-1]).getdata() ..asarray(dtype = uint8).reshape(-1, 3)
      if invert: color ^= -1
      color *= 6 / 256
      self.color = color = dot( color, self.rgbi ) ## convert to rgb666
      color[(color == 0) & (self.buf != self._)] = 1 ## paint darkest nonempty pixel blud instead of invisible black
    else: self.color = color = None
    return self

  def __call__(self, *args, **kwds): return self.load(*args, **kwds).tostr()

  def test(self):
    img = "mario.jpg"
    txt = self(
      img,
      scale = 0.5, ## scale image size (0.5 = half, 1 = original, 2 = double)
      invert = 0, ## invert colors
      whitespace = True, ## True for optimal algorithm, False to deny a non-empty block from being written as whitespace (e.g. u want to see every datapoint in a plot)
      )
    print( txt )

img2plaintxt = _img2txt(plaintxt = True) ## creates portable plain txt image
img2txt = _img2txt(plaintxt = None) ## creates colorized txt image for display in terminals (xterm, putty, ...)

######## (z, y, t) datapoint storage object
class dataZYT(_asarray):
  def __new__(self, yt = None, y = None, t = None, trange = None, tn = 256, z = None, zrange = None, zn = 64, ymin = None, ymax = None, tmin = None, tmax = None, log2 = None, parseonly = None):
    if trange is not None: assert t is None; t = linspace(trange[0], trange[1], tn)
    if zrange is not None: assert z is None; z = linspace(zrange[0], zrange[1], zn)

    if z is not None: ## z fnc
      assert yt is None and callable(y) and ndim(t) == ndim(z) == 1
      if len(t) * len(z) > 0x10000: raise ValuError("too many datapoints to calculate")
      yt = [ [(y(_t, _z), _t) for _t in t] for _z in z ]

    elif yt is not None: ## zipped yt
      assert y is None and t is None
      # yt = array(yt, dtype = float) ## copy yt
      # if yt.ndim == 2: yt = yt[newaxis]
      # elif yt.ndim > 3: yt = yt.reshape(r_[-1, yt.shape[-2:]])

      assert iterable(yt)
      try:
        yt = array(yt, dtype = float) ## copy yt
        yt = yt.reshape(r_[-1, -1, yt.shape[-2:]][-3:])
      except:
        yt = list(yt); amax = -1,
        for i, x in enumerate(yt):
          x = as2d(x); a, b = x.shape
          assert b == 2, (i, x.shape)
          if a > amax[0]: amax = a, i
          # yt[i] = cycle(x)
        # yt[amax[1]] = amax[2]
        yt = zip(x if i == amax[1] else cycle(x) for i, x in enumerate(yt)) ..list() ..asarray(dtype = float)
        
      # yt = array(yt, dtype = float) ## copy yt
      # if yt.ndim == 2: yt = yt[newaxis]
      # elif yt.ndim > 3: yt = yt.reshape(r_[-1, yt.shape[-2:]])

    else: ## individual y, t
      if t is None: y = as2d(y, dtype = float); t = arange(y.shape[-1], dtype = float)
      t = asarray(t, dtype = float); assert t.ndim == 1 and y is not None
      assert iterable(y)
      if len(y) and callable(y[0]): y = [[f(x) for x in t] for f in y]
      y = as2d(y, dtype = float)
      assert y.shape[1] == len(t), shapes(y, t)
      if parseonly: return y, t ## return parsed y, t
      yt = transpose((y, t[newaxis].repeat(len(y), axis = 0)), (1, 2, 0))

    self = _asarray.__new__(self, yt, dtype = float)
    if not None is ymin is ymax is tmin is tmax:
      y, t = self.reshape(-1, 2).T
      if ymin is not None: y[y < ymin] = ymin
      if ymax is not None: y[y > ymax] = ymax
      if tmin is not None: t[t < tmin] = tmin
      if tmax is not None: t[t > tmax] = tmax
    self.z = z = arange(len(self)) if z is None else asarray(z, dtype = float)
    self.log2 = log2
    return self

  def roots(self):
    if not self.minmax[0, 0] <= 0 <= self.minmax[1, 0]: return
    assert self.sorted; roots = []
    for i, (y, t) in enumerate(self.transpose(0, 2, 1)):
      y = y.copy(); y[y < 0] = -1; y[y > 0] = 1; y = y[:-1] != y[1:]
      roots.append(t[y])
    return roots

  def analyze(self):
    self.minmax = minmax = [(x.min(), x.max()) for x in self.T] ..transpose() ## self.minmax
    if any(minmax[0] == minmax[1]):
      if minmax[0, 1] == minmax[1, 1]: raise ValueError("datapoints all lie on vertical line t = %s" % minmax[0, 1])
      else: raise ValueError("datapoints all lie on horizontal line y = %s" % minmax[0, 0])
    self.origin = origin = [0.0 if a <= 0 <= b else a if 0 < a else b for a, b in minmax.T] ..asarray() ## self.origin

    for yt in self:
      t = yt[:, 1]
      if any(t[:-1] > t[1:]): yt[:] = yt[t.argsort()] ## sort t-axis
    self.sorted = True
    arr = []; y = self[..., 0] ## self.extrema
    for ye in y.min(axis = 1), y.max(axis = 1): cll = find2nd(y, ye); te = self[cll[0], cll[1], 1]; arr.append((ye, te))
    self.extrema = extrema = transpose(arr, (2, 0, 1)); return self

  def concat(self, x): return (self, x) ..concatenate(axis = 0) ..dataZYT()

  def norm(self, arr = None): ## normalize data points
    a, b = self.minmax; assert not any(a == b)
    if arr is None: arr = self
    arr = asarray(arr); arr = arr.reshape(r_[1, 1, arr.shape][-3:]).astype(float); arr -= a; arr *= 1 / (b - a) # norm
    n = linspace(0, 1, len(arr)); n = n[newaxis, :].repeat(arr.shape[1], axis = -1).reshape(r_[arr.shape[:-1], 1])
    arr = concatenate((n, arr), axis = -1)
    if self.log2: arr[..., 1] = log2(1 + arr[..., 1])
    return arr

  @staticmethod
  def test():
    if 1:
      x = dataZYT(y = [ [0,1,2,-1,3], [1, 0, 0, 4, 0] ], t = [4,3,2,7,8]).init()
      print(); print( x, x.minmax, x.origin )
      print(); print( x.norm(x) )

######## general plotter
class _plot(_img2txt):
  def s2rgb(s, rgb): return [(int(a), int(b), int(c)) for a,b,c in s] ..dot(rgb) ## convert array of string triplets -> rgb666
  def printrgb(rgbi = None): print( len(rgbi), "".join(img2txt.rgb[rgbi]) )

  rgb = img2txt.rgb; rgbi = img2txt.rgbi
  monoi = """
000
001 002 003 004 005
015 025 035 045 045
055 155 255 355 455
555
""".replace("\n", " ").split(" ")[1:-1]
  bluei = s2rgb(monoi, (36, 6, 1))
  greeni = s2rgb(monoi, (1, 36, 6))
  redi = s2rgb(monoi, (6, 1, 36))
  gradienti = """
000
001 010 100 011 101 110 111
112 121 211 122 212 221 222
223 232 322 233 323 332 333
334 343 433 344 434 443 444
445 454 544 455 545 554 555
""".replace("\n", " ").split(" ")[1:-1] ..s2rgb((6, 36, 1))
  rainbowi = """
000
001 002 003 004 005
015 025 035 045 055
054 053 052 051 050
150 250 350 450 550
540 530 520 510 500
501 502 503 504 505
515 525 535 545 555
""".replace("\n", " ").split(" ")[1:-1] ..s2rgb((1, 6, 36))
  blueredi = """
000
001 002 003 004 005
015 025 035 045 055
155 255 355 455 555
554 553 552 551 550
540 530 520 510 500
400 300 200 100 000
""".replace("\n", " ").split(" ")[1:-1] ..s2rgb((36, 6, 1))

  if 0 and DEBUG:
    printrgb(arange(216))
    printrgb(greeni)
    printrgb(gradienti)
    printrgb(rainbowi)

  colori = rainbowi[4:] # plot color
  zeroi = dot( (36, 6, 1), (5, 0, 0) )
  s2rgb = staticmethod(s2rgb)
  printrgb = staticmethod(printrgb)

  def __call__(self, yt = None, y = None, itp = True, colori = rainbowi[5:], yres = None, **kwds):
    if yt is None and y is None: data = self.data; norm = self.norm
    else: self.data = data = dataZYT(yt = yt, y = y, **kwds).analyze(); self.norm = norm = data.norm()

    self.colori = colori ## colori
    if yres is None: yres = YRES
    self.res = res = screensize() ..asarray(); res[0] *= yres ## res
    if isinstance(self, _plotsurf): res[0] = min(res[0], len(data))
    if len(self.buf) != res.prod(): self.buf = empty(res.prod(), dtype = int64) ## resize buf
    if len(self.color) != res.prod(): self.color = empty(res.prod(), dtype = int64) ## resize color buf
    buf = self.buf; color = self.color; buf[:] = color[:] = 0 ### reset buf
    s = self.plot(itp = itp).tostr(); print( "" ); print( self.header() ); print( s )

  def inverty(self, arr): arr = arr.copy(); arr[..., 1] = 1 - arr[..., 1]; return arr
  def scaleyt(self, yt, inverty, res = None):
    yt = self.data.norm(yt).reshape(-1, 3)[:, 1:]
    if inverty: yt[:, 0] = 1 - yt[:, 0]
    # yt = roundint( yt * ((res if res else self.res) - 1) ); return yt
    yt = asarray( yt * ((res if res else self.res) - 1), dtype = int ); return yt

  ## plot algorithm
  def plot(self, itp = True):
    buf = self.buf; color = self.color; colori = self.colori; data = self.data; fres = self.fres; res = self.res; arr = self.inverty(self.norm.reshape(-1, 3))

    c = colori[ roundint( arr[:, 0] * (len(colori) - 1) ) ]
    # arr = roundint( arr[:, 1:] * (res * fres - 1) )
    arr = asarray( arr[:, 1:] * (res * fres - 1), dtype = int )
    a, b = divmod(arr, fres) ..transpose((0, 2, 1))
    a = a[0] * res[1] + a[1]; b = 1 ..bitshift64(b[0] * fres[1] + b[1])
    color[a] = c ## fill color buf
    orequal(buf, a, b) ## fill buf
    # self.itp(wmatch = 7, wmismatch = 1.5, whitespace = 0) ## itp
    # if not itp or len(arr) < 64: buf[buf != self._] = 160 ## cutoff to use block datapoints for better visibility
    cll = buf != 0
    if cll.sum() < 64: itp = None ## cutoff to use block datapoints for better visibility
    if itp: self.itp(wmatch = 7, wmismatch = 1.5, whitespace = 0) ## itp
    else: buf[cll] = ord(" ") + 128; buf[cll^True] = self._

    o = self.scaleyt(data.origin, inverty = True).ravel(); o = asarray((o, res - 1)).min(axis = 0) ## origin
    cll = arange(0, len(buf), res[1]) + o[1]; cll = cll[buf[cll] == self._]; buf[cll] = ord("|"); color[cll] = self.zeroi ## y axis
    cll = arange(res[1]) + o[0] * res[1]; cll = cll[buf[cll] == self._]; buf[cll] = ord("-"); color[cll] = self.zeroi ## t axis
    cll = arange(res[1]); cll = r_[cll, -1 - cll]; cll = cll[ buf[cll] == self._ ]; buf[cll] = ord("-"); color[cll] = 43 ## box

    a, b = arr = data.extrema[:, :, 0].T; x, i = find2nd(arr, (a.min(), b.max())) ## extrema
    self.mmi = mmi = colori[roundint( i * (len(colori) - 1) / (len(data) - 1) )]
    y, t = self.scaleyt( data.extrema[i, [0, 1]], inverty = True ).T; x = t + o[0] * res[1]
    buf[x] = 160; color[x] = mmi
    return self

  ## print header info
  def header(self):
    colori = self.colori; data = self.data
    c = linspace(0, len(colori) - 1, min(len(data), len(colori))) ..roundint(); c = self.rgb[colori[c]]; mm = data.minmax
    return "SIDEVIEW Y:\t\tZ  %s to %s  %s\t\tY  %s to %s\t\tT  %s to %s\t\tMIN MAX  %s" % (
      data.z[0], data.z[-1], "".join(c),
      mm[0, 0], mm[1, 0],
      mm[0, 1], mm[1, 1],
      " ".join(self.rgb[self.mmi])
      )

  def test(self, plot = None):
    if plot: self = plot
    if 1:
      t = linspace(0, 1, 256) - 0.25
      y = [ t, cos(t * 2 * pi), sin(t * 4 * pi), cos(t * 2 * pi) + 0.25 ]
      yt = None
      yres = 1 / 3
      self(yt = yt, y = y, t = t, yres = yres)

    if 1:
      trange = -1, 1
      zrange = 0, 1
      y = lambda t, z: sin( t*(2*pi + z) ) * (0.5 + z) - z
      yres = 1 / 3
      self(y = y, trange = trange, zrange = zrange, yres = yres)

######## surface plotter
class _plotsurf(_plot):
  colori = _plot.gradienti[1:] # plot color

  def plot(self, **kwds):
    res = self.res; buf = self.buf.reshape(res); color = self.color.reshape(res); data = self.data; arr = self.norm.reshape(-1, 3)

    arr = arr[arr[:, 1].argsort()]; z, t = roundint( arr.T[[0, 2]] * (res[:, newaxis] - 1) ); y = arr[:, 1]
    buf[z, t] = self.ford[roundint( y * (len(self.ford) - 1) )]
    color[z, t] = self.colori[roundint( y * (len(self.colori) - 1) )]

    roots = data.roots(); i = linspace(0, res[0] - 1, len(roots)) ..roundint() ## plot y roots
    for i, t in zip(i, roots): t = self.scaleyt(transpose((t, t)), inverty = None)[:, 1]; buf[i, t] = 160; color[i, t] = self.zeroi
    return self

  def header(self):
    colori = self.colori; data = self.data; c = self.rgb[colori]; mm = data.minmax
    return "TOPVIEW Z:\t\tZ  %s to %s  (top to bottom)\t\tY  %s to %s  %s\t\tT  %s to %s\t\tROOTS  %s" % (
      data.z[0], data.z[-1],
      mm[0, 0], mm[1, 0], "".join(c),
      mm[0, 1], mm[1, 1],
      self.rgb[self.zeroi],
      )

plot = _plot(plaintxt = None)
plotsurf = _plotsurf(plaintxt = None)
def plot3d(**kwds):
  plot(colori = _plot.bluei[1:], **kwds)
  plotsurf.data = plot.data; plotsurf.norm = plot.norm; plotsurf(colori = _plot.gradienti[1:], **kwds)
plot3d.test = lambda: plot.test(plot = plot3d)
