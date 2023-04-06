import React, { useState } from "react";
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { storeTokenInLocalStorage } from '../lib/auth';
import { useUser } from '../lib/customHooks';


const Login = () => {

  const navigate = useNavigate();
  const authenticated = useUser();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const doLogin = async (e) => {
    e.preventDefault()
    const token = await api.login({ username, password })
    storeTokenInLocalStorage(token);
    navigate('/')
  }
  const doLogout = async (e) => {
    storeTokenInLocalStorage(null);
    navigate('/')
  }
  if (authenticated) {
    return (
      <div>
        <h1>Already logged in</h1>
        <button onClick={doLogout}>Log out</button>
      </div>
    )
  } else {
    return (
      <div>
        <h1>Login</h1>
        <form onSubmit={doLogin}>
          <div>
            <label htmlFor="username">Username</label>
            <input type="text" required id="username" onChange={(e) => setUsername(e.target.value)} />
          </div>
          <div>
            <label htmlFor="password">Password</label>
            <input type="password" required id="password" onChange={(e) => setPassword(e.target.value)} />
          </div>
          <button type="submit">Submit</button>
        </form>
      </div>
    )
  }
}

export default Login