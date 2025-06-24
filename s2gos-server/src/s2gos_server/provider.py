#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.


from .service import Service


class ServiceProvider:
    _service: Service | None = None

    @classmethod
    def instance(cls) -> Service:
        assert isinstance(cls._service, Service)
        return cls._service

    @classmethod
    def set_instance(cls, service: Service):
        assert isinstance(service, Service)
        cls._service = service
