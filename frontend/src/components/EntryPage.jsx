import { React, useEffect, useState } from "react";
import { useParams } from 'react-router-dom';
import api from '../api';
import VisList from "./VisList";

const EntryPage = () => {
  const { entryId } = useParams();
  const [entry, setEntry] = useState({ teams: [] });

  const fetchEntry = async () => {
    const { data } = await api.getEntry(entryId);
    setEntry(data);
  };
  useEffect(() => {
    fetchEntry();
  }, []);

  return (
    <div>
      entry {entryId}
      <br /><br />
      <table>
        <tbody>
          <tr><td>dt</td><td>{entry.dt}</td></tr>
          <tr><td>date_start</td><td>{entry.date_start}</td></tr>
          <tr><td>date_end</td><td>{entry.date_end}</td></tr>
          <tr><td>teams</td><td>{entry.teams.join(', ')}</td></tr>
          <tr><td>merge_time_min</td><td>{entry.merge_time_min}</td></tr>
          <tr><td>merge_time_max</td><td>{entry.merge_time_max}</td></tr>
          <tr><td>merge_time_mean</td><td>{entry.merge_time_mean}</td></tr>
          <tr><td>merge_time_median</td><td>{entry.merge_time_median}</td></tr>
        </tbody>
      </table>
      <VisList />
    </div>
  )
}

export default EntryPage
