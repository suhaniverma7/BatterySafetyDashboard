BATTERY SAFETY DASHBOARD

1. Put your correct IA2.csv file in this folder, beside app.py.
2. Your CSV must contain columns named battery_temp_C and time_s.
3. Install dependencies:
   pip install -r requirements.txt
4. Run:
   python app.py
5. Open the local URL printed by Flask, usually http://127.0.0.1:5000

The dashboard includes dataset summary cards, Matplotlib visualizations, a manual
temperature input with BMS decision/probability outputs, and a searchable table
preview of the first 100 dataset rows.

Note: The CSV attached in the chat appeared to have one column and did not contain
the required battery_temp_C and time_s columns, so it has not been included here.
