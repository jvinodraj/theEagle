from garminconnect import Garmin

EMAIL = "vinodraj.j@gmail.com"
PASSWORD = "dummy_password"  # Replace with your actual password or use environment variables

client = Garmin(EMAIL, PASSWORD)
client.login()

# Example activity ID
activity_id = 23038610778

details = client.get_activity_details(activity_id)

print(details)