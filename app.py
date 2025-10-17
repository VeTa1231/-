from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import pyodbc


app = FastAPI()

conn_str = (
    r"DRIVER={ODBC Driver 17 for SQL Server};"
    r"SERVER=(localdb)\MSSQLLocalDB;"
    r"DATABASE=EventsPlatform;"
    r"Trusted_Connection=yes;"
)


def get_connection():
    return pyodbc.connect(conn_str)


# Pydantic модели

class OrganizerBase(BaseModel):
    name: str
    contact_info: Optional[str] = None


class OrganizerCreate(OrganizerBase):
    pass


class OrganizerRead(OrganizerBase):
    id: int


class VenueBase(BaseModel):
    name: str
    address: Optional[str] = None


class VenueCreate(VenueBase):
    pass


class VenueRead(VenueBase):
    id: int


class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    organizer_id: int
    venue_id: int
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class EventCreate(EventBase):
    pass


class EventRead(EventBase):
    id: int


class TicketBase(BaseModel):
    event_id: int
    price: float
    ticket_type: str
    quantity: int


class TicketCreate(TicketBase):
    pass


class TicketRead(TicketBase):
    id: int


class AttendeeBase(BaseModel):
    ticket_id: int
    name: str
    email: str


class AttendeeCreate(AttendeeBase):
    pass


class AttendeeRead(AttendeeBase):
    id: int


# --- Organizers CRUD ---

@app.post("/organizers/", response_model=OrganizerRead)
def create_organizer(org: OrganizerCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO organizers (name, contact_info) OUTPUT INSERTED.id VALUES (?, ?)",
        org.name, org.contact_info
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return OrganizerRead(id=new_id, **org.model_dump())


@app.get("/organizers/", response_model=List[OrganizerRead])
def read_organizers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, contact_info FROM organizers")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [OrganizerRead(id=row[0], name=row[1], contact_info=row[2]) for row in rows]


@app.get("/organizers/{organizer_id}", response_model=OrganizerRead)
def read_organizer(organizer_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, contact_info FROM organizers WHERE id=?", organizer_id)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Organizer not found")
    return OrganizerRead(id=row[0], name=row[1], contact_info=row[2])


@app.put("/organizers/{organizer_id}", response_model=OrganizerRead)
def update_organizer(organizer_id: int, org: OrganizerCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE organizers SET name=?, contact_info=? WHERE id=?", org.name, org.contact_info, organizer_id)
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Organizer not found")
    conn.commit()
    cursor.close()
    conn.close()
    return OrganizerRead(id=organizer_id, **org.model_dump())


@app.delete("/organizers/{organizer_id}")
def delete_organizer(organizer_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM organizers WHERE id=?", organizer_id)
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Organizer not found")
    conn.commit()
    cursor.close()
    conn.close()
    return {"detail": "Organizer deleted"}


# --- Venues CRUD ---

@app.post("/venues/", response_model=VenueRead)
def create_venue(venue: VenueCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO venues (name, address) OUTPUT INSERTED.id VALUES (?, ?)",
        venue.name, venue.address
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return VenueRead(id=new_id, **venue.model_dump())


@app.get("/venues/", response_model=List[VenueRead])
def read_venues():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, address FROM venues")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [VenueRead(id=row[0], name=row[1], address=row[2]) for row in rows]


@app.get("/venues/{venue_id}", response_model=VenueRead)
def read_venue(venue_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, address FROM venues WHERE id=?", venue_id)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Venue not found")
    return VenueRead(id=row[0], name=row[1], address=row[2])


@app.put("/venues/{venue_id}", response_model=VenueRead)
def update_venue(venue_id: int, venue: VenueCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE venues SET name=?, address=? WHERE id=?", venue.name, venue.address, venue_id)
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Venue not found")
    conn.commit()
    cursor.close()
    conn.close()
    return VenueRead(id=venue_id, **venue.model_dump())


@app.delete("/venues/{venue_id}")
def delete_venue(venue_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM venues WHERE id=?", venue_id)
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Venue not found")
    conn.commit()
    cursor.close()
    conn.close()
    return {"detail": "Venue deleted"}


# --- Events CRUD ---

@app.post("/events/", response_model=EventRead)
def create_event(event: EventCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (title, description, organizer_id, venue_id, start_date, end_date) OUTPUT INSERTED.id VALUES (?, ?, ?, ?, ?, ?)",
        event.title, event.description, event.organizer_id, event.venue_id, event.start_date, event.end_date
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return EventRead(id=new_id, **event.model_dump())


@app.get("/events/", response_model=List[EventRead])
def read_events():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, description, organizer_id, venue_id, start_date, end_date FROM events")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [EventRead(
        id=row[0], title=row[1], description=row[2], organizer_id=row[3],
        venue_id=row[4], start_date=row[5], end_date=row[6]) for row in rows]


@app.get("/events/{event_id}", response_model=EventRead)
def read_event(event_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, description, organizer_id, venue_id, start_date, end_date FROM events WHERE id=?", event_id)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Event not found")
    return EventRead(
        id=row[0], title=row[1], description=row[2], organizer_id=row[3],
        venue_id=row[4], start_date=row[5], end_date=row[6])


@app.put("/events/{event_id}", response_model=EventRead)
def update_event(event_id: int, event: EventCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE events SET title=?, description=?, organizer_id=?, venue_id=?, start_date=?, end_date=? WHERE id=?",
        event.title, event.description, event.organizer_id, event.venue_id, event.start_date, event.end_date, event_id
    )
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Event not found")
    conn.commit()
    cursor.close()
    conn.close()
    return EventRead(id=event_id, **event.model_dump())


@app.delete("/events/{event_id}")
def delete_event(event_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE id=?", event_id)
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Event not found")
    conn.commit()
    cursor.close()
    conn.close()
    return {"detail": "Event deleted"}


# --- Tickets CRUD ---

@app.post("/tickets/", response_model=TicketRead)
def create_ticket(ticket: TicketCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tickets (event_id, price, ticket_type, quantity) OUTPUT INSERTED.id VALUES (?, ?, ?, ?)",
        ticket.event_id, ticket.price, ticket.ticket_type, ticket.quantity
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return TicketRead(id=new_id, **ticket.model_dump())


@app.get("/tickets/", response_model=List[TicketRead])
def read_tickets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, event_id, price, ticket_type, quantity FROM tickets")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [TicketRead(id=row[0], event_id=row[1], price=float(row[2]), ticket_type=row[3], quantity=row[4]) for row in rows]


@app.get("/tickets/{ticket_id}", response_model=TicketRead)
def read_ticket(ticket_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, event_id, price, ticket_type, quantity FROM tickets WHERE id=?", ticket_id)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return TicketRead(id=row[0], event_id=row[1], price=float(row[2]), ticket_type=row[3], quantity=row[4])


@app.put("/tickets/{ticket_id}", response_model=TicketRead)
def update_ticket(ticket_id: int, ticket: TicketCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tickets SET event_id=?, price=?, ticket_type=?, quantity=? WHERE id=?",
        ticket.event_id, ticket.price, ticket.ticket_type, ticket.quantity, ticket_id
    )
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Ticket not found")
    conn.commit()
    cursor.close()
    conn.close()
    return TicketRead(id=ticket_id, **ticket.model_dump())


@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickets WHERE id=?", ticket_id)
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Ticket not found")
    conn.commit()
    cursor.close()
    conn.close()
    return {"detail": "Ticket deleted"}


# --- Attendees CRUD ---

@app.post("/attendees/", response_model=AttendeeRead)
def create_attendee(att: AttendeeCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO attendees (ticket_id, name, email) OUTPUT INSERTED.id VALUES (?, ?, ?)",
        att.ticket_id, att.name, att.email
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    cursor.close()
    conn.close()
    return AttendeeRead(id=new_id, **att.model_dump())


@app.get("/attendees/", response_model=List[AttendeeRead])
def read_attendees():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, ticket_id, name, email FROM attendees")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [AttendeeRead(id=row[0], ticket_id=row[1], name=row[2], email=row[3]) for row in rows]


@app.get("/attendees/{attendee_id}", response_model=AttendeeRead)
def read_attendee(attendee_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, ticket_id, name, email FROM attendees WHERE id=?", attendee_id)
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return AttendeeRead(id=row[0], ticket_id=row[1], name=row[2], email=row[3])


@app.put("/attendees/{attendee_id}", response_model=AttendeeRead)
def update_attendee(attendee_id: int, att: AttendeeCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE attendees SET ticket_id=?, name=?, email=? WHERE id=?",
        att.ticket_id, att.name, att.email, attendee_id
    )
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Attendee not found")
    conn.commit()
    cursor.close()
    conn.close()
    return AttendeeRead(id=attendee_id, **att.model_dump())


@app.delete("/attendees/{attendee_id}")
def delete_attendee(attendee_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendees WHERE id=?", attendee_id)
    if cursor.rowcount == 0:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Attendee not found")
    conn.commit()
    cursor.close()
    conn.close()
    return {"detail": "Attendee deleted"}
