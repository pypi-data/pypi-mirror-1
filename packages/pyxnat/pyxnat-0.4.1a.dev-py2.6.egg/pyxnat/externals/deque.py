import collections

class Deque(collections.deque):
    def __init__(self, iterable, maxlen=None):
        self.__maxlen = maxlen

    def append(self, obj):
        if self.__maxlen != None and len(self) >= self.__maxlen:
            self.rotate(-1)
            self.pop()

        collections.deque.append(self, obj)

    def appendleft(self, obj):
        if self.__maxlen != None and len(self) >= self.__maxlen:
            self.rotate(1)
            self.popleft()

        collections.deque.appendleft(self, obj)
