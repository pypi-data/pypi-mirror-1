# -*- coding: utf-8 -*-

import logging
import os
import subprocess

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from djboss.commands import *


@command
@argument('-w', '--watch', action='store_true', default=False,
    help="Monitor the source directory, rebuilding the CSS when Sass changes")
@argument('-t', '--trace', action='store_true', default=False,
    help="Print a full Ruby stacktrace on errors.")
def compass(args):
    """Compile Sass stylesheets using Compass."""
    
    # Get the only required settings.
    input_dir = getattr(settings, 'COMPASS_INPUT', None)
    output_dir = getattr(settings, 'COMPASS_OUTPUT', None)
    
    if not (input_dir or output_dir):
        raise ImproperlyConfigured(
            "Please specify COMPASS_INPUT and COMPASS_OUTPUT settings")
    elif not input_dir:
        raise ImproperlyConfigured("Please specify a COMPASS_INPUT setting")
    elif not output_dir:
        raise ImproperlyConfigured("Please specify a COMPASS_OUTPUT setting")
    
    # Optional Django settings
    style = getattr(settings, 'COMPASS_STYLE', 'compact')
    requires = getattr(settings, 'COMPASS_REQUIRES', ())
    image_dir = getattr(settings, 'COMPASS_IMAGE_DIR', None)
    script_dir = getattr(settings, 'COMPASS_SCRIPT_DIR', None)
    relative_urls = getattr(settings, 'COMPASS_RELATIVE_URLS', False)
    
    # Build the command line
    command_line = ['compass']
    
    # Directories
    command_line.extend(['--sass-dir', input_dir])
    command_line.extend(['--css-dir', output_dir])
    if image_dir:
        command_line.extend(['--images-dir', image_dir])
    if script_dir:
        command_line.extend(['--javascripts-dir', script_dir])
    
    # Extra options
    command_line.extend(['--output-style', style])
    for requirement in requires:
        command_line.extend(['--require', requirement])
    if relative_urls:
        command_line.extend(['--relative-assets'])
    
    # Runtime options
    if getattr(logging, args.log_level) >= logging.WARN:
        command_line.extend(['--quiet'])
    if args.watch:
        command_line.extend(['--watch'])
    if args.trace:
        command_line.extend(['--trace'])
    
    logging.info(subprocess.list2cmdline(command_line))
    os.execvp('compass', command_line)
