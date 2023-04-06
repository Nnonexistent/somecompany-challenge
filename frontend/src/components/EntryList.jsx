import { Link } from "react-router-dom";
import { React, useEffect, useState } from "react";
import { useUser } from '../lib/customHooks';

import api from '../api';
import NewEntryForm from "./NewEntryForm";

const EntryList = () => {
  const authenticated = useUser(false);
  const [entries, setEntries] = useState([]);

  const fetchEntries = async () => {
    const { data } = await api.getEntriesList();
    const entries = data;
    setEntries(entries);
  };

  useEffect(() => {
    fetchEntries();
  }, []);

  if (!authenticated) {
    return <div>
      <h1>Dashboard</h1>
      <p>Please <Link to="/login">Login</Link></p>
    </div>;
  } else {
    return (<div>
      <h1>Entries</h1>
      <NewEntryForm fetchEntries={fetchEntries} />
      {entries.map((entry) => (
        <p key={entry.id}>Entry from {entry.dt} [<Link to={`/entries/${entry.id}`}>open</Link>]</p>
      ))}
    </div>)
  }
}

export default EntryList