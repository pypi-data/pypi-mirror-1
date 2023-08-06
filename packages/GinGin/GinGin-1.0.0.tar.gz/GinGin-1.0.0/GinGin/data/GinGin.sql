create table docs (doc_id integer primary key autoincrement, title text,
	doc_body text, pdate text, creator text, published integer);

create table urls (url_id integer primary key, title text,
	url text unique, abstract text, pdate text, creator text);

create table keywords (kw_id integer primary key autoincrement,
        keyword text unique);

create table kws_docs (kw_id integer, doc_id integer);

create table kws_urls (kw_id integer, url_id integer);

create table kws_rels (parent integer, child integer);

create table afiles (af_id integer primary key, doc_id integer,
	afkey text, afname text, mtype text);

create table trackbacks (doc_id integer, title text, excerpt text,
	url text, blog_name text, rhost text, pdate text);

create table referers (ref_id integer primary key, doc_id integer,
	src_url text, unique(doc_id, src_url));

create table antispam (
        doc_id integer primary key,
	key text,
	plain text,
	cipher text);

create table comments (
	cmt_id integer primary key,
	doc_id integer,
	name text,
	email text,
	website text,
	msg text,
	pdate text);

CREATE TABLE hot_kws (
       keyword text unique,
       num integer);

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

insert into docs values(1, 'GinGin', '==GinGin==',
	'2005-01-01 00:00:00 CST', 'nobody', 1);
