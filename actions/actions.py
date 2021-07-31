# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet,EventType,AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
import zomatopy
import json

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ValidateRestaurantForm(Action):
    def name(self) -> Text:
        return "user_details_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        required_slots = ["name", "number"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]

class ActionSubmit(Action):
    def name(self) -> Text:
        return "action_submit"

    def run(
        self,
        dispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_details_thanks",
                                 Name=tracker.get_slot("name"),
                                 Mobile_number=tracker.get_slot("number"))


# class ActionHelloWorld(Action):

#     def name(self) -> Text:
#         return "action_hello_world"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         dispatcher.utter_message(text="Hello World!")

#         return []

class ResetForm(Action):
    def name(self) -> Text:
        return "reset_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        

        return [AllSlotsReset()]

class RestaurantForm(Action):
    def name(self) -> Text:
        return "resturant_details_form"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        required_slots = ["location", "cuisine","price"]

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]

        # All slots are filled.
        return [SlotSet("requested_slot", None)]


class ActionSearchRestaurants(Action):
    def name(self):
        return 'action_search_restaurants'
        
    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        required_slots = ["location", "cuisine","price"]   

        for slot_name in required_slots:
            if tracker.slots.get(slot_name) is None:
                # The slot is not filled yet. Request the user to fill this slot next.
                return [SlotSet("requested_slot", slot_name)]   
        count = 0
        config={ "user_key":"58bfb0a49fb349006fc871842b463a62"} #Get your key from zomato api
        zomato = zomatopy.initialize_app(config)
        loc = tracker.get_slot('location')
        cuisine = tracker.get_slot('cuisine')
        price = tracker.get_slot('price')
        location_detail=zomato.get_location(loc, 1)
        d1 = json.loads(location_detail)
        lat=d1["location_suggestions"][0]["latitude"]
        lon=d1["location_suggestions"][0]["longitude"]
        cuisines_dict={'chinese':25,'italian':55,'north indian':50,'south indian':85,'american':1,'mexican':73}
        price_dict = {'low':1,'medium':2,'high':3}
        results=zomato.restaurant_search("", lat, lon, str(cuisines_dict.get(cuisine)), 50000)
        d = json.loads(results)
        response="Showing you top rated restaurants:"+"\n"
        if d['results_found'] == 0:
            response= "No restaurant found for your criteria"
            dispatcher.utter_message(response)
        else:           
            for restaurant in sorted(d['restaurants'], key=lambda x: x['restaurant']['user_rating']['aggregate_rating'], reverse=True): 
                #Getting Top 10 restaurants for chatbot response
                if((price_dict.get(price) == 1) and (restaurant['restaurant']['average_cost_for_two'] < 300) and (count < 10)):
                    response=response+str(count+1)+". "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+ " has been rated "+ restaurant['restaurant']['user_rating']['aggregate_rating']+""
                    response=response+". And the average price for two people here is: "+ str(restaurant['restaurant']['average_cost_for_two'])+"Rs\n"
                    count = count + 1
                elif((price_dict.get(price) == 2) and (restaurant['restaurant']['average_cost_for_two'] >= 300) and (restaurant['restaurant']['average_cost_for_two'] <= 700) and (count < 10)):
                    response=response+str(count+1)+". "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+ " has been rated "+ restaurant['restaurant']['user_rating']['aggregate_rating']+""
                    response=response+". And the average price for two people here is: "+ str(restaurant['restaurant']['average_cost_for_two'])+"Rs\n"
                    count = count + 1                        
                elif((price_dict.get(price) == 3) and (restaurant['restaurant']['average_cost_for_two'] > 700) and (count < 10)):
                    response=response+str(count+1)+". "+ restaurant['restaurant']['name']+ " in "+ restaurant['restaurant']['location']['address']+ " has been rated "+ restaurant['restaurant']['user_rating']['aggregate_rating']+""
                    response=response+". And the average price for two people here is: "+ str(restaurant['restaurant']['average_cost_for_two'])+"Rs\n"
                    count = count + 1         
                if(count==5):
                    dispatcher.utter_message(response)
        if(count<5 and count>0):
            dispatcher.utter_message(response)
        if(count==0):
            response = "Sorry, No results found for your criteria. Would you like to search for some other restaurants?"
            dispatcher.utter_message(response)
        return [SlotSet('emailbody',response)]

        
class ActionSendEmail(Action):

    def name(self):
        return 'action_sendemail'

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        # required_slots = ["email", "emailbody"] 
        # for slot_name in required_slots:
        #     if tracker.slots.get(slot_name) is None:
        #         # The slot is not filled yet. Request the user to fill this slot next.
        #         return [SlotSet("requested_slot", slot_name)]
        from_user = 'foodierasabot@gmail.com' # create your gmail id and paste here
        to_user = tracker.get_slot('email')
        password = 'aspire1d257' # create your gmail id and paste here
        server = smtplib.SMTP('smtp.gmail.com',587)
        server.starttls()
        server.login(from_user, password)
        subject = 'Foodie''s - Top Restaurants for you'
        msg = MIMEMultipart()
        msg['From'] = from_user
        msg['TO'] = to_user
        msg['Subject'] = subject
        body = tracker.get_slot('emailbody')
        body_header = '''Hi User, \n \n'''
        body_footer = '''\n\n Thanks & Regards \n Team: Foodie's \n For more information reply on same mail. Our Team will connect with you soon.'''
        body = body_header+body+body_footer
        msg.attach(MIMEText(body,'plain'))
        text = msg.as_string()
        server.sendmail(from_user,to_user,text)
        server.close()
        
class ActionCheckLocation(Action):

    def name(self):
        return 'action_chklocation'

    def run(self, dispatcher, tracker, domain):
        if tracker.slots.get("location") is None:
            # The slot is not filled yet. Request the user to fill this slot next.
            return [SlotSet("requested_slot", "location")]
        loc = tracker.get_slot('location')
        
        cities=['Agra', 'Ajmer', 'Aligarh', 'Amravati', 'Amritsar', 'Asansol', 'Aurangabad', 'Bareilly', 'Belgaum', 'Bhavnagar', 'Bhiwandi', 'Bhopal', 'Bhubaneswar', 'Bikaner', 'Bilaspur', 'BokaroSteelCity', 'Chandigarh', 'Coimbatore', 'Cuttack', 'Dehradun', 'Dhanbad', 'Bhilai', 'Durgapur', 'Dindigul', 'Erode', 'Faridabad', 'Firozabad', 'Ghaziabad', 'Gorakhpur', 'Gulbarga', 'Guntur', 'Gwalior', 'Gurgaon', 'Guwahati', 'Hamirpur', 'Hubli–Dharwad', 'Indore', 'Jabalpur', 'Jaipur', 'Jalandhar', 'Jammu', 'Jamnagar', 'Jamshedpur', 'Jhansi', 'Jodhpur', 'Kakinada', 'Kannur', 'Kanpur', 'Karnal', 'Kochi', 'Kolhapur', 'Kollam', 'Kozhikode', 'Kurnool', 'Ludhiana', 'Lucknow', 'Madurai', 'Malappuram', 'Mathura', 'Mangalore', 'Meerut', 'Moradabad', 'Mysore', 'Nagpur', 'Nanded', 'Nashik', 'Nellore', 'Noida', 'Patna', 'Pondicherry', 'Purulia', 'Prayagraj', 'Raipur', 'Rajkot', 'Rajahmundry', 'Ranchi', 'Rourkela', 'Salem', 'Sangli', 'Shimla', 'Siliguri', 'Solapur', 'Srinagar', 'Surat', 'Thanjavur', 'Thiruvananthapuram', 'Thrissur', 'Tiruchirappalli', 'Tirunelveli', 'Ujjain', 'Bijapur', 'Vadodara', 'Varanasi', 'Vasai-VirarCity', 'Vijayawada', 'Visakhapatnam', 'Vellore', 'Warangal', 'Ahmedabad', 'Bengalore', 'Chennai', 'Delhi', 'Hyderabad', 'Kolkata', 'Mumbai', 'Pune']


        
        cities_lower=[x.lower() for x in cities]
        
        if loc.lower() not in cities_lower:
            dispatcher.utter_message("Sorry, we don’t operate in this city. Can you please specify some other location")
            return [SlotSet("location", None)]
        return 