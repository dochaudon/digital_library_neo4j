from database.neo4j_connection import neo4j_conn


# =========================
# GET GRAPH DATA (UNIFIED)
# =========================
def get_graph_data(document_id):

    if not document_id:
        return {"nodes": [], "edges": []}

    query = """
    MATCH (d {id: $id})

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (d)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (d)-[:PUBLISHED_BY]->(p:Publisher)
    OPTIONAL MATCH (d)-[:OWNED_BY]->(u:University)
    OPTIONAL MATCH (d)-[:PUBLISHED_IN]->(j:Journal)
    OPTIONAL MATCH (d)-[:HAS_CATEGORY]->(c:Category)
    OPTIONAL MATCH (d)-[:IN_LANGUAGE]->(l:Language)
    OPTIONAL MATCH (d)-[:RELATED_TO]-(rd)

    RETURN
        d,
        labels(d) AS labels,
        collect(DISTINCT a) AS authors,
        collect(DISTINCT s) AS subjects,
        collect(DISTINCT k) AS keywords,
        collect(DISTINCT p) AS publishers,
        collect(DISTINCT u) AS universities,
        collect(DISTINCT j) AS journals,
        collect(DISTINCT c) AS categories,
        collect(DISTINCT l) AS languages,
        collect(DISTINCT {node: rd, labels: labels(rd)}) AS related
    """

    result = neo4j_conn.query(query, {"id": document_id})

    if not result:
        return {"nodes": [], "edges": []}

    record = result[0]

    nodes = []
    edges = []
    node_ids = set()

    d = record.get("d") or {}
    labels = record.get("labels") or []

    # =========================
    # DETECT DOCUMENT TYPE
    # =========================
    doc_group = "book"

    if "Article" in labels:
        doc_group = "article"
    elif "Thesis" in labels:
        doc_group = "thesis"

    doc_id = d.get("id")
    doc_title = d.get("title") or "Unknown"

    # =========================
    # ADD DOCUMENT NODE
    # =========================
    nodes.append({
        "id": doc_id,
        "label": doc_title,
        "group": doc_group
    })

    node_ids.add(doc_id)

    # =========================
    # HELPER FUNCTION (FIXED)
    # =========================
    def add_nodes_and_edges(items, group, rel_type):
        if not items:
            return

        for item in items:
            if not item:
                continue

            name = item.get("name") or item.get("title") or "Unknown"

            # 🔥 FIX DUPLICATE NODE
            node_id = item.get("id") or f"{group}_{name}"

            if node_id not in node_ids:
                nodes.append({
                    "id": node_id,
                    "label": name,
                    "group": group
                })
                node_ids.add(node_id)

            edges.append({
                "from": doc_id,
                "to": node_id,
                "label": rel_type
            })

    # =========================
    # ADD RELATIONS (FIXED)
    # =========================
    add_nodes_and_edges(record.get("authors"), "author", "HAS_AUTHOR")
    add_nodes_and_edges(record.get("subjects"), "subject", "HAS_SUBJECT")
    add_nodes_and_edges(record.get("keywords"), "keyword", "HAS_KEYWORD")
    add_nodes_and_edges(record.get("publishers"), "publisher", "PUBLISHED_BY")
    add_nodes_and_edges(record.get("universities"), "university", "OWNED_BY")  # 🔥 FIX
    add_nodes_and_edges(record.get("journals"), "journal", "PUBLISHED_IN")
    add_nodes_and_edges(record.get("categories"), "category", "HAS_CATEGORY")
    add_nodes_and_edges(record.get("languages"), "language", "IN_LANGUAGE")

    # Related Documents
    related_items = record.get("related") or []
    for item in related_items:
        if not item:
            continue
        node = item.get("node")
        if not node:
            continue
        
        node_id = node.get("id")
        if not node_id:
            continue
            
        node_labels = item.get("labels") or []
        doc_group = "book"
        if "Article" in node_labels:
            doc_group = "article"
        elif "Thesis" in node_labels:
            doc_group = "thesis"
            
        name = node.get("title") or "Unknown"
        
        if node_id not in node_ids:
            nodes.append({
                "id": node_id,
                "label": name,
                "group": doc_group
            })
            node_ids.add(node_id)
            
        edges.append({
            "from": doc_id,
            "to": node_id,
            "label": "RELATED_TO"
        })

    return {
        "nodes": nodes,
        "edges": edges,
        "center_id": doc_id
    }


# =========================
# WRAPPER (GIỮ CHUẨN SERVICE)
# =========================
def get_document_graph_service(document_id):
    return get_graph_data(document_id)


def get_graph_auto(document_id):
    return get_graph_data(document_id)

# =========================
# SUBJECT GRAPH (ADMIN)
# =========================
def get_all_subjects_graph():
    query = """
    MATCH (s:Subject)
    OPTIONAL MATCH (s)-[r:RELATED_TO]-(s2:Subject)
    RETURN 
        s.id AS s_id, s.name AS s_name,
        s2.id AS s2_id, s2.name AS s2_name,
        type(r) AS rel_type
    """
    result = neo4j_conn.query(query)
    
    nodes_dict = {}
    edges = []
    
    # Track node degrees to find isolated nodes
    degrees = {}
    
    BLUE_BG = "#3b82f6"
    BLUE_BORDER = "#1d4ed8"
    BLACK_TEXT = "#000000"

    for record in result:
        s_id = record.get('s_id')
        s2_id = record.get('s2_id')
        
        # Initialize degree
        if s_id and s_id not in degrees:
            degrees[s_id] = 0
            
        if s2_id:
            degrees[s_id] += 1
            if s2_id not in degrees:
                degrees[s2_id] = 1
            else:
                degrees[s2_id] += 1
                
        if s_id and s_id not in nodes_dict:
            nodes_dict[s_id] = {
                'id': s_id,
                'label': record.get('s_name') or 'Unknown',
                'color': {
                    'background': BLUE_BG,
                    'border': BLUE_BORDER,
                    'highlight': { 'background': BLUE_BG, 'border': '#1e293b' }
                },
                'font': { 'color': BLACK_TEXT, 'size': 12, 'face': 'Inter, sans-serif' }
            }
            
        if s2_id:
            if s2_id not in nodes_dict:
                nodes_dict[s2_id] = {
                    'id': s2_id,
                    'label': record.get('s2_name') or 'Unknown',
                    'color': {
                        'background': BLUE_BG,
                        'border': BLUE_BORDER,
                        'highlight': { 'background': BLUE_BG, 'border': '#1e293b' }
                    },
                    'font': { 'color': BLACK_TEXT, 'size': 12, 'face': 'Inter, sans-serif' }
                }
            
            # Avoid duplicate edges
            edge_exists = False
            for e in edges:
                if (e['from'] == s_id and e['to'] == s2_id) or (e['from'] == s2_id and e['to'] == s_id):
                    edge_exists = True
                    break
            
            if not edge_exists:
                edges.append({
                    'from': s_id,
                    'to': s2_id,
                    'label': 'RELATED_TO'
                })

    # Connected Components Clustering
    import math
    adj = {n: [] for n in nodes_dict.keys()}
    for e in edges:
        adj[e['from']].append(e['to'])
        adj[e['to']].append(e['from'])

    visited = set()
    components = []
    
    for n in nodes_dict.keys():
        if n not in visited and degrees.get(n, 0) > 0:
            comp = []
            q = [n]
            visited.add(n)
            while q:
                curr = q.pop(0)
                comp.append(curr)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        q.append(neighbor)
            components.append(comp)

    # Place each connected component in a grid (5 clusters per row)
    COLS = 5
    SPACING_X = 800
    SPACING_Y = 800
    num_rows = math.ceil(len(components) / COLS) if components else 1
    
    for i, comp in enumerate(components):
        row = i // COLS
        col = i % COLS
        
        # Center the grid around (0,0)
        cx = (col - (COLS - 1) / 2) * SPACING_X
        cy = (row - (num_rows - 1) / 2) * SPACING_Y
        
        anchor_id = f"anchor_{i}"
        nodes_dict[anchor_id] = {
            'id': anchor_id,
            'shape': 'dot',
            'size': 1,
            'fixed': True,
            'x': cx,
            'y': cy,
            'color': 'rgba(0,0,0,0)', # Invisible
            'font': {'size': 0},
            'mass': 10
        }
        for n_id in comp:
            edges.append({
                'from': n_id,
                'to': anchor_id,
                'color': 'rgba(0,0,0,0)',
                'physics': True,
                'length': 150
            })

    # Arrange isolated nodes (degree == 0) in a separate area below the clusters
    isolated_x_start = - ((COLS - 1) / 2) * SPACING_X
    isolated_y_start = ((num_rows - 1) / 2) * SPACING_Y + 1000
    iso_cols = 10
    iso_spacing = 150
    count = 0
    
    for n_id, node in nodes_dict.items():
        if degrees.get(n_id, 0) == 0 and not str(n_id).startswith("anchor_"):
            row = count // iso_cols
            col = count % iso_cols
            node['x'] = isolated_x_start + col * iso_spacing
            node['y'] = isolated_y_start + row * iso_spacing
            node['physics'] = False  # Keep them fixed in the grid so they don't get pulled into the center
            count += 1
            
    return {
        'nodes': list(nodes_dict.values()),
        'edges': edges
    }

def relate_subjects_service(source_id, target_id):
    if not source_id or not target_id or source_id == target_id:
        return False
        
    query = """
    MATCH (s1:Subject {id: $source_id}), (s2:Subject {id: $target_id})
    MERGE (s1)-[r:RELATED_TO]->(s2)
    RETURN r
    """
    result = neo4j_conn.query(query, {'source_id': source_id, 'target_id': target_id})
    return len(result) > 0

def unrelate_subjects_service(source_id, target_id):
    if not source_id or not target_id:
        return False
        
    query = """
    MATCH (s1:Subject {id: $source_id})-[r:RELATED_TO]-(s2:Subject {id: $target_id})
    DELETE r
    """
    neo4j_conn.query(query, {'source_id': source_id, 'target_id': target_id})
    return True