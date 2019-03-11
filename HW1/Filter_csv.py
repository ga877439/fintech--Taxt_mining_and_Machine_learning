import csv
from datetime import datetime

path = r'C:\Users\User\Desktop\ETF分組\CURRENCY + PRE STOCK (第十五組)\第15組'


start_date = datetime.strptime( "2016/01/01" , "%Y/%m/%d")

with open( path + '\ETF List Filtered.csv', 'w',newline='') as out_file:
	with open( path + '\Currency ETF List (36).csv', 'r') as in_file:
	
		csv_reader = csv.DictReader(in_file)
		csv_writer = csv.writer(out_file)
		csv_writer.writerow(['Symbol', 'ETF Name', 'Inception','Type'])
		
		#讀出
		for a_row in csv_reader:
			symbol = a_row['Symbol']
			etf_name = a_row['ETF Name']
			inception = datetime.strptime( a_row['Inception'], "%Y/%m/%d")
		#寫入	
			if inception  <= start_date:
				csv_writer.writerow([symbol, etf_name, inception.date(), 'Currency'])
		
		
			
	with open( path + '\Preferred Stock ETF List (12).csv', 'r') as in_file:
	
		csv_reader = csv.DictReader(in_file)

		
		#讀出
		for a_row in csv_reader:
			symbol = a_row['Symbol']
			etf_name = a_row['ETF Name']
			inception = datetime.strptime( a_row['Inception'], "%Y/%m/%d")
		#寫入	
			if inception  <= start_date:
				csv_writer.writerow([symbol, etf_name, inception.date(), 'Prefered Stock'])			