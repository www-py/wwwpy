from tests.common.rpc.test_rpc import support2_module_name
from wwwpy.common.rpc.func_registry import from_package_name
from wwwpy.common.rpc.invoker import Invoker
from wwwpy.unasync import unasync


@unasync
async def test_module_invoke_async():
    module = from_package_name(support2_module_name)
    target = Invoker(module)

    # THEN
    actual = await target['support2_concat'].func('hello', ' world')
    assert actual == 'hello world'
