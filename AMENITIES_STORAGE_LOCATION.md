# Amenities Storage Location in Database

## Answer: Where is "AC, TV, Shower (tanpa water heater), Kettle, Mineral Water" stored?

### Database Location
- **Database**: PostgreSQL (`postgresql://localhost:5432/hotel_db`)
- **Table**: `room_types`
- **Column**: `amenities`
- **Data Type**: Text (string field)

### How It's Organized

Amenities are stored at the **Room Type level**, not at the individual room level. This means:

1. Each room type (Standard Room, Superior Room, Deluxe Room, etc.) has its own amenities list
2. Individual rooms inherit the amenities from their room type
3. All rooms of the same type share the same amenities

### Data Structure

```sql
-- Table: room_types
CREATE TABLE room_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    amenities TEXT,  -- <-- AMENITIES STORED HERE
    ...
)
```

### Example Data

| Room Type ID | Room Type Name        | Room Type Code | Amenities |
|---|---|---|---|
| 1 | Standard Room | STD | AC, TV, Shower (tanpa water heater), Kettle, Mineral Water |
| 2 | Standard Twin Room | STT | AC, TV, Shower (tanpa water heater), Kettle, Mineral Water |
| 3 | Superior Room | SUP | AC, TV, Shower (dengan water heater), Kettle, Mineral Water |
| 4 | Superior Twin Room | SUT | AC, TV, Shower (dengan water heater), Kettle, Mineral Water |
| 5 | Deluxe Room | DEL | AC, TV, Shower (dengan water heater), Mini Fridge, Kettle, Mineral Water |

### How Frontend Receives Amenities

When the API returns room data, it includes the amenities like this:

```json
{
  "id": 101,
  "room_number": "101",
  "floor": 1,
  "room_type_id": 1,
  "room_type": "STD",
  "room_type_name": "Standard Room",
  "amenities": "AC, TV, Shower (tanpa water heater), Kettle, Mineral Water",
  "monthly_rate": 500000,
  ...
}
```

### Why Store at Room Type Level?

This design choice makes sense because:

1. **Consistency**: All rooms of the same type have identical amenities
2. **Maintainability**: Update amenities once, affects all rooms of that type
3. **Storage Efficiency**: No redundant data duplication
4. **Business Logic**: Room types define standardized offerings, individual rooms are instances of those types

### API Implementation

In the backend (`backend/routes/rooms_router.py`), the `_format_room_response()` function retrieves amenities from the room type:

```python
def _format_room_response(room: Room) -> dict:
    return {
        ...
        "amenities": room.room_type.amenities if room.room_type else None,
        ...
    }
```

This ensures that when a room is returned via the API, its amenities (inherited from its room type) are included.

