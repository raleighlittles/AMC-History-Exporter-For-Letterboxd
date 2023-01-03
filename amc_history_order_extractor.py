import argparse
import csv
import datetime
import json
import pdb

if __name__ == "__main__":

    argparse_parser = argparse.ArgumentParser()

    argparse_parser.add_argument("-i", "--input-file", type=str, help="The text file containing order history. Must be copied directly from the 'order history', see documentation")
    argparse_parser.add_argument("-o", "--output-file", type=str, help="The output CSV file. This is the file that will be imported into Letterboxd")

    argparse_args = argparse_parser.parse_args()
    
    order_history_filename = argparse_args.input_file
    order_history_file = open(order_history_filename)
    order_history_str = order_history_file.read()

    order_history : dict = json.loads(order_history_str)

    print(len(order_history["edges"]), " orders found in file ", order_history_filename)

    # Prepare the CSV file -- see https://letterboxd.com/about/importing-data/
    # We don't have a way of determining:
    # (1) The year the movie was released, since AMC sometimes shows re-runs
    # (2) The directors of the movie
    # So the only column Letterboxd will actually use is the 'Title' column
    csv_headers = ["Title", "Watched Date", "Theater", "Ticket Cost"]

    current_date = datetime.datetime.now()

    csv_filename = argparse_args.output_file

    with open(csv_filename, 'w') as csv_file_handle:

        csv_writer = csv.writer(csv_file_handle)
        csv_writer.writerow(csv_headers)

        for order_event in order_history["edges"]:

            movies_from_order = list()
            showtimes = list()
            theaters = list()
            ticket_prices = list()

            # Don't count orders that were not fulfilled
            if (order_event["node"]["status"] == "Fulfilled"):

                for ticket_order in order_event["node"]["groups"]:

                    # Make sure the order isn't for a membership/concessions/etc
                    # and that no part of the order was cancelled/refunded
                    if ((ticket_order["type"].startswith("TICKET")) and (ticket_order['cancelledCharges'] is None) and (ticket_order['refundedCharges'] is None)):

                        # I'm not really sure why the order history is nested so much

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
                        # We don't want to add entries for movies if the showing date
                        # is in the future (the movie hasn't been seen yet)
                        showtime_date = datetime.datetime.strptime(showtimes[i], "%Y-%m-%dT%H:%M:%S.%fZ")
                        
                        if (current_date > showtime_date):
                            csv_writer.writerow([movies_from_order[i], showtimes[i].split("T")[0], theaters[i], ticket_prices[i]])

                        else:
                            print("Skipped ", movies_from_order[i], "since the showtime date was in the future")

                else:
                    print("Unable to create row in CSV file, data doesn't match expected format")

        print("Finished processing CSV file")