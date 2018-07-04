import matplotlib.pyplot as plt

from .utils import make_output_file


class Renderer:
    """
    Base class
    """
    def __init__(self, args):
        self.args = args

    @property
    def output(self):
        output = self.args.figoutput
        if output is None:
            base_path = self.args.data
            if base_path is None:
                base_path = 'iostat'
            output = make_output_file(base_path, 'png')
        return output

    def close_handler(self, event):
        plt.close(self.fig)
        raise SystemExit

    def render(self):
        if self.args.backend == 'Agg':
            self.save()
        else:
            self.show()
        plt.close(self.fig)
