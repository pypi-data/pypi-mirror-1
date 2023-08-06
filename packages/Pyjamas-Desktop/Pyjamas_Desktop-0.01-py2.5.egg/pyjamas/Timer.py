from gobject import timeout_add

class Timer:

    def __init__(self, time, notify):

        print "Timer arg count", notify.onTimer.func_code.co_argcount
        self.notify_fn = notify.onTimer
        self.id = timeout_add(time, self.notify)

    def notify(self, *args):
        if self.notify_fn.func_code.co_argcount == 2:
            self.notify_fn(self)
        else:
            self.notify_fn()

    def cancel(self):
        print "TODO"

    def getID(self):
        return id

