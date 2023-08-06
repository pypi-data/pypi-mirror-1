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



import os, sys
if sys.version_info[1] < 6: raise Exception("asciiporn requires Python 2.6 or higher")



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
__requires__ =	["PIL", "numpy"]
__url__ = "http://pypi.python.org/pypi/asciiporn"
__version__  = "2009.01.21"
## end setup info



if "DEBUG" not in globals(): DEBUG = 0 ## True prints debug info



import ast, collections, re ## pseudomethod parser
class parser(ast.NodeTransformer):
  def parse(self, s, fpath, mode):
    s = s.replace(".items()", ".iteritems()").replace(".keys()", ".iterkeys()").replace(".values()", ".itervalues()")
    s = s.replace("__next__", "next")

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
class importer(object):
  py3k_syntax = None ## identifier
  magic = "\nfrom __future__ import py3k_syntax\n"

  def __init__(self):
    sys.meta_path[:] = [self] + [x for x in sys.meta_path if not hasattr(x, "py3k_syntax")] ## restore sys.meta_path
    sys.path_importer_cache = {} ## reset cache

  def find_module(self, mname, path = None):
    if DEBUG and 1: print( "py3k_syntax find_module(mname = %s, path = %s)" % (mname, path) )

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
    s = s.replace(self.magic, "\nfrom __future__ import division, with_statement; from py3k_syntax import *\n", 1)
    s = s[1:-1] ## preserve lineno (for debugging)

    self.found = s, fpath, desc, tp; return self

  def load_module(self, mname):
    s, fpath, desc, tp = self.found
    if DEBUG and 1: print( "py3k_syntax load_module(mname = %s, fpath = %s, desc = %s)" % (mname, fpath, desc) )

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
importer()



import __builtin__ as builtins, itertools
if 1: ## builtins
  filter = itertools.ifilter
  filterfalse = itertools.ifilterfalse
  map = itertools.imap
  range = xrange
  zip = itertools.izip
  zip_longest = itertools.izip_longest
  def oct(x): return builtins.oct(x).replace("0", "0o", 1)

m = sys.modules.get("asciiporn._asciiporn")
if m: _asciiporn = reload(m)
else: import _asciiporn
from _asciiporn import *
