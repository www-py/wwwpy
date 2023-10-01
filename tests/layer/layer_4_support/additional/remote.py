def main():
    from js import document
    from addon_module import identity
    document.body.innerHTML = identity('additional')
