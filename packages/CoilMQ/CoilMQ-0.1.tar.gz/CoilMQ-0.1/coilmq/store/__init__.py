"""
Storage containers for durable queues and (planned) durable topics.
"""
__authors__ = ['"Hans Lellelid" <hans@xmpl.org>']
__copyright__ = "Copyright 2009 Hans Lellelid"
__license__ = """Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
 
  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License."""

from coilmq.util.concurrency import synchronized

class QueueStore(object):
    """
    Abstract base class for queue storage. 
    
    Extensions/implementations of this class must be thread-safe.
    """
    
    @synchronized
    def enqueue(self, destination, frame):
        raise NotImplementedError()
    
    @synchronized
    def dequeue(self, destination):
        raise NotImplementedError()
    
    @synchronized
    def requeue(self, destination, frame):
        self.enqueue(destination, frame)

    @synchronized
    def size(self, destination):
        """
        Size of the queue for specified destination.
        
        @param destination: The queue destination (e.g. /queue/foo)
        @type destination: C{str}
        """
        raise NotImplementedError()

    @synchronized
    def has_frames(self, destination):
        raise NotImplementedError()
    
    def frames(self, destination):
        """
        Returns an iterator for frames in specified destination.
        
        @param destination: The queue destination (e.g. /queue/foo)
        @type destination: C{str}
        """
        return QueueFrameIterator(self, destination)
    
    def __getitem__(self, key):
        return self.frames(key)
    
class QueueFrameIterator(object):
    """
    Provides an C{iterable} over the frames for a specified destination in a queue.
    
    @ivar store: The queue store.
    @type store: L{coilmq.store.QueueStore}
    
    @ivar destination: The destination for this iterator.
    @type destination: C{str}
    """
    def __init__(self, store, destination):
        self.store = store
        self.destination = destination
        
    def __iter__(self):
        return self
    
    def next(self):
        frame = self.store.dequeue(self.destination)
        if not frame:
            raise StopIteration()
        return frame
    
    def __len__(self):
        return self.store.size(self.destination)
    
    def __nonzero__(self):
        return self.store.has_frame(self.destination)
    
class TopicStore(object):
    """
    Abstract base class for non-durable topic storage.
    """
    
class DurableTopicStore(TopicStore):
    """
    Abstract base class for durable topic storage.
    """