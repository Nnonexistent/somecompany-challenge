import { useEffect, useState } from "react";
import { useParams } from 'react-router-dom';
import api from '../api';

const NewVisForm = (props) => {
  const { entryId } = useParams();

  const [visType, setVisType] = useState({ 'allowed_chart_types': [] });
  const [chartType, setChartType] = useState();
  const [availableVisTypes, setAvailableVisTypes] = useState([]);

  const handleCreate = () => api.createVis(entryId, visType.vis_type, chartType, []).then(props.fetchVisItems);
  const fetchAvailableVisTypes = async () => {
    const { data } = await api.getVisTypes()
    setAvailableVisTypes(data);
    setVisType(data[0]);
    setChartType(data[0].allowed_chart_types[0]);
  };
  const changeVisType = (event) => {
    const vt = availableVisTypes.find(i => (i.vis_type == event.target.value))
    setVisType(vt);
    setChartType(vt.allowed_chart_types[0]);
  }

  useEffect(() => {
    fetchAvailableVisTypes();
  }, []);

  return (
    <div>
      <p>
        <label htmlFor="vis_type">Type</label>
        <select name="vis_type" onChange={changeVisType}>
          {availableVisTypes.map((visType) => (
            <option key={visType.vis_type} value={visType.vis_type}>{visType.vis_type}</option>
          ))}
        </select>
      </p>
      <p>
        <label htmlFor="chart_type">Chart type</label>
        <select name="chart_type" onChange={(e) => setChartType(e.target.value)}>
          {visType.allowed_chart_types.map((ct) => (
            <option key={ct} value={ct}>{ct}</option>
          ))}
        </select>
      </p>
      <button onClick={handleCreate}>Create</button>
    </div>
  )
}



export default NewVisForm