from typing import List


# todo this could be a single function
class Bootstrap:
    def __init__(self) -> None:
        self._python: str = ''

    def add_python(self, code: str) -> None:
        self._python = code

    def get_javascript(self) -> str:
        return _js_content.replace('# python replace marker', self._python)


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
