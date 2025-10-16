import React, { useState } from 'react';
import './AddEventForm.css';

const AddEventForm = () => {
  const [title, setTitle] = useState('');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    // Aqui você pode adicionar lógica para enviar os dados para o backend
    console.log('Event:', { title, date, time });
  };

  return (
    <form onSubmit={handleSubmit} className="add-event-form">
      <div>
        <label htmlFor="title">Title</label>
        <input type="text" id="title" value={title} onChange={(e) => setTitle(e.target.value)} required />
      </div>

      <div>
        <label htmlFor="date">Date</label>
        <input type="date" id="date" value={date} onChange={(e) => setDate(e.target.value)} required />
      </div>

      <div>
        <label htmlFor="time">Time</label>
        <input type="time" id="time" value={time} onChange={(e) => setTime(e.target.value)} required />
      </div>

      <button type="submit">Add Event</button>
    </form>
  );
};

export default AddEventForm;