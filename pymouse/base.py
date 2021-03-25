from threading import Thread

class PyMouseMeta(object):

    def press(self, x, y, button = 1):
        raise NotImplementedError

    def release(self, x, y, button = 1):
        raise NotImplementedError

    def click(self, x, y, button = 1, n = 1):
        for i in range(n):
            self.press(x, y, button)
            self.release(x, y, button)
 
    def move(self, x, y):
        raise NotImplementedError

    def position(self):
        raise NotImplementedError

    def screen_size(self):
        raise NotImplementedError

class PyMouseEventMeta(Thread):
    def __init__(self, capture=False, captureMove=False):
        Thread.__init__(self)
        self.daemon = True
        self.capture = capture
        self.captureMove = captureMove
        self.state = True

    def stop(self):
        self.state = False

    def click(self, x, y, button, press):
        pass

    def move(self, x, y):
        pass
