import os

import moderngl_window


class GUI(moderngl_window.WindowConfig):
    gl_version = (4, 6)
    title = "Game of Life"
    window_size = (1024, 1024)
    aspect_ratio = window_size[0] / window_size[1]
    resizable = False

    resource_dir = os.path.normpath(os.path.join('..', 'resources'))


    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    @classmethod
    def add_arguments(cls, parser):
        cls.parser = parser
        parser.description='A shader-based implementation of John Horton Conway\'s game of life. The "game" simulates the life of cells on a grid. Cells are birthed or die depending on the state of its neighbors.'
        parser.add_argument('--seed', type=int, default=2106, help='the seed for the random number generator (default: 2106)')
        parser.add_argument('--width', type=int, default=1024, help='the width of the simulated cell grid (default: 1024)')
        parser.add_argument('--height', type=int, default=1024, help='the height of the simulated cell grid (default: 1024)')
        parser.add_argument('--colormap', type=str, default='life_00.png', help='the map to color the cells according to state; a 256x1 px file placed in the resources folder (default: life_00.png)')
        output_pattern=os.path.join('..', 'data', 'output', 'gol_{0}.{1}.png')
        parser.add_argument('--output', type=str, default=output_pattern, help=f'output destination of simulation frames (default: {output_pattern})')
        parser.add_argument('--distribution', type=str, default='uniform', help='the distribution according to which the grid is populated with living cells (default: uniform)', choices=['uniform', 'exponential', 'normal'])
    

    @classmethod
    def run(cls):
        moderngl_window.run_window_config(cls)


if __name__ == '__main__':
    pass