try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None

class CarbonNeo4jMapper:
    def __init__(self, uri, user, password):
        if GraphDatabase is None:
            raise ImportError('neo4j driver not installed')
        self.driver = GraphDatabase.driver(uri, auth=(user,password))
    def close(self):
        if self.driver: self.driver.close()
    def map(self, rows):
        with self.driver.session() as session:
            for r in rows:
                loc = r.get('location','UNKNOWN')
                session.run("MERGE (l:Location {name:$loc})", loc=loc)
                session.run("MERGE (c:CarbonStock {id:$id, baseline:$baseline})", id=r['id'], baseline=r.get('baseline_rate'))
                session.run("MATCH (l:Location {name:$loc}),(c:CarbonStock {id:$id}) MERGE (c)-[:MEASURED_IN]->(l)", loc=loc, id=r['id'])
                for s in r.get('scenarios', []):
                    session.run("MERGE (sc:Scenario {sid:$sid, practice:$prac, est:$est})", sid=f"{r['id']}-{s['practice']}", prac=s['practice'], est=s['estimated_rate'])
                    session.run("MATCH (c:CarbonStock {id:$id}),(sc:Scenario {sid:$sid}) MERGE (sc)-[:IMPROVES]->(c)", id=r['id'], sid=f"{r['id']}-{s['practice']}")
