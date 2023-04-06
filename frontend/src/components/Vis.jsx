import { React, useEffect, useState } from "react";
import { useParams } from 'react-router-dom';
import api from '../api';
import VisList from "./VisList";

const Vis = () => {
  const { entryId, visId } = useParams();
  const [vis, setVis] = useState({});

  const fetchVis = async () => {
    const { data } = await api.getVis(visId);
    setVis(data);
  };
  useEffect(() => {
    fetchVis();
  }, []);

  return (
    <div>
      entry {entryId}<br /> vis {visId}
      <br />
      <p><b>Created: </b> {vis.dt}</p>
      <p><b>Is public: </b> {vis.is_public ? 'yes' : 'no'}</p>
      <p><b>Type: </b> {vis.options?.vis_type}</p>
      <p><b>Chart type: </b> {vis.options?.chart_type}</p>
      {JSON.stringify(vis.data)}
    </div>
  )
}

export default Vis
