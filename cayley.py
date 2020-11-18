import numpy as np
from manim import *
from itertools import cycle
from random import shuffle

class CayleyGraph(Mobject):
    def __init__(self, N, gen, radius, edge_dirs, edge_bends=[1, -1],
                 color=BLACK, edge_colors=[BLUE, RED, GREEN],
                 label_func=True,
                 **kwargs):
        super().__init__(**kwargs)
        self.N = N
        self.gen = gen
        self.radius = radius
        self.edge_dirs = edge_dirs
        self.edge_bends = edge_bends
        self.edge_colors = edge_colors
        self.dlog = {self.gen**i % (self.N+1) : i for i in range(self.N)}
        
        self.vertices = [self.vertex(i, color=color, **kwargs)
                         for i in range(self.N)]
        self.add(*self.vertices)
        if label_func is not None:
            self.labels = [self.label(i, label_func=label_func, color=color, **kwargs)
                           for i in range(self.N)]
            self.add(*self.labels)
            
        self.edges = []
        for jump, α, col in zip(self.edge_dirs,
                                cycle(self.edge_bends),
                                cycle(self.edge_colors)):
            self.edges.append([self.edge(i, jump, α, color=col, z_index=-1)
                               for i in range(self.N)])
            self.add(*self.edges[-1])

    def polar(self, ρ, θ):
        return np.array((np.cos(θ) * ρ, np.sin(θ) * ρ, 0))

    def vertex_pos(self, n):
        return self.polar(self.radius, 2*n*PI/self.N)
    
    def vertex(self, n, **kwargs):
        return Dot(**kwargs).move_to(self.vertex_pos(n))

    def dlog_order(self):
        for i in range(1, self.N+1):
            yield self.dlog[i]

    def cycle_order(self, i):
        jump = self.edge_dirs[i]
        cyclen = self.N // np.gcd(self.N, jump)
        for i in range(self.N):
            yield ((i % cyclen)*jump + i // cyclen) % self.N

    def all_edges(self):
        for es in self.edges:
            for e in es:
                yield e
            
    def _label_func(self, n):
        return 'G' if n == 0 else '[%d]G' % (self.gen**n % (self.N + 1))
    
    def label(self, n, label_func=True, **kwargs):
        if not callable(label_func):
            label_func = self._label_func
        text = Text(label_func(n), **kwargs)
        dir = self.vertex_pos(n)
        text.next_to(dir, dir / np.linalg.norm(dir), buff=0.4)
        return text

    def edge(self, n, jump, bend, tip=False, **kwargs):
        if tip:
            return CurvedArrow(self.vertex_pos(n), self.vertex_pos(n + jump),
                               angle=bend, **kwargs)
        else:            
            return ArcBetweenPoints(self.vertex_pos(n), self.vertex_pos(n + jump),
                                    angle=bend, **kwargs)

    def path(self, path, start=0, **kwargs):
        edges = []
        for d, jump, bend, col in zip(path, cycle(self.edge_dirs),
                                      cycle(self.edge_bends), cycle(self.edge_colors)):
            for i in range(abs(d)):
                edges.append(self.edge(start, np.sign(d)*jump, np.sign(d)*bend,
                                       color=col, **kwargs))
                start += np.sign(d)*jump
        return edges, start
    
Text.CONFIG = {
    'font': 'Linux Libertine Display',
    'color': BLACK,
}
MathTex.CONFIG = {
    'color': BLACK,
}

class CSIDH(Scene):
    def construct(self):
        graph = CayleyGraph(N=18, gen=2, radius=3,
                            edge_dirs=(1,-5,-2), edge_bends=[1,1.5,1],
                            size=0.8, label_func=None).shift(2*LEFT)

        # Show vertices
        for i, d in enumerate(graph.dlog_order()):
            self.play(FadeIn(graph.vertices[d]),
                      run_time=0.1 + 0.9**i)

        # Show edges
        legend = Group()
        for i, es in enumerate(graph.edges):
            mul = Line([3.5,-1-0.7*i,0], [4.5,-1-0.7*i,0], color=graph.edge_colors[i])
            mul.add(Text('degree %d' % [2,3,5][i]).next_to(mul, RIGHT))
            legend.add(mul)
            self.play(ShowCreation(mul))
            for j, d in enumerate(graph.cycle_order(i)):
                self.play(ShowCreation(es[d]), run_time=0.1 + 0.5**j)
            self.wait(1)

        self.wait()


class Cayley(Scene):
    def construct(self):
        graph = CayleyGraph(N=18, gen=2, radius=3,
                            edge_dirs=(1,-5,-2), edge_bends=[1,1.5,1],
                            size=0.8).shift(2*LEFT)

        # Show vertices
        for i, d in enumerate(graph.dlog_order()):
            self.play(FadeIn(graph.vertices[d]), FadeIn(graph.labels[d]),
                      run_time=0.1 + 0.9**i)

        # Show edges
        legend = Group()
        for i, es in enumerate(graph.edges):
            mul = Line([3.5,-1-0.7*i,0], [4.5,-1-0.7*i,0], color=graph.edge_colors[i])
            mul.add(Text('A = %d[B]' % [2,3,5][i]).next_to(mul, RIGHT))
            legend.add(mul)
            self.play(ShowCreation(mul))
            for j, d in enumerate(graph.cycle_order(i)):
                self.play(ShowCreation(es[d]), run_time=0.1 + 0.5**j)
            self.wait(1)

        self.wait()

        # Present dlog
        self.play(*(FadeOut(l) for i, l in enumerate(graph.labels) if i not in [0,7]))

        self.wait()

        # Solve dlog
        self.play(*(ApplyMethod(e.fade, 0.9)
                    for i, e in enumerate(graph.all_edges())
                    if i not in [18, 13, 18 + 14, 2*18 + 9]))

        dlogeq = Text('3·2·3·5 = 14 mod 19').move_to([4.5,1,0])
        self.play(Write(dlogeq))

        self.wait()

        # No labels
        self.play(FadeOut(graph.labels[0]),
                  FadeOut(graph.labels[7]),
                  *(ApplyMethod(e.fade, -9) for e in graph.all_edges()))

        self.wait()
        
        # Change dlog eq to Z/q
        Zq = Text('(ℤ/19ℤ)*').move_to(dlogeq)
        self.play(Transform(dlogeq, Zq))
        
        self.wait()

        # Replace labels (graph of GF(617))
        jinvs = Group(*(graph.label(i, lambda x : str(j))
                        for i, j in enumerate([244, 91, 405, 280, 93, 174, 569, 245, 585,
                                               504, 309, 390, 540, 140, 387, 343, 391, 13]))
                      ).move_to(graph)
        self.play(FadeIn(jinvs))

        self.wait()
        
        # Eliminate Z/q
        self.play(FadeOut(dlogeq), FadeOut(legend))

        self.wait()

class KeyExchange(Scene):
    def construct(self):
        jinvs = lambda i: str([244, 91, 405, 280, 93, 174, 569, 245, 585,
                               504, 309, 390, 540, 140, 387, 343, 391, 13][i])
        graph = CayleyGraph(N=18, gen=2, radius=3,
                            edge_dirs=(1,-5,-2), edge_bends=[1,1.5,1],
                            label_func=jinvs, size=0.8).shift(2*LEFT)
        self.add(graph)

        self.wait()

        # Hide labels, fade edges
        self.play(*(FadeOut(l) for i, l in enumerate(graph.labels) if i not in [0]),
                  *(ApplyMethod(e.fade, 0.9) for e in graph.all_edges()))

        self.wait()
        
        # Alice path
        apath, ai = graph.path([2,-1,2], tip=True, stroke_width=5)
        apath = Group(*apath).shift(2*LEFT)
        bpath, bi = graph.path([-3,0,2], tip=True, stroke_width=5)
        bpath = Group(*bpath).shift(2*LEFT)
        apk = graph.labels[ai]
        apv = graph.vertices[ai]
        bpk = graph.labels[bi]
        bpv = graph.vertices[bi]
        shk = graph.labels[(ai + bi) % graph.N]
        shv = graph.vertices[(ai + bi) % graph.N]
        alice = Text('Alice', color=DARK_BLUE).next_to(apk, RIGHT)
        bob = Text('Bob', color=DARK_BLUE).next_to(bpk, LEFT)

        #akey = Text('Alice: ', '2', '-1', '2')
        #bkey = Text('Bob: ', '2', '-1', '2')
        
        self.play(ShowCreation(apath), run_time=2, rate_func=linear)
        self.play(FadeIn(apk), FadeIn(alice), ScaleInPlace(apv, 2))
        self.wait(1)
        self.play(ShowCreation(bpath), run_time=2, rate_func=linear)
        self.play(FadeIn(bpk), FadeIn(bob), ScaleInPlace(bpv, 2))

        self.wait()

        a2b = ArcBetweenPoints(alice.get_center(), bob.get_center(), 2)
        b2a = ArcBetweenPoints(bob.get_center(), alice.get_center(), 2)
        self.play(MoveAlongPath(alice, a2b), MoveAlongPath(bob, b2a), run_time=1)

        self.wait(1)

        self.add(apath.copy().fade(0.7))
        self.add(bpath.copy().fade(0.7))

        self.play(*(Rotating(e, radians=2*PI/graph.N*bi,
                             about_point=graph.get_center()) for e in apath))
        self.play(FadeIn(shk), ScaleInPlace(shv, 2))
        self.play(apath.fade, 0.7)
        
        self.play(*(Rotating(e, radians=2*PI/graph.N*ai,
                             about_point=graph.get_center()) for e in bpath))
        self.play(bpath.fade, 0.7)
        self.play(FadeToColor(shv, RED))
        
        self.wait()
