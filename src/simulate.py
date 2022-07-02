import os

import numpy
import moderngl
import PIL.Image

import gui


class GameOfLife(gui.GUI):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        seed = 2106
        rng = numpy.random.default_rng(seed)

        self.display_prog = self.ctx.program(
            vertex_shader = '''
                #version 460

                in vec2 in_vert;
                out vec2 tex;

                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                    tex = in_vert;
                }
            ''',
            fragment_shader='''
                #version 460

                uniform sampler2D Texture1;
                uniform sampler2D Texture2;

                in vec2 tex;
                out vec4 f_color;

                void main() {
                    vec4 world = texture(Texture1, vec2((tex.x + 1.) / 2., (tex.y + 1.) / 2.));
                    //vec4 colormap = texture(Texture2, vec2((tex.x + 1.) / 2., 0.0));
                    if(world.r > 0.5) {
                        f_color = texture(Texture2, vec2(world.g / 256., 0.0));
                    } else {
                        f_color = vec4(0., 0., 0., 1.);
                    }
                }
            ''',
        )

        self.transform_prog = self.ctx.program(
            vertex_shader = '''
                #version 460

                #define LIVING 0.0
                #define DEAD 1.0

                uniform sampler2D Texture1;

                out vec4 out_vert;

                vec2 cell(int x, int y) {
                    ivec2 tSize = textureSize(Texture1, 0).xy;
                    vec4 state = texelFetch(Texture1, ivec2((x + tSize.x) % tSize.x, (y + tSize.y) % tSize.y), 0);
                    return vec2(state.r, state.g);
                }

                void main() {
                    int width = textureSize(Texture1, 0).x;
                    ivec2 in_text = ivec2(gl_VertexID % width, gl_VertexID / width);
                    vec2 state = cell(in_text.x, in_text.y);

                    int neighbours = 0;
                    if (cell(in_text.x - 1, in_text.y - 1).x < 0.5) neighbours++;
                    if (cell(in_text.x - 1, in_text.y + 0).x < 0.5) neighbours++;
                    if (cell(in_text.x - 1, in_text.y + 1).x < 0.5) neighbours++;
                    if (cell(in_text.x + 1, in_text.y - 1).x < 0.5) neighbours++;
                    if (cell(in_text.x + 1, in_text.y + 0).x < 0.5) neighbours++;
                    if (cell(in_text.x + 1, in_text.y + 1).x < 0.5) neighbours++;
                    if (cell(in_text.x + 0, in_text.y + 1).x < 0.5) neighbours++;
                    if (cell(in_text.x + 0, in_text.y - 1).x < 0.5) neighbours++;

                    if (state.x < 0.5) {
                        if ((neighbours == 2 || neighbours == 3)) {
                            out_vert = vec4(LIVING, state.y, 1., 1.);
                        } else {
                            out_vert = vec4(DEAD, state.y + 1, 1., 1.);
                        }
                        
                    } else {
                        if ((neighbours == 3)) {
                            out_vert = vec4(LIVING, state.y, 1., 1.);
                        } else {
                            out_vert = vec4(DEAD, state.y, 1., 1.);
                        }
                    }
                }
            ''',
            varyings=['out_vert']
        )

        self.display_prog['Texture1'].value = 0
        self.display_prog['Texture2'].value = 1

        self.w_width = 4096
        self.w_height = 4096
        self.world = numpy.round(rng.random((self.w_width, self.w_height, 4))).astype('f4')
        # self.world = numpy.round(rng.normal(loc=0.5, scale=0.5 / 3, size=(self.w_width, self.w_height, 4))).astype('f4')
        # self.world = numpy.round(rng.exponential(scale=1, size=(self.w_width, self.w_height, 4))).astype('f4')
        self.world[:,:, 1] = 1

        self.texture_world = self.ctx.texture((self.w_width, self.w_height), 4, self.world.tobytes(), dtype='f4')
        self.texture_world.filter = moderngl.NEAREST, moderngl.NEAREST

        self.texture_colormap = self.load_texture_2d(f'life_00.png')

        vertices = numpy.array(
            [
                -1.0, -1.0,
                -1.0, 1.0,
                1.0, -1.0,
                1.0, 1.0
            ], dtype='f4')
        self.vbo = self.ctx.buffer(vertices)
        self.vao = self.ctx.vertex_array(self.display_prog, self.vbo, 'in_vert')

        self.tao = self.ctx.vertex_array(self.transform_prog, [])
        self.pbo = self.ctx.buffer(reserve=self.world.nbytes)

        self.update_delay = 1./64.
        self.last_updated = 0.

        self.fbo = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture(self.window_size, 4)]
        )

        self.recording = False
        self.recording_session = 0
        self.recording_frame = 0

        self.output_pattern = os.path.join('..', 'data', 'output', 'gol_{0}.{1}.png')


    def key_event(self, key, action, modifiers):
        if action == self.wnd.keys.ACTION_PRESS:
            if key == self.wnd.keys.SPACE:
                self.recording = not self.recording
                if not self.recording:
                    self.recording_session += 1
                    self.recording_frame = 0
            elif key == self.wnd.keys.ENTER:
                self.texture_world = self.ctx.texture((self.w_width, self.w_height), 4, self.world.tobytes(), dtype='f4')
                self.texture_world.filter = moderngl.NEAREST, moderngl.NEAREST

    
    def render(self, time, frame_time):
        self.ctx.clear(0., 0., 0.)
        self.texture_world.use(location=0)
        self.texture_colormap.use(location=1)

        if time - self.last_updated > self.update_delay:
            self.tao.transform(self.pbo, vertices=self.w_width * self.w_height)
            self.texture_world.write(self.pbo)
            self.last_updated = time

        self.vao.render(moderngl.TRIANGLE_STRIP)

        if self.recording:
            self.fbo.use()
            self.vao.render(moderngl.TRIANGLE_STRIP)
            image = PIL.Image.frombytes('RGBA', self.fbo.size, self.fbo.read(components=4))
            image = image.transpose(PIL.Image.Transpose.FLIP_TOP_BOTTOM)
            output_file_path = self.output_pattern.format(str(self.recording_session).zfill(2), str(self.recording_frame).zfill(6))
            image.save(output_file_path)
            self.recording_frame += 1


if __name__ == '__main__':
    GameOfLife.run()