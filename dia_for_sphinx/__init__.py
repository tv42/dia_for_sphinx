import os
import subprocess
from docutils.parsers.rst.directives import images
from docutils.parsers.rst import directives
from docutils import utils

def export_dia(dia_path, png_path):
    # dia insists on outputting a "src -> dst" text to stdout,
    # and subprocess can't pass other fds than stdin/out/err,
    # so we need to jump through hoops

    tmp = '%s.tmp' % png_path
    with file(dia_path, 'rb') as dia_fp:
        subprocess.check_call(
            args=[
                'dia',
                '--log-to-stderr',
                '--filter=cairo-png',
                '--export=%s' % tmp,
                '/dev/stdin',
                ],
            stdin=dia_fp,
            close_fds=False,
            )
    os.rename(tmp, png_path)

class Dia(images.Image):
    def run(self):
        (path,) = self.arguments
        base, ext = os.path.splitext(path)
        assert ext == '.dia'
        png = '%s.png' % base

        source = self.state_machine.document.current_source
        source_rel = utils.relative_path(None, source)
        source_dir = os.path.dirname(source_rel)

        # TODO check path for evil
        real_path = os.path.join(source_dir, path)

        # TODO put this elsewhere, don't litter source tree
        real_png = os.path.join(source_dir, png)

        print 'Dia from %s to %s' % (real_path, real_png)
        export_dia(
            dia_path=real_path,
            png_path=real_png,
            )
        self.arguments[0] = png
        return super(Dia, self).run()

def setup(Sphinx):
    Sphinx.add_directive('dia', Dia)
