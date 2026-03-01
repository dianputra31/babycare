/*
 Navicat Premium Data Transfer

 Source Server         : localhost_5432
 Source Server Type    : PostgreSQL
 Source Server Version : 130022
 Source Host           : localhost:5432
 Source Catalog        : babycare_db
 Source Schema         : babycare

 Target Server Type    : PostgreSQL
 Target Server Version : 130022
 File Encoding         : 65001

 Date: 16/02/2026 20:16:58
*/


-- ----------------------------
-- Sequence structure for cabang_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "babycare"."cabang_id_seq";
CREATE SEQUENCE "babycare"."cabang_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for jenis_terapi_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "babycare"."jenis_terapi_id_seq";
CREATE SEQUENCE "babycare"."jenis_terapi_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for notifikasi_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "babycare"."notifikasi_id_seq";
CREATE SEQUENCE "babycare"."notifikasi_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for pasien_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "babycare"."pasien_id_seq";
CREATE SEQUENCE "babycare"."pasien_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for pemasukan_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "babycare"."pemasukan_id_seq";
CREATE SEQUENCE "babycare"."pemasukan_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for pengeluaran_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "babycare"."pengeluaran_id_seq";
CREATE SEQUENCE "babycare"."pengeluaran_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for permissions_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "babycare"."permissions_id_seq";
CREATE SEQUENCE "babycare"."permissions_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for registrasi_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "babycare"."registrasi_id_seq";
CREATE SEQUENCE "babycare"."registrasi_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for roles_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "babycare"."roles_id_seq";
CREATE SEQUENCE "babycare"."roles_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 2147483647
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for terapis_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "babycare"."terapis_id_seq";
CREATE SEQUENCE "babycare"."terapis_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for transport_terapis_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "babycare"."transport_terapis_id_seq";
CREATE SEQUENCE "babycare"."transport_terapis_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Sequence structure for users_id_seq
-- ----------------------------
DROP SEQUENCE IF EXISTS "babycare"."users_id_seq";
CREATE SEQUENCE "babycare"."users_id_seq" 
INCREMENT 1
MINVALUE  1
MAXVALUE 9223372036854775807
START 1
CACHE 1;

-- ----------------------------
-- Table structure for cabang
-- ----------------------------
DROP TABLE IF EXISTS "babycare"."cabang";
CREATE TABLE "babycare"."cabang" (
  "id" int4 NOT NULL DEFAULT nextval('"babycare".cabang_id_seq'::regclass),
  "nama_cabang" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "alamat" text COLLATE "pg_catalog"."default",
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;

-- ----------------------------
-- Records of cabang
-- ----------------------------

-- ----------------------------
-- Table structure for jenis_terapi
-- ----------------------------
DROP TABLE IF EXISTS "babycare"."jenis_terapi";
CREATE TABLE "babycare"."jenis_terapi" (
  "id" int8 NOT NULL DEFAULT nextval('"babycare".jenis_terapi_id_seq'::regclass),
  "nama_terapi" varchar(200) COLLATE "pg_catalog"."default" NOT NULL,
  "harga" numeric(12,2) NOT NULL,
  "kategori_usia_min" numeric(4,1),
  "kategori_usia_max" numeric(4,1),
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "is_deleted" bool DEFAULT false
)
;

-- ----------------------------
-- Records of jenis_terapi
-- ----------------------------

-- ----------------------------
-- Table structure for notifikasi
-- ----------------------------
DROP TABLE IF EXISTS "babycare"."notifikasi";
CREATE TABLE "babycare"."notifikasi" (
  "id" int8 NOT NULL DEFAULT nextval('"babycare".notifikasi_id_seq'::regclass),
  "pasien_id" int8,
  "registrasi_id" int8,
  "jenis_notifikasi" varchar(50) COLLATE "pg_catalog"."default",
  "pesan" text COLLATE "pg_catalog"."default",
  "tanggal_notifikasi" date,
  "sudah_dibaca" bool DEFAULT false,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;

-- ----------------------------
-- Records of notifikasi
-- ----------------------------

-- ----------------------------
-- Table structure for pasien
-- ----------------------------
DROP TABLE IF EXISTS "babycare"."pasien";
CREATE TABLE "babycare"."pasien" (
  "id" int8 NOT NULL DEFAULT nextval('"babycare".pasien_id_seq'::regclass),
  "kode_pasien" varchar(20) COLLATE "pg_catalog"."default",
  "nama_anak" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "tanggal_lahir" date NOT NULL,
  "jenis_kelamin" char(1) COLLATE "pg_catalog"."default",
  "nama_orang_tua" varchar(150) COLLATE "pg_catalog"."default",
  "alamat" text COLLATE "pg_catalog"."default",
  "no_wa" varchar(20) COLLATE "pg_catalog"."default",
  "cabang_id" int4,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "is_deleted" bool DEFAULT false
)
;

-- ----------------------------
-- Records of pasien
-- ----------------------------

-- ----------------------------
-- Table structure for pemasukan
-- ----------------------------
DROP TABLE IF EXISTS "babycare"."pemasukan";
CREATE TABLE "babycare"."pemasukan" (
  "id" int8 NOT NULL DEFAULT nextval('"babycare".pemasukan_id_seq'::regclass),
  "registrasi_id" int8,
  "cabang_id" int4,
  "tanggal" date DEFAULT CURRENT_DATE,
  "jumlah" numeric(12,2) NOT NULL,
  "metode_pembayaran" varchar(50) COLLATE "pg_catalog"."default",
  "keterangan" text COLLATE "pg_catalog"."default",
  "created_by" int8,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;

-- ----------------------------
-- Records of pemasukan
-- ----------------------------

-- ----------------------------
-- Table structure for pengeluaran
-- ----------------------------
DROP TABLE IF EXISTS "babycare"."pengeluaran";
CREATE TABLE "babycare"."pengeluaran" (
  "id" int8 NOT NULL DEFAULT nextval('"babycare".pengeluaran_id_seq'::regclass),
  "cabang_id" int4,
  "tanggal" date DEFAULT CURRENT_DATE,
  "kategori" varchar(100) COLLATE "pg_catalog"."default",
  "jumlah" numeric(12,2) NOT NULL,
  "keterangan" text COLLATE "pg_catalog"."default",
  "created_by" int8,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;

-- ----------------------------
-- Records of pengeluaran
-- ----------------------------

-- ----------------------------
-- Table structure for permissions
-- ----------------------------
DROP TABLE IF EXISTS "babycare"."permissions";
CREATE TABLE "babycare"."permissions" (
  "id" int4 NOT NULL DEFAULT nextval('"babycare".permissions_id_seq'::regclass),
  "module" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "action" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "code" varchar(150) COLLATE "pg_catalog"."default" NOT NULL
)
;

-- ----------------------------
-- Records of permissions
-- ----------------------------

-- ----------------------------
-- Table structure for registrasi
-- ----------------------------
DROP TABLE IF EXISTS "babycare"."registrasi";
CREATE TABLE "babycare"."registrasi" (
  "id" int8 NOT NULL DEFAULT nextval('"babycare".registrasi_id_seq'::regclass),
  "kode_registrasi" varchar(20) COLLATE "pg_catalog"."default",
  "pasien_id" int8 NOT NULL,
  "jenis_terapi_id" int8 NOT NULL,
  "terapis_id" int8,
  "cabang_id" int4,
  "tanggal_kunjungan" date NOT NULL,
  "status" varchar(20) COLLATE "pg_catalog"."default" DEFAULT 'BOOKED'::character varying,
  "harga" numeric(12,2) NOT NULL,
  "biaya_transport" numeric(12,2) DEFAULT 0,
  "total_bayar" numeric(12,2),
  "catatan" text COLLATE "pg_catalog"."default",
  "created_by" int8,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "is_deleted" bool DEFAULT false
)
;

-- ----------------------------
-- Records of registrasi
-- ----------------------------

-- ----------------------------
-- Table structure for role_permissions
-- ----------------------------
DROP TABLE IF EXISTS "babycare"."role_permissions";
CREATE TABLE "babycare"."role_permissions" (
  "role_id" int4 NOT NULL,
  "permission_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of role_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for roles
-- ----------------------------
DROP TABLE IF EXISTS "babycare"."roles";
CREATE TABLE "babycare"."roles" (
  "id" int4 NOT NULL DEFAULT nextval('"babycare".roles_id_seq'::regclass),
  "nama_role" varchar(50) COLLATE "pg_catalog"."default" NOT NULL,
  "deskripsi" text COLLATE "pg_catalog"."default"
)
;

-- ----------------------------
-- Records of roles
-- ----------------------------

-- ----------------------------
-- Table structure for terapis
-- ----------------------------
DROP TABLE IF EXISTS "babycare"."terapis";
CREATE TABLE "babycare"."terapis" (
  "id" int8 NOT NULL DEFAULT nextval('"babycare".terapis_id_seq'::regclass),
  "nama_terapis" varchar(150) COLLATE "pg_catalog"."default" NOT NULL,
  "no_hp" varchar(20) COLLATE "pg_catalog"."default",
  "alamat" text COLLATE "pg_catalog"."default",
  "cabang_id" int4,
  "biaya_transport_default" numeric(12,2) DEFAULT 0,
  "is_active" bool DEFAULT true,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "updated_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP,
  "is_deleted" bool DEFAULT false
)
;

-- ----------------------------
-- Records of terapis
-- ----------------------------

-- ----------------------------
-- Table structure for transport_terapis
-- ----------------------------
DROP TABLE IF EXISTS "babycare"."transport_terapis";
CREATE TABLE "babycare"."transport_terapis" (
  "id" int8 NOT NULL DEFAULT nextval('"babycare".transport_terapis_id_seq'::regclass),
  "registrasi_id" int8 NOT NULL,
  "terapis_id" int8 NOT NULL,
  "jumlah_transport" numeric(12,2) NOT NULL,
  "tanggal" date DEFAULT CURRENT_DATE
)
;

-- ----------------------------
-- Records of transport_terapis
-- ----------------------------

-- ----------------------------
-- Table structure for user_roles
-- ----------------------------
DROP TABLE IF EXISTS "babycare"."user_roles";
CREATE TABLE "babycare"."user_roles" (
  "user_id" int8 NOT NULL,
  "role_id" int4 NOT NULL
)
;

-- ----------------------------
-- Records of user_roles
-- ----------------------------

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS "babycare"."users";
CREATE TABLE "babycare"."users" (
  "id" int8 NOT NULL DEFAULT nextval('"babycare".users_id_seq'::regclass),
  "username" varchar(100) COLLATE "pg_catalog"."default" NOT NULL,
  "password_hash" text COLLATE "pg_catalog"."default" NOT NULL,
  "full_name" varchar(150) COLLATE "pg_catalog"."default",
  "email" varchar(150) COLLATE "pg_catalog"."default",
  "cabang_id" int4,
  "is_active" bool DEFAULT true,
  "created_at" timestamp(6) DEFAULT CURRENT_TIMESTAMP
)
;

-- ----------------------------
-- Records of users
-- ----------------------------

-- ----------------------------
-- View structure for v_total_pendapatan
-- ----------------------------
DROP VIEW IF EXISTS "babycare"."v_total_pendapatan";
CREATE VIEW "babycare"."v_total_pendapatan" AS  SELECT pemasukan.cabang_id,
    sum(pemasukan.jumlah) AS total_pendapatan
   FROM babycare.pemasukan
  GROUP BY pemasukan.cabang_id;

-- ----------------------------
-- View structure for v_total_pengeluaran
-- ----------------------------
DROP VIEW IF EXISTS "babycare"."v_total_pengeluaran";
CREATE VIEW "babycare"."v_total_pengeluaran" AS  SELECT pengeluaran.cabang_id,
    sum(pengeluaran.jumlah) AS total_pengeluaran
   FROM babycare.pengeluaran
  GROUP BY pengeluaran.cabang_id;

-- ----------------------------
-- View structure for v_saldo_akhir
-- ----------------------------
DROP VIEW IF EXISTS "babycare"."v_saldo_akhir";
CREATE VIEW "babycare"."v_saldo_akhir" AS  SELECT p.cabang_id,
    COALESCE(p.total_pendapatan, 0::numeric) - COALESCE(g.total_pengeluaran, 0::numeric) AS saldo
   FROM babycare.v_total_pendapatan p
     LEFT JOIN babycare.v_total_pengeluaran g ON p.cabang_id = g.cabang_id;

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "babycare"."cabang_id_seq"
OWNED BY "babycare"."cabang"."id";
SELECT setval('"babycare"."cabang_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "babycare"."jenis_terapi_id_seq"
OWNED BY "babycare"."jenis_terapi"."id";
SELECT setval('"babycare"."jenis_terapi_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "babycare"."notifikasi_id_seq"
OWNED BY "babycare"."notifikasi"."id";
SELECT setval('"babycare"."notifikasi_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "babycare"."pasien_id_seq"
OWNED BY "babycare"."pasien"."id";
SELECT setval('"babycare"."pasien_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "babycare"."pemasukan_id_seq"
OWNED BY "babycare"."pemasukan"."id";
SELECT setval('"babycare"."pemasukan_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "babycare"."pengeluaran_id_seq"
OWNED BY "babycare"."pengeluaran"."id";
SELECT setval('"babycare"."pengeluaran_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "babycare"."permissions_id_seq"
OWNED BY "babycare"."permissions"."id";
SELECT setval('"babycare"."permissions_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "babycare"."registrasi_id_seq"
OWNED BY "babycare"."registrasi"."id";
SELECT setval('"babycare"."registrasi_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "babycare"."roles_id_seq"
OWNED BY "babycare"."roles"."id";
SELECT setval('"babycare"."roles_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "babycare"."terapis_id_seq"
OWNED BY "babycare"."terapis"."id";
SELECT setval('"babycare"."terapis_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "babycare"."transport_terapis_id_seq"
OWNED BY "babycare"."transport_terapis"."id";
SELECT setval('"babycare"."transport_terapis_id_seq"', 1, false);

-- ----------------------------
-- Alter sequences owned by
-- ----------------------------
ALTER SEQUENCE "babycare"."users_id_seq"
OWNED BY "babycare"."users"."id";
SELECT setval('"babycare"."users_id_seq"', 1, false);

-- ----------------------------
-- Primary Key structure for table cabang
-- ----------------------------
ALTER TABLE "babycare"."cabang" ADD CONSTRAINT "cabang_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table jenis_terapi
-- ----------------------------
ALTER TABLE "babycare"."jenis_terapi" ADD CONSTRAINT "jenis_terapi_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table notifikasi
-- ----------------------------
ALTER TABLE "babycare"."notifikasi" ADD CONSTRAINT "notifikasi_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table pasien
-- ----------------------------
ALTER TABLE "babycare"."pasien" ADD CONSTRAINT "pasien_kode_pasien_key" UNIQUE ("kode_pasien");

-- ----------------------------
-- Checks structure for table pasien
-- ----------------------------
ALTER TABLE "babycare"."pasien" ADD CONSTRAINT "pasien_jenis_kelamin_check" CHECK (jenis_kelamin = ANY (ARRAY['L'::bpchar, 'P'::bpchar]));

-- ----------------------------
-- Primary Key structure for table pasien
-- ----------------------------
ALTER TABLE "babycare"."pasien" ADD CONSTRAINT "pasien_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table pemasukan
-- ----------------------------
ALTER TABLE "babycare"."pemasukan" ADD CONSTRAINT "pemasukan_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table pengeluaran
-- ----------------------------
ALTER TABLE "babycare"."pengeluaran" ADD CONSTRAINT "pengeluaran_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table permissions
-- ----------------------------
ALTER TABLE "babycare"."permissions" ADD CONSTRAINT "permissions_code_key" UNIQUE ("code");

-- ----------------------------
-- Primary Key structure for table permissions
-- ----------------------------
ALTER TABLE "babycare"."permissions" ADD CONSTRAINT "permissions_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Uniques structure for table registrasi
-- ----------------------------
ALTER TABLE "babycare"."registrasi" ADD CONSTRAINT "registrasi_kode_registrasi_key" UNIQUE ("kode_registrasi");

-- ----------------------------
-- Primary Key structure for table registrasi
-- ----------------------------
ALTER TABLE "babycare"."registrasi" ADD CONSTRAINT "registrasi_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table role_permissions
-- ----------------------------
ALTER TABLE "babycare"."role_permissions" ADD CONSTRAINT "role_permissions_pkey" PRIMARY KEY ("role_id", "permission_id");

-- ----------------------------
-- Uniques structure for table roles
-- ----------------------------
ALTER TABLE "babycare"."roles" ADD CONSTRAINT "roles_nama_role_key" UNIQUE ("nama_role");

-- ----------------------------
-- Primary Key structure for table roles
-- ----------------------------
ALTER TABLE "babycare"."roles" ADD CONSTRAINT "roles_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table terapis
-- ----------------------------
ALTER TABLE "babycare"."terapis" ADD CONSTRAINT "terapis_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table transport_terapis
-- ----------------------------
ALTER TABLE "babycare"."transport_terapis" ADD CONSTRAINT "transport_terapis_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Primary Key structure for table user_roles
-- ----------------------------
ALTER TABLE "babycare"."user_roles" ADD CONSTRAINT "user_roles_pkey" PRIMARY KEY ("user_id", "role_id");

-- ----------------------------
-- Uniques structure for table users
-- ----------------------------
ALTER TABLE "babycare"."users" ADD CONSTRAINT "users_username_key" UNIQUE ("username");

-- ----------------------------
-- Primary Key structure for table users
-- ----------------------------
ALTER TABLE "babycare"."users" ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");

-- ----------------------------
-- Foreign Keys structure for table notifikasi
-- ----------------------------
ALTER TABLE "babycare"."notifikasi" ADD CONSTRAINT "notifikasi_pasien_id_fkey" FOREIGN KEY ("pasien_id") REFERENCES "babycare"."pasien" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "babycare"."notifikasi" ADD CONSTRAINT "notifikasi_registrasi_id_fkey" FOREIGN KEY ("registrasi_id") REFERENCES "babycare"."registrasi" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table pasien
-- ----------------------------
ALTER TABLE "babycare"."pasien" ADD CONSTRAINT "pasien_cabang_id_fkey" FOREIGN KEY ("cabang_id") REFERENCES "babycare"."cabang" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table pemasukan
-- ----------------------------
ALTER TABLE "babycare"."pemasukan" ADD CONSTRAINT "pemasukan_cabang_id_fkey" FOREIGN KEY ("cabang_id") REFERENCES "babycare"."cabang" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "babycare"."pemasukan" ADD CONSTRAINT "pemasukan_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "babycare"."users" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "babycare"."pemasukan" ADD CONSTRAINT "pemasukan_registrasi_id_fkey" FOREIGN KEY ("registrasi_id") REFERENCES "babycare"."registrasi" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table pengeluaran
-- ----------------------------
ALTER TABLE "babycare"."pengeluaran" ADD CONSTRAINT "pengeluaran_cabang_id_fkey" FOREIGN KEY ("cabang_id") REFERENCES "babycare"."cabang" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "babycare"."pengeluaran" ADD CONSTRAINT "pengeluaran_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "babycare"."users" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table registrasi
-- ----------------------------
ALTER TABLE "babycare"."registrasi" ADD CONSTRAINT "registrasi_cabang_id_fkey" FOREIGN KEY ("cabang_id") REFERENCES "babycare"."cabang" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "babycare"."registrasi" ADD CONSTRAINT "registrasi_created_by_fkey" FOREIGN KEY ("created_by") REFERENCES "babycare"."users" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "babycare"."registrasi" ADD CONSTRAINT "registrasi_jenis_terapi_id_fkey" FOREIGN KEY ("jenis_terapi_id") REFERENCES "babycare"."jenis_terapi" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "babycare"."registrasi" ADD CONSTRAINT "registrasi_pasien_id_fkey" FOREIGN KEY ("pasien_id") REFERENCES "babycare"."pasien" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "babycare"."registrasi" ADD CONSTRAINT "registrasi_terapis_id_fkey" FOREIGN KEY ("terapis_id") REFERENCES "babycare"."terapis" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table role_permissions
-- ----------------------------
ALTER TABLE "babycare"."role_permissions" ADD CONSTRAINT "role_permissions_permission_id_fkey" FOREIGN KEY ("permission_id") REFERENCES "babycare"."permissions" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "babycare"."role_permissions" ADD CONSTRAINT "role_permissions_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "babycare"."roles" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table terapis
-- ----------------------------
ALTER TABLE "babycare"."terapis" ADD CONSTRAINT "terapis_cabang_id_fkey" FOREIGN KEY ("cabang_id") REFERENCES "babycare"."cabang" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table transport_terapis
-- ----------------------------
ALTER TABLE "babycare"."transport_terapis" ADD CONSTRAINT "transport_terapis_registrasi_id_fkey" FOREIGN KEY ("registrasi_id") REFERENCES "babycare"."registrasi" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
ALTER TABLE "babycare"."transport_terapis" ADD CONSTRAINT "transport_terapis_terapis_id_fkey" FOREIGN KEY ("terapis_id") REFERENCES "babycare"."terapis" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table user_roles
-- ----------------------------
ALTER TABLE "babycare"."user_roles" ADD CONSTRAINT "user_roles_role_id_fkey" FOREIGN KEY ("role_id") REFERENCES "babycare"."roles" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;
ALTER TABLE "babycare"."user_roles" ADD CONSTRAINT "user_roles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "babycare"."users" ("id") ON DELETE CASCADE ON UPDATE NO ACTION;

-- ----------------------------
-- Foreign Keys structure for table users
-- ----------------------------
ALTER TABLE "babycare"."users" ADD CONSTRAINT "users_cabang_id_fkey" FOREIGN KEY ("cabang_id") REFERENCES "babycare"."cabang" ("id") ON DELETE NO ACTION ON UPDATE NO ACTION;
