import spacy
import sys
from neo4j import GraphDatabase

# Load English tokenizer, tagger, parser, NER and word vectors
nlp = spacy.load("en_core_web_sm")

# Process whole documents
text = sys.argv[1]

# Process the text
doc = nlp(text)

# Extract entities
entities = [ent.text for ent in doc.ents]

# Check if text contains station and extract its ID
if 'station' in text and entities:
    station_id = entities[0]
    
    # Now you can use this station_id to query your database:

    # Initialize Neo4j connection
    uri = "bolt://localhost:7687"  # or wherever your Neo4j is running
    driver = GraphDatabase.driver(uri)  # replace with your username and password

    def get_station_contracts(tx, station_id):
        result = tx.run("""
        MATCH (s:Station {station_id: $station_id})-[:HAS_CONTRACT]->(c:Contract)
        RETURN s.station_id AS station_id, collect(c.contract_value) AS contract_values
        """, station_id=station_id)

        for record in result:
            contract_values = ', '.join(map(str, record['contract_values']))
            print(f"The station with ID {record['station_id']} has contracts with the following values: {contract_values}.")

    with driver.session() as session:
        session.execute_read(get_station_contracts, station_id)

    driver.close()
