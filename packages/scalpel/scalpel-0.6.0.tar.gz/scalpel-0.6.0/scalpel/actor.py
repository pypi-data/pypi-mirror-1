import Queue
import threading

def command(method):
    """Decorator to enqueue method calls in Actor instances."""
    def enqueue_call(self, *args, **kwargs):
        args = list(args)
        args.insert(0, self)
        self._commands.put((method, args, kwargs))
    return enqueue_call


class Actor(threading.Thread):
    """An implementation of the actor model."""

    def __init__(self):
        threading.Thread.__init__(self)
        self._commands = Queue.Queue()
        self._must_stop = False

    @command
    def stop(self):
        self._must_stop = True

    def run(self):
        while not self._must_stop:
            cmd, args, kwargs = self._commands.get()
            cmd(*args, **kwargs)


if __name__ == '__main__':

    import time
    class MyActor(Actor):
        @command
        def say(self, sentence):
            time.sleep(0.1)
            print sentence

    a = MyActor()
    a.start()
    a.say("Hello.")
    a.say("Bye.")
    a.stop()
    print "Main thread finished."
