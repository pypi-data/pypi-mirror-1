from batcher import Batcher


def test_negative_index_returns_batch_from_end():

    items = list('ABCDE')
    batcher = Batcher(items, 2)

    assert list(batcher[-1]) == list('E')
    assert list(batcher[-2]) == list('CD')
    assert list(batcher[-3]) == list('AB')


def test_last_batch_of_padded_batches_is_correct_length():

    for items in [
        list('A'),
        list('AB'),
        list('ABC'),
        list('ABCD'),
        list('ABCDE'),
    ]:
        batcher = Batcher(items, 4, pad=True)

        assert len(list(batcher[-1])) == len(list(batcher[0])) == 4
