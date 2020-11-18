import networkx as nx
from manim import *
from itertools import cycle, zip_longest

class LabeledDot(Dot):
    def __init__(self, label, radius=None, **kwargs) -> None:
        if isinstance(label, str):
            rendered_label = MathTex(label, color=BLACK)
        else:
            rendered_label = label

        if radius is None:
            radius = (
                0.1 + max(rendered_label.get_width(), rendered_label.get_height()) / 2
            )
        Dot.__init__(self, radius=radius, **kwargs)
        rendered_label.move_to(self.get_center())
        self.add(rendered_label)


class Graph(Mobject):
    def __init__(self, graphs, vertex_color=RED, edge_colors=[BLACK], scale=5, **kwargs):
        super().__init__(**kwargs)
        self.edges = []
        self.graphs = [nx.MultiGraph(g) for g in graphs]
        self.layout = nx.kamada_kawai_layout(self.graphs[0], dim=3)
        self._scale = scale

        self.vertices = [self.vertex(n, fill_color=vertex_color, **kwargs)
                         for n in self.graphs[0].nodes]
        self.add(*self.vertices)

        for g, col in zip(self.graphs, cycle(edge_colors)):
            self.edges.append([])
            for n, e, _ in g.edges:
                self.edges[-1].append(self.edge(n, e, color=col, **kwargs))
            self.add(*self.edges[-1])

    def vertex(self, n, **kwargs):
        defaults = dict(
            radius=0.1,
            resolution=5,
            color=RED,
        )
        defaults.update(kwargs)
        return SimpleSphere(**defaults).move_to(self._scale*self.layout[n])

    def edge(self, start, end, **kwargs):
        if (start == end):
            return CubicBezier([
                self._scale*self.layout[end],
                self._scale*self.layout[end] + [1,1,1],
                self._scale*self.layout[end] + [-1,1,-1],
                self._scale*self.layout[end]], **kwargs)
        else:
            return Line(self._scale*self.layout[start],
                        self._scale*self.layout[end],
                        **kwargs)
    
    def path(self, start, end, graph=0, **kwargs):
        path = nx.shortest_path(self.graphs[graph], start, end)
        return [self.edge(prev, next, **kwargs)
                for prev, next in zip(path[:-1], path[1:])]

    def cycle(self, start, mid1, mid2, **kwargs):
        return (self.path(start, mid1, **kwargs)
                + self.path(mid1, mid2, **kwargs)
                + self.path(mid2, start, **kwargs))

class SimpleSphere(Dot):
    def __init__(self, resolution=20, **kwargs):
        super().__init__(**kwargs)
        for i in range(resolution):
            self.add(Dot(**kwargs).rotate(2*PI/resolution*i + PI/resolution, LEFT))
            self.add(Dot(**kwargs).rotate(2*PI/resolution*i + PI/resolution, UP))


class Rotating3DScene(ThreeDScene):
    def begin_ambient_camera_rotation(self, γ=0, φ=0, θ=0.02):
        for tracker, α in zip([self.renderer.camera.gamma_tracker,
                               self.renderer.camera.phi_tracker,
                               self.renderer.camera.theta_tracker],
                              [γ, φ, θ]):
            tracker.add_updater(lambda m, dt: m.increment_value(α * dt))
            self.add(tracker)

    def stop_ambient_camera_rotation(self):
        for tracker in [self.renderer.camera.gamma_tracker,
                            self.renderer.camera.phi_tracker,
                            self.renderer.camera.theta_tracker]:
            tracker.clear_updaters()
            self.remove(tracker)
    
class SSGraph(Rotating3DScene):
    def construct(self):
        graph = Graph([ssg2])
        for e in graph.edges:
            self.add(*e)
        self.add(*graph.vertices)
        self.begin_ambient_camera_rotation(0.111, 0.057, 0.049)
        self.wait(10)
        self.stop_ambient_camera_rotation()

class GraphConstruct(Rotating3DScene):
    def construct(self):
        graph = Graph([ssg2, ssg3], edge_colors=[DARK_BLUE, ORANGE])

        self.begin_ambient_camera_rotation(0.111, 0.057, 0.049)
        self.play(
            *(FadeIn(v, run_time=2) for v in graph.vertices[0::4]),
            *(FadeIn(v, run_time=3) for v in graph.vertices[1::4]),
            *(FadeIn(v, run_time=4) for v in graph.vertices[2::4]),
            *(FadeIn(v, run_time=5) for v in graph.vertices[3::4]))

        self.wait()

        self.play(*(ShowCreation(e) for e in graph.edges[0]), run_time=3)

        self.wait(3)
        
        self.play(*(FadeOut(e, run_time=1) for e in graph.edges[0]),
                  *(ShowCreation(e, run_time=3) for e in graph.edges[1]))

        self.wait(3)

        self.play(*(FadeOut(e) for e in graph.edges[1]),
                  *(FadeIn(e)  for e in graph.edges[0]))

        self.wait(1)
        
        self.play(*(FadeOut(e) for e in graph.edges[0]),
                  *(FadeIn(e)  for e in graph.edges[1]))

        self.wait(1)
        
        self.play(*(FadeIn(e)  for e in graph.edges[0]))

        self.wait()

        self.stop_ambient_camera_rotation()


class PathFinding(Rotating3DScene):
    def construct(self):
        graph = Graph([ssg2], edge_colors=[LIGHT_GRAY], opacity=0.5)

        self.begin_ambient_camera_rotation(0.111, 0.057, 0.049)
        self.play(FadeIn(graph))
        
        self.wait(19)

        # Isogeny walk problem
        start = graph.vertex(1, fill_color=DARK_BLUE, radius=0.3, resolution=10)
        end = graph.vertex(15, fill_color=DARK_BLUE, radius=0.3, resolution=10)
        self.play(TransformFromCopy(graph.vertices[1], start),
                  TransformFromCopy(graph.vertices[15], end))

        self.wait(8)

        path = graph.path(1, 15, color=BLACK, stroke_width=8)
        for e in path:
            self.play(ShowCreation(e))

        self.wait(18)

        # Undo walk
        self.play(Transform(end, graph.vertices[15]), *(FadeOut(e) for e in path))

        self.wait()

        # Short walk
        path = graph.path(1, 21, color=BLACK, stroke_width=8)
        for e in path:
            self.play(ShowCreation(e))

        end = graph.vertex(21, fill_color=DARK_BLUE, radius=0.3, resolution=10)
        self.play(TransformFromCopy(graph.vertices[21], end))

        self.wait(50)

        # Undo walk
        self.play(Transform(end, graph.vertices[21]), *(FadeOut(e) for e in path))

        self.wait()

        # Cycle
        path = (graph.path(1, 34, color=BLACK, stroke_width=8)
                + graph.path(34, 82, color=BLACK, stroke_width=8)
                + graph.path(82, 1, color=BLACK, stroke_width=8))
        for e in path:
            self.play(ShowCreation(e))

        self.wait(15)

        # Undo walk
        self.play(*(FadeOut(e) for e in path))

        self.wait()
        
        # Alternate path
        end = graph.vertex(15, fill_color=DARK_BLUE, radius=0.3, resolution=10)
        path = graph.path(1, 15, color=BLACK, stroke_width=8)
        altp = (graph.path(1, 3, color=DARK_BLUE, stroke_width=8)
                + graph.path(3, 15, color=DARK_BLUE, stroke_width=8))

        self.play(TransformFromCopy(graph.vertices[15], end), *(FadeIn(e) for e in path))

        self.wait()

        for e in altp:
            self.play(ShowCreation(e))

        self.wait(20)
        
        self.stop_ambient_camera_rotation()


class Cycles(Rotating3DScene):
    def construct(self):
        graph = Graph([ssg2], edge_colors=[LIGHT_GRAY], opacity=0.5)

        self.begin_ambient_camera_rotation(0.111, 0.057, 0.049)
        
        self.play(FadeIn(graph))

        self.wait()

        cycles = [
            Group(*graph.cycle(1, 34, 82, color=BLUE, stroke_width=8)),
            Group(*graph.cycle(51, 70, 33, color=RED, stroke_width=8)),
            Group(graph.edge(20, 20, color=BLACK, stroke_width=8)),
            Group(*graph.cycle(68, 73, 70, color=LIGHT_BROWN, stroke_width=8)),
            Group(*graph.cycle(38, 31, 83, color=GREEN, stroke_width=8)),
            Group(*graph.cycle(45, 71, 85, color=PURPLE, stroke_width=8)),
            Group(*graph.cycle(23, 15, 67, color=DARK_BLUE, stroke_width=8)),
            Group(*graph.cycle(19, 6, 31, color=TEAL, stroke_width=8)),
        ]

        for c in cycles:
            f = c.copy()
            f.set_color(WHITE)
            self.play(FadeIn(c), ShowPassingFlash(f))

        self.wait(5)
        
        self.play(*(FadeOut(c) for c in cycles))

        self.wait(5)
        
        self.stop_ambient_camera_rotation()

class SIDH(Rotating3DScene):
    def construct(self):
        graph = Graph([ssg2], edge_colors=[LIGHT_GRAY], opacity=0.5)

        self.begin_ambient_camera_rotation(0.111, 0.057, 0.049)
        
        self.play(FadeIn(graph))

        self.wait()
        
        start = graph.vertex(1, fill_color=BLUE, radius=0.2, resolution=10)
        self.play(Transform(graph.vertices[1], start))
        alice = graph.path(1, 15, color=DARK_BLUE, stroke_width=8)
        bob = graph.path(1, 50, color=GREEN, stroke_width=8)
        enda = graph.vertex(15, fill_color=BLUE, radius=0.2, resolution=10)
        endb = graph.vertex(50, fill_color=BLUE, radius=0.2, resolution=10)
        for es in zip_longest(alice, bob):
            self.play(*(ShowCreation(e) for e in es if e is not None))
        self.play(Transform(graph.vertices[15], enda),
                  Transform(graph.vertices[50], endb))
        self.wait()

        atxt = LabeledDot(Text('??', color=DARK_BLUE)).scale(1.5).next_to(enda, UP)
        btxt = LabeledDot(Text('??', color=RED)).scale(1.5).next_to(endb, UP)
        atxt.fade(0.9)
        btxt.fade(0.9)
        self.add_fixed_orientation_mobjects(atxt, btxt)
        self.play(ApplyMethod(atxt.fade, -9), ApplyMethod(btxt.fade, -9))
        self.wait(20)
        
        self.stop_ambient_camera_rotation()


class Hashing(Rotating3DScene):
    def construct(self):
        graph = Graph([ssg2], edge_colors=[LIGHT_GRAY], opacity=0.5)

        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        
        self.begin_ambient_camera_rotation(0.111, 0.057, 0.049)
        
        self.play(FadeIn(graph))

        self.wait()

        j1728 = graph.vertex(20, fill_color=BLUE, radius=0.2, resolution=10)
        l1728 = graph.edge(20, 20, color=BLUE, stroke_width=8)
        j0 = graph.vertex(26, fill_color=ORANGE, radius=0.2, resolution=10)
        l0 = graph.edge(26, 26, color=ORANGE, stroke_width=8)
        j38 = graph.vertex(38, fill_color=GREEN, radius=0.2, resolution=10)
        j31 = graph.vertex(31, fill_color=GREEN, radius=0.2, resolution=10)
        j83 = graph.vertex(83, fill_color=GREEN, radius=0.2, resolution=10)
        loop3 = graph.cycle(38, 31, 83, color=GREEN, stroke_width=8)
        self.play(TransformFromCopy(graph.vertices[20], j1728))
        self.play(ShowCreation(l1728))
        self.play(TransformFromCopy(graph.vertices[26], j0))
        self.play(ShowCreation(l0))
        self.play(TransformFromCopy(graph.vertices[38], j38),
                  TransformFromCopy(graph.vertices[31], j31),
                  TransformFromCopy(graph.vertices[83], j83))
        for e in loop3:
            self.play(ShowCreation(e))
        self.wait(15)

        self.play(FadeOut(l1728),
                  Transform(j0, graph.vertices[26]), FadeOut(l0),
                  Transform(j38, graph.vertices[38]),
                  Transform(j31, graph.vertices[31]),
                  Transform(j83, graph.vertices[83]),
                  *(FadeOut(e) for e in loop3))
        self.wait()

        walk = graph.path(20, 15, color=DARK_BLUE, stroke_width=8)
        end = graph.vertex(15, fill_color=RED, radius=0.2, resolution=10)
        for e in walk:
            self.play(ShowCreation(e))
        self.play(TransformFromCopy(graph.vertices[15], end))
        self.wait(2)
        
        cycle = Group(*graph.cycle(15, 83, 21, color=ORANGE, stroke_width=8))
        f = cycle.copy()
        f.set_color(WHITE)
        self.play(FadeIn(cycle), ShowPassingFlash(f))
        self.play(FadeOut(cycle))
        self.wait(10)

        self.play(*(FadeOut(e) for e in walk))
        self.wait(5)
        self.play(*(FadeIn(e) for e in walk))
        self.wait(5)
        self.play(*(FadeOut(e) for e in walk))
        self.wait(25)
        
        self.play(Transform(j1728, graph.vertices[20]))
        self.wait(40)
        
        self.stop_ambient_camera_rotation()


ssg2 = {0: [14],
  1: [25, 39, 82],
  2: [9, 42, 79],
  3: [30, 51, 70],
  4: [22, 43, 78],
  5: [28, 46, 75],
  6: [15, 22, 24],
  7: [12, 40, 81],
  8: [24, 55, 66],
  9: [21, 24],
  10: [15, 27],
  11: [12, 17, 29],
  12: [25],
  13: [26, 44, 77],
  14: [16, 22],
  15: [],
  16: [23, 28],
  17: [37, 84],
  18: [21, 26, 34],
  19: [21, 57, 64],
  20: [20, 30],
  21: [],
  22: [],
  23: [36, 85],
  24: [],
  25: [28],
  26: [26],
  27: [29, 32],
  28: [],
  29: [33],
  30: [32],
  31: [32, 38, 83],
  32: [],
  33: [43, 78],
  34: [39, 82],
  35: [48, 65, 76],
  36: [65, 74],
  37: [61, 69],
  38: [54, 83],
  39: [41],
  40: [48, 53],
  41: [60, 72],
  42: [51, 59],
  43: [63],
  44: [66, 75],
  45: [67, 75, 86],
  46: [76, 77],
  47: [69, 74, 85],
  48: [59],
  49: [56, 62, 80],
  50: [52, 53, 64],
  51: [58],
  52: [74, 84],
  53: [58],
  54: [64, 76],
  55: [61, 77],
  56: [85, 86],
  57: [67, 71],
  58: [78],
  59: [72],
  60: [66, 84],
  61: [80],
  62: [73, 79],
  63: [68, 70],
  64: [],
  65: [72],
  66: [],
  67: [83],
  68: [71, 81],
  69: [71],
  70: [79],
  71: [],
  72: [],
  73: [81, 86],
  74: [],
  75: [],
  76: [],
  77: [],
  78: [],
  79: [],
  80: [82],
  81: [],
  82: [],
  83: [],
  84: [],
  85: [],
  86: []}

ssg3 = {0: [0, 17],
  1: [5, 8, 58, 63],
  2: [3, 7, 60, 61],
  3: [34, 50, 71],
  4: [23, 33, 41, 80],
  5: [15, 57, 64],
  6: [27, 28, 55, 66],
  7: [7, 23],
  8: [24, 31],
  9: [12, 30, 55, 66],
  10: [13, 15, 46, 75],
  11: [14, 21, 48, 73],
  12: [16, 40, 81],
  13: [18, 31],
  14: [14, 37, 84],
  15: [44, 77],
  16: [22, 52, 69],
  17: [19, 59, 62],
  18: [29, 30],
  19: [20, 46, 75],
  20: [21],
  21: [44, 77],
  22: [29, 60, 61],
  23: [47, 74],
  24: [25, 32],
  25: [28, 53, 68],
  26: [26, 27, 32],
  27: [45, 76],
  28: [50, 71],
  29: [35, 86],
  30: [57, 64],
  31: [38, 83],
  32: [54, 67],
  33: [34, 56, 65],
  34: [44, 77],
  35: [49, 71, 86],
  36: [47, 78, 81, 85],
  37: [64, 72, 79],
  38: [44, 55, 83],
  39: [55, 70, 75, 78],
  40: [79, 81, 85],
  41: [45, 61, 79],
  42: [70, 80, 81, 84],
  43: [72, 78, 82, 85],
  44: [],
  45: [64, 76],
  46: [67, 82],
  47: [53, 63],
  48: [56, 62, 68],
  49: [59, 78, 84],
  50: [69, 86],
  51: [52, 68, 79, 82],
  52: [56, 71],
  53: [70, 73],
  54: [61, 67, 75],
  55: [],
  56: [65],
  57: [76, 84],
  58: [62, 63, 74],
  59: [63, 73],
  60: [67, 80],
  61: [],
  62: [72],
  63: [],
  64: [],
  65: [69, 73],
  66: [82, 83],
  67: [],
  68: [74],
  69: [70],
  70: [],
  71: [],
  72: [86],
  73: [],
  74: [85],
  75: [],
  76: [80],
  77: [83],
  78: [],
  79: [],
  80: [],
  81: [],
  82: [],
  83: [],
  84: [],
  85: [],
  86: []}
