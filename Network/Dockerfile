# Usar una imagen base ligera
FROM debian:bullseye-slim

# Instalar WireGuard, net-tools, y ping
RUN apt-get update && apt-get install -y \
    wireguard \
    net-tools \
    iproute2 \
    iputils-ping \
    procps \
    && apt-get clean

# Crear un directorio para configuraciones de WireGuard
RUN mkdir -p /etc/wireguard

# Establecer el entrypoint por defecto
CMD ["/bin/bash"]

# docker build -t virtual-interface-manager .
# docker run -it --rm --privileged virtual-interface-manager
# docker run -it --rm --cap-add=NET_ADMIN --cap-add=SYS_ADMIN virtual-interface-manager
