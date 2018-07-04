DROP SEQUENCE IF EXISTS each_seq;
CREATE SEQUENCE each_seq start with 1 increment by 1;

DROP TYPE IF EXISTS each_prop_type CASCADE;
CREATE TYPE each_prop_type AS ENUM ('bool', 'int', 'real', 'media', 'comment', 'like', 'location', 'post');

DROP TYPE IF EXISTS each_media_type CASCADE;
CREATE TYPE each_media_type AS ENUM ('image', 'equipment');

DROP TYPE IF EXISTS each_user_admin_type CASCADE;
CREATE TYPE each_user_admin_type AS ENUM ('admin', 'super');

DROP TABLE IF EXISTS "each_court";
CREATE TABLE "each_court" (
	"eachid" BIGSERIAL NOT NULL PRIMARY KEY ,
	"ownerid" BIGSERIAL NOT NULL,
	"name" VARCHAR(256) NOT NULL UNIQUE,
	"desc" VARCHAR(4000) NOT NULL DEFAULT '',
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	"updated" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "each_user";
CREATE TABLE "each_user" (
	"eachid" BIGSERIAL NOT NULL PRIMARY KEY,
	"name" VARCHAR(256) NOT NULL UNIQUE,
	"e_mail" VARCHAR(256) NOT NULL UNIQUE,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	"updated" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "each_media";
CREATE TABLE "each_media" (
	"eachid" BIGSERIAL NOT NULL PRIMARY KEY,
	"ownerid" BIGINT NOT NULL,
	"name" VARCHAR(256) NOT NULL DEFAULT '',
	"desc" VARCHAR(4000) NOT NULL DEFAULT '',
	"type" each_media_type NOT NULL,
	"url" VARCHAR(4000) NOT NULL UNIQUE,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "each_follow";
CREATE TABLE "each_follow" (
	"eachid" BIGINT NOT NULL,
	"followingid" BIGINT NOT NULL,
	"permit" INT NOT NULL DEFAULT 1,
	"is_user" BOOLEAN NOT NULL,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (eachid, followingid)
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "each_location";
CREATE TABLE "each_location" (
	"eachid" BIGSERIAL NOT NULL PRIMARY KEY,
	"name" VARCHAR(256) NOT NULL UNIQUE,
	"latitude" REAL NOT NULL,
	"longitude" REAL NOT NULL
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "each_prop";
CREATE TABLE "each_prop" (
	"eachid" BIGSERIAL NOT NULL PRIMARY KEY,
	"name" VARCHAR(40) NOT NULL UNIQUE,
	"type" each_prop_type NOT NULL
) WITH (
  OIDS=FALSE
);

INSERT INTO each_prop (eachid, name, type) VALUES (NEXTVAL('each_seq'), 'private', 'bool');
INSERT INTO each_prop (eachid, name, type) VALUES (NEXTVAL('each_seq'), 'isopen', 'bool');
INSERT INTO each_prop (eachid, name, type) VALUES (NEXTVAL('each_seq'), 'isfree', 'bool');
INSERT INTO each_prop (eachid, name, type) VALUES (NEXTVAL('each_seq'), 'isonair', 'bool');
INSERT INTO each_prop (eachid, name, type) VALUES (NEXTVAL('each_seq'), 'price', 'real');
INSERT INTO each_prop (eachid, name, type) VALUES (NEXTVAL('each_seq'), 'media', 'media');
INSERT INTO each_prop (eachid, name, type) VALUES (NEXTVAL('each_seq'), 'equipment', 'media');
INSERT INTO each_prop (eachid, name, type) VALUES (NEXTVAL('each_seq'), 'avatar', 'media');
INSERT INTO each_prop (eachid, name, type) VALUES (NEXTVAL('each_seq'), 'comment', 'comment');
INSERT INTO each_prop (eachid, name, type) VALUES (NEXTVAL('each_seq'), 'like', 'like');
INSERT INTO each_prop (eachid, name, type) VALUES (NEXTVAL('each_seq'), 'location', 'location');
INSERT INTO each_prop (eachid, name, type) VALUES (NEXTVAL('each_seq'), 'post', 'post');

DROP TABLE IF EXISTS "each_prop_bool";
CREATE TABLE "each_prop_bool" (
	"eachid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" BOOLEAN NOT NULL,
	PRIMARY KEY (eachid, propid, value)
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "each_prop_int";
CREATE TABLE "each_prop_int" (
    "eachid" BIGSERIAL NOT NULL,
	"propid" BIGSERIAL NOT NULL,
	"value" INT NOT NULL,
	PRIMARY KEY (eachid, propid, value)
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "each_prop_real";
CREATE TABLE "each_prop_real" (
    "eachid" BIGSERIAL NOT NULL,
	"propid" BIGSERIAL NOT NULL,
	"value" REAL NOT NULL,
	PRIMARY KEY (eachid, propid, value)
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "each_prop_media";
CREATE TABLE "each_prop_media" (
	"eachid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" BIGINT NOT NULL,
	PRIMARY KEY (eachid, propid, value)
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "each_prop_comment";
CREATE TABLE "each_prop_comment" (
	"eachid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL,
	PRIMARY KEY (eachid, propid, value)
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "each_prop_like";
CREATE TABLE "each_prop_like" (
	"eachid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL,
	PRIMARY KEY (eachid, propid, value)
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "each_prop_location";
CREATE TABLE "each_prop_location" (
	"eachid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" BIGINT NOT NULL,
	PRIMARY KEY (eachid, propid, value)
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "each_prop_post";
CREATE TABLE "each_prop_post" (
	"eachid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" BIGINT NOT NULL,
	PRIMARY KEY (eachid, propid, value)
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "each_post";
CREATE TABLE "each_post" (
	"eachid" BIGSERIAL NOT NULL PRIMARY KEY,
	"userid" BIGINT NOT NULL,
	"description" VARCHAR(256) NOT NULL,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	"updated" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "each_comment";
CREATE TABLE "each_comment" (
	"eachid" BIGSERIAL NOT NULL PRIMARY KEY ,
	"userid" BIGINT NOT NULL,
	"text" TEXT NOT NULL,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	"updated" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "each_like";
CREATE TABLE "each_like" (
	"eachid" BIGSERIAL NOT NULL PRIMARY KEY ,
	"userid" BIGINT NOT NULL,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	"weight" BIGINT NOT NULL
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "each_user_admin";
CREATE TABLE "each_user_admin" (
	"eachid" BIGSERIAL NOT NULL PRIMARY KEY,
	"userid" BIGINT NOT NULL,
	"level" each_user_admin_type NOT NULL
) WITH (
	OIDS=FALSE
);

commit;
