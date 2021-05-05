"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mspihole` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``spihole.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``spihole.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import os
import threading

import click

from .capture import Capture
from .display import Display
from .hub import Hub


@click.command(name='run')
@click.option("-c", "--configuration", type=click.Path(readable=True),
              default=os.path.join(os.path.sep, 'etc', 'spihole.conf'))
def main(configuration):
    click.echo(click.format_filename(configuration))
    hub = Hub()
    capture = Capture(hub.bus)
    display = Display()
    hub.add_subscriber(display)

    startables = [hub, display, capture]
    map(lambda x: x.start(), startables)

    stop_evt = threading.Event()
    while not stop_evt.is_set():
        stop_evt.wait(30)  # interruptible idle
