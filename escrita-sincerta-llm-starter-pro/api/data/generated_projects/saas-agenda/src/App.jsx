import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import EventList from './components/EventList';
import AddEventForm from './components/AddEventForm';

function App() {
  return (
    <Router>
      <div className="app">
        <h1>SaaS Agenda</h1>
        <Routes>
          <Route path="/" element={<EventList />} />
          <Route path="/add" element={<AddEventForm />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;