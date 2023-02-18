import requests
from math import *


class Vehicle:

    def __init__(self, name: str, model: str, year: int, color: str, 
                 price: int, latitude: float, longitude: float, id: int=0):
        self.__id = id
        self.__name = name
        self.__model = model
        self.__year = year
        self.__color = color
        self.__price = price
        self.__latitude = latitude
        self.__longitude = longitude

    def __str__(self):
        return f'<Vehicle: {self.__name} {self.__model} {self.__year} {self.__color} {self.__price}>'

    def __repr__(self):
        return f'<Vehicle: {self.__name} {self.__model} {self.__year} {self.__color} {self.__price}>'

    def get_props(self):
        return dict({'name': self.__name, 'model': self.__model, 'year': self.__year, 'color': self.__color,
                     'price': self.__price, 'latitude': self.__latitude, 'longitude': self.__longitude})

    def get_id(self):
        return self.__id

    @staticmethod
    def create_vehicle_from_dict(vehicle: dict):
        return Vehicle(id=vehicle.get('id', 0), 
                       name=vehicle.get('name', 'unknown'), 
                       model=vehicle.get('model', 'unknown'), 
                       year=vehicle.get('year', 0), 
                       color=vehicle.get('color', 'unknown'), 
                       price=vehicle.get('price', 0), 
                       latitude=vehicle.get('latitude', 0), 
                       longitude=vehicle.get('longitude', 0))


class VehicleManager:

    def __init__(self, url: str):
        self.__url = url

    @staticmethod
    def print_request_failed(request_type: str, status_code: int):
        print(f'Could not fulfill {request_type} request: HTTP code {status_code}')

    @staticmethod
    def calculate_distance(vehicle1: dict, vehicle2: dict):
            EARTH_RADIUS = 6371000
            lon1, lat1, lon2, lat2 = map(radians, [vehicle1.get('longitude', 0), vehicle1.get('latitude', 0),
                                                   vehicle2.get('longitude', 0), vehicle2.get('latitude', 0)])
            distance_lon, distance_lat = lon2 - lon1, lat2 - lat1

            a = sin(distance_lat / 2) ** 2 + sin(distance_lon / 2) ** 2 * cos(lat1) * cos(lat2)
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            distance = EARTH_RADIUS * c
            return distance


    # Get a list of all vehicles 
    def get_vehicles(self):
        r = requests.get(f'{self.__url}/vehicles')

        if r.status_code == 200:
            response_vehicles = r.json()
            vehicles_list = []

            for vehicle in response_vehicles:
                vehicles_list.append(Vehicle.create_vehicle_from_dict(vehicle=vehicle))
            print(vehicles_list)
        else:
            VehicleManager.print_request_failed(request_type='GET', status_code=r.status_code)


    # Get vehicles with certain parameters
    def filter_vehicles(self, params: dict):
        r = requests.get(f'{self.__url}/vehicles')

        if r.status_code == 200:
            response_vehicles = r.json()
            vehicles_list_filtered = []
            for vehicle in response_vehicles:
                ok = True
                for param, value in params.items():
                    if vehicle.get(param) != value:
                        ok = False
                        break
                if ok:
                    vehicles_list_filtered.append(Vehicle.create_vehicle_from_dict(vehicle=vehicle))
            print(vehicles_list_filtered)
        else:
            VehicleManager.print_request_failed(request_type='GET', status_code=r.status_code)


    # Get a vehicle with certain vehicle_id
    def get_vehicle(self, vehicle_id: int):
        r = requests.get(f'{self.__url}/vehicles/{vehicle_id}')

        if r.status_code == 200:
            response_vehicle = r.json()
            vehicle = Vehicle.create_vehicle_from_dict(response_vehicle)
            print(vehicle)
        else:
            VehicleManager.print_request_failed(request_type='GET', status_code=r.status_code)

    
    # Add a new vehicle to the list
    def add_vehicle(self, vehicle: Vehicle):
        r = requests.post(f'{self.__url}/vehicles', data=vehicle.get_props())

        if r.status_code == 201:
            response_created_vehicle = r.json()
            created_vehicle = Vehicle.create_vehicle_from_dict(response_created_vehicle)
            print(created_vehicle)    
        else:
            VehicleManager.print_request_failed(request_type='POST', status_code=r.status_code)


    # Update a certain vehicle
    def update_vehicle(self, vehicle: Vehicle):
        r = requests.put(f'{self.__url}/vehicles/{vehicle.get_id()}', data=vehicle.get_props())

        if r.status_code == 200:
            response_updated_vehicle = r.json()
            updated_vehicle = Vehicle.create_vehicle_from_dict(response_updated_vehicle)
            print(updated_vehicle)
        else:
            VehicleManager.print_request_failed(request_type='PUT', status_code=r.status_code)


    # Delete a vehicle with ceratin id
    def delete_vehicle(self, id: int):
        r = requests.delete(f'{self.__url}/vehicles/{id}')

        if r.status_code == 204:
            print(f'Vehicle with id {id} was deleted successfully')
        else:
            VehicleManager.print_request_failed(request_type='DELETE', status_code=r.status_code)


    # Get distance between two vehicles with id1 and id2
    def get_distance(self, id1: int, id2: int):
        r1 = requests.get(f'{self.__url}/vehicles/{id1}')
        r2 = requests.get(f'{self.__url}/vehicles/{id2}')

        if r1.status_code == 200 and r2.status_code == 200:
            vehicle1, vehicle2 = r1.json(), r2.json()
            distance = VehicleManager.calculate_distance(vehicle1=vehicle1, vehicle2=vehicle2)
            print(distance)

        elif r1.status_code != 200:
            VehicleManager.print_request_failed(request_type='GET', status_code=r1.status_code)
        else:
            VehicleManager.print_request_failed(request_type='GET', status_code=r2.status_code)


    # Get distance between a vehicle with certain id and the closest vehicle
    def get_nearest_vehicle(self, id: int):
        r_vehicle = requests.get(f'{self.__url}/vehicles/{id}')
        r_vehicles_list = requests.get(f'{self.__url}/vehicles')

        if r_vehicle.status_code == 200 and r_vehicles_list.status_code == 200:
            vehicle, vehicles_list = r_vehicle.json(), r_vehicles_list.json()
            closest_distance, closest_id = 1000000000, 0
            
            for vehicle_ in vehicles_list:
                if vehicle.get('id') != vehicle_.get('id'):
                    distance = VehicleManager.calculate_distance(vehicle1=vehicle, vehicle2=vehicle_)
                    if distance < closest_distance:
                        closest_distance, closest_id = distance, vehicle_.get('id')

            r_closest_vehicle = requests.get(f'{self.__url}/vehicles/{closest_id}')
            if r_closest_vehicle.status_code == 200:
                response_closest_vehicle = r_closest_vehicle.json()
                closest_vehicle = Vehicle.create_vehicle_from_dict(vehicle=response_closest_vehicle)
                print(closest_vehicle)
            else:
                VehicleManager.print_request_failed(request_type='GET', status_code=r_closest_vehicle.status_code)
        elif r_vehicle.status_code != 200:
            VehicleManager.print_request_failed(request_type='GET', status_code=r_vehicle.status_code)
        else:
            VehicleManager.print_request_failed(request_type='GET', status_code=r_vehicles_list.status_code)