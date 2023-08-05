create table docs (doc_id integer primary key, title text,
	doc_body text, pdate text, creator text);
create table urls (url_id integer primary key, title text,
	url text unique, abstract text, pdate text, creator text);
create table keywords (kw_id integer primary key, keyword text unique);
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
create view hot_kws as
       select keyword, count(*) num from (
       	 select a.keyword keyword from keywords a join kws_docs b on a.kw_id = b.kw_id
	 union all
	 select a.keyword keyword from keywords a join kws_urls b on a.kw_id = b.kw_id
       ) group by keyword;
insert into docs values(1, 'GinGin', '==GinGin==',
	'2005-01-01 00:00:00 CST', 'nobody');
