import requests
from celery import shared_task 
from product.models import Order,Booking,Route,DataReport
from hubs.models import Hub
import logging
from product.utilities import find_nearby_hubs,geocode_location,calculate_distance
import networkx as nx
import json 
from hubs.serializer import HubSerializer
from datetime import datetime, timedelta
from django.db.models import Q

import csv
from io import StringIO
from django.core.mail import EmailMessage
from django.core.files import File


logger = logging.getLogger(__name__)

@shared_task
def assign_route(order):
    hotspots=Hub.objects.filter(is_hotspot=True)
    from_hub=Hub.objects.filter(pk=order["booking"]["from_hub"])
    to_hub=Hub.objects.filter(pk=order["booking"]["to_hub"])
    if from_hub  not  in  hotspots:
        hotspots = hotspots | from_hub
    if to_hub  not  in  hotspots:
        hotspots = hotspots | to_hub
    G = nx.Graph()
    access_token = "pk.eyJ1IjoibmloYWxyb3NoYW4iLCJhIjoiY2xsZGIyNW5wMGFxMjN1cXkwZm5reHlrdSJ9.l2JGuFbgbkgYWJl4vDOUig"
    params = {
        "access_token": access_token,
    }
    for hotspot in hotspots:
        G.add_node(hotspot)
    
    
    
    for i in range(len(hotspots)):
        for j in range(len(hotspots)):
            if i != j:
                coordinates_str = f"{hotspots[i].location[0]},{hotspots[i].location[1]};{hotspots[j].location[0]},{hotspots[j].location[1]}"
                distance_api_url = "https://api.mapbox.com/directions/v5/mapbox/driving-traffic/{coordinates}".format(coordinates=coordinates_str)

                try:
                    response = requests.get(distance_api_url, params=params)
                    if response.status_code == 200:
                        data = response.json()
                        if "routes" in data and data["routes"]:
                            routes = data["routes"][0]
                            distance = routes["distance"]
                            G.add_edge(hotspots[i], hotspots[j], weight=distance)
                except Exception as e:
                    print("Error:", e)
            else:
                continue
    designated_hotspot = to_hub.first()  # Get the first Hub object from to_hub
    starting_hotspot = from_hub.first()  # Get the first Hub object from from_hub
    shortest_path = nx.shortest_path(G, source=starting_hotspot, target=designated_hotspot, weight='weight')
    shortest_path_data = HubSerializer(shortest_path, many=True).data
    # Serialize the shortest_path to JSON
    path_json = json.dumps(shortest_path_data, ensure_ascii=False)
    route_order = Order.objects.get(pk=order["id"])
    path = Route.objects.create(route=path_json, order=route_order, is_routed=True)
    path.save()

@shared_task
def Booking_delete():
    thirty_minutes_ago = datetime.now() - timedelta(minutes=30)
    booking=Booking.objects.filter(order__isnull=True,created_at__lt=thirty_minutes_ago)
    booking.delete()
    return

# @shared_task
# def Review():
#     # Get the current date and time
#     current_datetime = datetime.now()

#     # Get the current date as a separate object
#     current_date = current_datetime.date()
#     hubs = Hub.objects.all()
#     data = {}

#     for hub in hubs:
#         collect_pending_orders = Order.objects.filter(
#             booking__hbd__gte=current_date,
#             asign=False,
#             collected=False,
#             status="pending",
#             booking__from_hub=hub
#         )
#         delivery_pending_orders = Order.objects.filter(
#             booking__cpd__gte=current_date,
#             asign=False,
#             status="in_progress",
#             booking__to_hub=hub
#         )

#         # Create a dictionary entry for the hub
#         hub_data = {
#             "hub": hub,
#             "collect_pending_orders": collect_pending_orders,
#             "delivery_pending_orders": delivery_pending_orders
#         }

#         # Add hub data to the data dictionary
#         data[hub.id] = hub_data

#     # Add blocked_delivery to the data dictionary
#     blocked_delivery = Order.objects.filter(booking__cpd__lt=current_date).filter(~Q(status="completed") & ~Q(status="return"))
#     data["blocked_delivery"] = blocked_delivery

#     # Step 1: Generate a CSV file
#     csv_data = []
#     order_type_mapping = {
#         'collect_pending_orders': 'Collect Pending',
#         'delivery_pending_orders': 'Delivery Pending',
#         'blocked_delivery': 'Blocked Delivery',
#     }

#     # for order_type, order_list in data.items():
#     #     for hub_id, hub_data in order_list:
#     #         for order in hub_data[order_type]:
#     #             csv_data.append([
#     #                 hub_id,
#     #                 hub_data['hub'].name,
#     #                 order.order_id,
#     #                 order_type_mapping[order_type],
#     #                 # Add more fields as needed
#     #             ])
#     output = StringIO()
#     writer = csv.writer(output)
#     writer.writerow(["Hub ID", "Hub Name", "Collect Pending Orders", "Delivery Pending Orders"])

#     for hub_id, hub_data in data.items():
#         # hub_name = hub_data["hub"].hub_name
#         collect_pending_count = hub_data["collect_pending_orders"].count()
#         delivery_pending_count = hub_data["delivery_pending_orders"].count()
#         writer.writerow([hub_id, collect_pending_count, delivery_pending_count])
#     # Step 2: Save the CSV file to an in-memory StringIO object
#     # output = io.StringIO()
#     # csv_writer = csv.writer(output)
#     # csv_writer.writerow(['Hub ID', 'Hub Name', 'Order ID', 'Order Type',])  # Add headers
#     # csv_writer.writerows(csv_data)

#     # Step 3: Send an email with the CSV file attached
#     subject = 'Data Report'
#     message = 'Please find the attached data report.'
#     from_email = 'homehavenecom@gmail.com'
#     recipient_list = ['nihalroshan55@gmail.com']

#     email = EmailMessage(subject, message, from_email, recipient_list)
#     email.attach('data_report.csv', output.getvalue(), 'text/csv')
#     email.send()

#     # Step 4: Save the CSV file to the database
#     data_report = DataReport(name='Data Report')
#     data_report.csv_file.save('data_report.csv', File(output))
#     data_report.save()

#     return data