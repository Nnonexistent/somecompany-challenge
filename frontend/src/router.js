import { createBrowserRouter } from "react-router-dom";
import EntryList from "./components/EntryList";
import EntryPage from "./components/EntryPage";
import Layout from './components/Layout';
import Login from "./components/Login";
import Vis from "./components/Vis";

const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      {
        index: true,
        Component: EntryList,
      },
      {
        path: "/login",
        Component: Login,
      },
      {
        path: "/entries",
        Component: EntryList,
      },
      {
        path: "/entries/:entryId",
        Component: EntryPage,
      },
      {
        path: "/entries/:entryId/vis/:visId",
        Component: Vis,
      },
],
  },
]);


export default router