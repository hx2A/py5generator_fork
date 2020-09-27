# flake8: noqa
"""
This code demos py5 as it would look to a user running from the PDE a PDE "mode".

It can also be run from the command line, like so:

$ run_sketch test_pde_mode.py
"""


def settings():
    size(500, 500, P2D)


def setup():
    background(255)
    rect_mode(CENTER)
    print(width, height)


def draw():
    if is_key_pressed():
        print('frameRate', get_frame_rate())

    fill(random(255), random(255), random(255), 50.0)
    rect(mouse_x, mouse_y, 40, 40)

    if frame_count == 300:
        save_frame('/tmp/frame_###.png')


def mouse_entered():
    print('mouse entered')


def mouse_exited():
    print('mouse exited')
