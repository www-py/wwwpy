from wwwpy.unasync import unasync


def test_unsync():
    @unasync
    async def fun():
        return 'ok'

    assert fun() == 'ok'


def test_unsync_with_args():
    @unasync
    async def fun(arg1):
        return arg1

    assert fun('foo') == 'foo'
