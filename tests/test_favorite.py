import json
from http.client import OK
from http.client import NOT_FOUND
from http.client import CREATED
from http.client import BAD_REQUEST
from http.client import NO_CONTENT
from peewee import SqliteDatabase
from models import Item, User, Favorites
from app import app
import uuid


def create_user(id_user, number):
    return User.create(
        uuid=id_user,
        first_name='{}{}'.format('first_name_', number),
        last_name='{}{}'.format('last_name_', number),
        email='{}{}'.format('email_', number),
        password='{}{}'.format('password_', number),
    )


def create_item(id_item, number):
    return Item.create(
        uuid=id_item,
        name='{}{}'.format('name_', number),
        price=number,
        description='{}{}'.format('description_', number),
        category='{}{}'.format('category_', number),
    )


class TestFavorites:
    @classmethod
    def setup_class(cls):
        db = SqliteDatabase(':memory:')
        tables = [Favorites, Item, User]
        for table in tables:
            table._meta.database = db
            table.create_table()

        cls.app = app.test_client()

    def setup_method(self):
        Item.delete().execute()
        Favorites.delete().execute()
        User.delete().execute()

    def test_get__favorites(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        user_db = create_user(
            id_user,
            1)

        item_db = create_item(
            id_item,
            1)

        Favorites.create(
            user=user_db,
            item=item_db
        )

        resp = self.app.get('/favorites/')
        assert resp.status_code == OK
        data = json.loads(resp.data.decode())
        assert len(data) == 1
        assert user_db.favorite_items() == data

    def test_get__favorites_empty(self):
        resp = self.app.get('/favorites/')
        data = json.loads(resp.data.decode())
        assert not data
        assert resp.status_code == NOT_FOUND

    def test_post__create_favorite_success(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        create_user(id_user, 1)
        create_item(id_item, 1)

        sample_favorite = {
            'id_user': id_user,
            'id_item': id_item
        }

        resp = self.app.post('/favorites/', data=sample_favorite)
        assert resp.status_code == CREATED
        assert Favorites.count() == 1

    def test_post__failed_item_do_not_exist(self):
        id_user = uuid.uuid4()

        create_user(id_user, 1)
        create_item(uuid.uuid4(), 1)

        sample_favorite = {
            'id_user': id_user,
            'id_item': uuid.uuid4()
        }

        resp = self.app.post('/favorites/', data=sample_favorite)

        assert resp.status_code == NOT_FOUND
        assert Favorites.count() == 0

    def test_post__failed_uuid_not_valid(self):
        sample_favorite = {
            'id_user':  "Stringa di prova",
            'id_item': 123123
        }
        resp = self.app.post('/favorites/', data=sample_favorite)
        assert resp.status_code == BAD_REQUEST
        assert Favorites.count() == 0

    def test_post__failed_item_uuid_does_not_exists(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        create_user(id_user, 1)
        create_item(id_item, 1)

        sample_favorite = {
            'id_user': id_user,
            'id_item': uuid.uuid4()
        }

        resp = self.app.post('/favorites/', data=sample_favorite)
        assert resp.status_code == NOT_FOUND
        data = json.loads(resp.data.decode())
        assert not data
        assert Favorites.count() == 0

    def test_post__failed_user_uuid_does_not_exists(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        create_user(id_user, 1)
        create_item(id_item, 1)

        sample_favorite = {
            'id_user': uuid.uuid4(),
            'id_item': id_item
        }

        resp = self.app.post('/favorites/', data=sample_favorite)
        assert resp.status_code == NOT_FOUND
        data = json.loads(resp.data.decode())
        assert not data
        assert Favorites.count() == 0

    def test_delete__favorite_success(self):
        id_user = uuid.uuid4()
        id_item_1 = uuid.uuid4()
        id_item_2 = uuid.uuid4()

        create_user(id_user, 1)
        create_item(id_item_1, 1)

        item_2 = create_item(id_item_2, 1)

        Favorites.create(
            user=User.get(User.uuid == id_user),
            item=Item.get(Item.uuid == id_item_1),
        )

        Favorites.create(
            user=User.get(User.uuid == id_user),
            item=Item.get(Item.uuid == id_item_2),
        )

        resp = self.app.delete('/favorites/{}'.format(id_item_1))
        assert Favorites.count() == 1
        assert Favorites.item == item_2
        assert resp.status_code == NO_CONTENT

    def test_delete__failed_item_not_found(self):
        id_user = uuid.uuid4()
        id_item_1 = uuid.uuid4()

        create_user(id_user, 1)
        item_1 = create_item(id_item_1, 1)

        Favorites.create(
            user=User.get(User.uuid == id_user),
            item=Item.get(Item.uuid == id_item_1),
        )

        resp = self.app.delete('/favorites/{}'.format(uuid.uuid4()))

        assert Favorites.count() == 1
        assert Favorites.item == item_1
        assert resp.status_code == NOT_FOUND
        data = json.loads(resp.data.decode())
        assert not data

    def test_delete__failed_user_has_no_favorite_items(self):
        id_user_1 = uuid.uuid4()
        id_user_2 = uuid.uuid4()
        id_item_1 = uuid.uuid4()

        create_user(id_user_1, 1)
        create_user(id_user_2, 2)
        item_1 = create_item(id_item_1, 1)

        Favorites.create(
            user=User.get(User.uuid == id_user_2),
            item=Item.get(Item.uuid == id_item_1),
        )

        resp = self.app.delete('/favorites/{}'.format(id_item_1))

        assert Favorites.count() == 1
        assert Favorites.item == item_1
        assert resp.status_code == NOT_FOUND
        data = json.loads(resp.data.decode())
        assert not data

    def test_delete__database_has_no_favorites(self):
        id_user = uuid.uuid4()
        id_item = uuid.uuid4()

        create_user(id_user, 1)
        create_item(id_item, 1)

        resp = self.app.delete('/favorites/{}'.format(id_item))

        assert Favorites.count() == 0
        assert resp.status_code == NOT_FOUND
        data = json.loads(resp.data.decode())
        assert not data
