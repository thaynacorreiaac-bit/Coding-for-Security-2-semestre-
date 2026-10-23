use 2semestre;

create table alertas (
    id int auto_increment primary key,
    tipo varchar(50), ip_origem varchar(45),
    severidade enum('baixa','media','alta','critica'),
    status varchar(20) default 'aberto',
    criado_em timestamp default current_timestamp
);

insert into alertas (tipo, ip_origem, severidade)
values ('brute force', '192.168.1.50', 'alta');

insert into alertas (tipo, ip_origem, severidade)
values ('port scan', '10.0.0.7', 'media');

insert into alertas (tipo, ip_origem, severidade)
values ('sql injection', '172.16.0.20', 'critica');

insert into alertas (tipo, ip_origem, severidade)
values ('login suspeito', '192.168.1.99', 'alta');

select * from alertas
where severidade = 'alta';

update alertas
set status = 'resolvido'
where id = 1;

select severidade, count(*) as total
from alertas
group by severidade
order by severidade desc;

delete from alertas
where criado_em < now() - interval 90 day;

insert into alertas (tipo, ip_origem, severidade, criado_em)
values ('teste antigo', '10.0.0.1', 'baixa', '2026-01-01');

delete from alertas
where criado_em < now() - interval 90 day;