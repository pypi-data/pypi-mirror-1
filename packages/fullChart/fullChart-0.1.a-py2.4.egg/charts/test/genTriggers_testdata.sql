--drop table foo;
--drop table bar;
create table foo (
id INTEGER NOT NULL PRIMARY KEY
);

CREATE TABLE bar (
id INTEGER NOT NULL PRIMARY KEY,
foo_id INTEGER NOT NULL CONSTRAINT fk_foo_id REFERENCES foo(id) ON DELETE CASCADE --[bar]
);
