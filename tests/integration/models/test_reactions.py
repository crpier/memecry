from typing import Annotated

import pytest
from relax.test import check
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session, sessionmaker

import memecry.model


@pytest.fixture()
def create_model() -> sessionmaker[Session]:
    dsn = "sqlite://"
    engine = create_engine(dsn)
    with engine.begin() as conn:
        memecry.model.Base.metadata.create_all(conn)
    return sessionmaker(engine)


@check
def test_add_entry(
    session: Annotated[sessionmaker[Session], create_model],
):
    reaction = memecry.model.Reaction(user_id=1, comment_id=1, kind="Like", post_id=1)
    with session() as s:
        s.add(reaction)
        s.commit()


@check
def test_unique_constraint_user_id_and_post_id(
    session: Annotated[sessionmaker[Session], create_model],
):
    base_reaction = memecry.model.Reaction(user_id=1, kind="Like", post_id=1)
    reaction_duplicate_post_id = memecry.model.Reaction(
        user_id=1, kind="Like", post_id=1
    )

    with session() as s:
        s.add(base_reaction)
        s.commit()
        s.add(reaction_duplicate_post_id)
        with pytest.raises(IntegrityError):
            s.commit()


@check
def test_unique_constraint_user_id_and_comment_id(
    session: Annotated[sessionmaker[Session], create_model],
):
    base_reaction = memecry.model.Reaction(
        user_id=1, kind="Like", post_id=1, comment_id=1
    )
    reaction_duplicate_post_id = memecry.model.Reaction(
        user_id=1, kind="Like", post_id=2, comment_id=1
    )

    with session() as s:
        s.add(base_reaction)
        s.commit()
        s.add(reaction_duplicate_post_id)
        with pytest.raises(IntegrityError):
            s.commit()
