/* =======================
CLEAR DATABASE
======================= */
MATCH (n)
DETACH DELETE n;


/* =======================
CONSTRAINTS
======================= */

CREATE CONSTRAINT document_id IF NOT EXISTS
FOR (d:Document)
REQUIRE d.id IS UNIQUE;

CREATE CONSTRAINT author_id IF NOT EXISTS
FOR (a:Author)
REQUIRE a.id IS UNIQUE;

CREATE CONSTRAINT subject_id IF NOT EXISTS
FOR (s:Subject)
REQUIRE s.id IS UNIQUE;

CREATE CONSTRAINT keyword_id IF NOT EXISTS
FOR (k:Keyword)
REQUIRE k.id IS UNIQUE;

CREATE CONSTRAINT category_id IF NOT EXISTS
FOR (c:Category)
REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT publisher_id IF NOT EXISTS
FOR (p:Publisher)
REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT university_id IF NOT EXISTS
FOR (u:University)
REQUIRE u.id IS UNIQUE;

CREATE CONSTRAINT language_id IF NOT EXISTS
FOR (l:Language)
REQUIRE l.id IS UNIQUE;

CREATE CONSTRAINT journal_id IF NOT EXISTS
FOR (j:Journal)
REQUIRE j.id IS UNIQUE;

CREATE CONSTRAINT user_email_unique IF NOT EXISTS
FOR (u:User)
REQUIRE u.email IS UNIQUE;


/* =======================
IMPORT DOCUMENT
======================= */

LOAD CSV WITH HEADERS FROM 'file:///node_document.csv' AS row

MERGE (d:Document {id: row.id})

SET
    d.title = row.title,
    d.alternative_title = row.alternative_title,
    d.type = toLower(row.type),
    d.year = CASE
        WHEN row.year <> "" THEN toInteger(row.year)
        ELSE NULL
    END,
    d.pages = row.pages,
    d.image_url = row.image_url,
    d.file_url = row.file_url,
    d.abstract = row.abstract;


/* =======================
SET LABEL BY TYPE
======================= */

MATCH (d:Document)

FOREACH (_ IN CASE WHEN d.type = "book" THEN [1] ELSE [] END |
    SET d:Book
)

FOREACH (_ IN CASE WHEN d.type = "article" THEN [1] ELSE [] END |
    SET d:Article
)

FOREACH (_ IN CASE WHEN d.type = "thesis" THEN [1] ELSE [] END |
    SET d:Thesis
);


/* =======================
IMPORT AUTHOR
======================= */

LOAD CSV WITH HEADERS FROM 'file:///node_author.csv' AS row

MERGE (a:Author {id: row.id})

SET
    a.name = row.name;


/* =======================
IMPORT SUBJECT
======================= */

LOAD CSV WITH HEADERS FROM 'file:///node_subject.csv' AS row

MERGE (s:Subject {id: row.id})

SET
    s.name = row.name;


/* =======================
IMPORT KEYWORD
======================= */

LOAD CSV WITH HEADERS FROM 'file:///node_keyword.csv' AS row

MERGE (k:Keyword {id: row.id})

SET
    k.name = row.name;


/* =======================
IMPORT CATEGORY
======================= */

LOAD CSV WITH HEADERS FROM 'file:///node_category.csv' AS row

MERGE (c:Category {id: row.id})

SET
    c.name = row.name;


/* =======================
IMPORT PUBLISHER
======================= */

LOAD CSV WITH HEADERS FROM 'file:///node_publisher.csv' AS row

MERGE (p:Publisher {id: row.id})

SET
    p.name = row.name;


/* =======================
IMPORT UNIVERSITY
======================= */

LOAD CSV WITH HEADERS FROM 'file:///node_university.csv' AS row

MERGE (u:University {id: row.id})

SET
    u.name = row.name;


/* =======================
IMPORT LANGUAGE
======================= */

LOAD CSV WITH HEADERS FROM 'file:///node_language.csv' AS row

MERGE (l:Language {id: row.id})

SET
    l.name = row.name;


/* =======================
IMPORT JOURNAL
======================= */

LOAD CSV WITH HEADERS FROM 'file:///node_journal.csv' AS row

MERGE (j:Journal {id: row.id})

SET
    j.name = row.name;


/* =======================
RELATIONSHIP:
DOCUMENT - AUTHOR
======================= */

LOAD CSV WITH HEADERS FROM 'file:///rel_document_author.csv' AS row

MATCH (d:Document {id: row.doc_id})
MATCH (a:Author {id: row.author_id})

MERGE (d)-[:HAS_AUTHOR {
    role: row.role
}]->(a);


/* =======================
RELATIONSHIP:
DOCUMENT - SUBJECT
======================= */

LOAD CSV WITH HEADERS FROM 'file:///rel_document_subject.csv' AS row

MATCH (d:Document {id: row.doc_id})
MATCH (s:Subject {id: row.subject_id})

MERGE (d)-[:HAS_SUBJECT]->(s);


/* =======================
RELATIONSHIP:
DOCUMENT - KEYWORD
======================= */

LOAD CSV WITH HEADERS FROM 'file:///rel_document_keyword.csv' AS row

MATCH (d:Document {id: row.doc_id})
MATCH (k:Keyword {id: row.keyword_id})

MERGE (d)-[:HAS_KEYWORD]->(k);


/* =======================
RELATIONSHIP:
DOCUMENT - CATEGORY
======================= */

LOAD CSV WITH HEADERS FROM 'file:///rel_document_category.csv' AS row

MATCH (d:Document {id: row.doc_id})
MATCH (c:Category {id: row.category_id})

MERGE (d)-[:HAS_CATEGORY]->(c);


/* =======================
RELATIONSHIP:
DOCUMENT - PUBLISHER
======================= */

LOAD CSV WITH HEADERS FROM 'file:///rel_document_publisher.csv' AS row

MATCH (d:Document {id: row.doc_id})
MATCH (p:Publisher {id: row.publisher_id})

MERGE (d)-[:PUBLISHED_BY]->(p);


/* =======================
RELATIONSHIP:
DOCUMENT - UNIVERSITY
======================= */

LOAD CSV WITH HEADERS FROM 'file:///rel_document_university.csv' AS row

MATCH (d:Document {id: row.doc_id})
MATCH (u:University {id: row.university_id})

MERGE (d)-[:OWNED_BY]->(u);


/* =======================
RELATIONSHIP:
DOCUMENT - LANGUAGE
======================= */

LOAD CSV WITH HEADERS FROM 'file:///rel_document_language.csv' AS row

MATCH (d:Document {id: row.doc_id})
MATCH (l:Language {id: row.language_id})

MERGE (d)-[:IN_LANGUAGE]->(l);


/* =======================
RELATIONSHIP:
DOCUMENT - JOURNAL
======================= */

LOAD CSV WITH HEADERS FROM 'file:///rel_document_journal.csv' AS row

MATCH (d:Document {id: row.doc_id})
MATCH (j:Journal {id: row.journal_id})

MERGE (d)-[:PUBLISHED_IN]->(j);


/* =======================
RELATIONSHIP:
SUBJECT - SUBJECT
======================= */

LOAD CSV WITH HEADERS FROM 'file:///rel_subject_related.csv' AS row

MATCH (s1:Subject {id: row.subject1_id})
MATCH (s2:Subject {id: row.subject2_id})

WHERE s1.id <> s2.id

MERGE (s1)-[:RELATED_TO]->(s2);


/* =======================
RELATIONSHIP:
DOCUMENT - DOCUMENT
======================= */

LOAD CSV WITH HEADERS FROM 'file:///rel_document_related.csv' AS row

MATCH (d1:Document {id: row.doc1_id})
MATCH (d2:Document {id: row.doc2_id})

WHERE d1.id <> d2.id

MERGE (d1)-[:RELATED_TO]->(d2);


/* =======================
FULLTEXT INDEX
======================= */

CREATE FULLTEXT INDEX documentFulltextIndex IF NOT EXISTS
FOR (n:Book|Article|Thesis)
ON EACH [n.title, n.abstract];

