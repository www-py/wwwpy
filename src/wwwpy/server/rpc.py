from wwwpy.rpc import Services, Module


def configure_services(route_path: str) -> Services:
    services = Services(route_path)
    try:
        import server.rpc
        services.add_module(Module(server.rpc))
    except Exception as e:
        print(f'could not load rpc module: {e}')
    return services
