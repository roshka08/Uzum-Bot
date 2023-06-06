from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool

from data import config


class Database:
    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME,
        )

    async def execute(
        self,
        command,
        *args,
        fetch: bool = False,
        fetchval: bool = False,
        fetchrow: bool = False,
        execute: bool = False,
    ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:
                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        full_name VARCHAR(255) NOT NULL,
        username varchar(255) NULL,
        telegram_id BIGINT NOT NULL UNIQUE
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_categories(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Category (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL UNIQUE,
        description TEXT NULL
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_cart(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Cart (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        amount INTEGER NOT NULL
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_products(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Product (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL UNIQUE,
        description TEXT NULL,
        image VARCHAR(255) NOT NULL,
        price NUMERIC NOT NULL,
        cat_id INTEGER NOT NULL
        );
        """
        await self.execute(sql, execute=True)

    async def create_table_order(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Orders (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL,
        phone_number VARCHAR(20) NOT NULL,
        lat VARCHAR(30) NOT NULL,
        lon VARCHAR(30) NOT NULL,
        total_price NUMERIC NOT NULL,
        paid BOOLEAN NOT NULL
        );
        """
        await self.execute(sql, execute=True)
    
    async def create_table_order_product(self):
        sql = """
        CREATE TABLE IF NOT EXISTS OrderProduct (
        id SERIAL PRIMARY KEY,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        amount INTEGER NOT NULL
        );
        """
        await self.execute(sql, execute=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join(
            [f"{item} = ${num}" for num, item in enumerate(parameters.keys(), start=1)]
        )
        return sql, tuple(parameters.values())

    async def add_user(self, full_name, username, telegram_id):
        sql = "INSERT INTO users (full_name, username, telegram_id) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, full_name, username, telegram_id, fetchrow=True)

    async def add_product_to_cart(self, user_id, product_id, amount):
        sql = "INSERT INTO Cart (user_id, product_id, amount) VALUES($1, $2, $3) returning *"
        return await self.execute(sql,user_id, product_id, amount, fetchrow=True)
    
    async def update_product_to_cart(self, user_id, product_id, amount):
        sql = "UPDATE Cart SET amount=$1 WHERE user_id=$2 AND product_id=$3;"
        return await self.execute(sql, amount, user_id, product_id, execute=True)
                                  
    async def select_cart_product(self, **kwargs):
        sql = "SELECT * FROM Cart WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)
    
    async def select_all_cart_items(self, **kwargs):
        sql = "SELECT * FROM Cart WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)
    
    async def delete_cart_item(self, product_id, user_id):
        await self.execute("DELETE FROM Cart WHERE product_id=$1 And user_id=$2", product_id, user_id, execute=True)

    async def clear_cart_item(self, user_id):
        await self.execute("DELETE FROM Cart WHERE user_id=$1", user_id, execute=True)

    async def add_order(self, user_id, phone_number, lat, lon, total_price, paid=False):
        sql = "INSERT INTO Orders (user_id, phone_number, lat, lon, total_price, paid) VALUES($1, $2, $3, $4, $5, $6) returning *"
        return await self.execute(sql, user_id, phone_number, lat, lon, total_price, paid, fetchrow=True)
    
    async def select_all_orders(self, **kwargs):
        sql = "SELECT * FROM Orders WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)
    
    async def add_order_product(self, order_id, product_id, amount):   
        sql = "INSERT INTO OrderProduct (order_id, product_id, amount) VALUES($1, $2, $3) returning *"
        return await self.execute(sql, order_id, product_id, amount, fetchrow=True)
    
    async def select_all_users(self):
        sql = "SELECT * FROM Users"
        return await self.execute(sql, fetch=True)

    async def select_all_product(self):
        sql = "SELECT * FROM Product"
        return await self.execute(sql, fetch=True)

    async def select_all_cats(self):
        sql = "SELECT * FROM Category"
        return await self.execute(sql, fetch=True)

    async def select_category(self, **kwargs):
        sql = "SELECT * FROM Category WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)
    
    async def select_product_by_category(self, **kwargs):
        sql = "SELECT * FROM Product WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def select_product(self, **kwargs):
        sql = "SELECT * FROM Product WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)
    
    async def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetchrow=True)

    async def count_users(self):
        sql = "SELECT COUNT(*) FROM Users"
        return await self.execute(sql, fetchval=True)

    async def update_user_username(self, username, telegram_id):
        sql = "UPDATE Users SET username=$1 WHERE telegram_id=$2"
        return await self.execute(sql, username, telegram_id, execute=True)

    async def update_order_paid(self, order_id, paid=True):
        sql = "UPDATE Orders SET paid=$2 WHERE id=$1"
        return await self.execute(sql, order_id, paid, execute=True)

    async def select_order_product(self, **kwargs):
        sql = "SELECT * FROM OrderProduct WHERE "
        sql, parameters = self.format_args(sql, parameters=kwargs)
        return await self.execute(sql, *parameters, fetch=True)

    async def delete_users(self):
        await self.execute("DELETE FROM Users WHERE TRUE", execute=True)

    async def drop_users(self):
        await self.execute("DROP TABLE Users", execute=True)
