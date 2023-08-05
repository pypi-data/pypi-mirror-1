CREATE TABLE log(
id INTEGER PRIMARY KEY,
date DEFAULT CURRENT_TIMESTAMP,
md5sum TEXT);

CREATE TABLE data (
id INTEGER PRIMARY KEY,
log_id INTEGER NOT NULL CONSTRAINT fk_log_id REFERENCES log(id) ON DELETE CASCADE, --[data] 
node TEXT,
username TEXT,
cpu  FLOAT,
mem FLOAT);

create table last_inserted_master (master_id integer);
insert into last_inserted_master values(NULL);

create trigger master_id after insert on log
	begin
		update last_inserted_master set master_id = last_insert_rowid();
	end;


