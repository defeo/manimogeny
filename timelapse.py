from manim import *

class MyText(Text):
    CONFIG = {
        'font': 'Linux Libertine Display', #'Nimbus Roman',
        'size': 0.8,
        'color': BLACK,
        }

class Legend(MyText):
    CONFIG= {
        'weight': BOLD,
        'color': BLUE
        }

Mobject.CONFIG['color'] = BLACK
Dot.CONFIG['color'] = BLACK
Text.CONFIG = {
    'font': 'Linux Libertine Display',
    'color': BLACK,
}

class TimeLapse(Scene):
    def construct(self):
        number_line = NumberLine(x_min=1996, x_max=2020, number_at_center=2008,
                                 unit_size=0.5, add_start=0.5, add_end=0.5).shift(2.9*DOWN)
        pointer = Triangle(fill_opacity=1).scale(0.1)
        label = Integer(1996, group_with_commas=False)
        label.add_updater(lambda m: m.next_to(pointer, DOWN))

        pointer_value = ValueTracker(1996)
        pointer.add_updater(
            lambda m: m.next_to( number_line.n2p(pointer_value.get_value()), DOWN)
        )
        label.add_updater(lambda m: m.set_value(pointer_value.get_value()))
        self.add(number_line, pointer, label)

        couv = MyText("Couveignes' HHS").move_to([1,2.5,0])
        self.add(couv)
        keyex = Legend("Key exchange/\nEncryption").move_to([-5.5,2,0])
        self.add(keyex)
        
        self.play(pointer_value.set_value, 2006, rate_func=linear, run_time=8)
        cgl = MyText('Charles-Goren-Lauter').move_to([5,-2,0])
        hashf = Legend('Hash function').move_to(keyex).shift(4*DOWN)
        self.play(Write(cgl), Write(hashf))
        self.wait()
        rs = MyText('Rostovtsev-Stolbunov').next_to(couv, DOWN)
        self.play(Write(rs))

        self.play(pointer_value.set_value, 2011, rate_func=linear, run_time=8)
        sidh = MyText('SIDH').move_to([-2.5,2.5,0])
        self.play(Write(sidh))

        self.play(pointer_value.set_value, 2017, rate_func=linear, run_time=20)
        yoo = MyText('Yoo et al.').move_to([-2.5,0,0])
        sig = Legend('Signature', weight=BOLD).move_to(hashf).shift(2*UP)
        self.play(Write(yoo), Write(sig))
        sike = MyText('SIKE').next_to(sidh, DOWN)
        self.play(Write(sike))

        self.play(pointer_value.set_value, 2018, rate_func=linear, run_time=15)
        csidh = MyText('CSIDH').next_to(rs, DOWN).shift(.3*DOWN)
        self.play(Write(csidh))
        seasign = MyText('SeaSign').move_to(csidh).shift(DOWN)
        self.play(Write(seasign))
        csifish = MyText('CSI-FiSh').next_to(seasign, DOWN)
        self.play(Write(csifish))

        self.wait()

        sidh_hyp = Rectangle(height=5.5, width=2.2, color=RED, opacity=0.5).move_to([-2.5,0,0])
        csidh_hyp = Rectangle(height=5.5, width=3.7, color=DARK_BLUE, opacity=0.5).move_to([1,0,0])
        self.play(FadeIn(sidh_hyp), FadeIn(csidh_hyp))
        self.play(Write(Legend('SIDH assumption').move_to(sidh).shift(.7*UP)))
        self.play(Write(Legend('CSIDH assumption').move_to(couv).shift(.7*UP)))

        self.wait(20)

        osidh = MyText('O-SIDH').move_to(cgl).shift(4.5*UP)
        seta = MyText('Séta').next_to(osidh, DOWN).shift(.3*DOWN)
        bsidh = MyText('B-SIDH').next_to(sike, DOWN).shift(.3*DOWN)
        gps = MyText('Galbraith-Petit-Silva').move_to(cgl).shift(2*UP)
        sqisign = MyText('SQISign').next_to(gps, DOWN).shift(.3*DOWN)
        lossifish = MyText('Lossy CSI-FiSH').next_to(csifish, DOWN)

        self.play(Write(gps), run_time=2)
        self.wait()
        self.play(pointer_value.set_value, 2019, Write(osidh), Write(lossifish), 
                  rate_func=linear, run_time=1)
        self.play(pointer_value.set_value, 2020, Write(seta), Write(bsidh),
                  rate_func=linear, run_time=1)
        self.play(Write(sqisign), run_time=2)

        self.wait()

class NIST(Mobject):
    def __init__(self, xmin, xmax, ymin, ymax,
                 basex=2, basey=2,
                 x_axis_width=10, y_axis_height=6):
        self.basex = basex
        self.basey = basey
        xlogmin = np.log(xmin) / np.log(self.basex)
        xlogmax = np.log(xmax) / np.log(self.basex)
        ylogmin = np.log(ymin) / np.log(self.basey)
        ylogmax = np.log(ymax) / np.log(self.basey)
        self.xaxis = NumberLine(x_min=xlogmin, x_max=xlogmax,
                                number_at_center=xlogmin,
                                unit_size=x_axis_width / (xlogmax - xlogmin),
                                include_ticks=False)
        self.xaxis.shift(LEFT * x_axis_width / 2)
        self.yaxis = NumberLine(x_min=ylogmin, x_max=ylogmax,
                                number_at_center=ylogmin,
                                unit_size=y_axis_height / (ylogmax - ylogmin),
                                include_ticks=False)
        self.yaxis.shift(LEFT * y_axis_height / 2).rotate(PI / 2)
    
    def logx(self, x):
        return np.log(x)/np.log(self.basex)

    def logy(self, y):
        return np.log(y)/np.log(self.basey)
    
    def c2p(self, size, speed):
        return self.xaxis.n2p(self.logx(size)) + self.yaxis.n2p(self.logy(speed))

    def system(self, name, size, speed, label_pos=UP, **kwargs):
        sys = Dot(self.c2p(size, speed), **kwargs)
        return Group(sys, Text(name, **kwargs).next_to(sys, label_pos))


class KEM(Scene):
    def construct(self):
        nist = NIST(100, 300000, 80, 1.1*10**6)
        
        self.play(ShowCreation(nist.xaxis), ShowCreation(nist.yaxis),
                  Write(Text('small').next_to(nist.xaxis, LEFT)),
                  Write(Text('large').next_to(nist.xaxis, RIGHT)),
                  Write(Text('fast').next_to(nist.yaxis, DOWN)),
                  Write(Text('slow').next_to(nist.yaxis, UP)),
                  )
        
        self.wait()

        self.play(FadeIn(nist.system('SIKE', 330+346, 9681+10343, RIGHT, color=BLUE_E)))
        self.play(FadeIn(nist.system('compressed SIKE', 197+236, 15120+11077, LEFT, color=BLUE_E)))
        self.wait()
        self.play(FadeIn(nist.system('McEliece', 261120+128, 44+134, color=RED_D)))
        self.play(FadeIn(nist.system('HQC', 2249+4481, 220+384, color=RED_E)))
        self.play(FadeIn(nist.system('BIKE', 12323+12579, 220+2220, RIGHT, color=RED_E)))
        self.wait()
        self.play(FadeIn(nist.system('Kyber', 800+736, 49+40, LEFT, color=GREEN_D)))
        self.play(FadeIn(nist.system('NTRU', 699+699, 761+1940, color=GREEN_E)))
        self.play(FadeIn(nist.system('Saber', 672+736, 61+63, color=GREEN_D)))
        self.play(FadeIn(nist.system('Frodo', 9616+9720, 1862+1747, color=GREEN_D)))
        self.play(FadeIn(nist.system('NTRU prime', 994+897, 47+59, RIGHT, color=GREEN_E)))
        self.wait()
        
        csidh = nist.system('CSIDH', 64+64+32, 155000, RIGHT, color=BLUE_D)
        self.play(FadeIn(csidh))
        self.wait()
        self.play(csidh.move_to, nist.c2p(512+512+32, 10**6))
        self.wait()

class Sign(Scene):
    def construct(self):
        nist = NIST(200, 400000, 80, 10**9)
        
        self.play(ShowCreation(nist.xaxis), ShowCreation(nist.yaxis),
                  Write(Text('small').next_to(nist.xaxis, LEFT)),
                  Write(Text('large').next_to(nist.xaxis, RIGHT)),
                  Write(Text('fast').next_to(nist.yaxis, DOWN)),
                  Write(Text('slow').next_to(nist.yaxis, UP)),
                  )

        sec = 3*10**6
        msec = sec / 1000
        self.play(FadeIn(nist.system('SIDH', 10**5, 1*sec, color=BLUE_E)))
        self.wait()
        self.play(FadeIn(nist.system('CSIDH', 2000, 100*sec, color=BLUE_D)))
        self.wait()
        self.play(FadeIn(nist.system('CSI-FiSh', 512+956, 2*1.48*sec, color=BLUE_D)))
        self.wait()

        self.play(
            FadeIn(nist.system('Dilithium', 1184+2044, 313+109, RIGHT, color=GREEN_D)),
            FadeIn(nist.system('Falcon', 897+666, 2.3*10**6*(1./5948 + 1./27933), LEFT, color=GREEN_D)),
        )
        self.play(
            FadeIn(nist.system('Rainbow', 157800+528./8, 67+34, color=RED_E)),
            FadeIn(nist.system('GeMSS', 352188+258./8, 736000+80, color=RED_E)),
        )
        self.play(
            FadeIn(nist.system('Picnic', 32+34032, (1.37+1.10)*msec, color=ORANGE)),
            FadeIn(nist.system('SPHINCS+', 32+17088, 68541846+4801338, color=ORANGE)),
        )
        self.wait()

        self.play(FadeIn(nist.system('SQISign', 64+204, 7767000+142000, color=BLUE_C)))
        self.wait()


class Intro(Scene):
    def delay(self, start, evo, end, func=smooth):
        len = start + evo + end
        return lambda t: min(max(0, t * len - start) / evo, 1)
    
    def construct(self):
        sidh = Text('SIDH', color=DARK_BLUE).move_to((3,2,0)).scale(3)
        sike = Text('SIKE', color=DARK_GRAY).move_to((-4,-2,0)).scale(3)
        csidh = Text('CSIDH').move_to((0,0,0)).scale(3)
        self.play(
            FadeInFromLarge(sidh, scale_factor=0.1,
                            rate_func=self.delay(0, 2, 2)),
            FadeInFromLarge(sike, scale_factor=0.1,
                            rate_func=self.delay(1, 2, 1)),
            FadeInFromLarge(csidh, scale_factor=0.1,
                            rate_func=self.delay(2, 2, 0)),
            run_time=4
        )
        self.play(ApplyMethod(sidh.fade, 0.8), ApplyMethod(sike.fade, 0.8))
        self.wait()
        self.play(ApplyMethod(sidh.fade, -8))
        self.wait()
