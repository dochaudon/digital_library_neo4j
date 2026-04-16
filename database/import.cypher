/* =======================
CLEAR DATABASE (optional)
======================= */
MATCH (n) DETACH DELETE n;

// =========================
// 1. CONSTRAINTS
// =========================
CREATE CONSTRAINT document_id IF NOT EXISTS
FOR (d:Document) REQUIRE d.id IS UNIQUE;

CREATE CONSTRAINT author_id IF NOT EXISTS
FOR (a:Author) REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT subject_id IF NOT EXISTS
FOR (s:Subject) REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT keyword_id IF NOT EXISTS
FOR (k:Keyword) REQUIRE k.id IS UNIQUE;

CREATE CONSTRAINT category_id IF NOT EXISTS
FOR (c:Category) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT institution_id IF NOT EXISTS
FOR (i:Institution) REQUIRE i.id IS UNIQUE;

CREATE CONSTRAINT language_id IF NOT EXISTS
FOR (l:Language) REQUIRE l.id IS UNIQUE;

CREATE CONSTRAINT journal_id IF NOT EXISTS
FOR (j:Journal) REQUIRE j.id IS UNIQUE;


// =========================
// 2. IMPORT DOCUMENT
// =========================
LOAD CSV WITH HEADERS FROM 'file:///node_document.csv' AS row

MERGE (d:Document {id: row.id})
SET d.title = row.title,
    d.alternative_title = row.alternative_title,
    d.type = toLower(row.type),   // ✅ FIX QUAN TRỌNG
    d.year = CASE WHEN row.year <> "" THEN toInteger(row.year) ELSE NULL END,
    d.pages = row.pages,
    d.image_url = row.image_url,
    d.file_url = row.file_url,
    d.abstract = row.abstract;

// Gán label theo type (CHUẨN)
MATCH (d:Document)
FOREACH (_ IN CASE WHEN d.type = "book" THEN [1] ELSE [] END | SET d:Book)
FOREACH (_ IN CASE WHEN d.type = "article" THEN [1] ELSE [] END | SET d:Article)
FOREACH (_ IN CASE WHEN d.type = "thesis" THEN [1] ELSE [] END | SET d:Thesis);


// =========================
// 3. IMPORT AUTHOR
// =========================
LOAD CSV WITH HEADERS FROM 'file:///node_author.csv' AS row
MERGE (a:Author {id: row.id})
SET a.name = row.name;


// =========================
// 4. IMPORT SUBJECT
// =========================
LOAD CSV WITH HEADERS FROM 'file:///node_subject.csv' AS row
MERGE (s:Subject {id: row.id})
SET s.name = row.name;


// =========================
// 5. IMPORT KEYWORD
// =========================
LOAD CSV WITH HEADERS FROM 'file:///node_keyword.csv' AS row
MERGE (k:Keyword {id: row.id})
SET k.name = row.name;


// =========================
// 6. IMPORT CATEGORY
// =========================
LOAD CSV WITH HEADERS FROM 'file:///node_category.csv' AS row
MERGE (c:Category {id: row.id})
SET c.name = row.name;


// =========================
// 7. IMPORT INSTITUTION
// =========================
LOAD CSV WITH HEADERS FROM 'file:///node_institution.csv' AS row
MERGE (i:Institution {id: row.id})
SET i.name = row.name,
    i.type = row.type;


// =========================
// 8. IMPORT LANGUAGE
// =========================
LOAD CSV WITH HEADERS FROM 'file:///node_language.csv' AS row
MERGE (l:Language {id: row.id})
SET l.name = row.name;


// =========================
// 9. IMPORT JOURNAL
// =========================
LOAD CSV WITH HEADERS FROM 'file:///node_journal.csv' AS row
MERGE (j:Journal {id: row.id})
SET j.name = row.name;


// =========================
// 10. RELATIONSHIPS
// =========================

// Document - Author
LOAD CSV WITH HEADERS FROM 'file:///rel_document_author.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (a:Author {id: row.author_id})
MERGE (d)-[:HAS_AUTHOR {role: row.role}]->(a);


// Document - Subject
LOAD CSV WITH HEADERS FROM 'file:///rel_document_subject.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (s:Subject {id: row.subject_id})
MERGE (d)-[:HAS_SUBJECT]->(s);


// Document - Keyword
LOAD CSV WITH HEADERS FROM 'file:///rel_document_keyword.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (k:Keyword {id: row.keyword_id})
MERGE (d)-[:HAS_KEYWORD]->(k);


// Document - Category
LOAD CSV WITH HEADERS FROM 'file:///rel_document_category.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (c:Category {id: row.category_id})
MERGE (d)-[:HAS_CATEGORY]->(c);


// Document - Institution (Publisher)
LOAD CSV WITH HEADERS FROM 'file:///rel_document_institution.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (i:Institution {id: row.institution_id})
MERGE (d)-[:PUBLISHED_BY]->(i);


// Document - Institution (Submitted Thesis)
LOAD CSV WITH HEADERS FROM 'file:///rel_document_submitted.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (i:Institution {id: row.institution_id})
MERGE (d)-[:SUBMITTED_TO]->(i);


// Document - Language
LOAD CSV WITH HEADERS FROM 'file:///rel_document_language.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (l:Language {id: row.language_id})
MERGE (d)-[:IN_LANGUAGE]->(l);


// Document - Journal
LOAD CSV WITH HEADERS FROM 'file:///rel_document_journal.csv' AS row
MATCH (d:Document {id: row.doc_id})
MATCH (j:Journal {id: row.journal_id})
MERGE (d)-[:PUBLISHED_IN]->(j);



/* =======================
USER
======================= */
CREATE CONSTRAINT user_email_unique IF NOT EXISTS
FOR (u:User)
REQUIRE u.email IS UNIQUE;

CREATE (u:User {
id: "user_admin_001",
username: "admin",
email: "admin@gmail.com",
password: "123456",
role: "admin",
status: "active",
created_at: datetime()
});

// =========================
// 12. INDEX FULLTEXT (SEARCH)
// =========================
CALL db.index.fulltext.createNodeIndex(
    "documentSearchIndex",
    ["Document"],
    ["title", "abstract"]
);
CREATE FULLTEXT INDEX documentSearchIndex
FOR (n:Document)
ON EACH [n.title, n.abstract]