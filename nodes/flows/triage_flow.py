from nodes.data_ingestion_node import DataIngestionNode
from nodes.triage_node import TriageNode
from nodes.resource_allocation_node import ResourceAllocationNode

class TriageFlow:
    def __init__(self):
        self.data_ingestion_node = DataIngestionNode()
        self.triage_node = TriageNode()
        self.resource_allocation_node = ResourceAllocationNode()

    def run(self, input_data):
        # Step 1: Ingest data
        processed_data = self.data_ingestion_node.process(input_data)
        # Step 2: Assign triage score
        triage_result = self.triage_node.process(processed_data)
        # Step 3: Allocate resources
        allocation_result = self.resource_allocation_node.process(triage_result)
        return allocation_result