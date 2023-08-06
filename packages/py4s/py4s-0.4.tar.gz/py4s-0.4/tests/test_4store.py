from py4s import FourStore
try:
	from rdflib.term import URIRef, Literal
	from rdflib.namespace import RDF
	from rdflib.graph import Graph
except ImportError:
	from rdflib import URIRef, RDF, RDFS, Literal
	from rdflib.Graph import Graph

TEST_GRAPH = "http://example.org/"
store = FourStore("py4s_test")
store.connect()

class TestClass:
	def test_00_purge(self):
		cursor = store.cursor()
		cursor.delete_model(all=True)
		assert not cursor.execute("ASK WHERE { ?s ?p ?o }")
	def test_01_no_query(self):
		cursor = store.cursor()
	def test_10_add_graph(self):
		g = Graph(identifier=TEST_GRAPH)
		g.add((URIRef("http://irl.styx.org/"), RDFS.label, Literal("Idiosyntactix Research Laboratiries")))
		g.add((URIRef("http://www.okfn.org/"), RDFS.label, Literal("Open Knowledge Foundation")))
		cursor = store.cursor()
		cursor.add_model(g)
		graphs = list(map(lambda x: x[0], cursor.execute("SELECT DISTINCT ?g WHERE { graph ?g { ?s ?p ?o } } ORDER BY ?g")))
		assert graphs == [URIRef(TEST_GRAPH)]
	def test_11_add_triple(self):
		cursor = store.cursor()
		s = (
			URIRef("http://irl.styx.org/foo"),
			RDF.type,
			URIRef("http://irl.styx.org/Thing")
		)
		cursor.add(s, TEST_GRAPH)
		for count, in cursor.execute("SELECT DISTINCT COUNT(?s) AS c WHERE { graph <%s> { ?s ?p ?o } }" % TEST_GRAPH): pass
		assert count == 3
	def test_99_delete_graph(self):
		cursor = store.cursor()
		cursor.delete_model(TEST_GRAPH)
		graphs = list(map(lambda x: x[0], cursor.execute("SELECT DISTINCT ?g WHERE { graph ?g { ?s ?p ?o } } ORDER BY ?g")))
		assert graphs == []

if __name__ == '__main__':
	t = TestClass()
	t.test_add_triple()
	t.test_add_triple()
	print "-----------------------------"

