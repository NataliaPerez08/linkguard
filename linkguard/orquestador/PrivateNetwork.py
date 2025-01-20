import ipaddress
from endpoint import Endpoint
from linkguard.orquestador.db import get_db

class PrivateNetwork:
    def __init__(self, id_red, user_id, name, ip_addr, mask_network):
        self.id = id_red
        self.user_id = user_id
        self.name = name
        self.mask_network = mask_network
        self.ip_addr = ipaddress.IPv4Network(f"{ip_addr}/{mask_network}")
        self.available_hosts = self.calcule_network_range()
    
    @staticmethod
    def get(private_network_id):
        db = get_db()
        private_network = db.execute(
            "SELECT * FROM vpn WHERE id = ?", (private_network_id,)
        ).fetchone()
        if not private_network:
            return None

        private_network = PrivateNetwork(
            id_red=private_network[0], user_id=private_network[1], name=private_network[2], ip_addr=private_network[3], mask_network=private_network[4]
        )
        return private_network
    
    @staticmethod
    def create_by_name(user_id, name):
        db = get_db()
        db.execute(
            "INSERT INTO vpn (user_id, name) VALUES (?, ?)", (user_id, name)
        )
        db.commit()
        private_network_id = db.execute(
            "SELECT id FROM vpn WHERE user_id = ? AND name = ?", (user_id, name)
        ).fetchone()[0]
        return PrivateNetwork.get(private_network_id)