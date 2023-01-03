import argparse
import json
import pdb
import csv

if __name__ == "__main__":
    
    order_history_filename = "order_history_2022.txt"
    order_history_file = open(order_history_filename)
    order_history_str = order_history_file.read()

    order_history : dict = json.loads(order_history_str)

    print(len(order_history["edges"]), " orders found in file ", order_history_filename)

    # Prepare the CSV file -- these have to match the letterboxd format
    # https://letterboxd.com/about/importing-data/
    csv_headers = ["Title", "Watched Date", "Ticket Cost", "Theater"]

    csv_filename = "order_history.csv"

    with open(csv_filename, 'w') as csv_file_handle:

        csv_writer = csv.writer(csv_file_handle)
        csv_writer.writerow(csv_headers)

        for order_event in order_history["edges"]:

            # To account for the fact that the user can buy multiple tickets at once
            movies_from_order = list()
            showtimes = list()
            theaters = list()
            ticket_prices = list()

            # Don't count orders that were refunded/cancelled
            if (order_event["node"]["status"] == "Fulfilled"):

                for ticket_order in order_event["node"]["groups"]:

                    # Make sure the order isn't for a membership/concessions/etc
                    if (ticket_order["type"].startswith("TICKET")):
                        movies_from_order.append(ticket_order["movie"]["name"])
                        showtimes.append(ticket_order["showtime"]["showDateTimeUtc"])
                        theaters.append(ticket_order["theatre"]["name"])

                        tickets_cost = 0
                        
                        for individual_ticket_order in ticket_order["items"]:
                            tickets_cost += individual_ticket_order["cost"]

                        ticket_prices.append(tickets_cost)

                if (len(movies_from_order) == len(showtimes) == len(theaters) == len(ticket_prices)):
                    for i in range(0, len(movies_from_order)):
                        # Desired date format is YYYY-MM-DD, and the timestamp looks like:
                        # 2021-12-18T20:00:00.000Z
                        # so only extract the date part, ignoring the time
                        csv_writer.writerow([movies_from_order[i], showtimes[i].split("T")[0], theaters[i], ticket_prices[i]])

                else:
                    print("Unable to create row in CSV file, data doesn't match expected format")

        print("Finished processing CSV file")