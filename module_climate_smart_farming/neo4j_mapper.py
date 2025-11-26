try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

class StrategyNeo4jMapper:
    def __init__(self, uri, user, password):
        if GraphDatabase is None:
            raise ImportError('neo4j driver not installed')
        self.driver = GraphDatabase.driver(uri, auth=(user,password))
    def close(self):
        if self.driver: self.driver.close()
    def map(self, records):
        with self.driver.session() as session:
            for r in records:
                session.run("MERGE (l:Location {name:$loc})", loc=r.get('location','UNKNOWN'))
                for s in r.get('strategies', []):
                    session.run("MERGE (st:Strategy {id:$id, practice:$prac})", id=s['strategy_id'], prac=s['practice'])
                    session.run("MATCH (l:Location {name:$loc}),(st:Strategy {id:$id}) MERGE (st)-[:APPLIES_IN]->(l)", loc=r.get('location','UNKNOWN'), id=s['strategy_id'])
