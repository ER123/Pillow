#
# The Python Imaging Library
# $Id$
#
# screen grabber (macOS and Windows only)
#
# History:
# 2001-04-26 fl  created
# 2001-09-17 fl  use builtin driver, if present
# 2002-11-19 fl  added grabclipboard support
#
# Copyright (c) 2001-2002 by Secret Labs AB
# Copyright (c) 2001-2002 by Fredrik Lundh
#
# See the README file for information on usage and redistribution.
#

import os
import subprocess
import sys
import tempfile

from . import Image

if sys.platform not in ["win32", "darwin"]:
    raise ImportError("ImageGrab is macOS and Windows only")


def grab(bbox=None, include_layered_windows=False, all_screens=False):
    if sys.platform == "darwin":
        fh, filepath = tempfile.mkstemp(".png")
        os.close(fh)
        subprocess.call(["screencapture", "-x", filepath])
        im = Image.open(filepath)
        im.load()
        os.unlink(filepath)
        if bbox:
            im_cropped = im.crop(bbox)
            im.close()
            return im_cropped
    else:
        offset, size, data = Image.core.grabscreen(include_layered_windows, all_screens)
        im = Image.frombytes(
            "RGB",
            size,
            data,
            # RGB, 32-bit line padding, origin lower left corner
            "raw",
            "BGR",
            (size[0] * 3 + 3) & -4,
            -1,
        )
        if bbox:
            x0, y0 = offset
            left, top, right, bottom = bbox
            im = im.crop((left - x0, top - y0, right - x0, bottom - y0))
    return im


def grabclipboard():
    if sys.platform == "darwin":
        fh, filepath = tempfile.mkstemp(".jpg")
        os.close(fh)
        commands = [
            'set theFile to (open for access POSIX file "'
            + filepath
            + '" with write permission)',
            "try",
            "    write (the clipboard as JPEG picture) to theFile",
            "end try",
            "close access theFile",
        ]
        script = ["osascript"]
        for command in commands:
            script += ["-e", command]
        subprocess.call(script)

        im = None
        if os.stat(filepath).st_size != 0:
            im = Image.open(filepath)
            im.load()
        os.unlink(filepath)
        return im
    else:
        data = Image.core.grabclipboard()
        if isinstance(data, bytes):
            from . import BmpImagePlugin
            import io

            return BmpImagePlugin.DibImageFile(io.BytesIO(data))
        return data
