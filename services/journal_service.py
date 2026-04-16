from models.journal_model import (
    create_journal,
    get_all_journals,
    get_journal_by_id,
    update_journal,
    delete_journal
)


def create_journal_service(data):
    if not data.get("name"):
        raise ValueError("Name is required")
    return create_journal(data)


def get_journals_service():
    return get_all_journals()


def get_journal_detail_service(id):
    return get_journal_by_id(id)


def update_journal_service(id, data):
    if not data.get("name"):
        raise ValueError("Name is required")
    update_journal(id, data)


def delete_journal_service(id):
    delete_journal(id)