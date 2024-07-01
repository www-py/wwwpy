from js import document
import pytest

def test_first():
    document.body.innerHTML = '<input id="tag1" value="foo1">'
    assert document.getElementById('tag1').value == 'foo1'

@pytest.mark.asyncio
async def test_second():
    pass