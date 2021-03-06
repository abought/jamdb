from jam import Logger
from jam import Storage
from jam import Snapshot
from jam import Collection
from jam.backends import EphemeralBackend


class EphemeralSnapshot(Snapshot):
    def __init__(self):
        super().__init__(EphemeralBackend())


if __name__ == '__main__':
    logger = Logger(EphemeralBackend())
    storage = Storage(EphemeralBackend())
    snapshot = Snapshot(EphemeralBackend())

    collection = Collection(storage, logger, snapshot, regenerate=False)

    collection.create('key', 'value')
    collection.create('value', {'keee': 'eeeeee'})
    collection.rename('value', 'otherkey')

    clone = Collection(storage, logger, EphemeralSnapshot(), regenerate=True)

    assert clone.read('key') == collection.read('key')
    assert clone.read('otherkey') == collection.read('otherkey')

    hist = list(collection.history('value'))
