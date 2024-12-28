# Usar una imagen base ligera
FROM debian:bullseye-slim

# Instalar WireGuard, net-tools, y ping
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wireguard-tools \
        iproute2 \
        net-tools \
        iputils-ping && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Crear un directorio para configuraciones de WireGuard
RUN mkdir -p /etc/wireguard

# Establecer el entrypoint por defecto
CMD ["/bin/bash"]

# docker build -t virtual-interface-manager .
# docker run -it --rm --privileged virtual-interface-manager
# docker run -it --rm --cap-add=NET_ADMIN --cap-add=SYS_ADMIN virtual-interface-manager
