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
        pass


    @classmethod
    def run(cls):
        moderngl_window.run_window_config(cls)


if __name__ == '__main__':
    pass