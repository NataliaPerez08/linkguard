# Allow forwarding traffic from wg0 interface
sudo iptables -A FORWARD -i wg0 -o wg0 -j ACCEPT

# Allow traffic from host A to host B and vice versa
sudo iptables -t nat -A POSTROUTING -s 172.16.0.2/32 -d 10.0.0.3/32 -o wg0 -j MASQUERADE
sudo iptables -t nat -A POSTROUTING -s 10.0.0.3/32 -d 10.0.0.2/32 -o wg0 -j MASQUERADE
