import matplotlib.pyplot as plt


class Renderer:
    """
    Base class
    """
    def __init__(self, args):
        self.args = args

    def close_handler(self, event):
        plt.close(self.fig)
        raise SystemExit

    def render(self):
        if self.args.backend == 'Agg':
            self.save()
        else:
            self.show()
        plt.close(self.fig)
