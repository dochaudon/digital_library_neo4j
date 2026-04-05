/* =======================
CLEAR DATABASE (optional)
======================= */
MATCH (n) DETACH DELETE n;

/* =======================
CREATE CONSTRAINT (UPDATE)
======================= */
CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (b:Book) REQUIRE b.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (a2:Article) REQUIRE a2.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (t:Thesis) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT IF NOT EXISTS FOR (a:Author) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (s:Subject) REQUIRE s.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (k:Keyword) REQUIRE k.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (c:Category) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (l:Language) REQUIRE l.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (i:Institution) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (j:Journal) REQUIRE j.id IS UNIQUE;

/* =======================
IMPORT DOCUMENT + LABEL
======================= */
LOAD CSV WITH HEADERS FROM 'file:///node_document.csv' AS row

MERGE (d:Document {id: row.id})
SET d.title = row.title,
d.alternative_title = row.alternative_title,
d.year = toInteger(row.year),
d.pages = row.pages,
d.image_url = row.image_url,
d.file_url = row.file_url,
d.abstract = row.abstract

// 🔥 GÁN LABEL THEO TYPE
FOREACH (_ IN CASE WHEN toLower(row.type) = "book" THEN [1] ELSE [] END |
SET d:Book
)

FOREACH (_ IN CASE WHEN toLower(row.type) = "article" THEN [1] ELSE [] END |
SET d:Article
)

FOREACH (_ IN CASE WHEN toLower(row.type) = "thesis" THEN [1] ELSE [] END |
SET d:Thesis
);

/* =======================
IMPORT NODE KHÁC
======================= */

// Author
LOAD CSV WITH HEADERS FROM 'file:///node_author.csv' AS row
MERGE (a:Author {id: row.id})
SET a.name = row.name;

// Subject
LOAD CSV WITH HEADERS FROM 'file:///node_subject.csv' AS row
MERGE (s:Subject {id: row.id})
SET s.name = row.name;

// Keyword
LOAD CSV WITH HEADERS FROM 'file:///node_keyword.csv' AS row
MERGE (k:Keyword {id: row.id})
SET k.name = row.name;

// Category
LOAD CSV WITH HEADERS FROM 'file:///node_category.csv' AS row
MERGE (c:Category {id: row.id})
SET c.name = row.name;

// Language
LOAD CSV WITH HEADERS FROM 'file:///node_language.csv' AS row
MERGE (l:Language {id: row.id})
SET l.name = row.name;

// Institution
LOAD CSV WITH HEADERS FROM 'file:///node_institution.csv' AS row
MERGE (i:Institution {id: row.id})
SET i.name = row.name,
i.type = row.type;

// Journal
LOAD CSV WITH HEADERS FROM 'file:///node_journal.csv' AS row
MERGE (j:Journal {id: row.id})
SET j.name = row.name;

/* =======================
IMPORT RELATIONSHIP
======================= */

// HAS_AUTHOR
LOAD CSV WITH HEADERS FROM 'file:///rel_document_author.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (a:Author {id: row.author_id})
MERGE (d)-[:HAS_AUTHOR {role: row.role}]->(a);

// HAS_SUBJECT
LOAD CSV WITH HEADERS FROM 'file:///rel_document_subject.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (s:Subject {id: row.subject_id})
MERGE (d)-[:HAS_SUBJECT]->(s);

// HAS_KEYWORD
LOAD CSV WITH HEADERS FROM 'file:///rel_document_keyword.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (k:Keyword {id: row.keyword_id})
MERGE (d)-[:HAS_KEYWORD]->(k);

// HAS_CATEGORY
LOAD CSV WITH HEADERS FROM 'file:///rel_document_category.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (c:Category {id: row.category_id})
MERGE (d)-[:HAS_CATEGORY]->(c);

// IN_LANGUAGE
LOAD CSV WITH HEADERS FROM 'file:///rel_document_language.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (l:Language {id: row.language_id})
MERGE (d)-[:IN_LANGUAGE]->(l);

// PUBLISHED_BY
LOAD CSV WITH HEADERS FROM 'file:///rel_document_institution.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (i:Institution {id: row.institution_id})
MERGE (d)-[:PUBLISHED_BY]->(i);

// PUBLISHED_IN
LOAD CSV WITH HEADERS FROM 'file:///rel_document_journal.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (j:Journal {id: row.journal_id})
MERGE (d)-[:PUBLISHED_IN]->(j);

// SUBMITTED_TO
LOAD CSV WITH HEADERS FROM 'file:///rel_document_submitted.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (i:Institution {id: row.institution_id})
MERGE (d)-[:SUBMITTED_TO]->(i);

/* =======================
USER
======================= */
CREATE CONSTRAINT user_email_unique IF NOT EXISTS
FOR (u:User)
REQUIRE u.email IS UNIQUE;

CREATE (u:User {
id: "user_admin_001",
username: "admin",
email: "[admin@gmail.com](mailto:admin@gmail.com)",
password: "123456",
role: "admin",
status: "active",
created_at: datetime()
});

CREATE (u:User {
id: "user_001",
username: "user1",
email: "[user1@gmail.com](mailto:user1@gmail.com)",
password: "123456",
role: "user",
status: "active",
created_at: datetime()
});

MATCH (d:Document)
WHERE toLower(d.type) = "book"
SET d:Book;

MATCH (d:Document)
WHERE toLower(d.type) = "article"
SET d:Article;

MATCH (d:Document)
WHERE toLower(d.type) = "thesis"
SET d:Thesis;