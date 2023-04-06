import { useEffect, useState } from "react";
import { Link, useParams } from 'react-router-dom';

import api from '../api';
import NewVisForm from './NewVisForm';

const VisList = () => {
  const { entryId } = useParams();

  const [visItems, setVisItems] = useState([]);

  const fetchVisItems = async () => {
    const { data } = await api.getVisList(entryId);
    setVisItems(data);
  };

  useEffect(() => {
    fetchVisItems();
  }, []);

    return (<div>
      <h3>Visualizations</h3>
      <NewVisForm fetchVisItems={fetchVisItems} />
      {visItems.map((vis) => (
        <p key={vis.id}>Vis from {vis.dt} [<Link to={`/entries/${entryId}/vis/${vis.id}`}>open</Link>]</p>
      ))}
    </div>)
}

export default VisList