CREATE TABLE user (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL
);

CREATE TABLE vpn (
  id TEXT PRIMARY KEY,
  user_id TEXT NOT NULL,
  name TEXT NOT NULL,
  mask_network TEXT NOT NULL,
  ip_address TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user(id)
);

CREATE TABLE endpoint(
  id TEXT PRIMARY KEY,
  vpn_id TEXT NOT NULL,
  name TEXT NOT NULL,
  peer_ip TEXT NOT NULL,
  peer_port TEXT NOT NULL,
  private_ip TEXT NOT NULL,
  private_key TEXT NOT NULL,
  public_key TEXT NOT NULL,
  FOREIGN KEY (vpn_id) REFERENCES vpn(id)
);

CREATE TABLE user_simple (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);