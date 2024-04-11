G = nx.Graph()

# # Add nodes for hub and end devices
# G.add_node("Hub")
# for device in end_devices:
#     G.add_node(device.device_id)

# # Add edges for connections
# for device in end_devices:
#     G.add_edge("Hub", device.device_id)

# # Visualize the network topology
# pos = nx.spring_layout(G)
# nx.draw_networkx_nodes(G, pos, nodelist=["Hub"], node_color='blue', node_size=3000)
# nx.draw_networkx_nodes(G, pos, nodelist=[device.device_id for device in end_devices], node_color='skyblue', node_size=3000)
# nx.draw_networkx_edges(G, pos, width=2)

# nx.draw_networkx_labels(G, pos, font_size=12, font_family='sans-serif')

# plt.title("Network Topology - Hub with End Devices")
# plt.axis('off')
# plt.show()
