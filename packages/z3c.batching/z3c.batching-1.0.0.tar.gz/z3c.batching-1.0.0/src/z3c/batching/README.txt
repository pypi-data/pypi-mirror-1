===============
Simple Batching
===============

This module implements a simple batching mechanism that allows you to split a
large sequence into smaller batches. Let's start by creating a simple list,
which will be our full sequence:

Batch on empty root

  >>> from z3c.batching.batch import Batch
  >>> batch = Batch([], size=3)
  >>> len(batch)
  0
  >>> batch.firstElement
  Traceback (most recent call last):
  ...
  IndexError: ...

  >>> batch.lastElement
  Traceback (most recent call last):
  ...
  IndexError: ...

  >>> batch[0]
  Traceback (most recent call last):
  ...
  IndexError: ...

  >>> batch.next is None
  True

  >>> batch.previous is None
  True


  >>> sequence = ['one', 'two', 'three', 'four', 'five', 'six', 'seven',
  ...             'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen']

We can now create a batch for this sequence. Let's make our batch size 3:

  >>> batch = Batch(sequence, size=3)

The first argument to the batch is always the full sequence. If no start
element is specified, the batch starts at the first element:

  >>> list(batch)
  ['one', 'two', 'three']

The start index is commonly specified in the constructor though:

  >>> batch = Batch(sequence, start=6, size=3)
  >>> list(batch)
  ['seven', 'eight', 'nine']

Note that the start is an index and starts at zero. If the start index is
greater than the largest index of the sequence, an index error is raised:

  >>> Batch(sequence, start=15, size=3)
  Traceback (most recent call last):
  ...
  IndexError: start index key out of range

A batch implements the finite sequence interface and thus supports some
standard methods. For example, you can ask the batch for its length:

  >>> len(batch)
  3

Note that the length returns the true size of the batch, not the size we asked
for:

  >>> len(Batch(sequence, start=12, size=3))
  1

You can also get an element by index, which is relative to the batch:

  >>> batch[0]
  'seven'
  >>> batch[1]
  'eight'
  >>> batch[2]
  'nine'

Slicing 

  >>> batch[:1]
  ['seven']

  >>> batch[1:2]
  ['eight']

  >>> batch[1:]	
  ['eight', 'nine']

  >>> batch[:]
  ['seven', 'eight', 'nine']

  >>> batch[10:]
  []
  

If you ask for inex that is out of range, an index error is raised:

  >>> batch[3]
  Traceback (most recent call last):
  ...
  IndexError: batch index out of range

You can also iterate through the batch:

  >>> iterator = iter(batch)
  >>> iterator.next()
  'seven'
  >>> iterator.next()
  'eight'
  >>> iterator.next()
  'nine'

Batch also implement some of IReadSequence interface

  >>> 'eight' in batch
  True

  >>> 'ten' in batch
  False

  >>> batch == Batch(sequence, start=6, size=3)
  True

  >>> batch != Batch(sequence, start=6, size=3)
  False

  >>> batch != Batch(sequence, start=3, size=3)
  True

Besides all of those common API methods, there are several properties that were
designed to make your life simpler. The start and size are specified:

  >>> batch.start
  6
  >>> batch.size
  3

The end index of the batch is immediately computed:

  >>> batch.end
  8

The UI often requires that the number of the btach and the total number of
batches is computed:

  >>> batch.number
  3
  >>> batch.total
  5

You can also ask for the next batch:

  >>> batch.next
  <Batch start=9, size=3>

If the current batch is the last one, the next batch is None:

  >>> Batch(sequence, start=12, size=3).next is None
  True

The previous batch shows the previous batch:

  >>> batch.previous
  <Batch start=3, size=3>

If the current batch is the first one, the previous batch is None:

  >>> Batch(sequence, start=0, size=3).previous is None
  True

The final two properties deal with the elements within the batch. They ask for
the first and last element of the batch:

  >>> batch.firstElement
  'seven'

  >>> batch.lastElement
  'nine'


Total batches

  >>> batch = Batch(sequence[:-1], size=3)
  >>> batch.total
  4

We can get access to all batches

  >>> len(batch.batches)
  4

  >>> batch.batches[0]
  <Batch start=0, size=3>

  >>> batch.batches[3]
  <Batch start=9, size=3>

  >>> batch.batches[4]
  Traceback (most recent call last):
  ...
  IndexError: ...

  >>> batch.batches[-1]
  <Batch start=9, size=3>

  >>> batch.batches[-2]
  <Batch start=6, size=3>

Slicing

  >>> batch.batches[:1]
  [<Batch start=0, size=3>]
	
  >>> batch.batches[:]
  [<Batch start=0, size=3>, <Batch start=3, size=3>, <Batch start=6, size=3>]
	
  >>> batch.batches[1:2]
  [<Batch start=3, size=3>]
	
  >>> batch.batches[1:]
  [<Batch start=3, size=3>, <Batch start=6, size=3>]

  >>> batch.batches[10:]
  []
