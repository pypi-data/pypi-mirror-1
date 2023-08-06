# PyStar grid demo.

from Tkinter import *
from astar.grid import Grid
from random import randint

BUTTONS = (("Start", "start"),
           ("Finish", "finish"),
           ("Blocked", "block"),
           ("Walkable (0)", 0),
           ("Walkable (1)", 1),
           ("Walkable (2)", 2),
           ("Walkable (3)", 3))

COLOURS = {
    0: "green1",
    1: "green2",
    2: "green3",
    3: "green4",
    "block": "black",
    "start": "blue",
    "finish": "red",
    "path": "yellow",
    "selected": "white",
    "outline": "grey"
}

class GridDemo(Frame):
    def __init__(self, parent, width = 30, height = 30, diag = False,
                 boxsize = 20, linewidth = 5):
        Frame.__init__(self, parent)

        self.grid = Grid(width, height, diag)
        self.width = width
        self.height = height
        self.path = None

        self.boxsize = boxsize
        self.linewidth = linewidth

        self.canvas = Canvas(self,
                             width = width * boxsize,
                             height = height * boxsize,
                             relief = SUNKEN)

        self.canvas.bind("<Button-1>", self.paint)
        self.canvas.bind("<ButtonRelease-1>", self.update_path)
        self.canvas.bind("<B1-Motion>", self.paint)

        self.canvas.pack(side = LEFT)

        self.panel = Frame(self, relief = SUNKEN, borderwidth = 2)
        self.panel.pack(side = RIGHT, fill = Y)

        self.paintflag = IntVar()
        self.paintflag.set(2)

        for (num, (name, tag)) in enumerate(BUTTONS):
            button = Radiobutton(self.panel, text = name, value = num,
                                 variable = self.paintflag, fg = "white",
                                 bg = COLOURS[tag], padx = 5, pady = 5,
                                 selectcolor = COLOURS["selected"],
                                 anchor = W)
            button.pack(side = TOP, fill = X)

        button = Button(self.panel, text = "Reset", padx = 5, pady = 5,
                        command = self.reset)
        button.pack(side = TOP, fill = X)

        button = Button(self.panel, text = "Randomize", padx = 5, pady = 5,
                        command = self.randomize)
        button.pack(side = TOP, fill = X)

        self.status = Label(self.panel, bg = "bisque")
        self.status.pack(side = TOP, fill = BOTH, expand = TRUE)

        self.ids = {}
        self.coords = {}
        for x in xrange(width):
            for y in xrange(height):
                x1 = x * boxsize
                y1 = y * boxsize
                x2 = x1 + boxsize + 2
                y2 = y1 + boxsize + 2

                id = self.canvas.create_rectangle(x1, y1, x2, y2)

                self.ids[x, y] = id
                self.coords[id] = (x, y)

        self.reset()
        self.pack()

    def reset(self):
        self.start = (1, 1)
        self.finish = (self.width - 2, self.height - 2)

        for x in xrange(self.width):
            for y in xrange(self.height):
                self.grid.set_weight((x, y), 0)
                self.update_box(self.ids[x, y])

        self.update_path(True)

    def randomize(self):
        for x in xrange(self.width):
            for y in xrange(self.height):
                if (x, y) == self.start:
                    continue

                if (x, y) == self.finish:
                    continue

                if self.grid.get_weight((x, y)) is None:
                    continue

                weight = randint(0, 3)
                self.grid.set_weight((x, y), weight)
                self.update_box(self.ids[x, y])

        self.update_path(True)

    def update_path(self, force = False):
        if not self.path or force:
            self.remove_path()
            self.after_idle(self.draw_path)

    def paint(self, event):
        self.remove_path()
        id = self.canvas.find_closest(event.x, event.y)[0]
        pos = self.coords[id]
        flag = self.paintflag.get()
        tag = BUTTONS[flag][1]

        if   tag == "start":
            oldid = self.ids[self.start]
            self.start = self.coords[id]
            self.update_box(oldid)
        elif tag == "finish":
            oldid = self.ids[self.finish]
            self.finish = self.coords[id]
            self.update_box(oldid)
        elif tag == "block":
            self.grid.set_weight(pos, None)
        else:
            self.grid.set_weight(pos, tag)

        self.update_box(id)

    def update_box(self, id):
        pos = self.coords[id]

        if   pos == self.start:
            colour = COLOURS["start"]
        elif pos == self.finish:
            colour = COLOURS["finish"]
        else:
            weight = self.grid.get_weight(pos)
            if weight is None: weight = "block"
            colour = COLOURS[weight]

        self.canvas.itemconfig(id, fill = colour,
                               outline = COLOURS["outline"])

    def draw_path(self):
        self.path = self.grid.find_path(self.start, self.finish)

        if self.path:
            points = []
            for (x, y) in self.path:
                points.append((x + 0.5) * self.boxsize)
                points.append((y + 0.5) * self.boxsize)

            kw = dict(fill = COLOURS["path"], width = self.linewidth,
                      arrow = LAST, tags = ("path"))

            self.canvas.create_line(*points, **kw)
            status = "Path cost: %g" % self.grid.cost
        else:
            status = "No path"

        self.status.config(text = status)

    def remove_path(self):
        self.canvas.delete("path")
        self.path = None

if __name__ == "__main__":
    root = Tk()
    root.title("PyStar Grid Demo")
    root.resizable(False, False)
    app = GridDemo(root, diag = False)
    app.mainloop()
