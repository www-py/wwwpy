import js
import wwwpy.remote.component as wpc
from wwwpy.remote import dict_to_js

from .rpc_issue import RpcIssueAlert


class Component1(wpc.Component, tag_name='component-1'):
    slButton1: js.HTMLElement = wpc.element()
    slInput1: js.HTMLElement = wpc.element()
    slIconButton1: js.HTMLElement = wpc.element()
    slTextarea1: js.HTMLElement = wpc.element()
    form1: js.HTMLElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """<span>component-1</span>
<form data-name="form1">
    <sl-input data-name="slInput1" placeholder="Message" title="" required></sl-input>
    <sl-button data-name="slButton1" type="submit">Send</sl-button>
    <sl-textarea data-name="slTextarea1" placeholder="slTextarea1" rows="10">Messages...</sl-textarea>
</form>
"""
        self.element.insertBefore(RpcIssueAlert().element, self.element.firstChild)

        def new_message(message):
            self.slTextarea1.value += message + '\n'
            self.slTextarea1.scrollPosition(dict_to_js({'top': self.slTextarea1.scrollHeight}))

        import remote.rpc
        remote.rpc.messages_listeners.append(new_message)

    async def slButton1__click(self, event):
        js.console.log('handler slButton1__click event =', event)
        import server.rpc
        try:
            await server.rpc.send_message_to_all(self.slInput1.value)
            self.slInput1.value = ''
            self.slInput1.setCustomValidity('')
        except Exception as e:
            self.slInput1.setCustomValidity('Issues sending message... ' + str(e))
            self.slInput1.reportValidity()

    def form1__submit(self, event):
        event.preventDefault()
