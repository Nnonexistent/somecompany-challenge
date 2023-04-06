import React from "react";
import { Link, Outlet } from "react-router-dom";

function Layout() {
  return (
    <div>
      <nav>
        <ul>
          <li><Link to="/login">Login</Link></li>
          <li><Link to="/entries">Dashboard</Link></li>
        </ul>
      </nav>

      <hr />

      <Outlet />
    </div>
  );
}

export default Layout