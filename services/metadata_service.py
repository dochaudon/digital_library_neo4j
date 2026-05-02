
# =====================================================
# AUTHOR
# =====================================================
from models.author_model import (
    create_author,
    get_all_authors,
    get_author_by_id,
    update_author,
    delete_author
)

def create_author_service(data):
    return create_author(data)

def get_authors_service():
    return get_all_authors()

def get_author_detail_service(author_id):
    return get_author_by_id(author_id)

def update_author_service(author_id, data):
    return update_author(author_id, data)

def delete_author_service(author_id):
    return delete_author(author_id)


# =====================================================
# SUBJECT
# =====================================================
from models.subject_model import (
    create_subject,
    get_all_subjects,
    get_subject_by_id,
    update_subject,
    delete_subject
)

def create_subject_service(data):
    return create_subject(data)

def get_subjects_service():
    return get_all_subjects()

def get_subject_detail_service(subject_id):
    return get_subject_by_id(subject_id)

def update_subject_service(subject_id, data):
    return update_subject(subject_id, data)

def delete_subject_service(subject_id):
    return delete_subject(subject_id)


# =====================================================
# KEYWORD
# =====================================================
from models.keyword_model import (
    create_keyword,
    get_all_keywords,
    get_keyword_by_id,
    update_keyword,
    delete_keyword
)

def create_keyword_service(data):
    return create_keyword(data)

def get_keywords_service():
    return get_all_keywords()

def get_keyword_detail_service(keyword_id):
    return get_keyword_by_id(keyword_id)

def update_keyword_service(keyword_id, data):
    return update_keyword(keyword_id, data)

def delete_keyword_service(keyword_id):
    return delete_keyword(keyword_id)


# =====================================================
# CATEGORY
# =====================================================
from models.category_model import (
    create_category,
    get_all_categories,
    get_category_by_id,
    update_category,
    delete_category
)

def create_category_service(data):
    return create_category(data)

def get_categories_service():
    return get_all_categories()

def get_category_detail_service(category_id):
    return get_category_by_id(category_id)

def update_category_service(category_id, data):
    return update_category(category_id, data)

def delete_category_service(category_id):
    return delete_category(category_id)


# =====================================================
# INSTITUTION (CÓ TYPE)
# =====================================================
from models.institution_model import (
    create_institution,
    get_all_institutions,
    get_institution_by_id,
    update_institution,
    delete_institution
)

def create_institution_service(data):
    return create_institution(data)

def get_institutions_service():
    return get_all_institutions()

def get_institution_detail_service(inst_id):
    return get_institution_by_id(inst_id)

def update_institution_service(inst_id, data):
    return update_institution(inst_id, data)

def delete_institution_service(inst_id):
    return delete_institution(inst_id)


# =====================================================
# LANGUAGE (NEW)
# =====================================================
from models.language_model import (
    create_language,
    get_all_languages,
    delete_language
)

def create_language_service(data):
    return create_language(data)

def get_languages_service():
    return get_all_languages()

def delete_language_service(lang_id):
    return delete_language(lang_id)


# =====================================================
# JOURNAL (NEW)
# =====================================================
from models.journal_model import (
    create_journal,
    get_all_journals,
    delete_journal
)

def create_journal_service(data):
    return create_journal(data)

def get_journals_service():
    return get_all_journals()

def delete_journal_service(journal_id):
    return delete_journal(journal_id)