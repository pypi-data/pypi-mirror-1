-- drop all the tables, if they exist

BEGIN;

DROP TABLE replicas;
DROP TABLE servers;
DROP TABLE files;
DROP TABLE domains;

COMMIT;

-- create the tables

BEGIN;

CREATE TABLE domains (
    id serial,
    name varchar(255) NOT NULL,
    folder varchar(255) NOT NULL,
    url varchar(255) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (name)
);

CREATE TABLE files (
    id serial,
    domain_id integer NOT NULL,
    key varchar(255) NOT NULL,
    bytes integer NULL,
    checksum char(32) NULL,
    created_on timestamp without time zone NOT NULL DEFAULT now(),
    deleted_on timestamp without time zone NULL,
    status char(1) NOT NULL CHECK (status IN ('T', 'R', 'D')),
    class integer NOT NULL DEFAULT 2,
    replicas integer NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    FOREIGN KEY (domain_id) REFERENCES domains (id)
);

CREATE INDEX files_ndx_domain_key_status ON files (domain_id, key, status);
CREATE INDEX files_ndx_created_on ON files (created_on, id) WHERE status = 'R';
CREATE INDEX files_ndx_deleted_on ON files (deleted_on, id) WHERE status = 'D';

CREATE TABLE servers (
    id serial,
    name varchar(255) NOT NULL,
    host varchar(255) NOT NULL,
    status char(1) NOT NULL CHECK (status IN ('Y', 'N')),
    PRIMARY KEY (id),
    UNIQUE (name),
    UNIQUE (host)
);

CREATE INDEX servers_ndx_status ON servers (status, id);

CREATE TABLE servers_domains (
    id serial,
    server_id integer NOT NULL,
    domain_id integer NOT NULL,
    PRIMARY KEY (id),
    UNIQUE (server_id, domain_id),
    FOREIGN KEY (server_id) REFERENCES servers (id),
    FOREIGN KEY (domain_id) REFERENCES domains (id)
);

CREATE TABLE replicas (
    id serial,
    file_id integer NOT NULL,
    server_id integer NOT NULL,
    created_on timestamp without time zone NOT NULL DEFAULT now(),
    PRIMARY KEY (id),
    UNIQUE (server_id, file_id),
    FOREIGN KEY (file_id) REFERENCES files (id),
    FOREIGN KEY (server_id) REFERENCES servers (id)
);

CREATE INDEX replicas_ndx_file_id ON replicas (file_id);

CREATE OR REPLACE FUNCTION update_replicas() RETURNS TRIGGER AS $$
BEGIN
  IF (TG_OP = 'INSERT') THEN
    UPDATE files SET replicas = replicas + 1 WHERE id = NEW.file_id;
  ELSIF (TG_OP = 'DELETE') THEN
    UPDATE files SET replicas = replicas - 1 WHERE id = OLD.file_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_replicas_insert ON replicas;
CREATE TRIGGER update_replicas_insert AFTER INSERT ON replicas
  FOR EACH ROW EXECUTE PROCEDURE update_replicas();

DROP TRIGGER IF EXISTS update_replicas_delete ON replicas;
CREATE TRIGGER update_replicas_delete AFTER DELETE ON replicas
  FOR EACH ROW EXECUTE PROCEDURE update_replicas();

COMMIT;
