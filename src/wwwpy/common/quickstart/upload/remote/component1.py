import js
import logging

import wwwpy.remote.component as wpc

from remote.upload_component import UploadComponent

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    multiple_checkbox: js.HTMLInputElement = wpc.element()
    upload1: UploadComponent = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div style='padding: 0.5em; margin: 0.5em; '>
        <div>Component1 in component1.py</div>
<div>The following component is defined in file upload_component.py</div>
<div>The files are uploaded in the project root 'uploads' folder. To change this behaviour see file server/rpc.py</div>
<label style='display: block'>
    <input data-name="multiple_checkbox" placeholder="input1" type="checkbox">
 Multiple files upload</label>
 
<wwwpy-quickstart-upload data-name="upload1"></wwwpy-quickstart-upload>
<h2>You need to restart the server process because it does not support the server.rpc complete hot-reload yet</h2>  
 </div>               
        """
        self.multiple_checkbox.checked = self.upload1.multiple

    async def multiple_checkbox__input(self, event):
        js.console.log('handler multiple_checkbox__input event =', event)
        self.upload1.multiple = self.multiple_checkbox.checked

    
