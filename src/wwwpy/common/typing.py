try:
    from typing_extensions import Protocol
except:
    try:
        from typing import Protocol
    except:
        class Protocol:
            ...
