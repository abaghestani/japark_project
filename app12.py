#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

import json
import random
import string
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Constants
TOTAL_SEATS = 25  # Number of seats
TIME_SLOTS = [
    "8-9", "9-10", "10-11", "11-12", "12-13",
    "13-14", "14-15", "15-16", "16-17", "17-18",
    "18-19", "19-20", "20-21", "21-22", "22-23", "23-24"
]
SEAT_PRICES = {'B': 5, 'G': 10}  # Regular and VIP prices
DATA_FILE = "reservations.json"

# Initialize or load reservation data
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {time: {'B': [], 'G': []} for time in TIME_SLOTS}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Reservation data
reservation_data = load_data()

def generate_seat_code():
    """Generate a random 5-character alphanumeric code."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=5))

def reserve_seat(username, time_slots, seat_type, seat_number):
    """Reserve a seat of a particular type at specific time slots."""
    total_cost = 0
    code = generate_seat_code()

    for time_slot in time_slots:
        if seat_number in reservation_data[time_slot][seat_type]:
            return None, 0, f"This seat is already taken for {time_slot}. Please choose another seat."

        reservation_data[time_slot][seat_type].append(seat_number)
        total_cost += SEAT_PRICES[seat_type]

    save_data(reservation_data)  # Save to file after successful reservation
    return code, total_cost, None

def plot_seat_availability(seats_reserved, total_seats=TOTAL_SEATS):
    """Plot seat availability as a grid."""
    fig, ax = plt.subplots(figsize=(8, 6))
    available_seats = set(range(1, total_seats + 1)) - set(seats_reserved)

    for seat in range(1, total_seats + 1):
        if seat in seats_reserved:
            color = 'red'  # Reserved seats
        else:
            color = 'green'  # Available seats
        ax.add_patch(plt.Rectangle(((seat - 1) % 5, (seat - 1) // 5), 1, 1, color=color))

    # Add seat numbers
    for seat in range(1, total_seats + 1):
        x, y = (seat - 1) % 5 + 0.5, (seat - 1) // 5 + 0.5
        ax.text(x, y, str(seat), ha='center', va='center', fontsize=8, color='white')

    ax.set_xlim(0, 5)
    ax.set_ylim(0, total_seats // 5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_aspect('equal')
    plt.gca().invert_yaxis()
    plt.title("Seat Availability")
    return fig

# Streamlit UI
st.title("JAPARK")

# User login
username = st.text_input("Enter your username:")
if username:
    # Seat reservation
    st.subheader("Reserve a Parking Spot")
    time_slot = st.selectbox("Select Time Slot:", TIME_SLOTS)
    seat_type = st.radio("Select Seat Type:", options=["Regular", "VIP"], index=0)
    seat_type_code = 'B' if seat_type == "Regular" else 'G'
    
    # Show seat availability
    st.subheader("Seat Availability")
    seats_reserved = reservation_data[time_slot][seat_type_code]
    seat_fig = plot_seat_availability(seats_reserved)
    st.pyplot(seat_fig)

    # Select seat number
    available_seats = [seat for seat in range(1, TOTAL_SEATS + 1) if seat not in seats_reserved]
    seat_number = st.selectbox("Select Seat Number:", options=available_seats)

    # Reserve seat
    if st.button("Reserve Seat"):
        code, total_cost, error_message = reserve_seat(username, [time_slot], seat_type_code, seat_number)
        if error_message:
            st.error(error_message)
        else:
            st.success(f"Seat {seat_number} reserved successfully! Your booking code: {code}")
            st.info(f"Total cost: ${total_cost}")

