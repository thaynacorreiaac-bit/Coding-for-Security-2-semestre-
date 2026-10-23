use 2semestre;

create table ativos (
id int auto_increment primary key,
nome varchar(100) not null unique,
ip varchar(15) not null unique,
tipo varchar(20) not null,
criticidade int not null -- 1 a 5
);

create table vulnerabilidades (
id int auto_increment primary key,
cve_id varchar(20) not null unique,
descricao varchar(200) not null,
severidade enum('Baixa', 'Média', 'Alta') not null,
cvss decimal(3,1) not null
);

create table ativo_vulnerabilidade (
ativo_id int not null,
vuln_id int not null,
status enum('aberta', 'em andamento', 'encerrado') not null,
detectada_em datetime not null,
primary key (ativo_id, vuln_id),
foreign key (ativo_id) references ativos(id),
foreign key (vuln_id) references vulnerabilidades(id)
);

-- Teste do enunciado
insert into ativos (nome, ip, tipo, criticidade)
values ('SRV-WEB01', '192.168.1.10', 'Servidor', 4);

insert into vulnerabilidades (cve_id, descricao, severidade, cvss)
values ('CVE-2024-001', 'Vulnerabilidade de teste', 'Alta', 8.5);

insert into ativo_vulnerabilidade (ativo_id, vuln_id, status, detectada_em)
values (1, 1, 'aberta', now());