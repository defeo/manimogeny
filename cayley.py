import numpy as np
from manim import *

class MathText(Text):
    CONFIG = {
        'font': 'Linux Libertine Display', #'Nimbus Roman',
        'size': 0.7,
        }

class Cayley(Scene):
    N = 12
    gen = 2
    edges = [(1, 1, BLUE), (4, -1, RED), (-3, 0.5, GREEN)]
    radius = 2.5
    text_radius = 3

    def label(self, exp):
        return 'G' if exp == 0 else '[%d]G' % (self.gen**exp % (self.N + 1))
    
    def polar(self, ρ, θ):
        return [np.cos(θ) * ρ, np.sin(θ) * ρ, 0]
    
    def construct(self):
        group = {self.gen**i % (self.N+1) : i for i in range(self.N)}
        vertices = [Dot().move_to(self.polar(self.radius, 2*i*PI/self.N))
                        for i in range(self.N)]
        labels = [MathText(self.label(i)).move_to(self.polar(self.text_radius, 2*i*PI/self.N))
                      for i in range(self.N)]
        
        arrows = {}
        for jump, α, col in self.edges:
            arrows[jump] = []
            cosets = np.gcd(self.N, jump)
            for coset in range(cosets):
                for j in range(self.N // cosets):
                    arrows[jump].append(
                        ArcBetweenPoints(vertices[(coset + j*jump) % self.N].get_center(),
                                             vertices[(coset + (j+1)*jump) % self.N].get_center(),
                                             angle=α, color=col, z_index=-1))
        
        for i in range(1, self.N + 1):
            self.play(FadeIn(vertices[group[i]]),
                          FadeIn(labels[group[i]]), run_time=0.1 + 0.9**i)

        for arr in arrows.values():
            for i, a in enumerate(arr):
                self.play(ShowCreation(a), run_time=0.1 + 0.5**i)
            self.wait(1)
        
        self.wait(1)
