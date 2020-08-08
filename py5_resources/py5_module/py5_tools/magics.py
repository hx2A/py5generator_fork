import time
import io
from pathlib import Path
import tempfile

from IPython.display import display, SVG, Image
from IPython.core.magic import Magics, magics_class, cell_magic, line_magic
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring

import PIL

from .run import run_single_frame_sketch


_unspecified = object()


@magics_class
class Py5Magics(Magics):

    def _filename_check(self, filename):
        filename = Path(filename)
        if not filename.parent.exists():
            filename.parent.mkdir(parents=True)
        return filename

    @magic_arguments()
    @argument('width', type=int, help='width of SVG drawing')
    @argument('height', type=int, help='height of SVG drawing')
    @argument('--filename', type=str, dest='filename', help='save SVG image to file')
    @argument('--no-warnings', dest='suppress_warnings', action='store_true',
              help="suppress name conflict warnings")
    @cell_magic
    def py5drawsvg(self, line, cell):
        """Create an SVG image with py5 and embed result in the notebook.

        For users who are familiar with Processing and py5 programming, you can
        pretend the code in this cell will be executed in a sketch with no
        `draw()` function and your code in the `setup()` function. It will use
        the SVG renderer.

        The below example will create a red square on a gray background:

        ```
            %%py5drawsvg 500 250
            background(128)
            fill(255, 0, 0)
            rect(80, 100, 50, 50)
        ```

        As this is creating an SVG image, you cannot do operations on the
        `pixels` or `np_pixels` arrays. Use `%%py5draw` instead.

        Code used in this cell can reference functions and variables defined in
        other cells. This will create a name conflict if your functions and
        variables overlap with py5's. A name conflict may cause an error. If
        such a conflict is detected, py5 will issue a helpful warning to alert
        you to the potential problem. You can suppress warnings with the
        --no_warnings flag.
        """
        args = parse_argstring(self.py5drawsvg, line)
        svg = run_single_frame_sketch(
            'SVG', cell, args.width, args.height, user_ns=self.shell.user_ns,
            suppress_warnings=args.suppress_warnings)
        if svg:
            if args.filename:
                filename = self._filename_check(args.filename)
                with open(filename, 'w') as f:
                    f.write(svg)
            display(SVG(svg))

    @magic_arguments()
    @argument('width', type=int, help='width of PNG drawing')
    @argument('height', type=int, help='height of PNG drawing')
    @argument('--filename', dest='filename', help='save image to file')
    @argument('--no-warnings', dest='suppress_warnings', action='store_true',
              help="suppress name conflict warnings")
    @cell_magic
    def py5draw(self, line, cell):
        """Create a PNG image with py5 and embed result in the notebook.

        For users who are familiar with Processing and py5 programming, you can
        pretend the code in this cell will be executed in a sketch with no
        `draw()` function and your code in the `setup()` function. It will use
        the default renderer.

        The below example will create a red square on a gray background:

        ```
            %%py5draw 500 250
            background(128)
            fill(255, 0, 0)
            rect(80, 100, 50, 50)
        ```

        Code used in this cell can reference functions and variables defined in
        other cells. This will create a name conflict if your functions and
        variables overlap with py5's. A name conflict may cause an error. If
        such a conflict is detected, py5 will issue a helpful warning to alert
        you to the potential problem. You can suppress warnings with the
        --no_warnings flag.
        """
        args = parse_argstring(self.py5draw, line)
        png = run_single_frame_sketch(
            'HIDDEN', cell, args.width, args.height, user_ns=self.shell.user_ns,
            suppress_warnings=args.suppress_warnings)
        if png:
            if args.filename:
                filename = self._filename_check(args.filename)
                PIL.Image.open(io.BytesIO(png)).convert(
                    mode='RGB').save(filename)
            display(Image(png))

    @line_magic
    @magic_arguments()
    @argument('-d', type=int, dest='delay', default=0, help='delay in seconds')
    def py5screenshot(self, line):
        """Take a screenshot of the current running sketch.

        Use the -d argument to wait before taking the screenshot.

        The returned image is a `PIL.Image` object. It can be assigned to a
        variable or embedded in the notebook.

        Below is an example demonstrating how to take a screenshot after a two
        second delay and assign it to the `img` variable. The image is then
        saved to a file. When run from a notebook, the image is embedded in the
        output.

        ```
            img = %py5screenshot -d 2
            img.save('image.png')
            img
        ```
        """
        args = parse_argstring(self.py5screenshot, line)
        import py5
        sketch = py5.get_current_sketch()

        if not sketch.is_running:
            print('The current sketch is not running.')
            return

        class Hook:

            def __init__(self, filename):
                self.filename = filename
                self.is_ready = False

            def __call__(self, sketch):
                sketch.save_frame(self.filename)
                sketch._remove_post_hook('draw', 'py5screenshot_hook')
                self.is_ready = True

        time.sleep(args.delay)

        with tempfile.NamedTemporaryFile(suffix='.png') as png_file:
            hook = Hook(png_file.name)
            sketch._add_post_hook('draw', 'py5screenshot_hook', hook)

            while not hook.is_ready:
                time.sleep(0.02)

            img = PIL.Image.open(png_file.name)

            return img

    @line_magic
    @magic_arguments()
    @argument('dirname', type=str, help='directory to save the frames')
    @argument('--filename', type=str, dest='filename', default='frame_####.png',
              help='filename to save frames to')
    @argument('-d', type=int, dest='start_delay', default=0,
              help='recording start delay in seconds')
    @argument('-s', dest='start', type=int,
              help='frame starting number instead of sketch frame_count')
    @argument('--limit', type=int, dest='limit', default=0,
              help='limit the number of frames to save (default 0 means no limit)')
    def py5screencapture(self, line):
        """Save the current running sketch's frames to a directory.

        Use the -d argument to wait before starting.

        The below example will save the next 50 frames to the `/tmp/frames`
        directory after a 3 second delay. The filenames will be saved with the
        default name 'frame_####.png' with numbering that starts at 0.

        ```
            %py5screencapture /tmp/frames -d 3 -s 0 --limit 50
        ```

        If a limit is given, this line magic will wait to return a list of the
        filenames. Otherwise, it will return right away as the frames are saved
        in the background.
        """
        args = parse_argstring(self.py5screencapture, line)
        import py5
        sketch = py5.get_current_sketch()

        if not sketch.is_running:
            print('The current sketch is not running.')
            return

        dirname = Path(args.dirname)
        if not dirname.exists():
            dirname.mkdir(parents=True)
        print(f'writing frames to {str(args.dirname)}...')

        time.sleep(args.start_delay)

        class Hook:

            def __init__(self):
                self.num_offset = None
                self.filenames = []
                self.exception = None
                self.is_ready = False

            def _end_hook(self, sketch):
                sketch._remove_post_hook('draw', 'py5screencapture_hook')
                self.is_ready = True

            def __call__(self, sketch):
                try:
                    if self.num_offset is None:
                        self.num_offset = 0 if args.start is None else sketch.frame_count - args.start
                    num = sketch.frame_count - self.num_offset
                    frame_filename = sketch._insert_frame(
                        str(dirname / args.filename), num=num)
                    sketch.save_frame(frame_filename)
                    self.filenames.append(frame_filename)
                    if len(self.filenames) == args.limit:
                        self._end_hook(sketch)
                except Exception as e:
                    self.exception = e
                    self._end_hook(sketch)

        hook = Hook()
        sketch._add_post_hook('draw', 'py5screencapture_hook', hook)

        if args.limit:
            while not hook.is_ready:
                time.sleep(0.02)
                print(f'saving frame {len(hook.filenames)}/{args.limit}', end='\r')
            print('')

            if hook.exception:
                print('error running magic:', hook.exception)
            else:
                return hook.filenames

    @line_magic
    @magic_arguments()
    @argument('filename', type=str, help='filename of gif to create')
    @argument('count', type=int, help='number of Sketch snapshots to create')
    @argument('delay', type=int, help='time in milliseconds between Sketch snapshots')
    @argument('duration', type=int, help='time in milliseconds between frames in the GIF')
    @argument('-d', type=int, dest='start_delay', default=0,
              help='recording start delay in seconds')
    @argument('-l', dest='loop', type=int, default=0,
              help='number of times for the GIF to loop (default of 0 loops indefinitely')
    @argument('--optimize', action='store_true', help='optimize GIF palette')
    def py5animatedgif(self, line):
        """Save the current running sketch's frames to a directory.

        Use the -d argument to wait before starting.

        The below example will create a 10 frame animated GIF saved to
        '/tmp/animated.gif'. The frames will be recorded 1000 milliseconds
        apart after a 3 second delay. The animated GIF will display the frames
        with a 500 millisecond delay between each one and will loop indefinitely.

        ```
            %py5screencapture /tmp/animated.gif 10 1000 500 -d 3
        ```
        """
        args = parse_argstring(self.py5animatedgif, line)
        import py5
        sketch = py5.get_current_sketch()

        if not sketch.is_running:
            print('The current sketch is not running.')
            return

        filename = Path(args.filename)
        time.sleep(args.start_delay)

        class Hook:

            def __init__(self):
                self.frames = []
                self.is_ready = False
                self.last_frame_time = 0
                self.exception = None

            def _end_hook(self, sketch):
                sketch._remove_post_hook('draw', 'py5animatedgif_hook')
                self.is_ready = True

            def __call__(self, sketch):
                try:
                    if time.time() - self.last_frame_time < args.delay / 1000:
                        return
                    sketch.load_np_pixels()
                    self.frames.append(sketch.np_pixels[:, :, 1:].copy())
                    self.last_frame_time = time.time()
                    if len(self.frames) == args.count:
                        self._end_hook(sketch)
                except Exception as e:
                    self.exception = e
                    self._end_hook(sketch)

        hook = Hook()
        sketch._add_post_hook('draw', 'py5animatedgif_hook', hook)

        while not hook.is_ready:
            time.sleep(0.05)
            print(f'collecting frame {len(hook.frames)}/{args.count}', end='\r')
        print('')

        if hook.exception:
            print('error running magic:', hook.exception)
        else:
            if not filename.parent.exists():
                filename.parent.mkdir(parents=True)

            img1 = PIL.Image.fromarray(hook.frames[0], mode='RGB')
            imgs = [PIL.Image.fromarray(arr, mode='RGB') for arr in hook.frames[1:]]
            img1.save(filename, save_all=True, duration=args.duration,
                      loop=args.loop, optimize=args.optimize, append_images=imgs)

            return str(filename)


def load_ipython_extension(ipython):
    ipython.register_magics(Py5Magics)
