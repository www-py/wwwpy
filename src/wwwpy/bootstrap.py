import textwrap


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
