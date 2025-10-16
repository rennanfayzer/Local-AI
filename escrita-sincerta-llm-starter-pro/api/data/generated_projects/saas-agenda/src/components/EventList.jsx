import React from 'react';
import { Event } from '../types';

const EventList = ({ events }: { events: Event[] }) => {
  return (
    <div className="event-list">
      <h2>Agendamentos</h2>
      <ul>
        {events.map((event, index) => (
          <li key={index}>
            <strong>{event.title}</strong> - {event.date} - {event.time}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default EventList;
```

```jsx
// src/types.ts
export interface Event {
  id: string;
  title: string;
  date: string;
  time: string;
}