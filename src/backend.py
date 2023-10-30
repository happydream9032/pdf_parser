from flask import Flask, request
from flask_cors import CORS
import PyPDF2
import re

array = []

result_data = {
    "start" : 0,
    "end" : 0,
    "total_number": 0,
    "total_indemnity": [],
    "total_premium": [],
    "total_net_indemnity" : [],
    "average_indemnity" : [],
    "annual_premium" : [],
    "avg_net_year" : [],
    "indemn_Prem" : [],
    "string_data": [],
    "value_data" : []
}

total_number = 0
total_indemnity = 0
per_indemnity = 0
total_premium = 0
per_prenium = 0
period = 0

app = Flask(__name__)
CORS(app)
@app.route('/api/upload', methods=['POST'])
def upload():
    # Check if the request contains the 'file' parameter
    if 'file' not in request.files:
        return "No file received", 400

    file = request.files['file']

    # Get the file name
    file_name = file.filename

    file.seek(100)
    # Process the file or return the file name
    # You can save it, manipulate it, or perform any other operations

    with open(file_name, 'rb') as pdf_file:
        # Create a PDF reader object

        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Get the total number of pages in the PDF
        num_pages = len(pdf_reader.pages)

        # Extract text from each page
        for page_number in range(num_pages):
            # Get the page object

            if page_number == 0:
                page0 = pdf_reader.pages[page_number]

                # Extract the text from the page
                text_array = page0.extract_text()
                temp_data = text_array.split("\n")
                for text in temp_data:

                    if text.__contains__("Total Net Acres") == True:
                        temp_array = text.split(" | ")

                        period = temp_array[1].replace("All PRF Policies", "")

                        period_array = period.split("-")

                        result_data["start"] = int(period_array[0])
                        result_data["end"] = int(period_array[1])

                        period = float(int(period_array[1]) - int(period_array[0]) + 1)

                        temp = temp_array[2].split(" ")
                        pattern = ","
                        total_number = float(re.sub(pattern, "", temp[1]))
                        result_data["total_number"] = total_number


                    elif text.__contains__("Total Indemnity") == True:
                        indemnity = []
                        indemnity_data = text.replace(" Total Indemnity: ", "")
                        item_array = indemnity_data.split(" ")

                        per_indemnity = float(item_array[0])
                        indemnity.append(per_indemnity)
                        pattern = ","

                        total_indemnity = float(re.sub(pattern, "", item_array[1]))
                        indemnity.append(total_indemnity)
                        result_data["total_indemnity"] = indemnity

                    elif text.__contains__("Total Premium") == True:
                        premium = []
                        premium_data = text.replace(" Total Premium: ", "")
                        item_array = premium_data.split(" ")

                        per_prenium = float(item_array[0])
                        premium.append(per_prenium)
                        pattern = ","

                        total_premium = float(re.sub(pattern, "", item_array[1]))
                        premium.append(total_premium)
                        result_data["total_premium"] = premium

                total_net_indemnity = []
                total_net_indemnity.append(round((total_indemnity-total_premium)/total_number, 2))
                total_net_indemnity.append(total_indemnity-total_premium)
                result_data["total_net_indemnity"] = total_net_indemnity

                average_indemnity = []
                average_indemnity.append(round(per_indemnity/period, 2))
                average_indemnity.append(round(total_indemnity/period, 2))
                result_data["average_indemnity"] = average_indemnity

                annual_premium = []
                annual_premium.append(round(per_prenium/period, 2))
                annual_premium.append(round(total_premium/period, 2))
                result_data["annual_premium"] = annual_premium

                avg_net_year = []
                avg_net_year.append(round(((total_indemnity-total_premium)/total_number)/period, 2))
                avg_net_year.append(round((total_indemnity-total_premium)/period, 2))
                result_data["avg_net_year"] = avg_net_year

                indemn_Prem = []
                indemn_Prem.append(round(per_indemnity/per_prenium, 2))
                indemn_Prem.append(round(per_indemnity/per_prenium, 2))
                result_data["indemn_Prem"] = indemn_Prem

            elif page_number == 1:

                price_array = []

                page1 = pdf_reader.pages[page_number]
                text_array = page1.extract_text()
                temp_data = text_array.split("\n")
                for text in temp_data:
                    if text.__contains__("(") == True and text.__contains__("$") == True:
                        price_array.append(text)

                temp_array = price_array[0].split(" $")
                last_element = temp_array[-1]

                avarage_list = last_element.split("$")
                avarage_value = '$'+ avarage_list[1]+'$'+ avarage_list[2]
                price_array[0] = avarage_value

                price_array.reverse()

                value_array = []
                for price_item in price_array:
                    get_price_split = price_item.split(" (")
                    get_price_remove_symbol = get_price_split[0].replace("$", "")
                    get_price_remove_bracket = get_price_remove_symbol.replace(",","")
                    value_array.append(int(get_price_remove_bracket))

                result_data["string_data"] = price_array
                result_data["value_data"] = value_array  
    return result_data


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
