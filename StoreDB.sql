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
CREATE TABLE stock (
    productid INT,
    supplierid INT,
    quantity INT,
    purchasedate DATE DEFAULT (CURRENT_DATE),
    PRIMARY KEY (productid, supplierid),
    FOREIGN KEY (productid) REFERENCES product(productid) ON DELETE CASCADE,
    FOREIGN KEY (supplierid) REFERENCES supplier(supplierid) ON DELETE cascade
);
delimiter //
create trigger after_sale
after insert on sale
for each row
begin
    DECLARE supplier_id INT;
    SELECT supplierid INTO supplier_id FROM stock WHERE productid = NEW.productid;
    update stock
    set quantity = quantity - new.quantity
    where productid = new.productid and supplierid = supplier_id;
end//
delimiter ;

delimiter //
create trigger update_sale
after update on sale
for each row
begin
    DECLARE supplier_id INT;
    SELECT supplierid INTO supplier_id FROM stock WHERE productid = NEW.productid;
    update stock
    set quantity = quantity + old.quantity - new.quantity
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
    set autocommit = 0;

    insert into sale (productid, customerid, quantity, saledate)
    values (p_productid, p_customerid, p_quantity, current_date());

    update stock
    set quantity = quantity - p_quantity
    where productid = p_productid;

    -- checking if any rows were affected by the update
    if row_count() = 0 then
        -- product not available, rollback the transaction
        rollback;
        signal sqlstate '45000'
        set message_text = 'product is not available. transaction rolled back.';
    else
        -- product available, commit the transaction
        commit;
    end if;
end //
delimiter ;
delimiter //
CREATE PROCEDURE updatesale(
    in p_customerid int,
    in p_productid int,
    in p_quantity int,
    in p_saleid int
)
BEGIN
    UPDATE sale
    SET customerid = p_customerid,
        productid = p_productid,
        quantity = p_quantity
    WHERE saleid = p_saleid;
END//
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
    ('Customer 1'),
    ('Customer 2'),
    ('Customer 3'),
    ('Customer 4'),
    ('Customer 5');
INSERT INTO stock (productid, supplierid, quantity, purchasedate)
VALUES
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


