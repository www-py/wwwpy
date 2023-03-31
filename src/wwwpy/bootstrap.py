import textwrap
from typing import List, Iterable, Tuple

from wwwpy.http import HttpRoute, HttpResponse
from wwwpy.resources import Resource, build_archive

bootstrap_javascript_placeholder = '// #bootstrap-placeholder#'


def bootstrap_routes(
        iterable_resource: Iterable[Resource],
        html: str = f'<h1>Loading...</h1><script>{bootstrap_javascript_placeholder}</script>',
) -> Tuple[HttpRoute, HttpRoute]:
    def zip_response() -> HttpResponse:
        zip_bytes = build_archive(iter(iterable_resource))
        return HttpResponse.application_zip(zip_bytes)

    zip_path = '/wwwpy/bundle.zip'
    zip_route = HttpRoute(zip_path, lambda request: zip_response())

    bootstrap_python = f"""
import sys
from pyodide.http import pyfetch
response = await pyfetch('{zip_route.path}')
await response.unpack_archive(extract_dir='/wwwpy_bundle')
sys.path.insert(0, '/wwwpy_bundle')
import remote
# if remote.main is not None:
#    await remote.main()
    """

    javascript = get_javascript_for(bootstrap_python)
    html_replaced = html.replace(bootstrap_javascript_placeholder, javascript)
    bootstrap_route = HttpRoute('/', lambda request: HttpResponse.text_html(html_replaced))
    return bootstrap_route, zip_route


def get_javascript_for(python_code: str) -> str:
    return _js_content.replace('# python replace marker', python_code)


# language=javascript
_js_content = """
if (typeof loadPyodide === 'undefined') {
    let script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/pyodide/v0.22.1/full/pyodide.js';
    script.onload = async () => {
        let pyodide = await loadPyodide();
        window.pyodide = pyodide;
        console.log('loading pyodide.runPythonAsync(...). See in the following lines for the code');
        console.log('-----------------------  START PYTHON CODE  -------------------------------');
        console.log(`# python replace marker`);
        console.log('-----------------------  END PYTHON CODE    -------------------------------');
        pyodide.runPythonAsync(`# python replace marker`);
    };
    document.body.append(script)
}
"""


def wrap_in_tryexcept(code: str, exception_block: str) -> str:
    """It will wrap the code in try/except and catch `Exception as exception`"""
    result = 'try:\n' + textwrap.indent(code, ' ' * 4) + '\n' + \
             'except Exception as exception:\n' + textwrap.indent(exception_block, ' ' * 4)
    return result
