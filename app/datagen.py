from core.database import SessionLocal

from users.models import UserModel
from costs.models import Cost

from faker import Faker

fake = Faker()


def seed_users(db):
    user = UserModel(username=fake.user_name())
    user.set_password("12345678")
    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"Fake user created with 'username': {user.username} and 'ID': {user.id}")
    return user


def seed_costs(db, user, count=10):
    costs_list = []
    for _ in range(count):
        costs_list.append(
            Cost(
                user_id=user.id,
                title=fake.sentence(nb_words=3).rstrip("."),
                amount=round(
                    fake.pyfloat(min_value=10, max_value=1000, right_digits=2), 2
                ),
                description=fake.paragraph(nb_sentences=2),
            )
        )
    db.add_all(costs_list)
    db.commit()
    print(f"Fake added 10 costs for 'user_id': {user.id}")


def main():
    db = SessionLocal()
    try:
        user = seed_users(db)
        seed_costs(db, user)
    finally:
        db.close()


if __name__ == "__main__":
    main()
