import pandas as pd
from neo4j import GraphDatabase

uri = "bolt://localhost:7687"  # or wherever your Neo4j is running
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))  # replace with your username and password


def add_stations(tx, stations_data):
    for index, row in stations_data.iterrows():
        tx.run("CREATE (:Station {station_id: $station_id, station_type: $station_type, station_capacity: $station_capacity})", 
               station_id=row['station_id'], station_type=row['station_type'], station_capacity=row['station_capacity'])


def add_contracts(tx, contracts_data):
    for index, row in contracts_data.iterrows():
        tx.run("""
        MATCH (s:Station {station_id: $station_id})
        CREATE (c:Contract {contract_id: $contract_id, contract_value: $contract_value, contract_type: $contract_type}),
        (s)-[:HAS_CONTRACT]->(c)
        """, station_id=row['station_id'], contract_id=row['contract_id'], contract_value=row['contract_value'], contract_type=row['contract_type'])


def get_stations_and_contracts(tx):
    result = tx.run("""
    MATCH (s:Station)-[:HAS_CONTRACT]->(c:Contract)
    RETURN s.station_id AS station_id, s.station_type AS station_type, s.station_capacity AS station_capacity, 
           collect(c.contract_id) AS contracts, collect(c.contract_value) AS contract_values, collect(c.contract_type) AS contract_types
    """)

    for record in result:
        print(f"Station ID: {record['station_id']}, Station Type: {record['station_type']}, "
              f"Station Capacity: {record['station_capacity']} MW, Contracts: {record['contracts']}, "
              f"Contract Values: {record['contract_values']}, Contract Types: {record['contract_types']}")

stations_data = {
    'station_id': ['S1', 'S2', 'S3', 'S4'],
    'station_type': ['Power Station', 'Substation', 'Power Station', 'Substation'],
    'station_capacity': [500, 200, 600, 150]  # In megawatts (MW)
}
df_stations = pd.DataFrame(stations_data)

# Create a DataFrame for contracts
contracts_data = {
    'contract_id': ['C1', 'C2', 'C3', 'C4', 'C5', 'C6'],
    'station_id': ['S1', 'S1', 'S2', 'S3', 'S4', 'S4'],
    'contract_value': [10000, 12000, 8000, 15000, 7000, 6000],  # In dollars
    'contract_type': ['Maintenance', 'Upgrade', 'Maintenance', 'Upgrade', 'Maintenance', 'Upgrade']
}
df_contracts = pd.DataFrame(contracts_data)


with driver.session() as session:
    session.read_transaction(get_stations_and_contracts)

driver.close()


