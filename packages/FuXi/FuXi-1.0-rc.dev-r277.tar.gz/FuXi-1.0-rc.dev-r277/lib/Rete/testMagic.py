PROGRAM2=\
"""
@prefix ex: <http://doi.acm.org/10.1145/28659.28689#>.
{ ?X ex:flat ?Y } => { ?X ex:sg ?Y }.
{ ?X ex:up ?Z1 . ?Z1 ex:sg ?Z2. ?Z2 ex:flat ?Z3. ?Z3 ex:sg ?Z4. ?Z4 ex:down ?Y } => { ?X ex:sg ?Y }.
"""

PROGRAM1=\
"""
@prefix : <http://example.com#>.
{ ?X par ?Y } => { ?X anc ?Y }
{ ?X par ?Z . ?Z  anc ?Y } => { ?X anc ?Y }
"""

PARTITION_LP_DB_PREDICATES=\
"""
@prefix ex: <http://doi.acm.org/10.1145/16856.16859#>.
ex:a ex:father ex:b.
ex:b ex:parent ex:c.
ex:b ex:grandfather ex:d.
{ ?X ex:father ?Z. ?X ex:parent ?Y } => { ?X ex:grandfather ?Y }.
"""

NON_LINEAR_MS_QUERY=\
"""
PREFIX ex: <http://doi.acm.org/10.1145/28659.28689#>
SELECT * WHERE { ex:john ex:sg ?X }
"""