# Calculate the Distance Between Two Locations
Uses google maps api to get geo coordinates

## Setup
```
cp .env.example .env
```
Add your google api key to the .env file
```
python -m venv code_challenge_virt_env
source code_challenge_virt_env/bin/activate
pip install -r requirements.txt
cd code_challenge
python manage.py migrate  # if first time running
python manage.py runserver
```

## Testing
Use the included postman collection to test the data or you can use the following curl: 
```bash
curl --location --request GET 'http://127.0.0.1:8000/geo_calc/search' \
--header 'Content-Type: application/json' \
--data-raw '{
    "origin_location": "Phoenix, AZ",
    "destination_location": "Los Angeles, CA"
}'
```
origin_location and destination_location can be changed as desired

response should look like the following: 
```json
{
    "Location 1": "Phoenix, AZ, USA",
    "Location 2": "Los Angeles, CA, USA",
    "Distance Between Locations": "574261.72 meters"
}
```