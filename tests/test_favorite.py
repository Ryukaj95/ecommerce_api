import json
from http.client import OK
from http.client import NOT_FOUND
from http.client import CREATED
from http.client import BAD_REQUEST
from http.client import NO_CONTENT
from http.client import UNAUTHORIZED
from peewee import SqliteDatabase
from models import Item, User, Favorites
from app import app
from views.user import crypt_password
import base64
import uuid

from .base_test import BaseTest


class TestFavorites(BaseTest):
    def create_user(self, id_user, number):
        return User.create(
            uuid=id_user,
            first_name='{}{}'.format('first_name_', number),
            last_name='{}{}'.format('last_name_', number),
            email='{}{}'.format('email_', number),
            password=crypt_password('{}{}'.format('password_', number)),
        )

    def create_item(self, id_item, number):
        return Item.create(
            uuid=id_item,
            name='{}{}'.format('name_', number),
            price=number,
            description='{}{}'.format('description_', number),
            category='{}{}'.format('category_', number),
        )

    def test_get__favorites(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        user_db = self.create_user(
            id_user,
            1)

        item_db = self.create_item(
            id_item,
            1)

        Favorites.create(
            uuid=uuid.uuid4(),
            user=user_db,
            item=item_db
        )

        resp = self.open_with_auth(
            '/favorites/', 'get', 'email_1', 'password_1', data=None)

        assert resp.status_code == OK
        data = json.loads(resp.data.decode())
        assert len(data) == 1
        assert user_db.favorite_items() == data

    def test_get__favorites_is_empty(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        user_db = self.create_user(
            id_user,
            1)

        item_db = self.create_item(
            id_item,
            1)

        resp = self.open_with_auth(
            '/favorites/', 'get', 'email_1', 'password_1', data=None)

        assert resp.status_code == OK
        data = json.loads(resp.data.decode())
        assert len(data) == 0
        assert user_db.favorite_items() == []

    def test_post__create_favorite_success(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        self.create_user(id_user, 1)
        self.create_item(id_item, 1)

        sample_favorite = {
            'id_item': id_item
        }

        resp = self.open_with_auth(
            '/favorites/', 'post', 'email_1', 'password_1', data=sample_favorite)
        assert resp.status_code == CREATED
        assert Favorites.count() == 1

    def test_post__failed_item_uuid_not_valid(self):
        id_user = uuid.uuid4()

        self.create_user(id_user, 1)

        sample_favorite = {
            'id_item': 123123
        }

        resp = self.open_with_auth(
            '/favorites/', 'post', 'email_1', 'password_1', data=sample_favorite)
        assert resp.status_code == BAD_REQUEST
        assert Favorites.count() == 0

    def test_post__failed_item_does_not_exists(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        self.create_user(id_user, 1)
        self.create_item(id_item, 1)

        sample_favorite = {
            'id_item': uuid.uuid4()
        }

        resp = self.open_with_auth(
            '/favorites/', 'post', 'email_1', 'password_1', data=sample_favorite)
        assert resp.status_code == BAD_REQUEST
        data = json.loads(resp.data.decode())
        assert not data
        assert Favorites.count() == 0

    def test_delete__favorite_success(self):
        id_user = uuid.uuid4()
        id_item_1 = uuid.uuid4()
        id_item_2 = uuid.uuid4()

        self.create_user(id_user, 1)
        self.create_item(id_item_1, 1)

        item_2 = self.create_item(id_item_2, 1)

        Favorites.create(
            uuid=uuid.uuid4(),
            user=User.get(User.uuid == id_user),
            item=Item.get(Item.uuid == id_item_1),
        )

        Favorites.create(
            uuid=uuid.uuid4(),
            user=User.get(User.uuid == id_user),
            item=Item.get(Item.uuid == id_item_2),
        )

        resp = self.open_with_auth(
            '/favorites/{}'.format(id_item_1), 'delete', 'email_1', 'password_1', data=None)
        assert Favorites.count() == 1
        assert Favorites.item == item_2
        assert resp.status_code == NO_CONTENT

    def test_delete__failed_item_not_found(self):
        id_user = uuid.uuid4()
        id_item_1 = uuid.uuid4()

        self.create_user(id_user, 1)
        item_1 = self.create_item(id_item_1, 1)

        Favorites.create(
            uuid=uuid.uuid4(),
            user=User.get(User.uuid == id_user),
            item=Item.get(Item.uuid == id_item_1),
        )

        resp = self.open_with_auth(
            '/favorites/{}'.format(uuid.uuid4()), 'delete', 'email_1', 'password_1', data=None)

        assert Favorites.count() == 1
        assert Favorites.item == item_1
        assert resp.status_code == NOT_FOUND
        data = json.loads(resp.data.decode())
        assert not data

    def test_delete__failed_user_has_no_favorite_items(self):
        id_user_1 = uuid.uuid4()
        id_user_2 = uuid.uuid4()
        id_item_1 = uuid.uuid4()

        self.create_user(id_user_1, 1)
        self.create_user(id_user_2, 2)
        item_1 = self.create_item(id_item_1, 1)

        Favorites.create(
            uuid=uuid.uuid4(),
            user=User.get(User.uuid == id_user_2),
            item=Item.get(Item.uuid == id_item_1),
        )

        resp = self.open_with_auth(
            '/favorites/{}'.format(id_item_1), 'delete', 'email_1', 'password_1', data=None)

        assert Favorites.count() == 1
        assert Favorites.item == item_1
        assert resp.status_code == NOT_FOUND
        data = json.loads(resp.data.decode())
        assert not data

    def test_delete__database_has_no_favorites(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        self.create_user(id_user, 1)
        self.create_item(id_item, 1)

        resp = self.open_with_auth(
            '/favorites/{}'.format(id_item), 'delete', 'email_1', 'password_1', data=None)

        assert Favorites.count() == 0
        assert resp.status_code == NOT_FOUND
        data = json.loads(resp.data.decode())
        assert not data
