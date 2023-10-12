# # import requests
# # # from celery import shared_task
# # from product.models import Order,Booking,Route
# # from hubs.models import Hub
# # import logging
# # from product.utilities import find_nearby_hubs,geocode_location,calculate_distance
# # import networkx as nx
# # import json 
# # from hubs.serializer import HubSerializer
# # import re
# from hubs.models import Hub
# from product.models import Order, Route
# from hubs.serializer import HubSerializer
# import json
# import networkx as nx
# import requests



# def asign_route(order):
#     hotspots=Hub.objects.filter(is_hotspot=True)
#     from_hub=Hub.objects.filter(pk=order["booking"]["from_hub"])
#     to_hub=Hub.objects.filter(pk=order["booking"]["to_hub"])
#     if from_hub  not  in  hotspots:
#         hotspots = hotspots | from_hub
#     if to_hub  not  in  hotspots:
#         hotspots = hotspots | to_hub
#     G = nx.Graph()
#     access_token = "pk.eyJ1IjoibmloYWxyb3NoYW4iLCJhIjoiY2xsZGIyNW5wMGFxMjN1cXkwZm5reHlrdSJ9.l2JGuFbgbkgYWJl4vDOUig"
#     params = {
#         "access_token": access_token,
#     }
#     for hotspot in hotspots:
#         G.add_node(hotspot)
    
    
    
#     for i in range(len(hotspots)):
#         for j in range(len(hotspots)):
#             if i != j:
#                 coordinates_str = f"{hotspots[i].location[0]},{hotspots[i].location[1]};{hotspots[j].location[0]},{hotspots[j].location[1]}"
#                 distance_api_url = "https://api.mapbox.com/directions/v5/mapbox/driving-traffic/{coordinates}".format(coordinates=coordinates_str)

#                 try:
#                     response = requests.get(distance_api_url, params=params)
#                     if response.status_code == 200:
#                         data = response.json()
#                         if "routes" in data and data["routes"]:
#                             routes = data["routes"][0]
#                             distance = routes["distance"]
#                             G.add_edge(hotspots[i], hotspots[j], weight=distance)
#                 except Exception as e:
#                     print("Error:", e)
#             else:
#                 continue
#     designated_hotspot = to_hub.first()  # Get the first Hub object from to_hub
#     starting_hotspot = from_hub.first()  # Get the first Hub object from from_hub
#     shortest_path = nx.shortest_path(G, source=starting_hotspot, target=designated_hotspot, weight='weight')
#     shortest_path_data = HubSerializer(shortest_path, many=True).data
#     # Serialize the shortest_path to JSON
#     path_json = json.dumps(shortest_path_data, ensure_ascii=False)
#     route_order = Order.objects.get(pk=order["id"])
#     path = Route.objects.create(route=path_json, order=route_order, is_routed=True)
#     path.save()