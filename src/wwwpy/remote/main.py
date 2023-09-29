from inspect import iscoroutinefunction


async def entry_point():
    from wwwpy.common.tree import print_tree
    print_tree('/wwwpy_bundle')
    import js
    try:
        js.document.body.innerHTML = 'Going to import remote'
        import remote
        if hasattr(remote, 'main'):
            if iscoroutinefunction(remote.main):
                await remote.main()
            else:
                remote.main()
    except ImportError as e:
        import traceback
        msg = 'module remote load failed. Error: ' + str(e) + '\n\n' + traceback.format_exc() + '\n\n'
        js.document.body.innerHTML = msg.replace('\n', '<br>')
