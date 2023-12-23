drop database storedb;
create database storedb;
use storedb;
-- create product table with auto-incremented primary key
create table product (
    productid int primary key auto_increment,
    name varchar(255),
    price decimal(10, 2)
);
-- create supplier table with auto-incremented primary key
create table supplier (
    supplierid int primary key auto_increment,
    name varchar(255)
);
-- create customer table with auto-incremented primary key
create table customer (
    customerid int primary key auto_increment,
    name varchar(255)
);
-- create sale table with auto-incremented primary key
create table sale (
    saleid int primary key auto_increment,
    productid int,
    customerid int,
    quantity int,
    saledate date default(current_date),
    foreign key (productid) references product(productid) on delete set null,
    foreign key (customerid) references customer(customerid) on delete cascade
);
-- create stock table
create table stock (
    productid int,
    supplierid int,
    quantity int,
    purchasedate date default (current_date),
    primary key (productid, supplierid),
    foreign key (productid) references product(productid) on delete cascade,
    foreign key (supplierid) references supplier(supplierid) on delete cascade
);
delimiter //
create trigger after_sale
after insert on sale
for each row
begin
    declare supplier_id int;
    select supplierid into supplier_id from stock where productid = new.productid;
    update stock
    set quantity = quantity - new.quantity
    where productid = new.productid and supplierid = supplier_id;
end//
delimiter ;

delimiter //
create trigger update_sale
before update on sale
for each row
begin
    declare supplier_id int;
    select supplierid into supplier_id from stock where productid = old.productid;
    update stock
        set quantity = quantity + old.quantity
        where productid = old.productid and supplierid = supplier_id;
    update stock
        set quantity = quantity - new.quantity
        where productid = new.productid and supplierid = supplier_id;
end//
delimiter ;

delimiter //
create procedure makepurchase(
    in p_customerid int,
    in p_productid int,
    in p_quantity int
)
begin
    declare current_quantity int;
    select quantity into current_quantity from stock
    where productid = p_productid;

    if current_quantity - p_quantity < 0 then
        rollback;
        signal sqlstate '45000'
        set message_text = 'Product is not available in sufficient quantity. Transaction rolled back.';
    else
        insert into sale (productid, customerid, quantity, saledate)
        values (p_productid, p_customerid, p_quantity, current_date());
        commit;
    end if;
end //
delimiter ;
delimiter //
create procedure updatesale(
    in p_customerid int,
    in p_productid int,
    in p_quantity int,
    in p_saleid int
)
begin
    declare current_quantity int;
    select quantity into current_quantity from stock
    where productid = p_productid;
    if current_quantity - p_quantity < 0 then
        rollback;
        signal sqlstate '45000'
        set message_text = 'Product is not available in sufficient quantity. Transaction rolled back.';
    else
        update sale
        set customerid = p_customerid,
            productid = p_productid,
            quantity = p_quantity
        where saleid = p_saleid;
        commit;
    end if;
end//
delimiter ;
insert into supplier (name)
values
    ('supplier a'),
    ('supplier b'),
    ('supplier c');
insert into product (name, price)
values
    ('product x', 1000.00),
    ('product y', 5000.00),
    ('product z', 8000.00),
    ('product a', 342.00),
    ('product b', 800.50);
insert into customer (name)
values
    ('customer 1'),
    ('customer 2'),
    ('customer 3'),
    ('customer 4'),
    ('customer 5');
insert into stock (productid, supplierid, quantity, purchasedate)
values
    (1, 1, 100, '2023-01-01'),
    (2, 2, 50, '2023-01-02'),
    (3, 3, 75, '2023-01-03'),
    (4, 1, 120, '2023-01-04'),
    (5, 2, 30, '2023-01-05');
insert into sale (productid, customerid, quantity, saledate)
values
    (1, 1, 5, '2023-12-01'),
    (2, 2, 10, '2023-12-02'),
    (3, 3, 8, '2023-12-03'),
    (4, 2, 3, '2023-12-03'),
    (5, 1, 4, '2023-12-03');


