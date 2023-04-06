import { React, useState } from "react";
import api from '../api';

const NewEntryForm = (props) => {
  const [file, setFile] = useState();
  const handleFileChange = (e) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleUploadClick = () => {
    if (!file) {
      return;
    }
    api.createEntry(file)
    .then(props.fetchEntries)
  };

  return (
    <div>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleUploadClick}>Upload</button>
    </div>
  )
}



export default NewEntryForm