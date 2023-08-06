create table docs_new (doc_id integer primary key autoincrement, title text,
       doc_body text, pdate text, creator text, published integer);
insert into docs_new select *, 1 from docs;
drop table docs;
alter table docs_new rename to docs;

create table keywords_new (kw_id integer primary key autoincrement,
       keyword text unique);
insert into keywords_new select * from keywords;
drop table keywords;
alter table keywords_new rename to keywords;

create table q_hot_kws (keyword text unique, num integer);
insert into q_hot_kws select * from hot_kws;
drop view hot_kws;
alter table q_hot_kws rename to hot_kws;

CREATE INDEX index_hot_kws on hot_kws (num desc);

CREATE INDEX last_docs on docs (pdate desc);

CREATE TRIGGER update_docs update on docs when new.published != old.published
begin
update hot_kws set num = num + (new.published = 1) - (new.published = 0)
       where keyword in
                    (select keyword from keywords left join kws_docs
            on keywords.kw_id = kws_docs.kw_id
            where kws_docs.doc_id = new.doc_id);
end;

CREATE TRIGGER ins_keyword insert on keywords
begin
insert into hot_kws values(new.keyword, 0);
end;

CREATE TRIGGER del_keyword delete on keywords
begin
delete from keywords where keyword = old.keyword;
end;

CREATE TRIGGER delete_doc_keyword delete on kws_docs
begin
update hot_kws set num = num - 1
       where keyword =
                    (select keyword from keywords
            left join kws_docs on keywords.kw_id = kws_docs.kw_id
            left join docs on kws_docs.doc_id = docs.doc_id
            where kws_docs.kw_id = old.kw_id
                  and kws_docs.doc_id = old.doc_id
                  and docs.published = 1);
end;


CREATE TRIGGER delete_urls delete on kws_urls
begin
update hot_kws set num = num - 1
       where keyword = (select keyword from keywords where kw_id = old.kw_id);
end;

CREATE TRIGGER add_doc_keyword insert on kws_docs
begin
update hot_kws set num = num + 1
       where keyword =
                    (select keyword from keywords
            left join kws_docs on keywords.kw_id = kws_docs.kw_id
            left join docs on kws_docs.doc_id = docs.doc_id
            where kws_docs.kw_id = new.kw_id
                  and kws_docs.doc_id = new.doc_id
                  and docs.published = 1);
end;

CREATE TRIGGER update_urls insert on kws_urls
begin
update hot_kws set num = num + 1
       where keyword = (select keyword from keywords where kw_id = new.kw_id);
end;
