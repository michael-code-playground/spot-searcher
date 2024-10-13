from flask import Flask, render_template, request, session, redirect, url_for
from datetime import datetime
from flask import send_file
from phonenumbers.phonenumberutil import region_code_for_country_code, country_code_for_region
from get_location import *
import googlemaps
import csv
import os

app = Flask(__name__)
app.secret_key = os.getenv('SPOT_SEARCH_KEY')

@app.route("/")
def main():
    gmaps = googlemaps.Client(key=os.getenv('GOOGLE_MAPS_API'))
    location = get_location()
    lat = location[0]
    lng = location[1]
    city = location[2]
    country = location[3]
    
    query = request.args.get("query")
    radius = request.args.get("radius")
    location = {'lat': lat, 'lng': lng}
    radius = 30000  # 30 kilometer, just to test
    

    iso_country_code = country
    phone_country_code = country_code_for_region(iso_country_code)
    phone_country_code = ("+"+str(phone_country_code))
    places_to_display = []
    
    try:
        if query is not None:
        #run the search
            # Find spots within the specified radius
            places_result = gmaps.places_nearby(location=location, radius=radius,keyword=query) 
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') 
            for place in places_result['results']:
                rating = float(place.get('rating'))
                if rating < 4.5:             
                    continue
                
                name = place['name']
                address = place.get('vicinity', 'No address available')
                id = place['place_id']
                
                #print for debugging purposes
                print(place['name'], "-", place.get('vicinity', 'No address available'), place.get('rating'))
                
    
    
                details = gmaps.place(place_id=id, fields=['formatted_phone_number', 'international_phone_number'])
                phone_number = details['result'].get('formatted_phone_number') or details['result'].get('international_phone_number', 'No phone number available')
    
                if phone_number != "No phone number available":
                    phone_number=phone_number.replace(" ","")
    
                
                    phone=phone_country_code+phone_number
                

                places_to_display.append({'name': name,'vicinity': address,'rating': rating,'phone': phone})
                #display for debugging purposes
                print(places_to_display)

            
                #request another page
                #if places_result['next_page_token']:
                    #token = places_result['next_page_token']
                    #print("Want more spots?"+token)
            
        session['places_to_display'] = places_to_display 
        
        return render_template('index.html',places_to_display=places_to_display, timestamp=timestamp)
    
    
    except:
        pass
        
    return render_template('index.html',city=city, country = country, radius = radius)
    
# Route to handle downloading a CSV   
@app.route('/download', methods=['POST'])    
def download_csv():
    
    timestamp = request.form.get('timestamp')
    file_name = f"places_{timestamp}.csv"
    places_to_display = session.get('places_to_display')
    
    with open(file_name, 'a', newline='', encoding='utf-8') as file:
        writer =csv.writer(file, delimiter=';', quotechar='"')
        for place in places_to_display:
            writer.writerow([place['name'], place['vicinity'], place['rating'], place['phone']])
            
        
        pass
    
    # Send the file as an attachment
    return send_file(file_name, as_attachment=True, download_name=file_name)   

# Route to send SMS  
@app.route('/send_sms',methods=['POST'])    
def sms_route():
    
# Construct the SMS URL
    
    selected_numbers = request.form.getlist('selected_numbers')  # Get selected phone numbers
    message = "Hello from the app!"  # Message to send

    if not selected_numbers:
        return "No numbers selected."
    
    #functional but it's interrupted after the first iteration
    # Loop through the selected numbers and open SMS for each
    #for number in selected_numbers:
        #sms_url = f'sms:{number}?body={message}'
        # Here we redirect to the first SMS URL to trigger it (one by one handling)
        #return redirect(sms_url)  # Redirecting to SMS app to send the message
        ####
      
    # Store all the selected numbers in session
    session['remaining_numbers'] = selected_numbers

    # Redirect to the first SMS
    return redirect(url_for('continue_sms'))


    #return "Messages sent!"


    #return redirect(sms_url)

@app.route('/continue_sms')
def continue_sms():
    remaining_numbers = session.get('remaining_numbers', [])
    message = "Hello from the app!"  # Message to send

    if not remaining_numbers:
        return "All messages sent!"  # Show this message when all SMS are sent

    # Get the next number
    next_number = remaining_numbers[0]
    sms_url = f'sms:{next_number}?body={message}'

    # Render the template with the "Send Next SMS" button
    return render_template('continue_sms.html', sms_url=sms_url, remaining_numbers=remaining_numbers)


@app.route('/sms_sent', methods=['POST'])
def sms_sent():
    remaining_numbers = session.get('remaining_numbers', [])

    # After the first SMS is sent, remove it from the list
    if remaining_numbers:
        remaining_numbers.pop(0)

    # Update the session with the remaining numbers
    session['remaining_numbers'] = remaining_numbers

    # Redirect to the continue_sms route to send the next SMS
    return redirect(url_for('continue_sms'))





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)



# Another route for a specific feature, like getting contact info
#@app.route('/contact')
#def contact():
    #return "Contact page"
