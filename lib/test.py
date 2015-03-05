from flowdata import FlowData
from flow_tsne import tsne
fd = FlowData('2-Enriched.fcs')


fd = tsne([fd])
